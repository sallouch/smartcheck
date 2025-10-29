# database/attendance_repository.py
from typing import List, Tuple, Optional
from .db_connection import get_connection
import sqlite3

def add_session(id_matiere: int, id_classe: int, id_enseignant: int, date: str, heure_debut: str, heure_fin: str) -> bool:
    """
    Insert a new session into the seances table.
    Returns True if successful, False on error (e.g., foreign key violation).
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO seances (id_matiere, id_classe, id_enseignant, date, heure_debut, heure_fin)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_matiere, id_classe, id_enseignant, date, heure_debut, heure_fin))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print("IntegrityError:", e)
        return False
    finally:
        conn.close()

def get_all_sessions() -> List[Tuple]:
    """Return all sessions in the database as a list of tuples."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM seances")
    sessions = cursor.fetchall()
    conn.close()
    return sessions

def get_sessions_by_teacher(id_enseignant: int) -> List[Tuple]:
    """Return all sessions for a specific teacher."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM seances WHERE id_enseignant = ?", (id_enseignant,))
    sessions = cursor.fetchall()
    conn.close()
    return sessions

def add_presence(id_seance: int, id_etudiant: int, present: int = 1) -> bool:
    """
    Insert a presence record for a student in a session.
    present = 1 if student is present, 0 if absent.
    Returns True if successful, False on error.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO presences (id_seance, id_etudiant, present)
            VALUES (?, ?, ?)
        """, (id_seance, id_etudiant, present))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print("IntegrityError:", e)
        return False
    finally:
        conn.close()

def get_presences_by_session(id_seance: int) -> List[Tuple]:
    """Return all presences for a specific session."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM presences WHERE id_seance = ?", (id_seance,))
    presences = cursor.fetchall()
    conn.close()
    return presences
def get_students_by_presence(session_id: int, present: int = 1) -> List[Tuple]:
    """
    Returns a list of students in a session filtered by presence.
    present = 1 => present students
    present = 0 => absent students
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if present == 1:
        # Students marked present
        cursor.execute("""
            SELECT DISTINCT u.nom, u.prenom
            FROM presences p
            JOIN utilisateurs u ON p.id_etudiant = u.id
            WHERE p.id_seance = ? AND p.present = 1
        """, (session_id,))
    else:
        # Students absent (not in presences table as present)
        cursor.execute("""
            SELECT DISTINCT u.nom, u.prenom
            FROM utilisateurs u
            WHERE u.role = 'etudiant' AND u.id NOT IN (
                SELECT id_etudiant
                FROM presences
                WHERE id_seance = ? AND present = 1
            )
        """, (session_id,))
    
    result = cursor.fetchall()
    conn.close()
    return result
