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
