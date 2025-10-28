# routers/account_manager_controller.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import secrets

router = APIRouter(
    prefix="/account",
    tags=["Account Management"]
)

# Simuler une "base de données" temporaire en mémoire
users_db = {}

class User(BaseModel):
    username: str
    email: str
    password: str
    role: str  # "student" ou "teacher"
    verified: bool = False

@router.post("/register")
async def register_user(user: User):
    """
    Inscription d’un utilisateur avec double authentification simulée.
    """
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Utilisateur déjà existant")

    # Génération d’un code de vérification
    verification_code = secrets.token_hex(3)
    users_db[user.username] = user.dict()
    users_db[user.username]["verification_code"] = verification_code

    # Simuler l’envoi d’un e-mail de vérification
    return {"message": f"Utilisateur créé. Code de vérification envoyé : {verification_code}"}

@router.post("/verify/{username}/{code}")
async def verify_user(username: str, code: str):
    """
    Validation du compte après réception du code.
    """
    user = users_db.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    if user["verification_code"] != code:
        raise HTTPException(status_code=400, detail="Code incorrect")

    user["verified"] = True
    return {"message": "Compte vérifié avec succès !"}


@router.post("/login")
async def login_user(username: str, password: str):
    """
    Authentification utilisateur.
    """
    user = users_db.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    if user["password"] != password:
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    if not user["verified"]:
        raise HTTPException(status_code=401, detail="Compte non vérifié")

    return {"message": f"Bienvenue {username} !"}