from fastapi import APIRouter, HTTPException
from services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance", tags=["Attendance"])
service = AttendanceService()

# Statistiques d'un étudiant
@router.get("/student/{etudiant_id}")
def student_attendance_stats(etudiant_id: int):
    result = service.get_student_attendance_stats(etudiant_id)
    if result["success"]:
        return result
    raise HTTPException(status_code=404, detail=result.get("message", "Utilisateur non trouvé"))

# Rapport d'un enseignant
@router.get("/teacher/{enseignant_id}")
def teacher_attendance_report(enseignant_id: int):
    result = service.get_teacher_attendance_report(enseignant_id)
    if result["success"]:
        return result
    raise HTTPException(status_code=404, detail=result.get("message", "Enseignant non trouvé"))

# Ajouter une séance (optionnel)
@router.post("/session")
def add_session(id_matiere: int, id_classe: int, id_enseignant: int, date: str, heure_debut: str, heure_fin: str):
    success = service.attendance_repo.add_session(id_matiere, id_classe, id_enseignant, date, heure_debut, heure_fin)
    if success:
        return {"message": "Séance ajoutée avec succès"}
    raise HTTPException(status_code=400, detail="Erreur lors de l'ajout de la séance")
# Ajouter une présence
@router.post("/presence")
def add_presence(id_seance: int, id_etudiant: int, present: int = 1):
    success = service.attendance_repo.add_presence(id_seance, id_etudiant, present)
    if success:
        return {"message": "Présence enregistrée"}
    raise HTTPException(status_code=400, detail="Erreur lors de l'enregistrement de la présence")





