from typing import List, Tuple, Optional
import sqlite3
from datetime import datetime
from database.db_connection import get_connection



import sqlite3
from services.auth_utils import hash_password

DB_PATH = "database.db"

def add_user(nom, prenom, email, mot_de_passe, role):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Hash du mot de passe
    hashed = hash_password(mot_de_passe)

    cursor.execute(
        "INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe, role) VALUES (?, ?, ?, ?, ?)",
        (nom, prenom, email, hashed, role)
    )

    conn.commit()
    conn.close()


def get_all_users() -> List[Tuple]:
    """Return a list of all users as tuples (id, nom, prenom, email, ...)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM utilisateurs")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_user_by_email(email: str) -> Optional[Tuple]:
    """Return a single user tuple matching the given email, or None if not found."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM utilisateurs WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

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









