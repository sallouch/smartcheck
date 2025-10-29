import qrcode
import secrets
import string
import json
import base64
from datetime import datetime, timedelta
from io import BytesIO
from typing import Dict, Optional, Tuple
from sqlalchemy.orm import Session
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ..models.attendance_models import QRCodeGenerate, QRCodeScan
from ..database import SessionLocal
from ..models.academic_models import Seance
from ..models.attendance_models import Presence

class QRService:
    def __init__(self):
        self.active_qr_codes: Dict[int, list] = {}  # {seance_id: [liste des qr_codes actifs]}
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        
        # Configuration des durées
        self.QR_VALIDITY_DURATION = 10  # 10 secondes de validité par QR code
        self.SESSION_DURATION = 180     # 3 minutes de génération continue
        self.GENERATION_INTERVAL = 10    # Générer un nouveau QR toutes les 10 secondes
        
        # Démarrer le nettoyage automatique des QR codes expirés
        self._start_cleanup_task()
    
    def start_qr_generation_session(self, seance_id: int, db: Session) -> dict:
        """Démarrer une session de génération de QR codes pour une séance"""
        try:
            # Vérifier si la séance existe
            seance = db.query(Seance).filter(Seance.id == seance_id).first()
            if not seance:
                raise ValueError("Séance non trouvée")
            
            # Arrêter toute session existante pour cette séance
            self.stop_qr_generation_session(seance_id)
            
            # Initialiser la liste des QR codes pour cette séance
            self.active_qr_codes[seance_id] = []
            
            # Générer le premier QR code immédiatement
            first_qr = self._generate_single_qr_code(seance_id, db)
            self.active_qr_codes[seance_id].append(first_qr)
            
            # Planifier la génération continue pendant 3 minutes
            self._schedule_continuous_generation(seance_id, db)
            
            # Planifier l'arrêt automatique après 3 minutes
            self._schedule_session_stop(seance_id)
            
            return {
                "message": f"Session QR code démarrée pour la séance {seance_id}",
                "duration_minutes": self.SESSION_DURATION / 60,
                "qr_validity_seconds": self.QR_VALIDITY_DURATION,
                "generation_interval": self.GENERATION_INTERVAL,
                "current_qr": first_qr["qr_code_data"],
                "expires_at": first_qr["expires_at"]
            }
            
        except Exception as e:
            raise ValueError(f"Erreur lors du démarrage de la session QR: {str(e)}")
    
    def _generate_single_qr_code(self, seance_id: int, db: Session) -> dict:
        """Générer un seul QR code avec une validité de 10 secondes"""
        # Générer un token unique
        token = self._generate_unique_token()
        
        # Calculer la date d'expiration (10 secondes)
        expiration = datetime.now() + timedelta(seconds=self.QR_VALIDITY_DURATION)
        
        # Créer les données du QR code
        qr_data_dict = {
            "seance_id": seance_id,
            "token": token,
            "expires_at": expiration.isoformat(),
            "generated_at": datetime.now().isoformat(),
            "validity_duration": self.QR_VALIDITY_DURATION
        }
        
        # Générer l'image QR code
        qr_image_base64 = self._generate_qr_image(qr_data_dict)
        
        # Créer l'objet QR code
        qr_info = {
            "data": qr_data_dict,
            "qr_code_data": json.dumps(qr_data_dict),
            "qr_image_base64": qr_image_base64,
            "expires_at": expiration,
            "generated_at": datetime.now(),
            "is_active": True,
            "token": token,
            "scanned_by": set()  # Suivi des étudiants ayant scanné ce QR spécifique
        }
        
        return qr_info
    
    def _schedule_continuous_generation(self, seance_id: int, db: Session):
        """Planifier la génération continue de QR codes toutes les 5 secondes"""
        job_id = f"qr_continuous_generation_{seance_id}"
        
        self.scheduler.add_job(
            self._generate_next_qr,
            trigger=IntervalTrigger(seconds=self.GENERATION_INTERVAL),
            args=[seance_id, db],
            id=job_id,
            max_instances=1,
            replace_existing=True
        )
    
    def _generate_next_qr(self, seance_id: int, db: Session):
        """Générer le prochain QR code dans la séquence"""
        try:
            if seance_id not in self.active_qr_codes:
                return
                
            # Nettoyer les QR codes expirés pour cette séance
            self._cleanup_expired_qrs_for_session(seance_id)
            
            # Générer un nouveau QR code
            new_qr = self._generate_single_qr_code(seance_id, db)
            self.active_qr_codes[seance_id].append(new_qr)
            
            print(f"Nouveau QR code généré pour séance {seance_id}, valide jusqu'à {new_qr['expires_at'].strftime('%H:%M:%S')}")
            
            # Garder seulement les 10 derniers QR codes pour éviter la surcharge mémoire
            if len(self.active_qr_codes[seance_id]) > 10:
                self.active_qr_codes[seance_id] = self.active_qr_codes[seance_id][-10:]
                
        except Exception as e:
            print(f"Erreur lors de la génération du QR code suivant: {e}")
    
    def _schedule_session_stop(self, seance_id: int):
        """Planifier l'arrêt de la session après 3 minutes"""
        job_id = f"qr_session_stop_{seance_id}"
        
        self.scheduler.add_job(
            self.stop_qr_generation_session,
            trigger='date',
            run_date=datetime.now() + timedelta(seconds=self.SESSION_DURATION),
            args=[seance_id],
            id=job_id,
            replace_existing=True
        )
    
    def stop_qr_generation_session(self, seance_id: int):
        """Arrêter la génération de QR codes pour une séance"""
        # Arrêter les jobs de génération
        generation_job_id = f"qr_continuous_generation_{seance_id}"
        stop_job_id = f"qr_session_stop_{seance_id}"
        
        try:
            if self.scheduler.get_job(generation_job_id):
                self.scheduler.remove_job(generation_job_id)
            if self.scheduler.get_job(stop_job_id):
                self.scheduler.remove_job(stop_job_id)
        except Exception as e:
            print(f"Erreur lors de l'arrêt des jobs: {e}")
        
        # Nettoyer les QR codes
        if seance_id in self.active_qr_codes:
            del self.active_qr_codes[seance_id]
        
        print(f"Session QR code arrêtée pour la séance {seance_id}")
    
    def validate_and_register_attendance(self, scan_data: QRCodeScan, db: Session) -> Presence:
        """Vérifier si le QR est valide et marquer la présence de l'étudiant"""
        try:
            # Parser les données du QR code
            qr_data = json.loads(scan_data.qr_code_data)
            seance_id = qr_data.get("seance_id")
            token = qr_data.get("token")
            
            # Vérifier si la séance a des QR codes actifs
            if seance_id not in self.active_qr_codes:
                raise ValueError("Aucune session QR code active pour cette séance")
            
            # Trouver le QR code correspondant au token
            qr_info = None
            for qr in self.active_qr_codes[seance_id]:
                if qr["token"] == token and qr["is_active"]:
                    qr_info = qr
                    break
            
            if not qr_info:
                raise ValueError("QR code non trouvé ou inactif")
            
            # 1. Vérifier si le QR code est expiré
            if self._is_qr_expired(qr_info):
                raise ValueError("QR code expiré")
            
            # 2. Vérifier si l'étudiant a déjà scanné ce QR code spécifique
            if scan_data.etudiant_id in qr_info["scanned_by"]:
                raise ValueError("Vous avez déjà scanné ce QR code")
            
            # 3. Vérifier si la séance existe
            seance = db.query(Seance).filter(Seance.id == seance_id).first()
            if not seance:
                raise ValueError("Séance non trouvée")
            
            # 4. Vérifier si l'étudiant est déjà présent pour cette séance (dans la base)
            existing_presence = db.query(Presence).filter(
                Presence.etudiant_id == scan_data.etudiant_id,
                Presence.seance_id == seance_id
            ).first()
            
            if existing_presence:
                raise ValueError("Présence déjà enregistrée pour cette séance")
            
            # 5. Marquer la présence de l'étudiant
            presence = Presence(
                date_heure_scan=datetime.now(),
                etat=True,
                etudiant_id=scan_data.etudiant_id,
                seance_id=seance_id
            )
            
            db.add(presence)
            db.commit()
            db.refresh(presence)
            
            # Ajouter l'étudiant à la liste des scans de ce QR code spécifique
            qr_info["scanned_by"].add(scan_data.etudiant_id)
            
            # Désactiver ce QR code spécifique après utilisation
            qr_info["is_active"] = False
            
            return presence
            
        except json.JSONDecodeError:
            raise ValueError("Format de QR code invalide")
        except Exception as e:
            db.rollback()
            raise ValueError(f"Erreur lors de l'enregistrement de la présence: {str(e)}")
    
    def _is_qr_expired(self, qr_info: dict) -> bool:
        """Vérifier si le QR code est expiré"""
        return datetime.now() > qr_info["expires_at"] or not qr_info["is_active"]
    
    def _generate_unique_token(self) -> str:
        """Générer un token unique sécurisé"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    
    def _generate_qr_image(self, qr_data: dict) -> str:
        """Générer l'image QR code en base64"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir en base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            raise ValueError(f"Erreur lors de la génération de l'image QR: {str(e)}")
    
    def get_current_qr_code(self, seance_id: int) -> Optional[dict]:
        """Obtenir le QR code actuellement actif pour une séance"""
        if seance_id not in self.active_qr_codes:
            return None
        
        # Trouver le QR code le plus récent qui est encore actif
        current_time = datetime.now()
        active_qrs = [
            qr for qr in self.active_qr_codes[seance_id] 
            if qr["is_active"] and current_time <= qr["expires_at"]
        ]
        
        if not active_qrs:
            return None
        
        # Retourner le QR code le plus récent
        latest_qr = max(active_qrs, key=lambda x: x["generated_at"])
        
        return {
            "qr_code_data": latest_qr["qr_code_data"],
            "qr_image_base64": latest_qr["qr_image_base64"],
            "expires_at": latest_qr["expires_at"],
            "time_remaining": (latest_qr["expires_at"] - datetime.now()).total_seconds(),
            "generated_at": latest_qr["generated_at"]
        }
    
    def get_session_status(self, seance_id: int) -> Optional[dict]:
        """Obtenir le statut de la session QR code pour une séance"""
        if seance_id not in self.active_qr_codes:
            return None
        
        current_qr = self.get_current_qr_code(seance_id)
        all_qrs = self.active_qr_codes[seance_id]
        
        active_qrs = [qr for qr in all_qrs if qr["is_active"] and not self._is_qr_expired(qr)]
        expired_qrs = [qr for qr in all_qrs if self._is_qr_expired(qr)]
        
        return {
            "seance_id": seance_id,
            "is_session_active": len(active_qrs) > 0,
            "current_qr": current_qr,
            "active_qr_count": len(active_qrs),
            "expired_qr_count": len(expired_qrs),
            "total_scans": sum(len(qr["scanned_by"]) for qr in all_qrs)
        }
    
    def _cleanup_expired_qrs_for_session(self, seance_id: int):
        """Nettoyer les QR codes expirés pour une session spécifique"""
        if seance_id not in self.active_qr_codes:
            return
        
        current_time = datetime.now()
        self.active_qr_codes[seance_id] = [
            qr for qr in self.active_qr_codes[seance_id]
            if current_time <= qr["expires_at"] or len(qr["scanned_by"]) > 0  # Garder ceux avec des scans
        ]
    
    def _start_cleanup_task(self):
        """Démarrer la tâche de nettoyage périodique"""
        self.scheduler.add_job(
            self._global_cleanup,
            trigger=IntervalTrigger(seconds=30),  # Nettoyage toutes les 30 secondes
            id="global_cleanup",
            replace_existing=True
        )
    
    def _global_cleanup(self):
        """Nettoyage global de tous les QR codes expirés"""
        current_time = datetime.now()
        sessions_to_remove = []
        
        for seance_id, qr_list in self.active_qr_codes.items():
            # Nettoyer les QR codes expirés
            self.active_qr_codes[seance_id] = [
                qr for qr in qr_list
                if current_time <= qr["expires_at"] + timedelta(seconds=60) or len(qr["scanned_by"]) > 0
            ]
            
            # Marquer les sessions vides pour suppression
            if not self.active_qr_codes[seance_id]:
                sessions_to_remove.append(seance_id)
        
        # Supprimer les sessions vides
        for seance_id in sessions_to_remove:
            del self.active_qr_codes[seance_id]
    
    def stop_service(self):
        """Arrêter complètement le service"""
        self.scheduler.shutdown()