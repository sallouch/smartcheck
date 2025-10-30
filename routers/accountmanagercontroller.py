from fastapi import APIRouter, HTTPException
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ------------------- Login -------------------
@router.post("/login")
def login(email: str, password: str):
    result = AuthService.authenticate_user(email, password)
    if result:
        return result
    raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect.")

# ------------------- Validate Token -------------------
@router.get("/validate")
def validate_token(token: str):
    is_valid = AuthService.validate_token(token)
    return {"valid": is_valid}

# ------------------- Logout -------------------
@router.post("/logout")
def logout(token: str):
    from database.token_repository import delete_token
    success = delete_token(token)
    if success:
        return {"message": "Déconnexion réussie."}
    raise HTTPException(status_code=400, detail="Token invalide ou déjà supprimé.")









