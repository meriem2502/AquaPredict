"""
AquaPredict AI - Module Machine Learning
Entraînement, évaluation et prédiction des fuites
Algorithmes : Random Forest + XGBoost
"""

import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from sklearn.pipeline import Pipeline

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
os.makedirs(MODEL_DIR, exist_ok=True)


# ── Génération de données d'entraînement synthétiques ────────

def generate_training_data(n_samples: int = 2000) -> pd.DataFrame:
    """
    Génère un dataset synthétique réaliste pour l'entraînement.
    Features : pression, debit, temperature, age, nb_reparations, materiau, diametre
    Target   : risque (0=Faible, 1=Moyen, 2=Élevé)
    """
    np.random.seed(42)

    data = {
        "pression": np.random.uniform(1.0, 12.0, n_samples),
        "debit": np.random.uniform(5.0, 600.0, n_samples),
        "temperature": np.random.uniform(5.0, 35.0, n_samples),
        "age": np.random.randint(1, 60, n_samples),
        "nb_reparations": np.random.randint(0, 20, n_samples),
        "diametre": np.random.choice([100, 150, 200, 250, 300, 400, 500], n_samples),
        "longueur": np.random.uniform(50, 2000, n_samples),
    }
    df = pd.DataFrame(data)

    # Règles métier pour générer le risque de manière réaliste
    risk_score = np.zeros(n_samples)
    risk_score += np.where(df["age"] > 40, 2.5, np.where(df["age"] > 25, 1.2, 0))
    risk_score += np.where(df["pression"] > 9, 2.0, np.where(df["pression"] > 7, 0.8, 0))
    risk_score += np.where(df["debit"] < 20, 1.5, np.where(df["debit"] < 50, 0.5, 0))
    risk_score += np.where(df["nb_reparations"] > 10, 2.0, np.where(df["nb_reparations"] > 5, 0.8, 0))
    risk_score += np.where(df["diametre"] < 150, 0.5, 0)
    risk_score += np.random.normal(0, 0.3, n_samples)  # bruit

    # Convertir en classes
    df["risque"] = np.where(risk_score < 1.5, 0, np.where(risk_score < 3.5, 1, 2))
    return df


# ── Entraînement ─────────────────────────────────────────────

def train_model(algorithm: str = "Random Forest", df: pd.DataFrame = None):
    """
    Entraîne un modèle ML sur les données fournies ou générées.
    Retourne les métriques d'évaluation et sauvegarde le modèle.
    """
    if df is None:
        df = generate_training_data()

    feature_cols = ["pression", "debit", "temperature", "age", "nb_reparations", "diametre", "longueur"]
    available_cols = [c for c in feature_cols if c in df.columns]

    X = df[available_cols]
    y = df["risque"] if "risque" in df.columns else df.iloc[:, -1]

    # Encodage si nécessaire
    if y.dtype == object:
        le = LabelEncoder()
        y = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Choix de l'algorithme
    if algorithm == "Random Forest":
        clf = RandomForestClassifier(n_estimators=200, max_depth=10, min_samples_split=5,
                                     random_state=42, n_jobs=-1)
    elif algorithm == "XGBoost" and XGBOOST_AVAILABLE:
        clf = XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1,
                            use_label_encoder=False, eval_metric="mlogloss", random_state=42)
    elif algorithm == "Gradient Boosting":
        clf = GradientBoostingClassifier(n_estimators=150, max_depth=5, learning_rate=0.1, random_state=42)
    else:
        clf = RandomForestClassifier(n_estimators=200, random_state=42)

    # Pipeline avec normalisation
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", clf)
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    # Métriques
    metrics = {
        "algorithm": algorithm,
        "accuracy": round(accuracy_score(y_test, y_pred) * 100, 2),
        "precision": round(precision_score(y_test, y_pred, average="weighted", zero_division=0) * 100, 2),
        "recall": round(recall_score(y_test, y_pred, average="weighted", zero_division=0) * 100, 2),
        "f1_score": round(f1_score(y_test, y_pred, average="weighted", zero_division=0) * 100, 2),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred,
                                                        target_names=["Faible", "Moyen", "Élevé"],
                                                        zero_division=0),
        "feature_names": available_cols,
        "n_train": len(X_train),
        "n_test": len(X_test),
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Importance des variables (si disponible)
    try:
        importances = pipeline.named_steps["classifier"].feature_importances_
        metrics["feature_importances"] = dict(zip(available_cols, importances.tolist()))
    except AttributeError:
        metrics["feature_importances"] = {}

    # Cross-validation
    cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring="accuracy")
    metrics["cv_mean"] = round(cv_scores.mean() * 100, 2)
    metrics["cv_std"] = round(cv_scores.std() * 100, 2)

    # Sauvegarde du modèle
    model_path = os.path.join(MODEL_DIR, f"model_{algorithm.replace(' ', '_').lower()}.pkl")
    with open(model_path, "wb") as f:
        pickle.dump({"pipeline": pipeline, "feature_names": available_cols, "metrics": metrics}, f)

    # Sauvegarde du modèle "actif"
    active_path = os.path.join(MODEL_DIR, "active_model.pkl")
    with open(active_path, "wb") as f:
        pickle.dump({"pipeline": pipeline, "feature_names": available_cols, "metrics": metrics}, f)

    return metrics


