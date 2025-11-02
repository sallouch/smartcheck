# create_users.py
import sqlite3
import bcrypt
from datetime import datetime

DB_PATH = "smartcheck.db"  # Chemin vers ta base

# ----------------- Utilisateurs -----------------
users = [
    {"nom": "Alice", "prenom": "Marie", "email": "alice@example.com", "password": "pass123", "role": "etudiant", "cin": "12345678"},
    {"nom": "Bob", "prenom": "Jean", "email": "bob@example.com", "password": "pass456", "role": "enseignant", "cin": "23456789"},
    {"nom": "BenAli", "prenom": "Karim", "email": "karim.benali@univ.tn", "password": "pass123", "role": "enseignant", "cin": "34567890"},
    {"nom": "trojet", "prenom": "islem", "email": "islem@trojet.tn", "password": "pass123", "role": "admin", "cin": "76549898"},
    {"nom": "boujdaria", "prenom": "fatma", "email":"fatma@bouj.com", "password":"pass123", "role":"etudiant", "cin":"98765432"},
    {"nom": "esselmi", "prenom": "houda", "email":"houda@esselmi.com", "password":"pass123", "role":"enseignant", "cin":"87654321"},
]

# ----------------- Classes -----------------
classes = [
    {"nom_classe": "Licence 1 Info", "niveau": "L1", "departement": "Info"},
    {"nom_classe": "Licence 2 Info", "niveau": "L2", "departement": "Info"},
    {"nom_classe": "Licence 3 Info", "niveau": "L3", "departement": "Info"},
]

# ----------------- Matières -----------------
matieres = [
    {"nom_matiere": "Mathématiques", "code_matiere": "MATH101", "id_enseignant": 2},
    {"nom_matiere": "Informatique", "code_matiere": "INFO101", "id_enseignant": 3},
    {"nom_matiere": "Physique", "code_matiere": "PHYS101", "id_enseignant": 3},
]

# ----------------- Séances -----------------
seances = [
    {"id_matiere": 1, "id_enseignant": 2, "id_classe": 1, "date": "2025-02-01", "heure_debut": "08:00", "heure_fin": "10:00", "statut": "en_attente"},
    {"id_matiere": 2, "id_enseignant": 3, "id_classe": 2, "date": "2025-02-01", "heure_debut": "10:00", "heure_fin": "12:00", "statut": "en_attente"},
    {"id_matiere": 3, "id_enseignant": 3, "id_classe": 3, "date": "2025-02-02", "heure_debut": "14:00", "heure_fin": "16:00", "statut": "en_attente"},
]

# ----------------- Fonctions utilitaires -----------------
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(plain_password: str) -> str:
    hashed = bcrypt.hashpw(plain_password[:72].encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

# ----------------- Insertions -----------------
def insert_utilisateurs():
    conn = get_connection()
    cursor = conn.cursor()
    for u in users:
        try:
            hashed_pw = hash_password(u["password"])
            cursor.execute("""
                INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe, role, cin)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (u["nom"], u["prenom"], u["email"], hashed_pw, u["role"], u["cin"]))
            print(f"Utilisateur {u['email']} créé.")
        except sqlite3.IntegrityError as e:
            print(f"Erreur utilisateur {u['email']}: {e}")
    conn.commit()
    conn.close()

def insert_classes():
    conn = get_connection()
    cursor = conn.cursor()
    for c in classes:
        try:
            cursor.execute("""
                INSERT INTO classes (nom_classe, niveau, departement)
                VALUES (?, ?, ?)
            """, (c["nom_classe"], c["niveau"], c["departement"]))
            print(f"Classe {c['nom_classe']} créée.")
        except sqlite3.IntegrityError as e:
            print(f"Erreur classe {c['nom_classe']}: {e}")
    conn.commit()
    conn.close()

def insert_matieres():
    conn = get_connection()
    cursor = conn.cursor()
    for m in matieres:
        try:
            cursor.execute("""
                INSERT INTO matieres (nom_matiere, code_matiere, id_enseignant)
                VALUES (?, ?, ?)
            """, (m["nom_matiere"], m["code_matiere"], m["id_enseignant"]))
            print(f"Matière {m['nom_matiere']} créée.")
        except sqlite3.IntegrityError as e:
            print(f"Erreur matière {m['nom_matiere']}: {e}")
    conn.commit()
    conn.close()

def insert_seances():
    conn = get_connection()
    cursor = conn.cursor()
    for s in seances:
        try:
            cursor.execute("""
                INSERT INTO seances (id_matiere, id_enseignant, id_classe, date, heure_debut, heure_fin, statut)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (s["id_matiere"], s["id_enseignant"], s["id_classe"], s["date"], s["heure_debut"], s["heure_fin"], s["statut"]))
            print(f"Séance {s['id_matiere']} pour classe {s['id_classe']} créée.")
        except sqlite3.IntegrityError as e:
            print(f"Erreur séance {s['id_matiere']}: {e}")
    conn.commit()
    conn.close()

# ----------------- Execution -----------------
if __name__ == "__main__":
    insert_utilisateurs()
    insert_classes()
    insert_matieres()
    insert_seances()
    print("Insertion complète.")




