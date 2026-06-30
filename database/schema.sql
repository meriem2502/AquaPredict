-- ============================================================
-- AquaPredict AI - Schéma SQLite Complet
-- Auteur : Master 2 Intelligence Artificielle
-- Version : 1.0
-- ============================================================

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Admin', 'Ingénieur', 'Technicien')),
    full_name TEXT,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active INTEGER DEFAULT 1
);

-- Table des canalisations
CREATE TABLE IF NOT EXISTS canalisations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    zone TEXT NOT NULL,
    materiau TEXT NOT NULL CHECK(materiau IN ('PVC', 'Fonte', 'Acier', 'PEHD', 'Amiante-Ciment', 'Béton')),
    diametre REAL NOT NULL,
    longueur REAL NOT NULL,
    date_installation DATE NOT NULL,
    age INTEGER,
    etat TEXT DEFAULT 'Bon' CHECK(etat IN ('Bon', 'Moyen', 'Mauvais', 'Critique')),
    pression_nominale REAL,
    debit_nominal REAL,
    latitude REAL,
    longitude REAL,
    nb_reparations INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des réservoirs
CREATE TABLE IF NOT EXISTS reservoirs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    nom TEXT NOT NULL,
    zone TEXT NOT NULL,
    capacite REAL NOT NULL,
    niveau_actuel REAL DEFAULT 0,
    latitude REAL,
    longitude REAL,
    date_construction DATE,
    etat TEXT DEFAULT 'Opérationnel',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table historique niveaux réservoirs
CREATE TABLE IF NOT EXISTS historique_reservoirs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reservoir_id INTEGER NOT NULL,
    niveau REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reservoir_id) REFERENCES reservoirs(id)
);

-- Table des mesures / capteurs
CREATE TABLE IF NOT EXISTS mesures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canalisation_id INTEGER,
    pression REAL,
    debit REAL,
    temperature REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (canalisation_id) REFERENCES canalisations(id)
);

-- Table des prédictions
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canalisation_id INTEGER,
    pression REAL,
    debit REAL,
    temperature REAL,
    age_canalisation INTEGER,
    nb_reparations INTEGER,
    risque_niveau TEXT CHECK(risque_niveau IN ('Faible', 'Moyen', 'Élevé')),
    score_risque REAL,
    modele_utilise TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (canalisation_id) REFERENCES canalisations(id)
);

-- Table des alertes
CREATE TABLE IF NOT EXISTS alertes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canalisation_id INTEGER,
    type_alerte TEXT NOT NULL,
    priorite TEXT NOT NULL CHECK(priorite IN ('Basse', 'Moyenne', 'Haute', 'Critique')),
    message TEXT,
    est_resolue INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (canalisation_id) REFERENCES canalisations(id)
);

-- Table des interventions
CREATE TABLE IF NOT EXISTS interventions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canalisation_id INTEGER NOT NULL,
    technicien_id INTEGER,
    alerte_id INTEGER,
    description TEXT,
    statut TEXT DEFAULT 'Planifié' CHECK(statut IN ('Planifié', 'En cours', 'Terminé', 'Annulé')),
    priorite TEXT DEFAULT 'Moyenne',
    date_planifiee DATE,
    date_debut TIMESTAMP,
    date_fin TIMESTAMP,
    cout REAL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (canalisation_id) REFERENCES canalisations(id),
    FOREIGN KEY (technicien_id) REFERENCES users(id),
    FOREIGN KEY (alerte_id) REFERENCES alertes(id)
);

-- Table des fuites enregistrées
CREATE TABLE IF NOT EXISTS fuites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canalisation_id INTEGER NOT NULL,
    date_detection DATE NOT NULL,
    debit_perdu REAL,
    type_fuite TEXT,
    cause TEXT,
    est_reparee INTEGER DEFAULT 0,
    date_reparation DATE,
    cout_reparation REAL,
    FOREIGN KEY (canalisation_id) REFERENCES canalisations(id)
);

-- Table logs système
CREATE TABLE IF NOT EXISTS logs_systeme (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Index pour optimisation
CREATE INDEX IF NOT EXISTS idx_canalisations_zone ON canalisations(zone);
CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp);
CREATE INDEX IF NOT EXISTS idx_alertes_priorite ON alertes(priorite);
CREATE INDEX IF NOT EXISTS idx_interventions_statut ON interventions(statut);
