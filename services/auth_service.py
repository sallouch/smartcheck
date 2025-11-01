from datetime import datetime, timedelta
from typing import Optional, Dict
from database.user_repository import get_user_by_email
from database.token_repository import save_token, get_token, delete_token
import bcrypt
from pydantic import BaseModel, EmailStr

# ----------------- Pydantic Models -----------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    expires_at: str
    user_id: int
    role: str

# ----------------- AuthService -----------------
class AuthService:
    TOKEN_EXPIRE_HOURS = 4

    @staticmethod
    def authenticate_user(data: LoginRequest) -> Optional[TokenResponse]:
        """
        Authenticate a user by email and password (hashed check).
        Returns a TokenResponse if successful, else None.
        """
        user = get_user_by_email(data.email)
        if not user:
            return None

        hashed_pw = user[4]  # colonne mot_de_passe
        # Vérifie que le mot de passe correspond au hash
        if not bcrypt.checkpw(data.password.encode('utf-8'), hashed_pw.encode('utf-8')):
            return None

        # Générer token
        expires_at = (datetime.utcnow() + timedelta(hours=AuthService.TOKEN_EXPIRE_HOURS)).strftime("%Y-%m-%d %H:%M:%S")
        token_str = f"token_{user[0]}_{int(datetime.utcnow().timestamp())}"

        success = save_token(user_id=user[0], role=user[5], token=token_str, expires_at=expires_at)
        if not success:
            return None

        return TokenResponse(
            access_token=token_str,
            expires_at=expires_at,
            user_id=user[0],
            role=user[5]
        )

    @staticmethod
    def validate_token(token_str: str) -> bool:
        entry = get_token(token_str)
        if not entry:
            return False

        if datetime.utcnow() > entry["expires_at"]:
            delete_token(token_str)
            return False

        return True