"""
AquaPredict AI - Génération de Rapports
"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_manager import get_dashboard_stats, get_all_canalisations, get_alertes, get_predictions_history
from utils.ui_helpers import section_header, divider, info_box
from utils.pdf_generator import generate_rapport_journalier


def render():
    section_header("Rapports & Exports", "Génération de rapports PDF et exports Excel", "📄")

    tab1, tab2 = st.tabs(["📋 Rapports PDF", "📊 Exports Excel/CSV"])

    with tab1:
        st.markdown("### Générer un Rapport PDF")

        col1, col2 = st.columns(2)
        with col1:
            type_rapport = st.selectbox("Type de rapport",
                                         ["Rapport Journalier", "Rapport Mensuel", "Rapport Réseau Complet"])
            inclure_alertes = st.checkbox("Inclure les alertes", value=True)
            inclure_predictions = st.checkbox("Inclure les prédictions ML", value=True)
        with col2:
            inclure_canalisations = st.checkbox("Inclure état des canalisations", value=True)
            st.markdown("""
            <div style="background:#E3F2FD;border-radius:10px;padding:1rem;color:#1565C0;font-size:0.88rem">
                📌 Le rapport inclura : KPIs, statistiques du réseau, alertes actives, prédictions ML et recommandations.
            </div>""", unsafe_allow_html=True)

        divider()

        if st.button("📄 Générer le Rapport PDF", type="primary", use_container_width=True):
            with st.spinner("Génération du rapport en cours..."):
                user = st.session_state.get("user", {"full_name": "Système"})
                stats = get_dashboard_stats()
                canalisations = get_all_canalisations() if inclure_canalisations else []
                alertes = get_alertes() if inclure_alertes else []
                predictions = get_predictions_history(20) if inclure_predictions else []

                pdf_bytes = generate_rapport_journalier(
                    stats, canalisations, alertes, predictions,
                    user_name=user.get("full_name", "Système")
                )

            st.success("✅ Rapport généré avec succès !")
            st.download_button(
                "⬇️ Télécharger le PDF",
                pdf_bytes,
                f"rapport_aquapredict_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                "application/pdf",
                use_container_width=True,
            )

        divider()
        st.markdown("""
        <div style="background:white;border-radius:12px;padding:1.2rem;box-shadow:0 2px 8px rgba(0,0,0,0.07)">
            <h4 style="color:#1565C0;margin:0 0 0.8rem 0">📋 Types de Rapports Disponibles</h4>
            <table style="width:100%;border-collapse:collapse;font-size:0.88rem">
                <tr style="background:#E3F2FD"><th style="padding:8px;text-align:left">Rapport</th><th>Contenu</th><th>Fréquence</th></tr>
                <tr><td style="padding:8px">📊 Journalier</td><td>KPIs, alertes du jour, prédictions</td><td>Quotidien</td></tr>
                <tr style="background:#F8FAFC"><td style="padding:8px">📅 Mensuel</td><td>Statistiques, tendances, zones critiques</td><td>Mensuel</td></tr>
                <tr><td style="padding:8px">🔩 Réseau Complet</td><td>État de toutes les canalisations</td><td>Trimestriel</td></tr>
            </table>
        </div>""", unsafe_allow_html=True)

    with tab2:
        st.markdown("### Exports de Données")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📥 Exporter Canalisations", use_container_width=True):
                cans = get_all_canalisations()
                df = pd.DataFrame(cans)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Télécharger CSV", csv, "canalisations.csv", "text/csv",
                                   use_container_width=True)
        with col2:
            if st.button("📥 Exporter Alertes", use_container_width=True):
                alertes = get_alertes() + get_alertes(resolues=True)
                df = pd.DataFrame(alertes)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Télécharger CSV", csv, "alertes.csv", "text/csv",
                                   use_container_width=True)
        with col3:
            if st.button("📥 Exporter Prédictions", use_container_width=True):
                preds = get_predictions_history(500)
                df = pd.DataFrame(preds)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Télécharger CSV", csv, "predictions.csv", "text/csv",
                                   use_container_width=True)
