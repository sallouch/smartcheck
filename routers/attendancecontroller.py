from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime

# Création du routeur pour le contrôleur de gestion des présences
router = APIRouter(prefix="/attendance", tags=["Attendance"])

# ----------------------------
# Données simulées (temporairement en mémoire)
# ----------------------------

# Dictionnaire qui associe un étudiant à la liste de ses séances autorisées
students_sessions = {
    "fatma": [1, 2],  # Ex : l'étudiante Fatma est inscrite aux séances 1 et 2
    "islem": [2],
}

# Liste des présences déjà enregistrées
attendances = []

# Liste des demandes en attente (étudiants non autorisés qui demandent accès)
requests_pending = []


# ----------------------------
#  Modèles Pydantic (pour les requêtes HTTP)
# ----------------------------

class ScanRequest(BaseModel):
    student_name: str
    session_id: int
    qr_code_value: str  # le QR contient un code secret unique


class ValidationRequest(BaseModel):
    student_name: str
    session_id: int
    decision: bool  # True = accepter / False = refuser


# ----------------------------
# Fonctions API
# ----------------------------

@router.post("/scan_qr")
def scan_qr(data: ScanRequest):
    """
    Endpoint appelé quand un étudiant scanne un QR code.
    - Vérifie si l’étudiant est autorisé à assister à la séance.
    - Si oui → enregistre la présence.
    - Sinon → crée une demande d'accès temporaire.
    """

    # Vérification si l’étudiant appartient à la séance
    if data.session_id not in students_sessions.get(data.student_name, []):
        # L'étudiant n'appartient pas au groupe : créer une demande
        demande_existante = next(
            (d for d in requests_pending if d["student"] == data.student_name and d["session"] == data.session_id),
            None
        )
        if demande_existante:
            return {"message": "Une demande est déjà en attente de validation."}

        requests_pending.append({
            "student": data.student_name,
            "session": data.session_id,
            "status": "en attente",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        return {"message": "Demande envoyée à l’enseignant pour validation."}

    # Si l'étudiant est autorisé → on enregistre sa présence
    attendance_existante = next(
        (a for a in attendances if a["student"] == data.student_name and a["session"] == data.session_id),
        None
    )
    if attendance_existante:
        return {"message": "Présence déjà enregistrée."}

    attendances.append({
        "student": data.student_name,
        "session": data.session_id,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    return {"message": "Présence enregistrée avec succès."}


@router.get("/demandes")
def consulter_demandes():
    """
    Endpoint pour l'enseignant :
    Retourne toutes les demandes d’accès temporaire en attente.
    """
    return {"demandes_en_attente": requests_pending}


@router.post("/valider_demande")
def valider_demande(data: ValidationRequest):
    """
    Endpoint pour valider ou refuser une demande d’accès temporaire.
    Si validée → l’étudiant est ajouté à la séance et peut être marqué présent.
    """
    for demande in requests_pending:
        if demande["student"] == data.student_name and demande["session"] == data.session_id:
            if data.decision:
                # Ajout temporaire dans les séances autorisées
                students_sessions.setdefault(data.student_name, []).append(data.session_id)
                demande["status"] = "validée"
                return {"message": f"Demande de {data.student_name} validée. Étudiant ajouté temporairement."}
            else:
                demande["status"] = "refusée"
                return {"message": f"Demande de {data.student_name} refusée."}

    raise HTTPException(status_code=404, detail="Demande non trouvée.")


@router.get("/liste_presences")
def liste_presences():
    """
    Retourne toutes les présences enregistrées.
    (utile pour le tableau de bord de l’enseignant)
    """
    return {"presences": attendances}

