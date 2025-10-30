#attendance models.py
class Presence:
    """
    Modèle représentant une présence d'un étudiant à une séance.
    """
    def __init__(self, id: int, id_seance: int, id_etudiant: int, present: int,
                 timestamp: str = None):
        self.id = id
        self.id_seance = id_seance
        self.id_etudiant = id_etudiant
        self.present = present
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "id": self.id,
            "id_seance": self.id_seance,
            "id_etudiant": self.id_etudiant,
            "present": self.present,
            "timestamp": self.timestamp
        }

class QRCode:
    """
    Modèle représentant un QR code pour une séance.
    """
    def __init__(self, id: int, id_seance: int, code: str, date_generation: str = None,
                 expire_le: str = None, actif: int = 1):
        self.id = id
        self.id_seance = id_seance
        self.code = code
        self.date_generation = date_generation
        self.expire_le = expire_le
        self.actif = actif

    def to_dict(self):
        return {
            "id": self.id,
            "id_seance": self.id_seance,
            "code": self.code,
            "date_generation": self.date_generation,
            "expire_le": self.expire_le,
            "actif": self.actif
        }
