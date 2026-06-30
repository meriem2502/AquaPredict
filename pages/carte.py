"""
AquaPredict AI - Carte GIS
Visualisation géographique du réseau
"""

import streamlit as st
import streamlit.components.v1 as components
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.db_manager import get_all_canalisations, get_all_reservoirs
from utils.ui_helpers import section_header, divider
from utils.charts import create_map, create_reservoirs_map


def render():
    section_header("Carte GIS du Réseau", "Visualisation géographique des canalisations et alertes", "🗺️")

    # Contrôles
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        afficher_reservoirs = st.checkbox("Afficher réservoirs", value=False)
    with col2:
        show_heatmap = st.checkbox("Activer Heatmap risque", value=False)
    with col3:
        filtre_etat = st.selectbox("Filtrer par état", ["Tous", "Bon", "Moyen", "Mauvais", "Critique"])
    with col4:
        filtre_zone = st.selectbox("Filtrer par zone",
                                    [ "Toutes",
        "El Tarf Centre",
        "El Kala",
        "Besbes",
        "Dréan",
        "Bouteldja",
        "Ben M'Hidi",
        "Bouhadjar",
        "Chefia",
        "Zone Industrielle"])

    canalisations = get_all_canalisations(
        zone=None if filtre_zone == "Toutes" else filtre_zone,
        etat=None if filtre_etat == "Tous" else filtre_etat
    )
    reservoirs = get_all_reservoirs() if afficher_reservoirs else []

    # Statistiques rapides
    total = len(canalisations)
    critiques = sum(1 for c in canalisations if c.get("etat") == "Critique")
    mauvais = sum(1 for c in canalisations if c.get("etat") == "Mauvais")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Canalisations affichées", total)
    with c2:
        st.metric("Critiques 🔴", critiques)
    with c3:
        st.metric("Mauvais état 🟠", mauvais)
    with c4:
        st.metric("Réservoirs", len(reservoirs))

    divider()

    # Carte principale
    if not canalisations:
        st.warning("Aucune canalisation à afficher pour ces filtres.")
        return

    with st.spinner("Génération de la carte..."):
        m = create_map(canalisations, show_heatmap=show_heatmap)

        # Ajouter réservoirs si demandé
        if afficher_reservoirs and reservoirs:
            import folium
            for res in reservoirs:
                lat, lon = res.get("latitude"), res.get("longitude")
                if lat and lon:
                    pct = round(res["niveau_actuel"] / res["capacite"] * 100, 1) if res["capacite"] > 0 else 0
                    color = "green" if pct > 60 else ("orange" if pct > 30 else "red")
                    folium.Marker(
                        [lat, lon],
                        icon=folium.Icon(color=color, icon="tint", prefix="fa"),
                        tooltip=f"🏗️ {res['nom']} ({pct}%)",
                    ).add_to(m)

        map_html = m._repr_html_()
        components.html(map_html, height=560)

    # Légende
    st.markdown("""
    <div style="background:white;border-radius:12px;padding:1rem 1.5rem;box-shadow:0 2px 8px rgba(0,0,0,0.08);
                display:flex;gap:2rem;align-items:center;flex-wrap:wrap;margin-top:0.5rem">
        <b style="color:#1565C0">Légende :</b>
        <span>🟢 <b>Bon état</b></span>
        <span>🔵 <b>État moyen</b></span>
        <span>🟠 <b>Mauvais état</b></span>
        <span>🔴 <b>État critique</b></span>
        <span style="color:#64748B;font-size:0.85rem">| Cliquer sur un marqueur pour les détails</span>
    </div>
    """, unsafe_allow_html=True)

    divider()

    # Tableau de localisation
    st.markdown("#### 📍 Canalisations Géolocalisées")
    import pandas as pd
    df = pd.DataFrame(canalisations)
    geo_df = df[["code", "zone", "materiau", "etat", "age", "latitude", "longitude", "nb_reparations"]].copy()
    geo_df.columns = ["Code", "Zone", "Matériau", "État", "Âge (ans)", "Latitude", "Longitude", "Nb Rép."]
    geo_df = geo_df.dropna(subset=["Latitude", "Longitude"])

    def color_etat(val):
        return {"Bon": "color:green", "Moyen": "color:steelblue",
                "Mauvais": "color:orange", "Critique": "color:red"}.get(val, "")

    st.dataframe(geo_df.style.applymap(color_etat, subset=["État"]),
                 use_container_width=True, hide_index=True)
