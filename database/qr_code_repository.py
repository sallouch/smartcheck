from typing import Optional, Tuple, List
import sqlite3
from .db_connection import get_connection
def insert_qr_code(id_seance: int,code: str,date_generation: str,expire_le: str,actif: int = 1) -> bool:
    """
    Inserts a new QR code record into the database.
    Only stores data — does not generate or validate logic.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO qrcodes (id_seance, code, date_generation, expire_le, actif)
            VALUES (?, ?, ?, ?, ?)
        """, (id_seance, code, date_generation, expire_le, actif))
        conn.commit()
        return True
    except Exception as e:
        print("Error (insert_qr_code):", e)
        return False
    finally:
        conn.close()


def get_qr_by_code(code: str) -> List[Tuple]:
    """
    Fetch a QR code record by its code value.
    Returns tuple (id, id_seance, code, date_generation, expire_le, actif)
    or None if not found.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, id_seance, code, date_generation, expire_le, actif FROM qrcodes WHERE code = ?", (code,))
    row = cur.fetchone()
    conn.close()
    return row

def deactivate_qr(qr_id: int) -> bool:
    """
    Marks a QR code as inactive.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE qrcodes SET actif = 0 WHERE id = ?", (qr_id,))
        conn.commit()
        return True
    except Exception as e:
        print("Error (deactivate_qr):", e)
        return False
    finally:
        conn.close()


def get_all_qr_codes(actif: Optional[int] = None) -> List[Tuple]:
    """
    Returns a list of all QR codes.
    If 'actif' is provided, filters by active/inactive status.
    """
    conn = get_connection()
    cur = conn.cursor()
    if actif is None:
        cur.execute("SELECT * FROM qrcodes")
    else:
        cur.execute("SELECT * FROM qrcodes WHERE actif = ?", (actif,))
    rows = cur.fetchall()
    conn.close()
    return rows
