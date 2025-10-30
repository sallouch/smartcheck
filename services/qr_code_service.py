# services/qr_code_service.py
import secrets
import qrcode
import base64
import io
from datetime import datetime, timedelta
from typing import Dict
from database.qr_code_repository import QRCodeRepository
from database import attendance_repository as att_repo
import qrcode
from qrcode.constants import ERROR_CORRECT_L

class QRCodeService:
    def __init__(self):
        self.qr_repo = QRCodeRepository()

    def generate_qr(self, id_seance: int, duree_validite_secondes: int = 30) -> Dict:
        """Génère un QR code pour une séance"""
        # Vérifier si la séance existe
        sessions = att_repo.get_all_sessions()
        if not any(s[0] == id_seance for s in sessions):
            return {"success": False, "message": "Séance non trouvée"}

        # Générer un code unique
        qr_token = secrets.token_urlsafe(32)
        date_generation = datetime.now().isoformat()
        expire_le = (datetime.now() + timedelta(seconds=duree_validite_secondes)).isoformat()

        # Désactiver les anciens QR codes pour cette séance
        all_qrs = self.qr_repo.get_all_qr_codes()
        for qr in all_qrs:
            if qr[1] == id_seance and qr[5] == 1:  # qr[1]=id_seance, qr[5]=actif
                self.qr_repo.deactivate_qr(qr[0])

        # Insérer le nouveau QR code
        success = self.qr_repo.insert_qr_code(id_seance, qr_token, date_generation, expire_le, 1)
        if not success:
            return {"success": False, "message": "Impossible de créer le QR code"}

        # Générer l'image QR
        qr_data = f"SMARTCHECK:{id_seance}:{qr_token}"
        qr_img = qrcode.QRCode(
            version=1,
            error_correction=ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_img.add_data(qr_data)
        qr_img.make(fit=True)
        img = qr_img.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return {
            "success": True,
            "qr_code_image": qr_base64,
            "qr_token": qr_token,
            "expire_le": expire_le,
            "id_seance": id_seance,
            "duree_validite": duree_validite_secondes
        }

    def scan_qr(self, qr_token: str, etudiant_id: int) -> Dict:
        """Traite le scan d'un QR code par un étudiant"""
        qr_data = self.qr_repo.get_qr_by_code(qr_token)
        if not qr_data:
            return {"success": False, "message": "QR code invalide"}

        qr_id, id_seance, _, date_generation, expire_le, actif = qr_data

        if actif != 1:
            return {"success": False, "message": "QR code déjà utilisé"}

        # Vérifier l'expiration
        if datetime.now() > datetime.fromisoformat(expire_le):
            self.qr_repo.deactivate_qr(qr_id)
            return {"success": False, "message": "QR code expiré"}

        # Vérifier si présence déjà enregistrée
        presences = att_repo.get_presences_by_session(id_seance)
        if any(p[1] == etudiant_id for p in presences):  # p[1] = id_etudiant
            return {"success": False, "message": "Présence déjà enregistrée"}

        # Enregistrer la présence
        success = att_repo.add_presence(id_seance, etudiant_id, 1)
        if not success:
            return {"success": False, "message": "Impossible d'enregistrer la présence"}

        # Désactiver le QR code après utilisation
        self.qr_repo.deactivate_qr(qr_id)

        return {
            "success": True,
            "message": "Présence enregistrée avec succès",
            "id_seance": id_seance,
            "id_etudiant": etudiant_id,
            "timestamp": datetime.now().isoformat()
        }

    def get_active_qr_codes(self, id_enseignant: int = None) -> Dict:
        """Récupère les QR codes actifs, optionnellement filtrés par enseignant"""
        active_qrs = self.qr_repo.get_all_qr_codes(actif=1)
        result = []

        sessions = att_repo.get_all_sessions() if id_enseignant else None

        for qr in active_qrs:
            qr_id, id_seance, code, date_gen, expire_le, _ = qr

            # Vérifier expiration
            if datetime.now() > datetime.fromisoformat(expire_le):
                self.qr_repo.deactivate_qr(qr_id)
                continue

            # Filtrage par enseignant si demandé
            if id_enseignant and sessions:
                session = next((s for s in sessions if s[0] == id_seance), None)
                if not session or session[3] != id_enseignant:  # session[3] = id_enseignant
                    continue
                date, heure_debut, id_matiere, id_classe, *_ = session
            else:
                session = next((s for s in sessions if s[0] == id_seance), None) if sessions else None
                date, heure_debut = session[4], session[5] if session else ("Unknown", "Unknown")

            result.append({
                "qr_id": qr_id,
                "id_seance": id_seance,
                "code": code,
                "date_generation": date_gen,
                "expire_le": expire_le,
                "date_seance": date,
                "heure_debut": heure_debut
            })

        return {"success": True, "active_qr_codes": result, "count": len(result)}
