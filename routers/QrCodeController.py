from fastapi import APIRouter, HTTPException
from services.qrcode_service import QRCodeService
from ..database.qr_code_repository import QRCodeRepository
from ..database.attendance_repository import AttendanceRepository

qr_repo = QRCodeRepository()
attendance_repo = AttendanceRepository()  
qr_service = QRCodeService(qr_repo, attendance_repo)

router = APIRouter(prefix="/qr", tags=["QR Code"])

# Génération du QR
@router.post("/generate")
def generate_qr(id_seance: int, duree_regeneration: int):
    try:
        token = qr_service.generate_qr(id_seance, duree_regeneration)
        return {
            "message": "QR généré",
            "qr_token": token,
            "seance_id": id_seance
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Scan du QR
@router.post("/scan")
def scan_qr(qr_token: str, etudiant_id: int):
    try:
        presence = qr_service.scan_qr(qr_token, etudiant_id)
        return {
            "message": "Présence enregistrée",
            "presence": presence
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
