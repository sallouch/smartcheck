from datetime import datetime
from enum import Enum


# Définition des rôles possibles pour les utilisateurs
class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class User:
    """
    Modèle représentant un utilisateur dans la table 'utilisateurs'.

    Attributs :
        id (int) : matricule / numéro d'inscription
        nom (str) : nom complet de l'utilisateur
        email (str) : adresse e-mail
        mot_de_passe (str) : mot de passe (stocké hashé si nécessaire)
        role (str) : rôle de l'utilisateur ('student', 'teacher', 'admin')
    """

    def __init__(self, id: int, nom: str, prenom: str, email: str, mot_de_passe: str,
                 role: str, matricule: str = None, numero_inscription: str = None,
                 cin: str = None, date_creation: str = None):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.mot_de_passe = mot_de_passe
        self.role = role
        self.matricule = matricule
        self.numero_inscription = numero_inscription
        self.cin = cin
        self.date_creation = date_creation

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "prenom": self.prenom,
            "email": self.email,
            "role": self.role,
            "matricule": self.matricule,
            "numero_inscription": self.numero_inscription,
            "cin": self.cin,
            "date_creation": self.date_creation
        }


class Token:
    """
    Modèle représentant un token d'accès dans la table 'tokens'.

    Attributs :
        access_token (str) : chaîne représentant le token
        user_id (int) : ID de l'utilisateur auquel le token appartient
        role (str) : rôle de l'utilisateur
        expires_at (str) : date/heure d'expiration du token (ISO format)
    """
    def __init__(self, access_token: str, user_id: int, role: str, expires_at: str):
        self.access_token = access_token
        self.user_id = user_id
        self.role = role
        self.expires_at = expires_at

    def to_dict(self):
        """
        Convertit l'objet Token en dictionnaire pour les réponses API.
        """
        return {
            "access_token": self.access_token,
            "token_type": "bearer",
            "user_id": self.user_id,
            "role": self.role,
            "expires_at": self.expires_at
        }
