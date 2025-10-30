from fastapi import APIRouter, HTTPException
from ..database import attendance_repository as repo

router = APIRouter(prefix="/attendance", tags=["Attendance"])


# Ajouter une séance
@router.post("/session")
def create_session(id_matiere: int, id_classe: int, id_enseignant: int,
                   date: str, heure_debut: str, heure_fin: str):
    ok = repo.add_session(id_matiere, id_classe, id_enseignant, date, heure_debut, heure_fin)
    if not ok:
        raise HTTPException(status_code=400, detail="Impossible d'ajouter la séance.")
    return {"message": "Séance créée avec succès"}


# Récupérer toutes les séances
@router.get("/sessions")
def get_sessions():
    return repo.get_all_sessions()


# Récupérer les séances d'un enseignant
@router.get("/sessions/teacher/{id_enseignant}")
def get_sessions_by_teacher(id_enseignant: int):
    return repo.get_sessions_by_teacher(id_enseignant)


# Ajouter une présence
@router.post("/presence")
def add_presence(id_seance: int, id_etudiant: int, present: int = 1):
    ok = repo.add_presence(id_seance, id_etudiant, present)
    if not ok:
        raise HTTPException(status_code=400, detail="Impossible d'ajouter la présence.")
    return {"message": "Présence enregistrée"}


# Récupérer présences d'une séance
@router.get("/session/{id_seance}/presences")
def get_presences_by_session(id_seance: int):
    return {"seance_id": id_seance, "presences": repo.get_presences_by_session(id_seance)}


# Étudiants présents
@router.get("/session/{id_seance}/present")
def get_present_students(id_seance: int):
    students = repo.get_students_by_presence(id_seance, present=1)
    return {"seance_id": id_seance, "present_students": students}


# Étudiants absents
@router.get("/session/{id_seance}/absent")
def get_absent_students(id_seance: int):
    students = repo.get_students_by_presence(id_seance, present=0)
    return {"seance_id": id_seance, "absent_students": students}






