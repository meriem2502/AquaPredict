"""
AquaPredict AI - Utilitaires : graphiques, cartes, helpers
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
import streamlit as st

# ── Couleurs ──────────────────────────────────────────────────
COLORS = {
    "primary": "#1565C0",
    "secondary": "#0288D1",
    "accent": "#00BCD4",
    "success": "#27AE60",
    "warning": "#F39C12",
    "danger": "#E74C3C",
    "bg": "#F0F4F8",
    "card": "#FFFFFF",
    "text": "#1A2332",
    "faible": "#27AE60",
    "moyen": "#F39C12",
    "eleve": "#E74C3C",
}

PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, sans-serif", "color": "#1A2332"},
        "colorway": ["#1565C0", "#0288D1", "#00BCD4", "#27AE60", "#F39C12", "#E74C3C"],
        "margin": {"l": 40, "r": 20, "t": 40, "b": 40},
    }
}


def apply_chart_style(fig):
    """Applique un style cohérent aux graphiques Plotly."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248,250,252,0.5)",
        font=dict(family="Inter, sans-serif", color="#1A2332"),
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="#E2E8F0", borderwidth=1),
    )
    fig.update_xaxes(gridcolor="#E2E8F0", linecolor="#CBD5E0")
    fig.update_yaxes(gridcolor="#E2E8F0", linecolor="#CBD5E0")
    return fig


# ── Graphiques Dashboard ──────────────────────────────────────

def chart_risque_gauge(score: float):
    """Jauge circulaire du score de risque."""
    color = COLORS["faible"] if score < 33 else (COLORS["moyen"] if score < 66 else COLORS["danger"])
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        number={"suffix": "%", "font": {"size": 36}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"size": 11}},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 33], "color": "#D4EFDF"},
                {"range": [33, 66], "color": "#FDEBD0"},
                {"range": [66, 100], "color": "#FADBD8"},
            ],
            "threshold": {"line": {"color": "red", "width": 2}, "value": 80},
        },
        title={"text": "Score de Risque Global", "font": {"size": 14}},
    ))
    fig.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=40, b=10))
    return fig


def chart_etat_canalisations(data: list):
    """Graphique en anneau — état des canalisations."""
    df = pd.DataFrame(data)
    if df.empty or "etat" not in df.columns:
        return go.Figure()
    counts = df["etat"].value_counts()
    color_map = {"Bon": COLORS["success"], "Moyen": "#3498DB",
                 "Mauvais": COLORS["warning"], "Critique": COLORS["danger"]}
    fig = go.Figure(go.Pie(
        labels=counts.index.tolist(),
        values=counts.values.tolist(),
        hole=0.55,
        marker_colors=[color_map.get(e, "#95A5A6") for e in counts.index],
        textinfo="label+percent",
        textfont_size=12,
    ))
    fig.update_layout(title="État des Canalisations", height=300, showlegend=True)
    return apply_chart_style(fig)


def chart_fuites_par_mois(data: list):
    """Graphique barres — fuites par mois."""
    if not data:
        return go.Figure()
    df = pd.DataFrame(data)
    df = df.sort_values("mois")
    fig = go.Figure(go.Bar(
        x=df["mois"], y=df["nb_fuites"],
        marker_color=COLORS["primary"],
        marker_line_color=COLORS["secondary"],
        marker_line_width=1,
        text=df["nb_fuites"], textposition="outside",
    ))
    fig.update_layout(title="Fuites Détectées par Mois", xaxis_title="Mois", yaxis_title="Nombre")
    return apply_chart_style(fig)


