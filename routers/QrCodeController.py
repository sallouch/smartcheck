# routers/qr_code_controller.py
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import qrcode
import secrets
import io
import base64

router = APIRouter(
    prefix="/qr",
    tags=["QR Code"]
)

# Dictionnaire temporaire pour stocker les QR codes actifs
active_qr_codes = {}

@router.get("/generate/{session_id}")
async def generate_qr_code(session_id: int):
    """
    Génère un QR code contenant l'ID de la séance et un code secret unique.
    Le QR code se régénère toutes les 10 secondes pendant 3 minutes.
    """
    end_time = datetime.now() + timedelta(minutes=3)
    qr_images = []

    while datetime.now() < end_time:
        # Génération d’un code secret unique à 16 caractères
        secret_code = secrets.token_hex(8)

        # Enregistrement du code temporaire pour validation ultérieure
        active_qr_codes[session_id] = {
            "secret": secret_code,
            "expires": datetime.now() + timedelta(seconds=10)
        }

        # Contenu du QR code
        qr_data = {
            "session_id": session_id,
            "secret_code": secret_code
        }

        # Génération du QR code en image
        qr = qrcode.make(str(qr_data))
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        # On ajoute le QR encodé dans une liste (tu peux l’afficher côté front)
        qr_images.append(qr_base64)

    return {"message": "QR codes générés pendant 3 minutes", "qr_codes": qr_images}


@router.get("/validate/{session_id}/{secret_code}")
async def validate_qr(session_id: int, secret_code: str):
    """
    Vérifie si le QR scanné est encore valide (code secret + expiration 10s)
    """
    qr_info = active_qr_codes.get(session_id)
    if not qr_info:
        raise HTTPException(status_code=404, detail="QR code non trouvé")

    if qr_info["secret"] != secret_code or datetime.now() > qr_info["expires"]:
        raise HTTPException(status_code=400, detail="QR code expiré ou invalide")

    return {"valid": True, "message": "QR code valide"}
