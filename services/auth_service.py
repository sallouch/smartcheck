# services/auth_service.py
from datetime import datetime, timedelta
from typing import Optional, Dict
from database.user_repository import get_user_by_email
from database.token_repository import save_token, get_token, delete_token

class AuthService:
    TOKEN_EXPIRE_HOURS = 4

    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[Dict]:
        """
        Authenticate a user by email and password.
        Returns a dict with token info if successful, else None.
        """
        user = get_user_by_email(email)
        if not user:
            return None

        # Password check (plaintext for now, could hash if implemented)
        if user[4] != password:  # index 4 = mot_de_passe
            return None

        # Generate token
        expires_at = (datetime.utcnow() + timedelta(hours=AuthService.TOKEN_EXPIRE_HOURS)).strftime("%Y-%m-%d %H:%M:%S")
        token_str = f"token_{user[0]}_{int(datetime.utcnow().timestamp())}"

        success = save_token(user_id=user[0], role=user[5], token=token_str, expires_at=expires_at)
        if not success:
            return None

        return {
            "access_token": token_str,
            "expires_at": expires_at,
            "user_id": user[0],
            "role": user[5]
        }

    @staticmethod
    def validate_token(token_str: str) -> bool:
        """
        Validate a token: check if it exists and not expired.
        """
        entry = get_token(token_str)
        if not entry:
            return False

        if datetime.utcnow() > entry["expires_at"]:
            delete_token(token_str)  # optional: remove expired token
            return False

        return True
