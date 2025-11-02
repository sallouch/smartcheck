# smartcheck

 ## Introduction
 *SmartCheck* est une application de gestion de présence académique basée sur un système de QR Code.
 Elle permet aux enseignants de générer un code QR dynamique permet aux étudiants de scanner ce code pour enregistrer leur présence automatiquement.
 Le projet suit une *architecture en couches* (Clean Architecture) :
 - *Interface / API Layer* : exposée via FastAPI

 - *Business Layer*: contient la logique métier (services)

 - *Persistence Layer* : gère la base de données SQLite

 - *Database* : stocke toutes les données liées aux utilisateurs, séances, présences, etc.

---

### Objectif
Faciliter le suivi des présences des étudiants.

---

### Fonctionnalités principales
- Authentification par rôle (étudiant / enseignant / admin)
- Génération et validation de QR Codes pour chaque séance
- Enregistrement automatique des présences
- Gestion de statistique
- Documentation Swagger automatique via *FastAPI*

---

### Technologies
- Langage :Python 3.10+, JavaScript
- Framework API :FastAPI
- Base de données :SQLite
- Documentation :Swagger UI
- Contrôle de version :Git & GitHub
 
 ---

 ## Architecture du projet
 ### Backend:
 Le fichier *main.py*, exécuté avec *FastAPI*, gère toute la logique côté serveur.
 Il:
 - reçoit les requêtes du frontend (par exemple, pour marquer une présence ou générer un QR Code).
 - interagit avec *la base de données SQLite* via la couche Persistence (database/).
 - utilise *la logique métier* (Business Layer) pour appliquer les règles de gestion (validation de tokens, génération de QR, etc.).
 - renvoie une réponse structurée au frontend, qui l’affiche ensuite à l’utilisateur.
 ### Frontend:
 Cette partie représente  *l’interface utilisateur* visible dans le navigateur.
 Elle contient le  fichier src/pages:
 - affichent les pages de connexion et d’interaction.
 - permettent aux utilisateurs d’envoyer ou de récupérer des informations.
 - envoient des requêtes HTTP vers le backend via des appels API.

 ---

  ## Installation:
 ## *Backend*:
```bash
### 1 Cloner le projet
git clone https://github.com/sallouch/smartcheck.git
cd SmartCheck
### 2 Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate   # (Windows)
# ou
source venv/bin/activate  # (Linux/Mac)

### 3 Installer les dépendances
pip install fastapi uvicorn

### 4 Lancer le serveur
uvicorn main:app --reload
````

---

## *Frontend*:
```bash 
### 1 Cloner le projet
git clone https://github.com/sallouch/smartcheck_frontend.git

### 2 Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate   # (Windows)
# ou
source venv/bin/activate  # (Linux/Mac)

### 3 Installer les dépendances
npm install

### 4 Lancer le serveur de développement
npm run dev 