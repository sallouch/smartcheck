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