def chart_zones_risque(data: list):
    """Graphique barres horizontales — risque par zone."""
    if not data:
        return go.Figure()
    df = pd.DataFrame(data)
    df["taux_critique"] = (df["nb_critiques"] / df["nb_canalisations"] * 100).round(1)
    df = df.sort_values("taux_critique")
    colors = [COLORS["danger"] if x > 30 else (COLORS["warning"] if x > 15 else COLORS["success"])
              for x in df["taux_critique"]]
    fig = go.Figure(go.Bar(
        x=df["taux_critique"], y=df["zone"],
        orientation="h",
        marker_color=colors,
        text=df["taux_critique"].apply(lambda x: f"{x}%"),
        textposition="outside",
    ))
    fig.update_layout(title="Taux de Risque par Zone (%)", xaxis_title="%", height=320)
    return apply_chart_style(fig)


def chart_age_distribution(canalisations: list):
    """Histogramme de la distribution des âges."""
    if not canalisations:
        return go.Figure()
    df = pd.DataFrame(canalisations)
    if "age" not in df.columns:
        return go.Figure()
    fig = px.histogram(df, x="age", nbins=20, title="Distribution de l'Âge des Canalisations",
                       color_discrete_sequence=[COLORS["primary"]])
    fig.update_layout(xaxis_title="Âge (années)", yaxis_title="Nombre")
    return apply_chart_style(fig)


def chart_materiau_pie(canalisations: list):
    """Camembert des matériaux."""
    if not canalisations:
        return go.Figure()
    df = pd.DataFrame(canalisations)
    counts = df["materiau"].value_counts()
    fig = go.Figure(go.Pie(labels=counts.index, values=counts.values, hole=0.4,
                           textinfo="label+percent"))
    fig.update_layout(title="Répartition par Matériau", height=280)
    return apply_chart_style(fig)


def chart_confusion_matrix(cm: list, labels=None):
    """Heatmap matrice de confusion."""
    if labels is None:
        labels = ["Faible", "Moyen", "Élevé"]
    cm_array = np.array(cm)
    fig = go.Figure(go.Heatmap(
        z=cm_array,
        x=[f"Prédit: {l}" for l in labels],
        y=[f"Réel: {l}" for l in labels],
        colorscale="Blues",
        text=cm_array.astype(str),
        texttemplate="%{text}",
        textfont={"size": 16},
        showscale=True,
    ))
    fig.update_layout(title="Matrice de Confusion", height=350)
    return apply_chart_style(fig)


def chart_feature_importance(importances: dict):
    """Graphique d'importance des variables."""
    if not importances:
        return go.Figure()
    items = sorted(importances.items(), key=lambda x: x[1])
    labels_fr = {
        "pression": "Pression", "debit": "Débit", "temperature": "Température",
        "age": "Âge", "nb_reparations": "Nb Réparations",
        "diametre": "Diamètre", "longueur": "Longueur"
    }
    features = [labels_fr.get(k, k) for k, _ in items]
    values = [v for _, v in items]
    fig = go.Figure(go.Bar(x=values, y=features, orientation="h",
                           marker_color=COLORS["secondary"],
                           text=[f"{v:.3f}" for v in values], textposition="outside"))
    fig.update_layout(title="Importance des Variables", height=350)
    return apply_chart_style(fig)


def chart_prediction_probabilities(probs: dict):
    """Graphique en barres des probabilités de prédiction."""
    colors = [COLORS["faible"], COLORS["moyen"], COLORS["danger"]]
    fig = go.Figure(go.Bar(
        x=list(probs.keys()),
        y=list(probs.values()),
        marker_color=colors,
        text=[f"{v:.1f}%" for v in probs.values()],
        textposition="outside",
    ))
    fig.update_layout(title="Probabilités par Niveau de Risque", yaxis_title="%",
                      yaxis_range=[0, 110], height=300)
    return apply_chart_style(fig)


def chart_reservoir_history(data: list, nom: str):
    """Graphique linéaire historique niveau réservoir."""
    if not data:
        return go.Figure()
    df = pd.DataFrame(data)
    fig = go.Figure(go.Scatter(x=df["timestamp"], y=df["niveau"],
                                mode="lines+markers", line=dict(color=COLORS["primary"], width=2),
                                fill="tozeroy", fillcolor=f"rgba(21,101,192,0.1)"))
    fig.update_layout(title=f"Historique Niveau — {nom}", xaxis_title="Date",
                      yaxis_title="Niveau (m³)", height=300)
    return apply_chart_style(fig)


