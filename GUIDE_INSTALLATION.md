# 🌊 AquaPredict AI — Guide d'Installation & de Démarrage

**Système Intelligent de Prédiction des Fuites dans les Réseaux de Distribution d'Eau**
*Master 2 Intelligence Artificielle · Version 1.0.0*

---

## Table des Matières

1. [Prérequis système](#1-prérequis-système)
2. [Structure du projet](#2-structure-du-projet)
3. [Installation de l'environnement](#3-installation-de-lenvironnement)
4. [Création & initialisation de la base de données SQLite](#4-création--initialisation-de-la-base-de-données-sqlite)
5. [Entraînement du modèle Machine Learning](#5-entraînement-du-modèle-machine-learning)
6. [Lancement de l'application](#6-lancement-de-lapplication)
7. [Génération des données de démonstration](#7-génération-des-données-de-démonstration)
8. [Import des datasets CSV](#8-import-des-datasets-csv)
9. [Comptes utilisateurs par défaut](#9-comptes-utilisateurs-par-défaut)
10. [Dépannage](#10-dépannage)
11. [Architecture technique](#11-architecture-technique)

---

## 1. Prérequis Système

| Composant | Version minimale | Notes |
|-----------|-----------------|-------|
| **Python** | 3.10+ | Recommandé : 3.11 ou 3.12 |
| **pip** | 23.0+ | `pip install --upgrade pip` |
| **RAM** | 4 Go minimum | 8 Go recommandé pour XGBoost |
| **Espace disque** | 500 Mo | Modèles ML + base de données |
| **OS** | Windows 10+ / Ubuntu 20.04+ / macOS 12+ | Multi-plateforme |

Vérifier votre version Python :
```bash
python --version        # ou python3 --version
pip --version
```

---

## 2. Structure du Projet

```
AquaPredict_AI/
│
├── app.py                          # ← Point d'entrée principal (lancer ici)
│
├── requirements.txt                # Dépendances Python
│
├── database/
│   ├── __init__.py
│   ├── schema.sql                  # Schéma SQLite complet (12 tables)
│   ├── db_manager.py               # CRUD, connexion, initialisation
│   └── aquapredict.db              # ← Créé automatiquement au démarrage
│
├── models/
│   ├── __init__.py
│   ├── ml_model.py                 # Random Forest, XGBoost, métriques
│   ├── active_model.pkl            # ← Créé après entraînement
│   └── model_random_forest.pkl     # ← Modèles sauvegardés
│
├── pages/
│   ├── __init__.py
│   ├── dashboard.py                # KPIs, graphiques temps réel
│   ├── canalisations.py            # CRUD canalisations
│   ├── reservoirs.py               # Gestion réservoirs
│   ├── ml_training.py              # Entraînement & évaluation ML
│   ├── prediction.py               # Prédiction individuelle
│   ├── alertes.py                  # Système d'alertes
│   ├── interventions.py            # Gestion des interventions
│   ├── carte.py                    # Carte GIS Folium
│   ├── statistiques.py             # Analyses & graphiques avancés
│   ├── data_management.py          # Import CSV/Excel, nettoyage
│   ├── rapports.py                 # Génération PDF, exports
│   └── parametres.py               # Admin : users, backup, config
│
├── utils/
│   ├── __init__.py
│   ├── charts.py                   # Graphiques Plotly & cartes Folium
│   ├── ui_helpers.py               # CSS, KPI cards, composants UI
│   └── pdf_generator.py            # Rapports PDF ReportLab
│
├── assets/
│   ├── sample_canalisations.csv    # 100 canalisations de démo
│   ├── sample_reservoirs.csv       # 10 réservoirs de démo
│   ├── sample_mesures.csv          # 500 mesures capteurs
│   ├── sample_fuites.csv           # 80 fuites historiques
│   └── config.json                 # Configuration (créé à l'exécution)
│
└── reports/                        # Rapports PDF générés
```

---

## 3. Installation de l'Environnement

### Option A — Environnement Virtuel (Recommandé)

```bash
# 1. Se placer dans le dossier du projet
cd AquaPredict_AI

# 2. Créer l'environnement virtuel
python -m venv venv

# 3. Activer l'environnement
# Windows :
venv\Scripts\activate
# Linux / macOS :
source venv/bin/activate

# 4. Mettre à jour pip
pip install --upgrade pip

# 5. Installer toutes les dépendances
pip install -r requirements.txt
```

### Option B — Installation directe (sans venv)

```bash
pip install -r requirements.txt
```

### Option C — Conda (Anaconda / Miniconda)

```bash
conda create -n aquapredict python=3.11
conda activate aquapredict
pip install -r requirements.txt
```

### Vérification de l'installation

```bash
python -c "import streamlit, sklearn, plotly, folium, reportlab; print('✅ Toutes les dépendances OK')"
```

---

## 4. Création & Initialisation de la Base de Données SQLite

### Méthode 1 — Automatique (recommandée)

La base de données est **créée et initialisée automatiquement** au premier lancement de l'application. Aucune action manuelle requise.

```bash
streamlit run app.py
# → database/aquapredict.db est créé automatiquement
# → Les 12 tables sont créées via database/schema.sql
# → Les comptes utilisateurs par défaut sont insérés
# → 50 canalisations + 5 réservoirs + 15 alertes + 24 fuites de démo sont générés
```

### Méthode 2 — Initialisation manuelle via Python

```bash
# Depuis le dossier racine du projet :
python -c "
from database.db_manager import init_database
init_database()
print('✅ Base de données initialisée avec succès')
print('📂 Fichier créé : database/aquapredict.db')
"
```

### Méthode 3 — Initialisation via script SQL pur

```bash
# Créer la base et exécuter le schéma directement
sqlite3 database/aquapredict.db < database/schema.sql
echo "✅ Schéma SQL appliqué"
```

### Vérification de la base de données

```bash
sqlite3 database/aquapredict.db ".tables"
# Doit afficher :
# alertes     canalisations   fuites          historique_reservoirs
# interventions   logs_systeme    mesures     predictions
# reservoirs  users
```

### Tables créées (12 tables)

| Table | Description | Clés |
|-------|-------------|------|
| `users` | Comptes utilisateurs & rôles | PK: id |
| `canalisations` | Réseau de conduites | PK: id, UK: code |
| `reservoirs` | Réservoirs d'eau | PK: id, UK: code |
| `historique_reservoirs` | Niveaux historiques | FK: reservoir_id |
| `mesures` | Données capteurs IoT | FK: canalisation_id |
| `predictions` | Résultats ML sauvegardés | FK: canalisation_id |
| `alertes` | Alertes système | FK: canalisation_id |
| `interventions` | Réparations planifiées | FK: canalisation_id, technicien_id |
| `fuites` | Historique fuites | FK: canalisation_id |
| `logs_systeme` | Journal des actions | FK: user_id |

---

## 5. Entraînement du Modèle Machine Learning

### Méthode 1 — Via l'Interface (Recommandée)

1. Lancer l'application : `streamlit run app.py`
2. Se connecter avec `admin / admin123`
3. Naviguer vers **🤖 ML — Entraînement**
4. Choisir l'algorithme (Random Forest, XGBoost, ou Gradient Boosting)
5. Régler le nombre d'exemples (1000–5000)
6. Cliquer **"🚀 Lancer l'Entraînement"**
7. Consulter les métriques dans l'onglet **📊 Évaluation**

### Méthode 2 — En ligne de commande

```bash
# Entraîner Random Forest (algorithme par défaut)
python -c "
from models.ml_model import train_model
metrics = train_model('Random Forest')
print(f'✅ Modèle entraîné')
print(f'   Accuracy  : {metrics[\"accuracy\"]:.1f}%')
print(f'   Précision : {metrics[\"precision\"]:.1f}%')
print(f'   Rappel    : {metrics[\"recall\"]:.1f}%')
print(f'   F1-Score  : {metrics[\"f1_score\"]:.1f}%')
print(f'   CV (5-fold): {metrics[\"cv_mean\"]:.1f}% ± {metrics[\"cv_std\"]:.1f}%')
"

# Entraîner XGBoost
python -c "
from models.ml_model import train_model
metrics = train_model('XGBoost')
print(f'✅ XGBoost entraîné — Accuracy: {metrics[\"accuracy\"]:.1f}%')
"

# Entraîner sur un CSV personnalisé
python -c "
import pandas as pd
from models.ml_model import train_model
df = pd.read_csv('assets/sample_mesures.csv')
# Ajouter la colonne cible manuellement si absente
# df['risque'] = ...
metrics = train_model('Random Forest', df)
print('Métriques:', metrics)
"
```

### Variables d'entrée (features) du modèle

| Feature | Type | Description |
|---------|------|-------------|
| `pression` | Float | Pression en bar (0–20) |
| `debit` | Float | Débit en m³/h (0–1000) |
| `temperature` | Float | Température en °C (-5–50) |
| `age` | Integer | Âge de la canalisation en années |
| `nb_reparations` | Integer | Nombre de réparations passées |
| `diametre` | Float | Diamètre en mm (50–1000) |
| `longueur` | Float | Longueur en m (1–5000) |

### Variable cible

| Classe | Valeur | Signification |
|--------|--------|--------------|
| `Faible` | 0 | Risque de fuite faible (< 33%) |
| `Moyen` | 1 | Risque modéré (33–66%) |
| `Élevé` | 2 | Risque élevé, intervention urgente (> 66%) |

### Modèles sauvegardés

Les modèles sont sérialisés en `.pkl` dans `models/` :
- `models/active_model.pkl` — modèle actif pour les prédictions
- `models/model_random_forest.pkl` — Random Forest
- `models/model_xgboost.pkl` — XGBoost
- `models/model_gradient_boosting.pkl` — Gradient Boosting

---

## 6. Lancement de l'Application

### Commande de base

```bash
# Depuis le dossier racine AquaPredict_AI/
streamlit run app.py
```

L'application s'ouvre automatiquement sur **http://localhost:8501**

### Options avancées

```bash
# Changer le port
streamlit run app.py --server.port 8080

# Accessible sur le réseau local (collègues, jury de soutenance)
streamlit run app.py --server.address 0.0.0.0

# Mode sans ouverture automatique du navigateur
streamlit run app.py --server.headless true

# Combinaison : réseau + port personnalisé
streamlit run app.py --server.address 0.0.0.0 --server.port 8080

# Désactiver la collecte de données Streamlit
streamlit run app.py --browser.gatherUsageStats false
```

### Accès réseau (pour présentation)

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
# → http://[VOTRE_IP]:8501  (trouvez votre IP avec : ipconfig / ip addr)
```

---

## 7. Génération des Données de Démonstration

### Automatique

Les données de démonstration sont insérées automatiquement lors de l'initialisation si la base est vide :
- **50 canalisations** réparties en 6 zones
- **5 réservoirs** avec niveaux variés
- **15 alertes** de priorités mixtes
- **24 fuites** historiques (2020–2024)

### Manuel via Python

```bash
python -c "
from database.db_manager import get_connection
from database.db_manager import init_database

# Réinitialiser complètement (ATTENTION : efface toutes les données)
import os
db_path = 'database/aquapredict.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print('🗑️  Ancienne base supprimée')

init_database()
print('✅ Base réinitialisée avec données de démo')
"
```

### Générer des mesures capteurs aléatoires

```bash
python -c "
import random
from database.db_manager import get_connection
from datetime import datetime, timedelta

conn = get_connection()
base = datetime.now()
for i in range(200):
    ts = base - timedelta(hours=random.randint(0,720))
    conn.execute(
        'INSERT INTO mesures (canalisation_id, pression, debit, temperature, timestamp) VALUES (?,?,?,?,?)',
        (random.randint(1,50), round(random.uniform(2,9),2),
         round(random.uniform(50,400),2), round(random.uniform(8,30),1),
         ts.strftime('%Y-%m-%d %H:%M:%S'))
    )
conn.commit()
conn.close()
print('✅ 200 mesures capteurs générées')
"
```

---

## 8. Import des Datasets CSV

Les fichiers CSV de démonstration se trouvent dans `assets/` :

| Fichier | Lignes | Usage |
|---------|--------|-------|
| `sample_canalisations.csv` | 100 | Réseau complet de canalisations |
| `sample_reservoirs.csv` | 10 | Réservoirs avec capacités |
| `sample_mesures.csv` | 500 | Mesures capteurs (pression, débit, température) |
| `sample_fuites.csv` | 80 | Historique de fuites avec causes |

### Via l'interface (recommandé)

1. Naviguer vers **📂 Gestion des Données**
2. Onglet **⬆️ Import de Données**
3. Sélectionner le type (canalisations / réservoirs / mesures / fuites)
4. Glisser-déposer le fichier CSV correspondant
5. Vérifier l'aperçu et cliquer **"⬆️ Importer"**

### Via Python script

```bash
python -c "
import pandas as pd
from database.db_manager import get_connection

def import_csv(path, table, required_cols):
    df = pd.read_csv(path)
    valid_cols = [c for c in required_cols if c in df.columns]
    conn = get_connection()
    inserted = 0
    for _, row in df[valid_cols].iterrows():
        try:
            cols = ', '.join(row.index)
            placeholders = ', '.join(['?' for _ in row])
            conn.execute(f'INSERT OR IGNORE INTO {table} ({cols}) VALUES ({placeholders})', tuple(row.values))
            inserted += 1
        except Exception as e:
            pass
    conn.commit()
    conn.close()
    return inserted

# Importer canalisations
n = import_csv('assets/sample_canalisations.csv', 'canalisations',
               ['code','zone','materiau','diametre','longueur','date_installation',
                'age','etat','pression_nominale','debit_nominal','latitude','longitude','nb_reparations'])
print(f'✅ {n} canalisations importées')

# Importer réservoirs
n = import_csv('assets/sample_reservoirs.csv', 'reservoirs',
               ['code','nom','zone','capacite','niveau_actuel','latitude','longitude'])
print(f'✅ {n} réservoirs importés')

# Importer mesures
n = import_csv('assets/sample_mesures.csv', 'mesures',
               ['canalisation_id','pression','debit','temperature','timestamp'])
print(f'✅ {n} mesures importées')

# Importer fuites
n = import_csv('assets/sample_fuites.csv', 'fuites',
               ['canalisation_id','date_detection','debit_perdu','type_fuite','cause','est_reparee'])
print(f'✅ {n} fuites importées')
"
```

---

## 9. Comptes Utilisateurs par Défaut

| Rôle | Identifiant | Mot de passe | Accès |
|------|------------|-------------|-------|
| 👑 **Admin** | `admin` | `admin123` | Accès complet à tous les modules |
| 🔬 **Ingénieur** | `ingenieur1` | `ing123` | Dashboard, ML, carte, stats, rapports |
| 🔧 **Technicien** | `tech1` | `tech123` | Dashboard, canalisations, alertes, interventions |
| 🔧 **Technicien** | `tech2` | `tech123` | Même accès que tech1 |

### Matrice des permissions

| Module | Admin | Ingénieur | Technicien |
|--------|-------|-----------|------------|
| Dashboard | ✅ | ✅ | ✅ |
| Canalisations | ✅ | ✅ | ✅ |
| Réservoirs | ✅ | ✅ | ✅ |
| ML Entraînement | ✅ | ✅ | ❌ |
| ML Prédiction | ✅ | ✅ | ✅ |
| Alertes | ✅ | ✅ | ✅ |
| Interventions | ✅ | ✅ | ✅ |
| Carte GIS | ✅ | ✅ | ✅ |
| Statistiques | ✅ | ✅ | ❌ |
| Gestion Données | ✅ | ✅ | ❌ |
| Rapports | ✅ | ✅ | ❌ |
| Paramètres | ✅ | ❌ | ❌ |

---

## 10. Dépannage

### ❌ Erreur : `ModuleNotFoundError: No module named 'xgboost'`

```bash
pip install xgboost
# ou si XGBoost pose problème :
# Dans ml_model.py, choisissez "Gradient Boosting" à la place
```

### ❌ Erreur : `sqlite3.OperationalError: no such table`

```bash
# La base n'est pas initialisée correctement
python -c "from database.db_manager import init_database; init_database()"
```

### ❌ Erreur : `streamlit: command not found`

```bash
# Streamlit n'est pas dans le PATH, utiliser python -m
python -m streamlit run app.py
```

### ❌ Erreur de port occupé

```bash
# Changer le port
streamlit run app.py --server.port 8502
```

### ❌ Carte GIS ne s'affiche pas

```bash
pip install folium streamlit-folium --upgrade
```

### ❌ Erreur lors de la génération PDF

```bash
pip install reportlab --upgrade
# Vérifier que Pillow est installé
pip install Pillow --upgrade
```

### ❌ `ImportError: cannot import name 'pages.dashboard'`

Vérifier que tous les `__init__.py` existent :
```bash
# Linux/macOS
touch pages/__init__.py database/__init__.py models/__init__.py utils/__init__.py
# Windows
type nul > pages\__init__.py
type nul > database\__init__.py
```

### ⚠️ Performance lente sur grands datasets

```python
# Dans db_manager.py, ajouter un index si nécessaire :
# CREATE INDEX IF NOT EXISTS idx_mesures_can ON mesures(canalisation_id);
```

---

## 11. Architecture Technique

### Stack Technologique

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Streamlit)                  │
│  Sidebar navigation · KPI Cards · Formulaires CRUD      │
│  Graphiques Plotly · Carte Folium · Téléchargements PDF  │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                    BACKEND (Python)                      │
│  pages/        → Logique de présentation par module      │
│  utils/        → Charts, UI helpers, PDF generator       │
│  models/       → Pipeline ML : train · predict · save    │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                  BASE DE DONNÉES (SQLite)                 │
│  database/schema.sql  → DDL complet                      │
│  database/db_manager.py → Connexion, CRUD, stats         │
│  database/aquapredict.db → Fichier SQLite                │
└─────────────────────────────────────────────────────────┘
```

### Pipeline Machine Learning

```
Données brutes (CSV / BD)
        ↓
Génération dataset synthétique (2000 exemples par défaut)
        ↓
Split Train (80%) / Test (20%) + Stratification
        ↓
Pipeline Scikit-Learn :
  [StandardScaler] → [RandomForest / XGBoost / GradientBoosting]
        ↓
Cross-Validation (5 folds) → Métriques finales
        ↓
Sauvegarde pickle → models/active_model.pkl
        ↓
Prédiction temps réel (pression, débit, temp, âge, réparations)
        ↓
Résultat : Faible / Moyen / Élevé + score % + probabilités
```

### Flux de données

```
Capteurs IoT → Import CSV → Base SQLite
                                ↓
                    Modèle ML (actif_model.pkl)
                                ↓
                    Prédiction → BD predictions
                                ↓
                    Alerte auto si Risque Élevé
                                ↓
                    Intervention planifiée
                                ↓
                    Rapport PDF → Export
```

---

## Notes pour la Soutenance Master 2

> 💡 **Conseil** : Pour la démonstration live devant le jury, lancez `streamlit run app.py` en avance et gardez la fenêtre ouverte. La BD SQLite est déjà remplie de données de démo.

**Points forts à mettre en avant :**
- Architecture **MVC** propre et modulaire
- Pipeline ML complet avec **métriques industrielles** (accuracy, precision, recall, F1, cross-validation)
- **Carte GIS interactive** avec heatmap de risque
- Système d'**alertes automatiques** déclenché par le ML
- **Export PDF** professionnel avec ReportLab
- **Contrôle d'accès par rôle** (Admin / Ingénieur / Technicien)
- **Import/Export CSV** pour l'interopérabilité avec les SCADA existants

---

*Documentation générée pour AquaPredict AI v1.0.0 — Master 2 Intelligence Artificielle · 2025*
