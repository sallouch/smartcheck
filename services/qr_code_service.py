import secrets
import qrcode
import base64
import io
from datetime import datetime, timedelta
from typing import Dict
from database.qr_code_repository import QRCodeRepository
from database import attendance_repository as att_repo
from qrcode.constants import ERROR_CORRECT_L

class QRCodeService:
    def __init__(self):
        self.qr_repo = QRCodeRepository()

    def generate_qr(self, id_seance: int, duree_validite_secondes: int = 30) -> Dict:
        sessions = att_repo.get_all_sessions()
        if not any(s[0] == id_seance for s in sessions):
            return {"success": False, "message": "Séance non trouvée"}

        qr_token = secrets.token_urlsafe(32)
        expire_le = (datetime.now() + timedelta(seconds=duree_validite_secondes)).isoformat()

        # Désactiver anciens QR codes
        for qr in self.qr_repo.get_all_qr_codes():
            if qr[1] == id_seance and qr[5] == 1:
                self.qr_repo.deactivate_qr(qr[0])

        self.qr_repo.insert_qr_code(id_seance, qr_token, datetime.now().isoformat(), expire_le, 1)

        qr_data = f"SMARTCHECK:{id_seance}:{qr_token}"
        qr_img = qrcode.QRCode(version=1, error_correction=ERROR_CORRECT_L, box_size=10, border=4)
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
            "id_seance": id_seance
        }

    def scan_qr(self, qr_token: str, etudiant_id: int) -> Dict:
        qr_data = self.qr_repo.get_qr_by_code(qr_token)
        if not qr_data:
            return {"success": False, "message": "QR code invalide"}

        qr_id, id_seance, _, _, expire_le, actif = qr_data
        if actif != 1:
            return {"success": False, "message": "QR code déjà utilisé"}

        if datetime.now() > datetime.fromisoformat(expire_le):
            self.qr_repo.deactivate_qr(qr_id)
            return {"success": False, "message": "QR code expiré"}

        presences = att_repo.get_presences_by_session(id_seance)
        if any(p[1] == etudiant_id for p in presences):
            return {"success": False, "message": "Présence déjà enregistrée"}

        att_repo.add_presence(id_seance, etudiant_id, 1)
        return {"success": True, "message": "Présence enregistrée avec succès"}

    def get_active_qr_codes(self, id_enseignant: int = None) -> Dict:
        """Retourne tous les QR codes actifs, optionnellement filtrés par enseignant"""
        active_qrs = self.qr_repo.get_all_qr_codes(actif=1)
        sessions = att_repo.get_all_sessions() if id_enseignant else None
        result = []

        for qr in active_qrs:
            qr_id, id_seance, code, date_gen, expire_le, _ = qr
            if datetime.now() > datetime.fromisoformat(expire_le):
                self.qr_repo.deactivate_qr(qr_id)
                continue

            # Filtrer par enseignant si demandé
            if id_enseignant and sessions:
                session = next((s for s in sessions if s[0] == id_seance), None)
                if not session or session[3] != id_enseignant:
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
