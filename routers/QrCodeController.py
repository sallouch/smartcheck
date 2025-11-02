from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.qr_code_service import QRCodeService

router = APIRouter(prefix="/qr", tags=["QR Code"])
service = QRCodeService()

# -------------------- Modèles --------------------
class GenerateQRRequest(BaseModel):
    id_seance: int
    duree_validite_secondes: int = 30

class ScanQRRequest(BaseModel):
    qr_token: str
    etudiant_id: int

# -------------------- Routes --------------------
@router.post("/generate")
def generate_qr(data: GenerateQRRequest):
    result = service.generate_qr(data.id_seance, data.duree_validite_secondes)
    if result.get("success"):
        return result
    raise HTTPException(status_code=400, detail=result.get("message"))

@router.post("/scan")
def scan_qr(data: ScanQRRequest):
    result = service.scan_qr(data.qr_token, data.etudiant_id)
    if result.get("success"):
        return result
    raise HTTPException(status_code=400, detail=result.get("message"))

@router.get("/active")
def list_active_qr_codes(id_enseignant: int = None):
    result = service.get_active_qr_codes(id_enseignant)
    if result.get("success"):
        return result
    raise HTTPException(status_code=400, detail="Impossible de récupérer les QR codes actifs")



