"""
AquaPredict AI - Module Machine Learning
Entraînement, évaluation et gestion des modèles
"""

import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.ml_model import train_model, get_model_info, list_saved_models, generate_training_data
from utils.ui_helpers import section_header, divider, success_box, info_box
from utils.charts import chart_confusion_matrix, chart_feature_importance


def render():
    section_header("Module Machine Learning", "Entraînement, évaluation et métriques des modèles", "🤖")

    tab1, tab2, tab3 = st.tabs(["🏋️ Entraînement", "📊 Évaluation", "📦 Modèles Sauvegardés"])

    # ── Tab 1 : Entraînement ─────────────────────────────────
    with tab1:
        st.markdown("### Configuration de l'Entraînement")
        col1, col2 = st.columns(2)
        with col1:
            algo = st.selectbox("Algorithme", ["Random Forest", "Gradient Boosting", "XGBoost"],
                                help="XGBoost nécessite la librairie xgboost installée")
            n_samples = st.slider("Taille du dataset", 500, 5000, 2000, 100)
        with col2:
            use_custom = st.checkbox("Utiliser un dataset CSV personnalisé")
            if use_custom:
                uploaded = st.file_uploader("CSV avec colonnes: pression, debit, temperature, age, nb_reparations, risque",
                                             type=["csv"])

        st.markdown("---")
        st.markdown("#### Paramètres Avancés")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.info(f"📊 Taille dataset : **{n_samples}** exemples")
        with c2:
            st.info("✂️ Split train/test : **80% / 20%**")
        with c3:
            st.info("🔄 Cross-validation : **5 folds**")

        divider()

        if st.button("🚀 Lancer l'Entraînement", type="primary", use_container_width=True):
            with st.spinner(f"Entraînement du modèle {algo} en cours..."):
                try:
                    df = None
                    if use_custom and uploaded:
                        df = pd.read_csv(uploaded)
                        st.info(f"Dataset chargé : {len(df)} lignes, {len(df.columns)} colonnes")
                    else:
                        df = generate_training_data(n_samples)

                    metrics = train_model(algo, df)
                    st.session_state["last_metrics"] = metrics
                    success_box(f"✅ Modèle **{algo}** entraîné avec succès !")

                except Exception as e:
                    st.error(f"❌ Erreur : {e}")

        # Afficher métriques si disponibles
        if "last_metrics" in st.session_state:
            m = st.session_state["last_metrics"]
            st.markdown("---")
            st.markdown("### 📈 Résultats d'Entraînement")

            c1, c2, c3, c4 = st.columns(4)
            metrics_display = [
                ("Accuracy", m.get("accuracy", 0), "🎯", "#1565C0"),
                ("Précision", m.get("precision", 0), "🔍", "#0288D1"),
                ("Rappel", m.get("recall", 0), "📡", "#27AE60"),
                ("F1-Score", m.get("f1_score", 0), "⚖️", "#8E44AD"),
            ]
            for col, (label, value, icon, color) in zip([c1, c2, c3, c4], metrics_display):
                with col:
                    st.markdown(f"""
                    <div style="background:white;border-radius:12px;padding:1rem;text-align:center;
                                box-shadow:0 2px 8px rgba(0,0,0,0.08);border-top:4px solid {color}">
                        <div style="font-size:1.8rem;font-weight:800;color:{color}">{value:.1f}%</div>
                        <div style="font-size:0.85rem;color:#64748B;font-weight:500">{icon} {label}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#E3F2FD;border-radius:10px;padding:0.8rem 1.2rem;margin:1rem 0;color:#1565C0">
                📊 Cross-Validation (5 folds) : <strong>{m.get('cv_mean', 0):.1f}% ± {m.get('cv_std', 0):.1f}%</strong>
                &nbsp;&nbsp;|&nbsp;&nbsp; 🏋️ Entraîné sur : <strong>{m.get('n_train', 0)}</strong> exemples
                &nbsp;&nbsp;|&nbsp;&nbsp; 🧪 Testé sur : <strong>{m.get('n_test', 0)}</strong> exemples
            </div>
            """, unsafe_allow_html=True)

    # ── Tab 2 : Évaluation ───────────────────────────────────
    with tab2:
        st.markdown("### 📊 Évaluation du Modèle Actif")
        model_info = get_model_info()

        if not model_info:
            info_box("Aucun modèle entraîné. Allez dans l'onglet **Entraînement**.")
            return

        st.markdown(f"""
        <div style="background:white;border-radius:12px;padding:1.2rem;box-shadow:0 2px 8px rgba(0,0,0,0.08);margin-bottom:1rem">
            <b>Algorithme:</b> {model_info.get('algorithm', 'N/A')} &nbsp;|&nbsp;
            <b>Entraîné le:</b> {model_info.get('trained_at', 'N/A')} &nbsp;|&nbsp;
            <b>Accuracy:</b> <span style="color:#1565C0;font-weight:700">{model_info.get('accuracy', 0):.1f}%</span>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            cm = model_info.get("confusion_matrix", [[0, 0, 0], [0, 0, 0], [0, 0, 0]])
            fig_cm = chart_confusion_matrix(cm)
            st.plotly_chart(fig_cm, use_container_width=True)

        with col2:
            fi = model_info.get("feature_importances", {})
            if fi:
                fig_fi = chart_feature_importance(fi)
                st.plotly_chart(fig_fi, use_container_width=True)
            else:
                st.info("Importance des variables non disponible pour cet algorithme.")

        # Rapport de classification
        st.markdown("#### 📄 Rapport de Classification")
        report = model_info.get("classification_report", "")
        if report:
            st.code(report, language="text")

        # Métriques résumé
        st.markdown("#### 📋 Métriques Résumé")
        metrics_df = pd.DataFrame({
            "Métrique": ["Accuracy", "Précision", "Rappel", "F1-Score", "CV Moyenne", "CV Écart-type"],
            "Valeur (%)": [
                model_info.get("accuracy", 0), model_info.get("precision", 0),
                model_info.get("recall", 0), model_info.get("f1_score", 0),
                model_info.get("cv_mean", 0), model_info.get("cv_std", 0),
            ]
        })
        metrics_df["Valeur (%)"] = metrics_df["Valeur (%)"].round(2)
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)

        # Export métriques
        csv = metrics_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Exporter métriques CSV", csv, "metriques_modele.csv", "text/csv")

    # ── Tab 3 : Modèles sauvegardés ──────────────────────────
    with tab3:
        st.markdown("### 📦 Modèles Entraînés")
        models = list_saved_models()

        if not models:
            info_box("Aucun modèle sauvegardé. Entraînez d'abord un modèle.")
            return

        for mod in models:
            col1, col2, col3, col4 = st.columns([2, 2, 1.5, 1])
            with col1:
                st.markdown(f"**🤖 {mod['algorithm']}**")
            with col2:
                st.markdown(f"📅 {mod['trained_at']}")
            with col3:
                color = "#27AE60" if mod['accuracy'] > 85 else "#F39C12"
                st.markdown(f"<span style='color:{color};font-weight:700'>🎯 {mod['accuracy']:.1f}%</span>",
                            unsafe_allow_html=True)
            with col4:
                st.markdown(f"`{mod['filename']}`")
            st.markdown("---")
