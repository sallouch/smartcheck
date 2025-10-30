from datetime import datetime, timedelta
from typing import Dict, List
import sqlite3
from database.db_connection import get_connection

class AttendanceService:
    def __init__(self):
        pass
    
    def get_student_attendance_stats(self, etudiant_id: int) -> Dict:
        """Récupère les statistiques de présence d'un étudiant"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Vérifier que l'utilisateur est bien un étudiant
            cursor.execute("SELECT role FROM utilisateurs WHERE id = ?", (etudiant_id,))
            user = cursor.fetchone()
            if not user or user[0] != 'etudiant':
                return {"success": False, "message": "Utilisateur non trouvé ou n'est pas un étudiant"}
            
            # Récupérer toutes les séances
            cursor.execute("SELECT id FROM seances")
            all_sessions = cursor.fetchall()
            
            total_seances = 0
            presences_count = 0
            absences_count = 0
            details = []
            
            for session in all_sessions:
                session_id = session[0]
                
                # Récupérer les infos de la séance
                cursor.execute("""
                    SELECT s.date, s.heure_debut, m.nom_matiere, c.nom_classe
                    FROM seances s
                    JOIN matieres m ON s.id_matiere = m.id
                    JOIN classes c ON s.id_classe = c.id
                    WHERE s.id = ?
                """, (session_id,))
                
                session_info = cursor.fetchone()
                if not session_info:
                    continue
                    
                date, heure_debut, nom_matiere, nom_classe = session_info
                
                # Vérifier si l'étudiant était présent
                cursor.execute("""
                    SELECT present FROM presences 
                    WHERE id_seance = ? AND id_etudiant = ?
                """, (session_id, etudiant_id))
                
                presence_data = cursor.fetchone()
                present = presence_data[0] if presence_data else 0
                
                total_seances += 1
                if present == 1:
                    presences_count += 1
                else:
                    absences_count += 1
                
                details.append({
                    "session_id": session_id,
                    "date": date,
                    "heure_debut": heure_debut,
                    "matiere": nom_matiere,
                    "classe": nom_classe,
                    "present": bool(present)
                })
            
            # Calculer le taux de présence
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
            
        except Exception as e:
            return {"success": False, "message": f"Erreur: {str(e)}"}
        finally:
            conn.close()
    
    def get_teacher_attendance_report(self, enseignant_id: int) -> Dict:
        """Génère un rapport de présence pour un enseignant"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Vérifier que l'utilisateur est bien un enseignant
            cursor.execute("SELECT nom, prenom FROM utilisateurs WHERE id = ? AND role = 'enseignant'", (enseignant_id,))
            enseignant = cursor.fetchone()
            if not enseignant:
                return {"success": False, "message": "Enseignant non trouvé"}
            
            nom_enseignant, prenom_enseignant = enseignant
            
            # Récupérer les séances de l'enseignant
            cursor.execute("""
                SELECT s.id, s.date, s.heure_debut, s.heure_fin, m.nom_matiere, c.nom_classe
                FROM seances s
                JOIN matieres m ON s.id_matiere = m.id
                JOIN classes c ON s.id_classe = c.id
                WHERE s.id_enseignant = ?
                ORDER BY s.date DESC, s.heure_debut DESC
            """, (enseignant_id,))
            
            sessions = cursor.fetchall()
            rapport = []
            total_presences = 0
            total_etudiants_potentiels = 0
            
            for session in sessions:
                session_id, date, heure_debut, heure_fin, nom_matiere, nom_classe = session
                
                # Compter les étudiants présents
                cursor.execute("""
                    SELECT COUNT(*) FROM presences 
                    WHERE id_seance = ? AND present = 1
                """, (session_id,))
                nb_presents = cursor.fetchone()[0]
                
                # Estimer le nombre total d'étudiants (basé sur la classe)
                cursor.execute("""
                    SELECT COUNT(*) FROM utilisateurs 
                    WHERE role = 'etudiant'
                    -- Ici vous devriez avoir une table de liaison étudiants-classes
                    -- Pour l'instant on utilise une estimation
                """)
                nb_total_etudiants = cursor.fetchone()[0] or 1  # Éviter division par zéro
                
                nb_absents = nb_total_etudiants - nb_presents
                taux_presence_session = (nb_presents / nb_total_etudiants * 100) if nb_total_etudiants > 0 else 0
                
                # Récupérer la liste des présents
                cursor.execute("""
                    SELECT u.nom, u.prenom 
                    FROM presences p
                    JOIN utilisateurs u ON p.id_etudiant = u.id
                    WHERE p.id_seance = ? AND p.present = 1
                """, (session_id,))
                etudiants_presents = [f"{row[0]} {row[1]}" for row in cursor.fetchall()]
                
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
            
            # Calculer les statistiques globales
            taux_presence_global = (total_presences / total_etudiants_potentiels * 100) if total_etudiants_potentiels > 0 else 0
            
            return {
                "success": True,
                "enseignant": f"{prenom_enseignant} {nom_enseignant}",
                "enseignant_id": enseignant_id,
                "statistiques_globales": {
                    "total_sessions": len(sessions),
                    "total_presences": total_presences,
                    "taux_presence_global": round(taux_presence_global, 2)
                },
                "rapport_detaille": rapport
            }
            
        except Exception as e:
            return {"success": False, "message": f"Erreur: {str(e)}"}
        finally:
            conn.close()
    
    def get_session_attendance_details(self, session_id: int) -> Dict:
        """Récupère les détails de présence pour une séance spécifique"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Récupérer les infos de la séance
            cursor.execute("""
                SELECT s.date, s.heure_debut, m.nom_matiere, c.nom_classe, u.nom, u.prenom
                FROM seances s
                JOIN matieres m ON s.id_matiere = m.id
                JOIN classes c ON s.id_classe = c.id
                JOIN utilisateurs u ON s.id_enseignant = u.id
                WHERE s.id = ?
            """, (session_id,))
            
            session_info = cursor.fetchone()
            if not session_info:
                return {"success": False, "message": "Séance non trouvée"}
            
            date, heure_debut, nom_matiere, nom_classe, nom_enseignant, prenom_enseignant = session_info
            
            # Récupérer les présences
            cursor.execute("""
                SELECT p.id, u.nom, u.prenom, p.present, p.timestamp
                FROM presences p
                JOIN utilisateurs u ON p.id_etudiant = u.id
                WHERE p.id_seance = ?
                ORDER BY u.nom, u.prenom
            """, (session_id,))
            
            presences = cursor.fetchall()
            etudiants_presents = []
            etudiants_absents = []
            
            for presence in presences:
                presence_id, nom, prenom, present, timestamp = presence
                etudiant_info = {
                    "etudiant_id": presence_id,
                    "nom": nom,
                    "prenom": prenom,
                    "timestamp": timestamp
                }
                
                if present == 1:
                    etudiants_presents.append(etudiant_info)
                else:
                    etudiants_absents.append(etudiant_info)
            
            return {
                "success": True,
                "session_info": {
                    "session_id": session_id,
                    "date": date,
                    "heure_debut": heure_debut,
                    "matiere": nom_matiere,
                    "classe": nom_classe,
                    "enseignant": f"{prenom_enseignant} {nom_enseignant}"
                },
                "presents": {
                    "count": len(etudiants_presents),
                    "etudiants": etudiants_presents
                },
                "absents": {
                    "count": len(etudiants_absents),
                    "etudiants": etudiants_absents
                },
                "total_etudiants": len(etudiants_presents) + len(etudiants_absents),
                "taux_presence": (len(etudiants_presents) / (len(etudiants_presents) + len(etudiants_absents)) * 100) if (len(etudiants_presents) + len(etudiants_absents)) > 0 else 0
            }
            
        except Exception as e:
            return {"success": False, "message": f"Erreur: {str(e)}"}
        finally:
            conn.close()
    
    def get_attendance_alerts(self, seuil_absences: int = 3) -> Dict:
        """Génère des alertes pour les étudiants avec trop d'absences"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Cette requête identifie les étudiants avec plus de X absences
            cursor.execute("""
                SELECT u.id, u.nom, u.prenom, u.email, 
                       COUNT(*) as absences_count
                FROM utilisateurs u
                JOIN presences p ON u.id = p.id_etudiant
                WHERE u.role = 'etudiant' AND p.present = 0
                GROUP BY u.id, u.nom, u.prenom, u.email
                HAVING COUNT(*) > ?
                ORDER BY absences_count DESC
            """, (seuil_absences,))
            
            alerts = cursor.fetchall()
            result = []
            
            for alert in alerts:
                etudiant_id, nom, prenom, email, absences_count = alert
                result.append({
                    "etudiant_id": etudiant_id,
                    "nom": nom,
                    "prenom": prenom,
                    "email": email,
                    "absences_count": absences_count,
                    "seuil_depasse": True
                })
            
            return {
                "success": True,
                "seuil_absences": seuil_absences,
                "alerts": result,
                "total_alertes": len(result)
            }
            
        except Exception as e:
            return {"success": False, "message": f"Erreur: {str(e)}"}
        finally:
            conn.close()