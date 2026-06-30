"""
AquaPredict AI - Page Réservoirs
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_manager import get_all_reservoirs, update_reservoir_niveau
from utils.ui_helpers import section_header, divider, success_box
from utils.charts import create_reservoirs_map
import streamlit.components.v1 as components


def render():
    section_header("Gestion des Réservoirs", "Surveillance des niveaux et capacités", "🏗️")

    reservoirs = get_all_reservoirs()
    if not reservoirs:
        st.info("Aucun réservoir configuré.")
        return

    # KPI réservoirs
    cols = st.columns(len(reservoirs))
    for col, res in zip(cols, reservoirs):
        capacite = res["capacite"] or 1
        niveau = res["niveau_actuel"] or 0
        pct = round(niveau / capacite * 100, 1)
        color = "#27AE60" if pct > 60 else ("#F39C12" if pct > 30 else "#E74C3C")
        with col:
            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:1rem;text-align:center;
                        box-shadow:0 2px 8px rgba(0,0,0,0.08);border-top:5px solid {color}">
                <div style="font-size:0.85rem;font-weight:700;color:#1565C0">{res['nom']}</div>
                <div style="font-size:1.8rem;font-weight:800;color:{color}">{pct}%</div>
                <div style="font-size:0.78rem;color:#64748B">{niveau:,.0f} / {capacite:,.0f} m³</div>
                <div style="font-size:0.75rem;color:#94A3B8">{res['zone']}</div>
            </div>""", unsafe_allow_html=True)

    divider()

    # Carte réservoirs
    st.markdown("#### 🗺️ Localisation des Réservoirs")
    m = create_reservoirs_map(reservoirs)
    components.html(m._repr_html_(), height=400)

    divider()

    # Mise à jour niveaux
    st.markdown("#### 🔄 Mettre à jour le Niveau")
    col1, col2, col3 = st.columns(3)
    res_opts = {r["nom"]: r for r in reservoirs}
    with col1:
        sel = st.selectbox("Réservoir", list(res_opts.keys()))
    with col2:
        res_sel = res_opts[sel]
        nouveau_niveau = st.number_input("Nouveau niveau (m³)", 0.0, float(res_sel["capacite"]),
                                         float(res_sel["niveau_actuel"]))
    with col3:
        st.write("")
        st.write("")
        if st.button("💾 Mettre à jour", type="primary", use_container_width=True):
            update_reservoir_niveau(res_sel["id"], nouveau_niveau)
            success_box("Niveau mis à jour !")
            st.rerun()
