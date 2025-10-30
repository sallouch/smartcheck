# database/user_repository.py
from typing import List, Tuple, Optional
import sqlite3
from datetime import datetime
from .db_connection import get_connection

# ---------------- User functions ----------------

def add_user(nom: str, prenom: str, email: str, mot_de_passe: str, role: str, cin: str) -> bool:
    """Insert a new user. Returns True on success, False on integrity error (duplicate email/CIN etc)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe, role, cin)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nom, prenom, email, mot_de_passe, role, cin))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print("IntegrityError:", e)
        return False
    finally:
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
