import requests

url = "http://127.0.0.1:8000/attendance/session"
params = {
    "id_matiere": 1,
    "id_classe": 1,
    "id_enseignant": 2,
    "date": "2025-02-01",
    "heure_debut": "08:00",
    "heure_fin": "10:00"
}

r = requests.post(url, params=params)
print(r.status_code, r.json())
