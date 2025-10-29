from datetime import datetime, timedelta
import random, string
from .db_connection import get_connection
import sqlite3

def generate_qr_code(id_seance: int, expire_seconds: int = 10) -> str:
    """
    Generate a random QR code for a session that expires after `expire_seconds`.
    Stores it in the qrcodes table.
    Returns the QR code string.
    """
    # Generate a random 8-character alphanumeric code
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    now = datetime.now()
    expire_time = now + timedelta(seconds=expire_seconds)

    # Store the QR code in the database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO qrcodes (id_seance, code, date_generation, expire_le, actif)
        VALUES (?, ?, ?, ?, 1)
    """, (
        id_seance,
        code,
        now.strftime("%Y-%m-%d %H:%M:%S"),
        expire_time.strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

    return code

def scan_qr_and_mark_presence(id_etudiant: int, qr_code: str) -> bool:
    """
    Validates a QR code and marks the student present if valid.
    Returns True if successfully marked, False otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Get QR code info
    cursor.execute("""
        SELECT id, id_seance, expire_le, actif 
        FROM qrcodes 
        WHERE code = ?
    """, (qr_code,))
    row = cursor.fetchone()

    if row is None:
        print("QR code not found.")
        conn.close()
        return False

    id_qr, id_seance, expire_le_str, actif = row
    expire_le = datetime.strptime(expire_le_str, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()

    if not actif or now > expire_le:
        print("QR code expired or inactive.")
        conn.close()
        return False

    # Mark presence
    try:
        cursor.execute("""
            INSERT INTO presences (id_seance, id_etudiant, present)
            VALUES (?, ?, 1)
        """, (id_seance, id_etudiant))
        conn.commit()

        # Optionally, deactivate QR code after use
        cursor.execute("UPDATE qrcodes SET actif = 0 WHERE id = ?", (id_qr,))
        conn.commit()

        return True
    except sqlite3.IntegrityError as e:
        print("IntegrityError:", e)
        return False
    finally:
        conn.close()