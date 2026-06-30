"""
AquaPredict AI - Gestionnaire de Base de Données SQLite
Gestion complète de la connexion et des opérations CRUD
"""

import sqlite3
import os
import hashlib
from datetime import datetime, date
import random

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "aquapredict.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_connection():
    """Retourne une connexion à la base de données SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database():
    """Initialise la base de données avec le schéma et les données de démo."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = get_connection()
    cursor = conn.cursor()

    # Lire et exécuter le schéma SQL
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()
    conn.executescript(schema)

    # Insérer les utilisateurs par défaut
    users = [
        ("admin", _hash_password("admin123"), "Admin", "Administrateur Système", "admin@aquapredict.dz"),
        ("ingenieur1", _hash_password("ing123"), "Ingénieur", "LINA", "lina@aquapredict.dz"),
        ("tech1", _hash_password("tech123"), "Technicien", "meriem", "meriem@aquapredict.dz"),
        ("tech2", _hash_password("tech123"), "Technicien", "TASNIM", "tasnim@aquapredict.dz"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO users (username, password_hash, role, full_name, email) VALUES (?,?,?,?,?)",
        users
    )

    # Vérifier si des données existent déjà
    count = cursor.execute("SELECT COUNT(*) FROM canalisations").fetchone()[0]
    if count == 0:
        _insert_demo_data(cursor)

    conn.commit()
    conn.close()


def _hash_password(password: str) -> str:
    """Hash le mot de passe avec SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(username: str, password: str):
    """Vérifie les identifiants et retourne l'utilisateur si valide."""
    conn = get_connection()
    hashed = _hash_password(password)
    user = conn.execute(
        "SELECT * FROM users WHERE username=? AND password_hash=? AND is_active=1",
        (username, hashed)
    ).fetchone()
    if user:
        conn.execute("UPDATE users SET last_login=? WHERE id=?", (datetime.now(), user["id"]))
        conn.commit()
    conn.close()
    return dict(user) if user else None


def _insert_demo_data(cursor):
    """Insère des données de démonstration réalistes."""
    zones = ["El Tarf Centre",
    "El Kala",
    "Besbes",
    "Dréan",
    "Bouteldja",
    "Ben M'Hidi",
    "Bouhadjar",
    "Chefia"]
    
    materiaux = ["PVC", "Fonte", "Acier", "PEHD", "Amiante-Ciment", "Béton"]
    etats = ["Bon", "Moyen", "Mauvais", "Critique"]

    # Coordonnées autour d'Alger
    base_lat, base_lon = 36.767, 8.314

    canalisations = []
    for i in range(1, 51):
        zone = random.choice(zones)
        materiau = random.choice(materiaux)
        annee = random.randint(1975, 2022)
        date_inst = date(annee, random.randint(1, 12), random.randint(1, 28))
        age = 2024 - annee
        nb_rep = random.randint(0, age // 5)
        etat = "Critique" if age > 40 else ("Mauvais" if age > 30 else ("Moyen" if age > 15 else "Bon"))

        canalisations.append((
            f"CAN-{i:04d}", zone, materiau,
            random.choice([100, 150, 200, 250, 300, 400, 500]),
            round(random.uniform(50, 2000), 1),
            str(date_inst), age, etat,
            round(random.uniform(2, 10), 1),
            round(random.uniform(10, 500), 1),
            round(base_lat + random.uniform(-0.3, 0.3), 5),
            round(base_lon + random.uniform(-0.3, 0.3), 5),
            nb_rep
        ))

    cursor.executemany("""
        INSERT OR IGNORE INTO canalisations
        (code, zone, materiau, diametre, longueur, date_installation, age, etat,
         pression_nominale, debit_nominal, latitude, longitude, nb_reparations)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, canalisations)

    # Réservoirs
    reservoirs_data = [
       
    ("RES-001", "Réservoir El Tarf Centre", "El Tarf Centre", 5000, 3800, 36.77, 8.31),
    ("RES-002", "Réservoir El Kala", "El Kala", 8000, 6200, 36.89, 8.44),
    ("RES-003", "Réservoir Besbes", "Besbes", 12000, 9500, 36.70, 7.85),
    ("RES-004", "Réservoir Dréan", "Dréan", 4000, 2800, 36.68, 8.15),
    ("RES-005", "Réservoir Bouteldja", "Bouteldja", 6000, 4500, 36.80, 8.15),
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO reservoirs (code, nom, zone, capacite, niveau_actuel, latitude, longitude) VALUES (?,?,?,?,?,?,?)",
        reservoirs_data
    )

    # Alertes de démo
    priorites = ["Basse", "Moyenne", "Haute", "Critique"]
    types = ["Pression anormale", "Débit anormal", "Fuite détectée", "Maintenance requise"]
    for i in range(1, 16):
        cursor.execute("""
            INSERT INTO alertes (canalisation_id, type_alerte, priorite, message, est_resolue)
            VALUES (?,?,?,?,?)
        """, (
            random.randint(1, 50),
            random.choice(types),
            random.choice(priorites),
            f"Anomalie détectée sur la canalisation - Vérification recommandée",
            random.randint(0, 1)
        ))

    # Fuites historiques
    for i in range(1, 25):
        annee = random.randint(2020, 2024)
        mois = random.randint(1, 12)
        cursor.execute("""
            INSERT INTO fuites (canalisation_id, date_detection, debit_perdu, type_fuite, cause, est_reparee)
            VALUES (?,?,?,?,?,?)
        """, (
            random.randint(1, 50),
            f"{annee}-{mois:02d}-{random.randint(1,28):02d}",
            round(random.uniform(0.5, 50), 2),
            random.choice(["Micro-fissure", "Rupture", "Joint défaillant", "Corrosion"]),
            random.choice(["Vieillissement", "Surpression", "Corrosion", "Défaut de pose"]),
            random.randint(0, 1)
        ))


# ── CRUD Canalisations ──────────────────────────────────────

def get_all_canalisations(zone=None, etat=None, search=None):
    conn = get_connection()
    query = "SELECT * FROM canalisations WHERE 1=1"
    params = []
    if zone:
        query += " AND zone=?"; params.append(zone)
    if etat:
        query += " AND etat=?"; params.append(etat)
    if search:
        query += " AND (code LIKE ? OR zone LIKE ?)"; params += [f"%{search}%", f"%{search}%"]
    rows = conn.execute(query + " ORDER BY id DESC", params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_canalisation(data: dict):
    conn = get_connection()
    conn.execute("""
        INSERT INTO canalisations (code, zone, materiau, diametre, longueur, date_installation,
        age, etat, pression_nominale, debit_nominal, latitude, longitude, nb_reparations)
        VALUES (:code,:zone,:materiau,:diametre,:longueur,:date_installation,
        :age,:etat,:pression_nominale,:debit_nominal,:latitude,:longitude,:nb_reparations)
    """, data)
    conn.commit(); conn.close()


def update_canalisation(id: int, data: dict):
    conn = get_connection()
    data["id"] = id; data["updated_at"] = datetime.now()
    conn.execute("""
        UPDATE canalisations SET zone=:zone, materiau=:materiau, diametre=:diametre,
        longueur=:longueur, date_installation=:date_installation, age=:age, etat=:etat,
        pression_nominale=:pression_nominale, debit_nominal=:debit_nominal,
        latitude=:latitude, longitude=:longitude, nb_reparations=:nb_reparations,
        updated_at=:updated_at WHERE id=:id
    """, data)
    conn.commit(); conn.close()


def delete_canalisation(id: int):
    conn = get_connection()
    conn.execute("DELETE FROM canalisations WHERE id=?", (id,))
    conn.commit(); conn.close()


def get_canalisation_by_id(id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM canalisations WHERE id=?", (id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ── CRUD Réservoirs ──────────────────────────────────────────

def get_all_reservoirs():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM reservoirs ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_reservoir_niveau(id: int, niveau: float):
    conn = get_connection()
    conn.execute("UPDATE reservoirs SET niveau_actuel=? WHERE id=?", (niveau, id))
    conn.execute("INSERT INTO historique_reservoirs (reservoir_id, niveau) VALUES (?,?)", (id, niveau))
    conn.commit(); conn.close()


# ── Alertes ──────────────────────────────────────────────────

def get_alertes(resolues=False):
    conn = get_connection()
    rows = conn.execute("""
        SELECT a.*, c.code as canalisation_code, c.zone
        FROM alertes a LEFT JOIN canalisations c ON a.canalisation_id = c.id
        WHERE a.est_resolue=? ORDER BY a.created_at DESC
    """, (1 if resolues else 0,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def resolve_alerte(id: int):
    conn = get_connection()
    conn.execute("UPDATE alertes SET est_resolue=1, resolved_at=? WHERE id=?", (datetime.now(), id))
    conn.commit(); conn.close()


def add_alerte(canalisation_id, type_alerte, priorite, message):
    conn = get_connection()
    conn.execute(
        "INSERT INTO alertes (canalisation_id, type_alerte, priorite, message) VALUES (?,?,?,?)",
        (canalisation_id, type_alerte, priorite, message)
    )
    conn.commit(); conn.close()


# ── Prédictions ──────────────────────────────────────────────

def save_prediction(data: dict):
    conn = get_connection()
    conn.execute("""
        INSERT INTO predictions (canalisation_id, pression, debit, temperature,
        age_canalisation, nb_reparations, risque_niveau, score_risque, modele_utilise)
        VALUES (:canalisation_id,:pression,:debit,:temperature,
        :age_canalisation,:nb_reparations,:risque_niveau,:score_risque,:modele_utilise)
    """, data)
    conn.commit(); conn.close()


def get_predictions_history(limit=50):
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.*, c.code as canalisation_code, c.zone
        FROM predictions p LEFT JOIN canalisations c ON p.canalisation_id = c.id
        ORDER BY p.timestamp DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Interventions ────────────────────────────────────────────

def get_all_interventions():
    conn = get_connection()
    rows = conn.execute("""
        SELECT i.*, c.code as canalisation_code, c.zone, u.full_name as technicien_nom
        FROM interventions i
        LEFT JOIN canalisations c ON i.canalisation_id = c.id
        LEFT JOIN users u ON i.technicien_id = u.id
        ORDER BY i.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_intervention(data: dict):
    conn = get_connection()
    conn.execute("""
        INSERT INTO interventions (canalisation_id, technicien_id, description,
        statut, priorite, date_planifiee, notes)
        VALUES (:canalisation_id,:technicien_id,:description,:statut,:priorite,:date_planifiee,:notes)
    """, data)
    conn.commit(); conn.close()


def update_intervention_statut(id: int, statut: str):
    conn = get_connection()
    conn.execute("UPDATE interventions SET statut=? WHERE id=?", (statut, id))
    conn.commit(); conn.close()


# ── Statistiques ─────────────────────────────────────────────

def get_dashboard_stats():
    conn = get_connection()
    stats = {}
    stats["nb_canalisations"] = conn.execute("SELECT COUNT(*) FROM canalisations").fetchone()[0]
    stats["nb_alertes"] = conn.execute("SELECT COUNT(*) FROM alertes WHERE est_resolue=0").fetchone()[0]
    stats["nb_alertes_critiques"] = conn.execute("SELECT COUNT(*) FROM alertes WHERE priorite='Critique' AND est_resolue=0").fetchone()[0]
    stats["nb_interventions_en_cours"] = conn.execute("SELECT COUNT(*) FROM interventions WHERE statut='En cours'").fetchone()[0]
    stats["nb_reservoirs"] = conn.execute("SELECT COUNT(*) FROM reservoirs").fetchone()[0]

    risk_row = conn.execute("SELECT AVG(score_risque) FROM predictions").fetchone()[0]
    stats["risque_moyen"] = round(risk_row, 1) if risk_row else 0

    stats["nb_fuites"] = conn.execute("SELECT COUNT(*) FROM fuites WHERE est_reparee=0").fetchone()[0]
    conn.close()
    return stats


def get_fuites_par_mois():
    conn = get_connection()
    rows = conn.execute("""
        SELECT strftime('%Y-%m', date_detection) as mois, COUNT(*) as nb_fuites
        FROM fuites GROUP BY mois ORDER BY mois DESC LIMIT 12
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_zones_stats():
    conn = get_connection()
    rows = conn.execute("""
        SELECT zone, COUNT(*) as nb_canalisations,
               AVG(age) as age_moyen,
               SUM(CASE WHEN etat='Critique' THEN 1 ELSE 0 END) as nb_critiques
        FROM canalisations GROUP BY zone
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_technicians():
    conn = get_connection()
    rows = conn.execute("SELECT id, full_name, username FROM users WHERE role='Technicien' AND is_active=1").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_users():
    conn = get_connection()
    rows = conn.execute("SELECT id, username, role, full_name, email, created_at, last_login, is_active FROM users ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_user(data: dict):
    conn = get_connection()
    data["password_hash"] = _hash_password(data.pop("password"))
    conn.execute(
        "INSERT INTO users (username, password_hash, role, full_name, email) VALUES (:username,:password_hash,:role,:full_name,:email)",
        data
    )
    conn.commit(); conn.close()


def toggle_user_active(id: int, active: int):
    conn = get_connection()
    conn.execute("UPDATE users SET is_active=? WHERE id=?", (active, id))
    conn.commit(); conn.close()


def log_action(user_id: int, action: str, details: str = ""):
    conn = get_connection()
    conn.execute("INSERT INTO logs_systeme (user_id, action, details) VALUES (?,?,?)", (user_id, action, details))
    conn.commit(); conn.close()