# ── Carte Folium ──────────────────────────────────────────────

def create_map(canalisations: list, alertes: list = None, show_heatmap: bool = False):
    """Crée une carte Folium interactive avec les canalisations et alertes."""
    m = folium.Map(location=[36.75, 3.04], zoom_start=12,
                   tiles="CartoDB positron",
                   attr="© OpenStreetMap | AquaPredict AI")

    # Style de la carte
    risk_colors = {"Bon": "green", "Moyen": "blue", "Mauvais": "orange", "Critique": "red"}

    # Données pour heatmap
    heat_data = []

    for can in canalisations:
        lat = can.get("latitude")
        lon = can.get("longitude")
        if not lat or not lon:
            continue

        etat = can.get("etat", "Bon")
        color = risk_colors.get(etat, "blue")

        # Marqueur
        folium.CircleMarker(
            location=[lat, lon],
            radius=7,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(f"""
                <div style='font-family:Inter,sans-serif;width:200px'>
                    <h4 style='color:#1565C0;margin:0'>{can.get('code','?')}</h4>
                    <hr style='margin:4px 0'>
                    <b>Zone:</b> {can.get('zone','')}<br>
                    <b>Matériau:</b> {can.get('materiau','')}<br>
                    <b>Âge:</b> {can.get('age','')} ans<br>
                    <b>État:</b> <span style='color:{color}'>{etat}</span><br>
                    <b>Réparations:</b> {can.get('nb_reparations',0)}
                </div>
            """, max_width=220),
            tooltip=f"{can.get('code','?')} — {etat}",
        ).add_to(m)

        if etat in ("Mauvais", "Critique"):
            heat_data.append([lat, lon, 1.0 if etat == "Critique" else 0.5])

    # Heatmap
    if show_heatmap and heat_data:
        HeatMap(heat_data, radius=25, blur=20, max_zoom=13,
                gradient={"0.4": "blue", "0.65": "orange", "1": "red"}).add_to(m)

    # Légende
    legend_html = """
    <div style='position:fixed;bottom:30px;left:30px;background:white;padding:12px;
                border-radius:8px;border:1px solid #ddd;z-index:1000;font-family:Inter,sans-serif;font-size:12px'>
        <b style='color:#1565C0'>État des canalisations</b><br>
        <span style='color:green'>● Bon</span> &nbsp;
        <span style='color:blue'>● Moyen</span><br>
        <span style='color:orange'>● Mauvais</span> &nbsp;
        <span style='color:red'>● Critique</span>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m


def create_reservoirs_map(reservoirs: list):
    """Carte des réservoirs avec indicateur de niveau."""
    m = folium.Map(location=[36.75, 3.04], zoom_start=12, tiles="CartoDB positron",
                   attr="© OpenStreetMap | AquaPredict AI")
    for res in reservoirs:
        lat, lon = res.get("latitude"), res.get("longitude")
        if not lat or not lon:
            continue
        capacite = res.get("capacite", 1)
        niveau = res.get("niveau_actuel", 0)
        pct = round(niveau / capacite * 100, 1) if capacite > 0 else 0
        color = "green" if pct > 60 else ("orange" if pct > 30 else "red")
        folium.Marker(
            [lat, lon],
            icon=folium.Icon(color=color, icon="tint", prefix="fa"),
            popup=folium.Popup(f"""
                <div style='font-family:Inter,sans-serif;width:180px'>
                    <h4 style='color:#1565C0;margin:0'>{res.get('nom','?')}</h4>
                    <b>Capacité:</b> {capacite:,} m³<br>
                    <b>Niveau:</b> {niveau:,} m³ ({pct}%)<br>
                    <b>Zone:</b> {res.get('zone','')}
                </div>
            """, max_width=200),
        ).add_to(m)
    return m
