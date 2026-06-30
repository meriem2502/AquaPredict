"""
AquaPredict AI - Page Dashboard
KPI, statistiques temps réel, graphiques synthétiques
"""

import streamlit as st
import sys, os

import streamlit as st



sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.db_manager import get_dashboard_stats, get_all_canalisations, get_fuites_par_mois, get_zones_stats, get_alertes
from utils.ui_helpers import kpi_card, section_header, divider
from utils.charts import (
    chart_etat_canalisations, chart_fuites_par_mois, chart_zones_risque,
    chart_materiau_pie, chart_age_distribution, chart_risque_gauge
)


def render():

   

    section_header("Dashboard", "Vue d'ensemble du réseau en temps réel", "📊")

    stats = get_dashboard_stats()

    canalisations = get_all_canalisations()

    fuites_mois = get_fuites_par_mois()
    zones = get_zones_stats()
    alertes = get_alertes()
        
    # ── KPI Row ──────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Canalisations", stats["nb_canalisations"], "🔩", "#1565C0", "Réseau surveillé")
    with c2:
        kpi_card("Alertes Actives", stats["nb_alertes"], "🚨",
                 "#E74C3C" if stats["nb_alertes"] > 5 else "#F39C12", "Non résolues")
    with c3:
        kpi_card("Score Risque Moyen", f"{stats['risque_moyen']:.1f}", "📈",
                 "#E74C3C" if stats["risque_moyen"] > 60 else "#27AE60", unit="%")
    with c4:
        kpi_card("Fuites Non Réparées", stats["nb_fuites"], "💧",
                 "#E74C3C" if stats["nb_fuites"] > 3 else "#27AE60")

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        kpi_card("Alertes Critiques", stats["nb_alertes_critiques"], "🔴",
                 "#E74C3C" if stats["nb_alertes_critiques"] > 0 else "#27AE60")
    with c6:
        kpi_card("Réservoirs", stats["nb_reservoirs"], "🏗️", "#0288D1")
    with c7:
        kpi_card("Interventions en cours", stats["nb_interventions_en_cours"], "🔧", "#8E44AD")
    with c8:
        total_can = len(canalisations)
        critiques = sum(1 for c in canalisations if c.get("etat") == "Critique")
        kpi_card("Canalisations Critiques", critiques, "⚠️",
                 "#E74C3C" if critiques > 5 else "#F39C12",
                 f"{critiques/total_can*100:.1f}% du réseau" if total_can else "")

    divider()

    # ── Row 2: Gauge + Etat ──────────────────────────────────
    col1, col2, col3 = st.columns([1.2, 1.5, 1.5])
    with col1:
        fig_gauge = chart_risque_gauge(stats["risque_moyen"])
        st.plotly_chart(fig_gauge, use_container_width=True)
    with col2:
        fig_etat = chart_etat_canalisations(canalisations)
        st.plotly_chart(fig_etat, use_container_width=True)
    with col3:
        fig_mat = chart_materiau_pie(canalisations)
        st.plotly_chart(fig_mat, use_container_width=True)

    # ── Row 3: Fuites par mois + Zones ──────────────────────
    col4, col5 = st.columns([1.5, 1.2])
    with col4:
        fig_fuites = chart_fuites_par_mois(fuites_mois)
        st.plotly_chart(fig_fuites, use_container_width=True)
    with col5:
        fig_zones = chart_zones_risque(zones)
        st.plotly_chart(fig_zones, use_container_width=True)

    # ── Row 4: Distribution âge + Alertes récentes ──────────
    col6, col7 = st.columns([1.5, 1.2])
    with col6:
        fig_age = chart_age_distribution(canalisations)
        st.plotly_chart(fig_age, use_container_width=True)
    with col7:
        st.markdown("#### 🚨 Dernières Alertes")
        if alertes:
            for a in alertes[:6]:
                p = a.get("priorite", "Basse")
                p_color = {"Critique": "🔴", "Haute": "🟠", "Moyenne": "🟡", "Basse": "🟢"}.get(p, "⚪")
                st.markdown(f"""
                <div style="background:white;border-radius:8px;padding:0.6rem 1rem;margin:0.3rem 0;
                            border-left:4px solid {'#E74C3C' if p=='Critique' else '#F39C12' if p=='Haute' else '#3498DB'};
                            box-shadow:0 1px 4px rgba(0,0,0,0.06)">
                    <div style="font-weight:600;font-size:0.88rem">{p_color} {a.get('type_alerte','')}</div>
                    <div style="color:#64748B;font-size:0.78rem">{a.get('zone','N/A')} | {p}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ Aucune alerte active")

    divider()

    # ── Tableau récapitulatif zones ──────────────────────────
    st.markdown("#### 🗺️ Récapitulatif par Zone")
    import pandas as pd
    if zones:
        df_zones = pd.DataFrame(zones)
        df_zones["age_moyen"] = df_zones["age_moyen"].round(1)
        df_zones.columns = ["Zone", "Nb Canalisations", "Âge Moyen (ans)", "Nb Critiques"]
        st.dataframe(df_zones.style.background_gradient(subset=["Nb Critiques"], cmap="Reds"),
                     use_container_width=True, hide_index=True)
