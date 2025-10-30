from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from database.user_repository import AccountRepository  
from user_models import Token

router = APIRouter(prefix="/account", tags=["Account"])

account_repo = AccountRepository()



# Générer un token pour un utilisateur

"""@router.post("/generate_token")
def generate_token(user_id: int, role: str):
    
    Crée un token pour un utilisateur et l'enregistre dans la base via le repository.
    
    expires = datetime.utcnow() + timedelta(hours=4)
    token = f"token_{user_id}_{role}_{int(expires.timestamp())}"

    success = account_repo.save_token(user_id=user_id, role=role, token=token, expires_at=expires)
    if not success:
        raise HTTPException(status_code=500, detail="Impossible de générer le token")

    return {"message": "Token généré", "access_token": token, "expires_at": expires}"""



# Valider un token

@router.post("/validate_token")
def validate_token(token: Token):
    """
    Vérifie si un token existe et n'est pas expiré, via le repository.
    """
    entry = account_repo.get_token(token)
    if not entry:
        raise HTTPException(status_code=401, detail="Token invalide")

    if datetime.utcnow() > entry["expires_at"]:
        raise HTTPException(status_code=401, detail="Token expiré")

    return {"valid": True, "user_id": entry["user_id"], "role": entry["role"]}







