# smartcheck/services/attendance_service.py
from typing import Dict, List
from database import user_repository, attendance_repository

class AttendanceService:
    def __init__(self):
        self.user_repo = user_repository
        self.attendance_repo = attendance_repository

    def get_student_attendance_stats(self, etudiant_id: int) -> Dict:
        """Récupère les statistiques de présence d'un étudiant via les repositories"""
        # Get the student from all users
        users = self.user_repo.get_all_users()
        student = next((u for u in users if u[0] == etudiant_id and u[5] == 'etudiant'), None)
        if not student:
            return {"success": False, "message": "Utilisateur non trouvé ou n'est pas un étudiant"}

        all_sessions = self.attendance_repo.get_all_sessions()
        total_seances = 0
        presences_count = 0
        absences_count = 0
        details = []

        for session in all_sessions:
            session_id = session[0]

            # Get session details
            date, heure_debut = session[4], session[5]
            nom_matiere = "matiere_id_" + str(session[1])  # placeholder, you can join with matieres table if needed
            nom_classe = "classe_id_" + str(session[2])   # placeholder

            present_students = self.attendance_repo.get_students_by_presence(session_id, present=1)
            present = any(etudiant_id == u_id for u_id, *_ in present_students)

            total_seances += 1
            if present:
                presences_count += 1
            else:
                absences_count += 1

            details.append({
                "session_id": session_id,
                "date": date,
                "heure_debut": heure_debut,
                "matiere": nom_matiere,
                "classe": nom_classe,
                "present": present
            })

        taux_presence = (presences_count / total_seances * 100) if total_seances > 0 else 0

        return {
            "success": True,
            "etudiant_id": etudiant_id,
            "statistiques": {
                "total_seances": total_seances,
                "presences": presences_count,
                "absences": absences_count,
                "taux_presence": round(taux_presence, 2)
            },
            "details": details
        }

    def get_teacher_attendance_report(self, enseignant_id: int) -> Dict:
        """Génère un rapport de présence pour un enseignant via repositories"""
        users = self.user_repo.get_all_users()
        teacher = next((u for u in users if u[0] == enseignant_id and u[5] == 'enseignant'), None)
        if not teacher:
            return {"success": False, "message": "Enseignant non trouvé"}

        sessions = self.attendance_repo.get_sessions_by_teacher(enseignant_id)
        rapport = []
        total_presences = 0
        total_etudiants_potentiels = 0

        for session in sessions:
            session_id = session[0]
            date, heure_debut, heure_fin = session[4], session[5], session[6]
            nom_matiere = "matiere_id_" + str(session[1])
            nom_classe = "classe_id_" + str(session[2])

            nb_presents = len(self.attendance_repo.get_students_by_presence(session_id, present=1))
            nb_total_etudiants = len([u for u in users if u[5] == 'etudiant']) or 1
            nb_absents = nb_total_etudiants - nb_presents
            taux_presence_session = (nb_presents / nb_total_etudiants * 100)

            etudiants_presents = [
                {"nom": u[1], "prenom": u[2]}
                for u_id, *u in self.attendance_repo.get_students_by_presence(session_id, present=1)
            ]

            rapport.append({
                "session_id": session_id,
                "date": date,
                "heure_debut": heure_debut,
                "heure_fin": heure_fin,
                "matiere": nom_matiere,
                "classe": nom_classe,
                "presents": nb_presents,
                "absents": nb_absents,
                "taux_presence": round(taux_presence_session, 2),
                "liste_presents": etudiants_presents
            })

            total_presences += nb_presents
            total_etudiants_potentiels += nb_total_etudiants

        taux_presence_global = (total_presences / total_etudiants_potentiels * 100)

        return {
            "success": True,
            "enseignant": f"{teacher[2]} {teacher[1]}",  # prenom + nom
            "enseignant_id": enseignant_id,
            "statistiques_globales": {
                "total_sessions": len(sessions),
                "total_presences": total_presences,
                "taux_presence_global": round(taux_presence_global, 2)
            },
            "rapport_detaille": rapport
        }
