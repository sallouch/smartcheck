import secrets
import qrcode
import base64
import io
from datetime import datetime, timedelta
from typing import Dict, Optional
import sqlite3
from database.db_connection import get_connection

class QRCodeService:
    def __init__(self):
        pass
    
    def generate_qr(self, id_seance: int, duree_validite_secondes: int = 30) -> Dict:
        """Génère un QR code dynamique pour une séance"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Vérifier si la séance existe
            cursor.execute("SELECT id FROM seances WHERE id = ?", (id_seance,))
            if not cursor.fetchone():
                return {"success": False, "message": "Séance non trouvée"}
            
            # Générer un code unique
            qr_token = secrets.token_urlsafe(32)
            
            # Calculer les dates
            date_generation = datetime.now().isoformat()
            expire_le = (datetime.now() + timedelta(seconds=duree_validite_secondes)).isoformat()
            
            # Désactiver les anciens QR codes pour cette séance
            cursor.execute("UPDATE qrcodes SET actif = 0 WHERE id_seance = ?", (id_seance,))
            
            # Insérer le nouveau QR code
            cursor.execute("""
                INSERT INTO qrcodes (id_seance, code, date_generation, expire_le, actif)
                VALUES (?, ?, ?, ?, ?)
            """, (id_seance, qr_token, date_generation, expire_le, 1))
            
            conn.commit()
            
            # Créer l'image QR code
            qr_data = f"SMARTCHECK:{id_seance}:{qr_token}"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir en base64 pour l'API
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                "success": True,
                "qr_code_image": qr_base64,
                "qr_token": qr_token,
                "expire_le": expire_le,
                "id_seance": id_seance,
                "duree_validite": duree_validite_secondes
            }
            
        except Exception as e:
            return {"success": False, "message": f"Erreur génération QR: {str(e)}"}
        finally:
            conn.close()
    
    def scan_qr(self, qr_token: str, etudiant_id: int) -> Dict:
        """Traite le scan d'un QR code par un étudiant"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Récupérer le QR code
            cursor.execute("""
                SELECT id, id_seance, code, date_generation, expire_le, actif 
                FROM qrcodes WHERE code = ?
            """, (qr_token,))
            
            qr_data = cursor.fetchone()
            if not qr_data:
                return {"success": False, "message": "QR code invalide"}
            
            qr_id, id_seance, code, date_generation, expire_le, actif = qr_data
            
            # Vérifier si le QR code est actif
            if actif != 1:
                return {"success": False, "message": "QR code déjà utilisé"}
            
            # Vérifier l'expiration
            expire_time = datetime.fromisoformat(expire_le)
            if datetime.now() > expire_time:
                # Désactiver le QR code expiré
                cursor.execute("UPDATE qrcodes SET actif = 0 WHERE id = ?", (qr_id,))
                conn.commit()
                return {"success": False, "message": "QR code expiré"}
            
            # Vérifier si l'étudiant est dans la classe de la séance
            cursor.execute("""
                SELECT s.id_classe 
                FROM seances s
                WHERE s.id = ?
            """, (id_seance,))
            
            seance_data = cursor.fetchone()
            if not seance_data:
                return {"success": False, "message": "Séance non trouvée"}
            
            id_classe = seance_data[0]
            
            # Vérifier si l'étudiant existe et est bien un étudiant
            cursor.execute("""
                SELECT id, role FROM utilisateurs 
                WHERE id = ? AND role = 'etudiant'
            """, (etudiant_id,))
            
            etudiant = cursor.fetchone()
            if not etudiant:
                return {"success": False, "message": "Étudiant non trouvé ou rôle invalide"}
            
            # Vérifier si la présence n'est pas déjà enregistrée
            cursor.execute("""
                SELECT id FROM presences 
                WHERE id_seance = ? AND id_etudiant = ?
            """, (id_seance, etudiant_id))
            
            if cursor.fetchone():
                return {"success": False, "message": "Présence déjà enregistrée pour cette séance"}
            
            # Enregistrer la présence
            cursor.execute("""
                INSERT INTO presences (id_seance, id_etudiant, present)
                VALUES (?, ?, ?)
            """, (id_seance, etudiant_id, 1))
            
            # Désactiver le QR code après utilisation
            cursor.execute("UPDATE qrcodes SET actif = 0 WHERE id = ?", (qr_id,))
            
            conn.commit()
            
            return {
                "success": True,
                "message": "Présence enregistrée avec succès",
                "id_seance": id_seance,
                "id_etudiant": etudiant_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except sqlite3.IntegrityError:
            return {"success": False, "message": "Erreur d'intégrité - présence peut-être déjà enregistrée"}
        except Exception as e:
            return {"success": False, "message": f"Erreur traitement QR: {str(e)}"}
        finally:
            conn.close()
    
    def get_active_qr_codes(self, id_enseignant: int = None) -> Dict:
        """Récupère les QR codes actifs, optionnellement filtrés par enseignant"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if id_enseignant:
                # QR codes des séances d'un enseignant spécifique
                cursor.execute("""
                    SELECT q.id, q.id_seance, q.code, q.date_generation, q.expire_le, q.actif,
                           s.date, s.heure_debut, m.nom_matiere, c.nom_classe
                    FROM qrcodes q
                    JOIN seances s ON q.id_seance = s.id
                    JOIN matieres m ON s.id_matiere = m.id
                    JOIN classes c ON s.id_classe = c.id
                    WHERE q.actif = 1 AND s.id_enseignant = ?
                """, (id_enseignant,))
            else:
                # Tous les QR codes actifs
                cursor.execute("""
                    SELECT q.id, q.id_seance, q.code, q.date_generation, q.expire_le, q.actif,
                           s.date, s.heure_debut, m.nom_matiere, c.nom_classe
                    FROM qrcodes q
                    JOIN seances s ON q.id_seance = s.id
                    JOIN matieres m ON s.id_matiere = m.id
                    JOIN classes c ON s.id_classe = c.id
                    WHERE q.actif = 1
                """)
            
            qr_codes = cursor.fetchall()
            result = []
            
            for qr in qr_codes:
                qr_id, id_seance, code, date_generation, expire_le, actif, date, heure_debut, nom_matiere, nom_classe = qr
                
                # Vérifier si le QR code n'a pas expiré
                expire_time = datetime.fromisoformat(expire_le)
                if datetime.now() > expire_time:
                    # Désactiver automatiquement les QR codes expirés
                    cursor.execute("UPDATE qrcodes SET actif = 0 WHERE id = ?", (qr_id,))
                    conn.commit()
                    continue
                
                result.append({
                    "qr_id": qr_id,
                    "id_seance": id_seance,
                    "code": code,
                    "date_generation": date_generation,
                    "expire_le": expire_le,
                    "date_seance": date,
                    "heure_debut": heure_debut,
                    "matiere": nom_matiere,
                    "classe": nom_classe
                })
            
            conn.commit()
            
            return {
                "success": True,
                "active_qr_codes": result,
                "count": len(result)
            }
            
        except Exception as e:
            return {"success": False, "message": f"Erreur: {str(e)}"}
        finally:
            conn.close()