class Classe:
    """
    Modèle représentant une classe dans la table 'classes'.
    """
    def __init__(self, id: int, nom_classe: str, niveau: str = None, departement: str = None):
        self.id = id
        self.nom_classe = nom_classe
        self.niveau = niveau
        self.departement = departement

    def to_dict(self):
        return {
            "id": self.id,
            "nom_classe": self.nom_classe,
            "niveau": self.niveau,
            "departement": self.departement
        }
class Matiere:
    """
    Modèle représentant une matière dans la table 'matieres'.
    """
    def __init__(self, id: int, nom_matiere: str, code_matiere: str, id_enseignant: int = None):
        self.id = id
        self.nom_matiere = nom_matiere
        self.code_matiere = code_matiere
        self.id_enseignant = id_enseignant

    def to_dict(self):
        return {
            "id": self.id,
            "nom_matiere": self.nom_matiere,
            "code_matiere": self.code_matiere,
            "id_enseignant": self.id_enseignant
        }
class Seance:
    """
    Modèle représentant une séance dans la table 'seances'.
    """
    def __init__(self, id: int, id_matiere: int, id_classe: int, id_enseignant: int,
                 date: str, heure_debut: str, heure_fin: str, statut: str = "en_attente"):
        self.id = id
        self.id_matiere = id_matiere
        self.id_classe = id_classe
        self.id_enseignant = id_enseignant
        self.date = date
        self.heure_debut = heure_debut
        self.heure_fin = heure_fin
        self.statut = statut

    def to_dict(self):
        return {
            "id": self.id,
            "id_matiere": self.id_matiere,
            "id_classe": self.id_classe,
            "id_enseignant": self.id_enseignant,
            "date": self.date,
            "heure_debut": self.heure_debut,
            "heure_fin": self.heure_fin,
            "statut": self.statut
        }