# ── Prédiction ───────────────────────────────────────────────

def load_active_model():
    """Charge le modèle actif ou en entraîne un nouveau."""
    active_path = os.path.join(MODEL_DIR, "active_model.pkl")
    if not os.path.exists(active_path):
        train_model("Random Forest")
    with open(active_path, "rb") as f:
        return pickle.load(f)


def predict_risk(pression: float, debit: float, temperature: float,
                 age: int, nb_reparations: int,
                 diametre: float = 200, longueur: float = 500):
    """
    Prédit le niveau de risque de fuite pour une canalisation.

    Returns:
        dict: {risque_niveau, score_risque, probabilities, label}
    """
    model_data = load_active_model()
    pipeline = model_data["pipeline"]
    feature_names = model_data["feature_names"]

    # Préparer les features dans le bon ordre
    feature_map = {
        "pression": pression, "debit": debit, "temperature": temperature,
        "age": age, "nb_reparations": nb_reparations,
        "diametre": diametre, "longueur": longueur
    }
    X = np.array([[feature_map.get(f, 0) for f in feature_names]])

    prediction = pipeline.predict(X)[0]
    probabilities = pipeline.predict_proba(X)[0]

    labels = {0: "Faible", 1: "Moyen", 2: "Élevé"}
    colors = {0: "#27AE60", 1: "#F39C12", 2: "#E74C3C"}

    score = round(probabilities[2] * 100, 1)  # % risque élevé

    return {
        "risque_niveau": labels[prediction],
        "score_risque": score,
        "probabilities": {
            "Faible": round(probabilities[0] * 100, 1),
            "Moyen": round(probabilities[1] * 100, 1),
            "Élevé": round(probabilities[2] * 100, 1),
        },
        "color": colors[prediction],
        "prediction_class": int(prediction),
    }


def get_model_info():
    """Retourne les informations du modèle actif."""
    active_path = os.path.join(MODEL_DIR, "active_model.pkl")
    if not os.path.exists(active_path):
        return None
    with open(active_path, "rb") as f:
        data = pickle.load(f)
    return data.get("metrics", {})


def list_saved_models():
    """Liste tous les modèles sauvegardés."""
    models = []
    for f in os.listdir(MODEL_DIR):
        if f.endswith(".pkl") and f != "active_model.pkl":
            path = os.path.join(MODEL_DIR, f)
            try:
                with open(path, "rb") as fp:
                    data = pickle.load(fp)
                metrics = data.get("metrics", {})
                models.append({
                    "filename": f,
                    "algorithm": metrics.get("algorithm", "Inconnu"),
                    "accuracy": metrics.get("accuracy", 0),
                    "trained_at": metrics.get("trained_at", "N/A"),
                })
            except Exception:
                pass
    return models
