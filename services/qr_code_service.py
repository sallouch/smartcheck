import secrets
import qrcode
import base64
import io
from datetime import datetime, timedelta
from typing import Dict, Optional
from database.qr_code_repository import insert_qr_code, get_qr_by_code, deactivate_qr
from database.attendance_repository import add_presence

class QRCodeService:
    def __init__(self):
        pass
    
    def generate_qr(self, id_seance: int, duree_validite_secondes: int = 30) -> Dict:
        """Génère un QR code dynamique pour une séance"""
        try:
            # Générer un code unique
            qr_token = secrets.token_urlsafe(32)
            
            # Calculer les dates
            date_generation = datetime.now().isoformat()
            expire_le = (datetime.now() + timedelta(seconds=duree_validite_secondes)).isoformat()
            
            # Insérer le QR code dans la base
            success = insert_qr_code(
                id_seance=id_seance,
                code=qr_token,
                date_generation=date_generation,
                expire_le=expire_le,
                actif=1
            )
            
            if not success:
                return {"success": False, "message": "Erreur lors de la création du QR code"}
            
            # Créer l'image QR code
            qr_data = f"SMARTCHECK:{id_seance}:{qr_token}"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir en base64 pour l'API
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
            
        except Exception as e:
            return {"success": False, "message": f"Erreur génération QR: {str(e)}"}
    
    def scan_qr(self, qr_token: str, etudiant_id: int) -> Dict:
        """Traite le scan d'un QR code par un étudiant"""
        try:
            # Récupérer le QR code
            qr_data = get_qr_by_code(qr_token)
            if not qr_data:
                return {"success": False, "message": "QR code invalide"}
            
            qr_id, id_seance, code, date_generation, expire_le, actif = qr_data
            
            # Vérifier si le QR code est actif
            if actif != 1:
                return {"success": False, "message": "QR code déjà utilisé"}
            
            # Vérifier l'expiration
            expire_time = datetime.fromisoformat(expire_le)
            if datetime.now() > expire_time:
                # Désactiver le QR code expiré
                deactivate_qr(qr_id)
                return {"success": False, "message": "QR code expiré"}
            
            # Enregistrer la présence
            success = add_presence(
                id_seance=id_seance,
                id_etudiant=etudiant_id,
                present=1
            )
            
            if not success:
                return {"success": False, "message": "Erreur lors de l'enregistrement de la présence"}
            
            # Désactiver le QR code après utilisation
            deactivate_qr(qr_id)
            
            return {
                "success": True,
                "message": "Présence enregistrée avec succès",
                "id_seance": id_seance,
                "id_etudiant": etudiant_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "message": f"Erreur traitement QR: {str(e)}"}
    
    def get_active_qr_codes(self) -> Dict:
        """Récupère tous les QR codes actifs"""
        try:
            from database.qr_code_repository import get_all_qr_codes
            
            qr_codes = get_all_qr_codes(actif=1)
            result = []
            
            for qr in qr_codes:
                qr_id, id_seance, code, date_generation, expire_le, actif = qr
                
                # Vérifier si le QR code n'a pas expiré
                expire_time = datetime.fromisoformat(expire_le)
                if datetime.now() > expire_time:
                    # Désactiver automatiquement les QR codes expirés
                    deactivate_qr(qr_id)
                    continue
                
                result.append({
                    "qr_id": qr_id,
                    "id_seance": id_seance,
                    "code": code,
                    "date_generation": date_generation,
                    "expire_le": expire_le
                })
            
            return {
                "success": True,
                "active_qr_codes": result,
                "count": len(result)
            }
            
        except Exception as e:
            return {"success": False, "message": f"Erreur: {str(e)}"}