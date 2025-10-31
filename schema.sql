CREATE TABLE IF NOT EXISTS utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL CHECK (nom GLOB '[A-Za-z]*'),
    prenom TEXT NOT NULL CHECK (prenom GLOB '[A-Za-z]*'),
    email TEXT UNIQUE NOT NULL,
    mot_de_passe TEXT NOT NULL,
    role TEXT CHECK(role IN ('student', 'teacher', 'admin')) NOT NULL,
    matricule TEXT,       -- for enseignants (teacher code)
    numero_inscription TEXT,  -- for students
    cin TEXT NOT NULL UNIQUE CHECK (cin GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
             -- for all users
    date_creation TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_classe TEXT NOT NULL,
    niveau TEXT,
    departement TEXT
);
CREATE TABLE IF NOT EXISTS matieres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_matiere TEXT NOT NULL,
    code_matiere TEXT UNIQUE NOT NULL,
    id_enseignant INTEGER,
    FOREIGN KEY (id_enseignant) REFERENCES utilisateurs(id)
);
CREATE TABLE IF NOT EXISTS seances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_matiere INTEGER NOT NULL,
    id_classe INTEGER NOT NULL,
    id_enseignant INTEGER NOT NULL,
    date TEXT NOT NULL,
    heure_debut TEXT NOT NULL,
    heure_fin TEXT NOT NULL,
    statut TEXT DEFAULT 'en_attente', -- en_attente, en_cours, terminee
    FOREIGN KEY (id_matiere) REFERENCES matieres(id),
    FOREIGN KEY (id_classe) REFERENCES classes(id),
    FOREIGN KEY (id_enseignant) REFERENCES utilisateurs(id)
);
CREATE TABLE IF NOT EXISTS presences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_seance INTEGER NOT NULL,
    id_etudiant INTEGER NOT NULL,
    present INTEGER CHECK(present IN (0, 1)) NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_seance) REFERENCES seances(id),
    FOREIGN KEY (id_etudiant) REFERENCES utilisateurs(id)
);
CREATE TABLE IF NOT EXISTS qrcodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_seance INTEGER NOT NULL,
    code TEXT NOT NULL,
    date_generation TEXT DEFAULT CURRENT_TIMESTAMP,
    expire_le TEXT,
    actif INTEGER DEFAULT 1,
    FOREIGN KEY (id_seance) REFERENCES seances(id)
);
CREATE TABLE IF NOT EXISTS tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    access_token TEXT UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES utilisateurs(id)
);

