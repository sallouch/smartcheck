from fastapi import APIRouter, HTTPException
from services.qr_code_service import QRCodeService

router = APIRouter(prefix="/qr", tags=["QR Code"])
service = QRCodeService()

# Générer un QR code
@router.post("/generate")
def generate_qr(id_seance: int, duree_validite_secondes: int = 30):
    result = service.generate_qr(id_seance, duree_validite_secondes)
    if result.get("success"):
        return result
    raise HTTPException(status_code=400, detail=result.get("message", "Erreur lors de la génération du QR code"))

# Scanner un QR code 
@router.post("/scan")
def scan_qr(qr_token: str, etudiant_id: int):
    result = service.scan_qr(qr_token, etudiant_id)
    if result.get("success"):
        return result
    raise HTTPException(status_code=400, detail=result.get("message", "Erreur lors du scan du QR code"))

# Lister les QR codes actifs
@router.get("/active")
def list_active_qr_codes(id_enseignant: int = None):
    result = service.get_active_qr_codes(id_enseignant)
    if result.get("success"):
        return result
    raise HTTPException(status_code=400, detail="Impossible de récupérer les QR codes actifs")
