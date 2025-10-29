from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import and_, or_, func

from ..models.attendance_models import Presence, Absence
from ..models.user_models import Etudiant, Enseignant
from ..models.academic_models import Seance, Classe

class AttendanceService:
    def __init__(self):
        self.absence_thresholds = {
            "cours": 3,      # 3 absences max pour les cours
            "td": 3,         # 3 absences max pour les TD
            "tp": 2          # 2 absence max pour les TP
        }
    
    def get_historique_etudiant(self, etudiant_id: int, db: Session) -> Dict[str, Any]:
        """Obtenir l'historique complet des présences/absences d'un étudiant"""
        try:
            # Vérifier que l'étudiant existe
            etudiant = db.query(Etudiant).filter(Etudiant.id == etudiant_id).first()
            if not etudiant:
                raise ValueError("Étudiant non trouvé")
            
            # Récupérer toutes les présences de l'étudiant
            presences = db.query(Presence).filter(
                Presence.etudiant_id == etudiant_id
            ).order_by(Presence.date_heure_scan.desc()).all()
            
            # Récupérer les absences (calculées)
            absences = self._calculate_absences_for_student(etudiant_id, db)
            
            # Statistiques
            total_seances_potentielles = self._get_total_seances_potentielles(etudiant_id, db)
            presence_count = len(presences)
            absence_count = len(absences)
            
            taux_presence = (presence_count / total_seances_potentielles) * 100 if total_seances_potentielles > 0 else 0
            
            # Vérifier les seuils d'alerte
            alertes = self._check_absence_thresholds(etudiant_id, db)
            
            return {
                "etudiant": {
                    "id": etudiant.id,
                    "nom": etudiant.nom,
                    "email": etudiant.email,
                    "matricule": getattr(etudiant, 'matricule', 'N/A')
                },
                "statistiques": {
                    "total_presences": presence_count,
                    "total_absences": absence_count,
                    "total_seances_potentielles": total_seances_potentielles,
                    "taux_presence": round(taux_presence, 2),
                    "seuils_atteints": alertes
                },
                "presences": [
                    {
                        "id": p.id,
                        "seance_id": p.seance_id,
                        "date_heure_scan": p.date_heure_scan,
                        "matiere": self._get_matiere_from_seance(p.seance_id, db),
                        "type_seance": self._get_type_seance(p.seance_id, db),
                        "enseignant": self._get_enseignant_from_seance(p.seance_id, db)
                    } for p in presences
                ],
                "absences": [
                    {
                        "date": a.date,
                        "matiere": a.matiere,
                        "type_seance": a.type_seance,
                        "enseignant": a.enseignant,
                        "justifiee": getattr(a, 'justifiee', False)
                    } for a in absences
                ],
                "derniere_mise_a_jour": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise ValueError(f"Erreur lors de la récupération de l'historique: {str(e)}")
    
    def get_historique_etudiant_par_matiere(self, etudiant_id: int, matiere: str, db: Session) -> Dict[str, Any]:
        """Obtenir l'historique des présences/absences pour une matière spécifique"""
        try:
            # Récupérer toutes les présences de l'étudiant pour cette matière
            presences_matiere = []
            toutes_presences = db.query(Presence).filter(
                Presence.etudiant_id == etudiant_id
            ).all()
            
            for presence in toutes_presences:
                matiere_seance = self._get_matiere_from_seance(presence.seance_id, db)
                if matiere_seance.lower() == matiere.lower():
                    presences_matiere.append(presence)
            
            # Calculer les absences pour cette matière
            absences_matiere = self._calculate_absences_for_student_matiere(etudiant_id, matiere, db)
            
            # Statistiques pour la matière
            total_seances_matiere = len(presences_matiere) + len(absences_matiere)
            taux_presence_matiere = (len(presences_matiere) / total_seances_matiere) * 100 if total_seances_matiere > 0 else 0
            
            return {
                "etudiant_id": etudiant_id,
                "matiere": matiere,
                "statistiques_matiere": {
                    "presences": len(presences_matiere),
                    "absences": len(absences_matiere),
                    "total_seances": total_seances_matiere,
                    "taux_presence": round(taux_presence_matiere, 2)
                },
                "presences": [
                    {
                        "id": p.id,
                        "seance_id": p.seance_id,
                        "date_heure_scan": p.date_heure_scan,
                        "type_seance": self._get_type_seance(p.seance_id, db)
                    } for p in presences_matiere
                ],
                "absences": [
                    {
                        "date": a.date,
                        "type_seance": a.type_seance,
                        "justifiee": getattr(a, 'justifiee', False)
                    } for a in absences_matiere
                ]
            }
            
        except Exception as e:
            raise ValueError(f"Erreur lors de la récupération de l'historique matière: {str(e)}")
    
    def get_resume_mensuel(self, etudiant_id: int, annee: int, mois: int, db: Session) -> Dict[str, Any]:
        """Obtenir un résumé mensuel des présences/absences"""
        try:
            # Déterminer les dates de début et fin du mois
            date_debut = date(annee, mois, 1)
            if mois == 12:
                date_fin = date(annee + 1, 1, 1) - timedelta(days=1)
            else:
                date_fin = date(annee, mois + 1, 1) - timedelta(days=1)
            
            # Récupérer les présences du mois
            presences_mois = db.query(Presence).filter(
                Presence.etudiant_id == etudiant_id,
                Presence.date_heure_scan >= datetime.combine(date_debut, datetime.min.time()),
                Presence.date_heure_scan <= datetime.combine(date_fin, datetime.max.time())
            ).order_by(Presence.date_heure_scan).all()
            
            # Calculer les absences du mois
            absences_mois = self._calculate_absences_for_period(etudiant_id, date_debut, date_fin, db)
            
            # Statistiques mensuelles
            total_jours_cours = self._get_jours_cours_mois(annee, mois, db)
            jours_presents = len(set(p.date_heure_scan.date() for p in presences_mois))
            jours_absents = total_jours_cours - jours_presents
            
            return {
                "etudiant_id": etudiant_id,
                "periode": {
                    "mois": mois,
                    "annee": annee,
                    "date_debut": date_debut,
                    "date_fin": date_fin
                },
                "statistiques_mensuelles": {
                    "jours_cours_total": total_jours_cours,
                    "jours_presents": jours_presents,
                    "jours_absents": jours_absents,
                    "taux_presence_mensuel": (jours_presents / total_jours_cours) * 100 if total_jours_cours > 0 else 0
                },
                "details_par_semaine": self._get_details_par_semaine(presences_mois, absences_mois, annee, mois),
                "presences_mois": [
                    {
                        "date": p.date_heure_scan.date(),
                        "heure": p.date_heure_scan.time(),
                        "matiere": self._get_matiere_from_seance(p.seance_id, db),
                        "type_seance": self._get_type_seance(p.seance_id, db)
                    } for p in presences_mois
                ]
            }
            
        except Exception as e:
            raise ValueError(f"Erreur lors de la récupération du résumé mensuel: {str(e)}")
    
    # Méthodes privées
    def _calculate_absences_for_student(self, etudiant_id: int, db: Session) -> List[Absence]:
        """Calculer les absences d'un étudiant basé sur les séances manquées"""
        absences = []
        
        # Récupérer toutes les séances auxquelles l'étudiant devrait assister
        seances_etudiant = db.query(Seance).all()
        
        for seance in seances_etudiant:
            presence = db.query(Presence).filter(
                Presence.etudiant_id == etudiant_id,
                Presence.seance_id == seance.id
            ).first()
            
            if not presence:
                absence = Absence(
                    date=seance.date,
                    matiere=self._get_matiere_from_seance(seance.id, db),
                    etudiant_id=etudiant_id,
                    type_seance=self._get_type_seance(seance.id, db),
                    enseignant=self._get_enseignant_from_seance(seance.id, db)
                )
                absences.append(absence)
        
        return absences
    
    def _calculate_absences_for_student_matiere(self, etudiant_id: int, matiere: str, db: Session) -> List[Absence]:
        """Calculer les absences d'un étudiant pour une matière spécifique"""
        absences_matiere = []
        toutes_absences = self._calculate_absences_for_student(etudiant_id, db)
        
        for absence in toutes_absences:
            if absence.matiere.lower() == matiere.lower():
                absences_matiere.append(absence)
        
        return absences_matiere
    
    def _calculate_absences_for_period(self, etudiant_id: int, date_debut: date, date_fin: date, db: Session) -> List[Absence]:
        """Calculer les absences pour une période spécifique"""
        absences_periode = []
        toutes_absences = self._calculate_absences_for_student(etudiant_id, db)
        
        for absence in toutes_absences:
            if date_debut <= absence.date <= date_fin:
                absences_periode.append(absence)
        
        return absences_periode
    
    def _check_absence_thresholds(self, etudiant_id: int, db: Session) -> List[Dict[str, Any]]:
        """Vérifier si l'étudiant atteint des seuils d'absence critiques"""
        alertes = []
        absences = self._calculate_absences_for_student(etudiant_id, db)
        
        # Compter les absences par type
        absences_par_type = {}
        for absence in absences:
            type_seance = getattr(absence, 'type_seance', 'cours')
            absences_par_type[type_seance] = absences_par_type.get(type_seance, 0) + 1
        
        # Vérifier les seuils
        for type_seance, count in absences_par_type.items():
            seuil = self.absence_thresholds.get(type_seance, 3)
            if count >= seuil:
                alertes.append({
                    "type": type_seance,
                    "absences": count,
                    "seuil": seuil,
                    "niveau": "CRITIQUE" if count > seuil else "ALERTE",
                    "message": f"{count} absence(s) en {type_seance.upper()} - Seuil: {seuil}"
                })
        
        return alertes
    
    def _get_matiere_from_seance(self, seance_id: int, db: Session) -> str:
        """Obtenir le nom de la matière d'une séance"""
        seance = db.query(Seance).filter(Seance.id == seance_id).first()
        return getattr(seance, 'matiere', 'Inconnue') if seance else 'Inconnue'
    
    def _get_type_seance(self, seance_id: int, db: Session) -> str:
        """Obtenir le type de séance (cours, td, tp)"""
        seance = db.query(Seance).filter(Seance.id == seance_id).first()
        return getattr(seance, 'type_seance', 'cours') if seance else 'cours'
    
    def _get_enseignant_from_seance(self, seance_id: int, db: Session) -> str:
        """Obtenir le nom de l'enseignant d'une séance"""
        seance = db.query(Seance).filter(Seance.id == seance_id).first()
        if seance and seance.enseignant_id:
            enseignant = db.query(Enseignant).filter(Enseignant.id == seance.enseignant_id).first()
            return enseignant.nom if enseignant else "Inconnu"
        return "Inconnu"
    
    def _get_total_seances_potentielles(self, etudiant_id: int, db: Session) -> int:
        """Obtenir le nombre total de séances potentielles pour un étudiant"""
        # Cette méthode doit être adaptée selon votre modèle de données
        return db.query(Seance).count()
    
    def _get_jours_cours_mois(self, annee: int, mois: int, db: Session) -> int:
        """Obtenir le nombre de jours de cours dans le mois"""
        # Logique simplifiée - à adapter selon l'emploi du temps réel
        date_debut = date(annee, mois, 1)
        if mois == 12:
            date_fin = date(annee + 1, 1, 1) - timedelta(days=1)
        else:
            date_fin = date(annee, mois + 1, 1) - timedelta(days=1)
        
        # Compter les jours de semaine (lundi-vendredi) dans le mois
        jours_cours = 0
        current_date = date_debut
        while current_date <= date_fin:
            if current_date.weekday() < 5:  # 0-4 = lundi-vendredi
                jours_cours += 1
            current_date += timedelta(days=1)
        
        return jours_cours
    
    def _get_details_par_semaine(self, presences: List[Presence], absences: List[Absence], annee: int, mois: int) -> List[Dict[str, Any]]:
        """Obtenir les détails des présences/absences par semaine"""
        semaines = []
        
        # Grouper par semaine
        for semaine in range(1, 6):  # Semaines 1 à 5
            debut_semaine = date(annee, mois, (semaine - 1) * 7 + 1)
            fin_semaine = min(date(annee, mois, semaine * 7), date(annee, mois, 28))
            
            presences_semaine = [p for p in presences if debut_semaine <= p.date_heure_scan.date() <= fin_semaine]
            absences_semaine = [a for a in absences if debut_semaine <= a.date <= fin_semaine]
            
            if presences_semaine or absences_semaine:
                semaines.append({
                    "semaine": semaine,
                    "date_debut": debut_semaine,
                    "date_fin": fin_semaine,
                    "presences": len(presences_semaine),
                    "absences": len(absences_semaine),
                    "taux_presence": (len(presences_semaine) / (len(presences_semaine) + len(absences_semaine))) * 100 if (len(presences_semaine) + len(absences_semaine)) > 0 else 0
                })
        
        return semaines