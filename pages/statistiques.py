"""
AquaPredict AI - Statistiques Avancées
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_manager import get_all_canalisations, get_fuites_par_mois, get_zones_stats, get_predictions_history
from utils.ui_helpers import section_header, divider
from utils.charts import apply_chart_style, COLORS


def render():
    section_header("Statistiques & Analyses", "Tableaux de bord analytiques approfondis", "📈")

    canalisations = get_all_canalisations()
    fuites_mois = get_fuites_par_mois()
    zones = get_zones_stats()
    predictions = get_predictions_history(200)

    tab1, tab2, tab3 = st.tabs(["🔩 Réseau", "💧 Fuites & Risques", "🤖 ML Analytics"])

    with tab1:
        if not canalisations:
            st.info("Aucune donnée disponible.")
            return

        df = pd.DataFrame(canalisations)

        col1, col2 = st.columns(2)
        with col1:
            # Distribution diamètres
            fig = px.histogram(df, x="diametre", nbins=15, title="Distribution Diamètres (mm)",
                               color_discrete_sequence=[COLORS["primary"]])
            fig.update_layout(xaxis_title="Diamètre (mm)", yaxis_title="Nb canalisations")
            st.plotly_chart(apply_chart_style(fig), use_container_width=True)
        with col2:
            # Scatter âge vs nb réparations
            df["etat_color"] = df["etat"].map({"Bon": COLORS["success"], "Moyen": "#3498DB",
                                               "Mauvais": COLORS["warning"], "Critique": COLORS["danger"]})
            fig2 = px.scatter(df, x="age", y="nb_reparations", color="etat", size="diametre",
                              title="Âge vs Réparations par État",
                              color_discrete_map={"Bon": COLORS["success"], "Moyen": "#3498DB",
                                                   "Mauvais": COLORS["warning"], "Critique": COLORS["danger"]})
            fig2.update_layout(xaxis_title="Âge (ans)", yaxis_title="Nb réparations")
            st.plotly_chart(apply_chart_style(fig2), use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            # Matériaux par zone - Heatmap
            if "materiau" in df.columns and "zone" in df.columns:
                ct = pd.crosstab(df["zone"], df["materiau"])
                fig3 = px.imshow(ct, title="Matériaux par Zone", color_continuous_scale="Blues",
                                 text_auto=True)
                st.plotly_chart(apply_chart_style(fig3), use_container_width=True)
        with col4:
            # Box plot âge par matériau
            fig4 = px.box(df, x="materiau", y="age", title="Distribution Âge par Matériau",
                          color="materiau",
                          color_discrete_sequence=px.colors.qualitative.Set2)
            fig4.update_layout(xaxis_title="Matériau", yaxis_title="Âge (ans)")
            st.plotly_chart(apply_chart_style(fig4), use_container_width=True)

        # Tableau stats descriptives
        st.markdown("#### 📊 Statistiques Descriptives")
        num_cols = ["diametre", "longueur", "age", "nb_reparations", "pression_nominale"]
        num_cols = [c for c in num_cols if c in df.columns]
        desc = df[num_cols].describe().round(2)
        desc.index = ["Nb observations", "Moyenne", "Écart-type", "Min", "Q1 (25%)", "Médiane", "Q3 (75%)", "Max"]
        st.dataframe(desc, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            if fuites_mois:
                df_f = pd.DataFrame(fuites_mois).sort_values("mois")
                fig = go.Figure()
                fig.add_trace(go.Bar(x=df_f["mois"], y=df_f["nb_fuites"],
                                     name="Fuites", marker_color=COLORS["danger"]))
                fig.add_trace(go.Scatter(x=df_f["mois"], y=df_f["nb_fuites"].rolling(3, min_periods=1).mean(),
                                         name="Tendance (3 mois)", line=dict(color=COLORS["warning"], width=2, dash="dash")))
                fig.update_layout(title="Fuites par Mois avec Tendance", xaxis_title="Mois", yaxis_title="Nb fuites")
                st.plotly_chart(apply_chart_style(fig), use_container_width=True)
        with col2:
            if zones:
                df_z = pd.DataFrame(zones)
                df_z["pct_critiques"] = (df_z["nb_critiques"] / df_z["nb_canalisations"] * 100).round(1)
                fig = px.treemap(df_z, path=["zone"], values="nb_canalisations",
                                 color="pct_critiques", title="Treemap Zones par Criticité",
                                 color_continuous_scale=["#27AE60", "#F39C12", "#E74C3C"])
                st.plotly_chart(apply_chart_style(fig), use_container_width=True)

    with tab3:
        if predictions:
            df_p = pd.DataFrame(predictions)
            col1, col2 = st.columns(2)
            with col1:
                if "risque_niveau" in df_p.columns:
                    counts = df_p["risque_niveau"].value_counts()
                    fig = go.Figure(go.Bar(x=counts.index, y=counts.values,
                                           marker_color=[COLORS["success"], COLORS["warning"], COLORS["danger"]],
                                           text=counts.values, textposition="outside"))
                    fig.update_layout(title="Distribution des Niveaux de Risque Prédits")
                    st.plotly_chart(apply_chart_style(fig), use_container_width=True)
            with col2:
                if "score_risque" in df_p.columns and "timestamp" in df_p.columns:
                    df_p["timestamp"] = pd.to_datetime(df_p["timestamp"])
                    df_p = df_p.sort_values("timestamp")
                    fig = px.line(df_p, x="timestamp", y="score_risque",
                                  title="Évolution du Score de Risque",
                                  color_discrete_sequence=[COLORS["danger"]])
                    fig.update_layout(xaxis_title="Date", yaxis_title="Score (%)")
                    st.plotly_chart(apply_chart_style(fig), use_container_width=True)
        else:
            st.info("Aucune prédiction enregistrée pour l'analyse.")
