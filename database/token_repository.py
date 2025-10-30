# database/token_repository.py
from typing import Optional, Dict
import sqlite3
from .db_connection import get_connection
from datetime import datetime

def save_token(user_id: int, role: str, token: str, expires_at: str) -> bool:
    """
    Save a new token in the database.
    Returns True if successful, False on integrity error.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO tokens (access_token, user_id, role, expires_at)
            VALUES (?, ?, ?, ?)
        """, (token, user_id, role, expires_at))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print("IntegrityError:", e)
        return False
    finally:
        conn.close()


def get_token(access_token: str) -> Optional[Dict]:
    """
    Retrieve a token record by its access_token.
    Returns a dict with token info or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, access_token, user_id, role, expires_at
        FROM tokens
        WHERE access_token = ?
    """, (access_token,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "access_token": row[1],
            "user_id": row[2],
            "role": row[3],
            "expires_at": datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
        }
    return None


def delete_token(access_token: str) -> bool:
    """
    Delete a token from the database.
    Returns True if a row was deleted, False otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tokens WHERE access_token = ?", (access_token,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted
