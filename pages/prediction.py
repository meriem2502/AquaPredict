"""
AquaPredict AI - Module de Prédiction
Prédiction du risque de fuite pour une canalisation
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.ml_model import predict_risk, get_model_info
from database.db_manager import get_all_canalisations, save_prediction, get_predictions_history, add_alerte
from utils.ui_helpers import section_header, divider, info_box
from utils.charts import chart_prediction_probabilities
from utils.pdf_generator import generate_rapport_prediction
import pandas as pd


def render():
    section_header("Prédiction des Fuites", "Analyse ML du risque par canalisation", "🔮")

    model_info = get_model_info()
    if not model_info:
        info_box("⚠️ Aucun modèle ML entraîné. Allez dans le module **Machine Learning** pour entraîner un modèle.")
        return

    st.markdown(f"""
    <div style="background:#E3F2FD;border-radius:10px;padding:0.7rem 1.2rem;margin-bottom:1rem;
                display:flex;align-items:center;gap:1rem;color:#1565C0">
        🤖 <b>Modèle actif:</b> {model_info.get('algorithm','N/A')} &nbsp;|&nbsp;
        🎯 <b>Accuracy:</b> {model_info.get('accuracy',0):.1f}% &nbsp;|&nbsp;
        📅 Entraîné le {model_info.get('trained_at','N/A')}
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔮 Nouvelle Prédiction", "📜 Historique"])

    with tab1:
        col_form, col_result = st.columns([1.2, 1])

        with col_form:
            st.markdown("### 📥 Paramètres d'Entrée")

            # Sélection canalisation optionnelle
            canalisations = get_all_canalisations()
            can_options = {"-- Entrée manuelle --": None}
            can_options.update({f"{c['code']} — {c['zone']}": c for c in canalisations})
            selected = st.selectbox("Sélectionner une canalisation (optionnel)", list(can_options.keys()))
            can = can_options[selected]

            with st.form("form_prediction"):
                st.markdown("#### Mesures en temps réel")
                c1, c2 = st.columns(2)
                with c1:
                    pression = st.number_input("Pression (bar) 💨", 0.0, 20.0,
                                               float(can.get("pression_nominale") or 5.0) if can else 5.0, 0.1)
                    debit = st.number_input("Débit (m³/h) 🌊", 0.0, 1000.0,
                                            float(can.get("debit_nominal") or 100.0) if can else 100.0, 5.0)
                    temperature = st.number_input("Température (°C) 🌡️", -5.0, 50.0, 20.0, 0.5)
                with c2:
                    age = st.number_input("Âge canalisation (ans) 📅", 0, 100,
                                          int(can.get("age") or 10) if can else 10)
                    nb_rep = st.number_input("Nb réparations 🔧", 0, 50,
                                             int(can.get("nb_reparations") or 0) if can else 0)
                    diametre = st.number_input("Diamètre (mm) 📏", 50, 1000,
                                               int(can.get("diametre") or 200) if can else 200, 50)
                    longueur = st.number_input("Longueur (m) 📐", 1.0, 5000.0,
                                               float(can.get("longueur") or 500.0) if can else 500.0, 50.0)

                auto_alerte = st.checkbox("Créer alerte automatique si risque élevé", value=True)
                submitted = st.form_submit_button("🚀 Analyser le Risque", type="primary", use_container_width=True)

        with col_result:
            if submitted:
                with st.spinner("Analyse en cours..."):
                    result = predict_risk(pression, debit, temperature, age, nb_rep, diametre, longueur)

                st.session_state["last_prediction"] = result
                st.session_state["last_pred_can"] = can

                # Sauvegarder en base
                save_prediction({
                    "canalisation_id": can["id"] if can else None,
                    "pression": pression, "debit": debit, "temperature": temperature,
                    "age_canalisation": age, "nb_reparations": nb_rep,
                    "risque_niveau": result["risque_niveau"],
                    "score_risque": result["score_risque"],
                    "modele_utilise": model_info.get("algorithm", "N/A"),
                })

                # Alerte automatique
                if auto_alerte and result["risque_niveau"] == "Élevé" and can:
                    add_alerte(can["id"], "Prédiction ML - Risque Élevé", "Critique",
                               f"Score de risque: {result['score_risque']:.1f}% — Intervention recommandée")
                    st.warning("🚨 Alerte critique créée automatiquement !")

            if "last_prediction" in st.session_state:
                result = st.session_state["last_prediction"]
                risk_colors = {"Faible": "#27AE60", "Moyen": "#F39C12", "Élevé": "#E74C3C"}
                risk_bg = {"Faible": "#D4EDDA", "Moyen": "#FFF3CD", "Élevé": "#FDE8E8"}
                color = risk_colors.get(result["risque_niveau"], "#333")
                bg = risk_bg.get(result["risque_niveau"], "#F5F5F5")

                st.markdown(f"""
                <div style="background:{bg};border-radius:16px;padding:2rem;text-align:center;
                            border:2px solid {color};margin:1rem 0;box-shadow:0 4px 20px rgba(0,0,0,0.08)">
                    <div style="font-size:3.5rem">{'🔴' if result['risque_niveau']=='Élevé' else '🟡' if result['risque_niveau']=='Moyen' else '🟢'}</div>
                    <div style="font-size:2rem;font-weight:800;color:{color}">{result['risque_niveau']}</div>
                    <div style="font-size:1rem;color:#64748B;margin-top:0.3rem">Niveau de Risque</div>
                    <div style="font-size:3rem;font-weight:800;color:{color};margin:0.5rem 0">{result['score_risque']:.1f}%</div>
                    <div style="font-size:0.9rem;color:#64748B">Score de Risque</div>
                </div>
                """, unsafe_allow_html=True)

                fig = chart_prediction_probabilities(result["probabilities"])
                st.plotly_chart(fig, use_container_width=True)

                # Recommandation
                recs = {
                    "Faible": "✅ Réseau en bon état. Surveillance standard recommandée.",
                    "Moyen": "⚠️ Surveillance renforcée. Inspection dans les 30 jours.",
                    "Élevé": "🚨 INTERVENTION URGENTE. Planifier dans les 7 jours !",
                }
                st.markdown(f"""
                <div style="background:white;border-radius:10px;padding:1rem;border-left:4px solid {color};
                            box-shadow:0 2px 8px rgba(0,0,0,0.06);margin-top:0.5rem">
                    <b>Recommandation:</b><br>{recs[result['risque_niveau']]}
                </div>
                """, unsafe_allow_html=True)

                # Export PDF
                can_info = st.session_state.get("last_pred_can") or {}
                user = st.session_state.get("user", {})
                pdf_bytes = generate_rapport_prediction(result, can_info, user.get("full_name", ""))
                st.download_button("📄 Télécharger Rapport PDF", pdf_bytes,
                                   "rapport_prediction.pdf", "application/pdf",
                                   use_container_width=True)

    with tab2:
        st.markdown("### 📜 Historique des Prédictions")
        history = get_predictions_history(100)
        if history:
            df = pd.DataFrame(history)
            cols = ["timestamp", "canalisation_code", "zone", "risque_niveau",
                    "score_risque", "pression", "debit", "temperature", "age_canalisation", "nb_reparations"]
            cols = [c for c in cols if c in df.columns]
            df_disp = df[cols].copy()
            df_disp.columns = ["Date", "Canalisation", "Zone", "Risque", "Score (%)",
                                "Pression", "Débit", "Temp.", "Âge", "Nb Rép."][:len(cols)]

            def color_risque(val):
                return {"Élevé": "background-color:#FDE8E8;color:#C0392B",
                        "Moyen": "background-color:#FFF3CD;color:#856404",
                        "Faible": "background-color:#D4EDDA;color:#155724"}.get(val, "")

            st.dataframe(df_disp.style.applymap(color_risque, subset=["Risque"] if "Risque" in df_disp.columns else []),
                         use_container_width=True, hide_index=True)

            csv = df_disp.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Exporter CSV", csv, "historique_predictions.csv", "text/csv")
        else:
            info_box("Aucune prédiction enregistrée. Effectuez une prédiction.")
