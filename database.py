import sqlite3
import os
from typing import List, Tuple, Optional
import random, string
from datetime import datetime, timedelta

# Database setup

db_path = "smartcheck.db"
def get_connection():
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")# enforce foreign keys
    return conn


def ensure_schema():
    """Create the database and tables from schema.sql if needed."""
    conn = get_connection()
    cursor = conn.cursor()
    if os.path.exists("schema.sql"):
        with open("schema.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()
        cursor.executescript(sql_script)
    else:
        raise FileNotFoundError("schema.sql not found in project folder")
    conn.commit()
    conn.close()#Closes the connection to the database

# ---------- User helper functions ----------

def add_user(nom: str, prenom: str, email: str, mot_de_passe: str, role: str, cin: str) -> bool:
    """
    Insert a new user. Returns True on success, False on integrity error (duplicate email/CIN etc).
    """
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
        # integrity error (unique constraint, not null, foreign key failure, ...)
        print("IntegrityError:", e)
        return False
    finally:
        conn.close()
def get_all_users() -> List[Tuple]:
    """Return a list of all users as tuples (id, nom, prenom, email, ...)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM utilisateurs")
    rows = cursor.fetchall() #Fetches all results from the query into Python
    conn.close()
    return rows
def get_user_by_email(email: str) -> Optional[Tuple]:
    """
    Return a single user tuple matching the given email, or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM utilisateurs WHERE email = ?", (email,))
    user = cursor.fetchone()  # fetchone returns the first row or None
    conn.close()
    return user

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
            INSERT INTO presences (id_seance, id_utilisateur, present)
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






# ---------- Self-test when run directly ----------

if __name__ == "__main__":
    # 1) ensure schema
    try:
        ensure_schema()
        print("Schema ensured.")
    except FileNotFoundError as e:
        print(e)
        raise SystemExit(1)

    # 2) show current users
    users = get_all_users()
    print("Existing users:", users)

    # 3) attempt to add a test user (will print IntegrityError if duplicate)
    ok = add_user("StepUser", "One", "stepuser@example.com", "pass123", "etudiant", "99999999")
    print("Inserted test user:", ok)

    # 4) show users again
    users = get_all_users()
    print("Users after insert:", users)

    found_user = get_user_by_email("stepuser@example.com")
    print("User found by email:", found_user)

    # Test: add a session
    ok = add_session(1, 1, 2, "2025-10-30", "09:00", "11:00")  # id_matiere, id_classe, id_enseignant
    print("Session inserted:", ok)

    sessions = get_all_sessions()
    print("All sessions:", sessions)

    teacher_sessions = get_sessions_by_teacher(2)  # Bob's id
    print("Sessions for teacher id 2:", teacher_sessions)
    # Test: mark Alice present for session 1
    ok = add_presence(id_seance=1, id_etudiant=1, present=1)
    print("Presence inserted:", ok)

    # Show all presences for session 1
    presences = get_presences_by_session(1)
    print("Presences for session 1:", presences)

    qr = generate_qr_code(1)  # generate QR for session 1
    print("Generated QR code for session 1:", qr)

    # Example test: Student with ID 1 scans a QR code
    ok = scan_qr_and_mark_presence(1, "Ax3pZ1bQ")
    print("Presence marked:", ok)

    #List students present in session 1
    present_students = get_students_by_presence(1)
    print("Present students:", present_students)

    # List students absent in session 1
    absent_students = get_students_by_presence(1, 0)
    print("Absent students:", absent_students)



 