from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ------------------- Pydantic Models -------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    expires_at: str
    user_id: int
    role: str

# ------------------- Login -------------------
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    """
    Endpoint pour authentifier un utilisateur.
    """
    result = AuthService.authenticate_user(data)
    if result:
        return result
    raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect.")

# ------------------- Validate Token -------------------
@router.get("/validate")
def validate_token(token: str):
    """
    Vérifie si le token est encore valide.
    """
    is_valid = AuthService.validate_token(token)
    return {"valid": is_valid}

# ------------------- Logout -------------------
@router.post("/logout")
def logout(token: str):
    """
    Supprime un token pour déconnexion.
    """
    from database.token_repository import delete_token
    success = delete_token(token)
    if success:
        return {"message": "Déconnexion réussie."}
    raise HTTPException(status_code=400, detail="Token invalide ou déjà supprimé.")









