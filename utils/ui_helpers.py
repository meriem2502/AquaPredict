"""
AquaPredict AI - Helpers UI Streamlit
KPI Cards, styles, composants réutilisables
"""

import streamlit as st


# ── CSS Global ────────────────────────────────────────────────

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Reset & Base */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.main { background: #F0F4F8; }
.block-container { padding: 1.5rem 2rem 3rem 2rem !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D2B55 0%, #1565C0 60%, #0288D1 100%);
    border-right: none;
}
[data-testid="stSidebar"] * { color: #E8F4FD !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] p { color: #B3D4F0 !important; font-size: 0.82rem; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }

/* Headers */
h1 { color: #1565C0 !important; font-weight: 800 !important; }
h2 { color: #1565C0 !important; font-weight: 700 !important; }
h3 { color: #0D2B55 !important; font-weight: 600 !important; }

/* KPI Cards */
.kpi-card {
    background: white;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 2px 12px rgba(21,101,192,0.1);
    border-left: 5px solid;
    transition: transform 0.2s, box-shadow 0.2s;
    margin-bottom: 0.5rem;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(21,101,192,0.18); }
.kpi-value { font-size: 2.2rem; font-weight: 800; line-height: 1.1; margin: 0.2rem 0; }
.kpi-label { font-size: 0.82rem; font-weight: 500; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-delta { font-size: 0.78rem; font-weight: 500; margin-top: 0.3rem; }

/* Alert badges */
.badge-critique { background:#FDE8E8; color:#C0392B; border:1px solid #F5C6C6; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-haute { background:#FEF3CD; color:#856404; border:1px solid #FCEBBF; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-moyenne { background:#D1ECF1; color:#0C5460; border:1px solid #BEE5EB; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-basse { background:#D4EDDA; color:#155724; border:1px solid #C3E6CB; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }

/* Risk level */
.risk-eleve { color: #E74C3C; font-weight: 700; }
.risk-moyen { color: #F39C12; font-weight: 700; }
.risk-faible { color: #27AE60; font-weight: 700; }

/* Cards */
.section-card {
    background: white;
    border-radius: 14px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(21,101,192,0.08);
    margin-bottom: 1rem;
}

/* Divider */
.aqua-divider {
    height: 3px;
    background: linear-gradient(90deg, #1565C0, #00BCD4, transparent);
    border: none;
    border-radius: 2px;
    margin: 1rem 0;
}

/* Page title */
.page-title {
    display: flex; align-items: center; gap: 0.6rem;
    padding-bottom: 0.5rem;
    border-bottom: 3px solid #E3F2FD;
    margin-bottom: 1.5rem;
}

/* Prediction result */
.pred-box {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    margin: 1rem 0;
}
.pred-risk-value { font-size: 3rem; font-weight: 800; }
.pred-score { font-size: 1.4rem; color: #64748B; }

/* Buttons override */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}

/* DataFrames */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

/* Info/Warning/Error boxes */
.stAlert { border-radius: 10px !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0 !important;
    font-weight: 500 !important;
}
</style>
"""


def inject_css():
    """Injecte le CSS global dans l'application."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def kpi_card(label: str, value, icon: str = "📊", color: str = "#1565C0",
             delta: str = "", unit: str = ""):
    """Affiche une KPI card stylisée."""
    delta_html = f'<div class="kpi-delta" style="color:{color}">{delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color:{color}">
        <div class="kpi-label">{icon} {label}</div>
        <div class="kpi-value" style="color:{color}">{value}<span style="font-size:1rem;font-weight:500"> {unit}</span></div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, subtitle: str = "", icon: str = ""):
    """Titre de section avec style cohérent."""
    st.markdown(f"""
    <div class="page-title">
        <span style="font-size:1.8rem">{icon}</span>
        <div>
            <h2 style="margin:0;color:#1565C0">{title}</h2>
            {f'<p style="color:#64748B;margin:0;font-size:0.9rem">{subtitle}</p>' if subtitle else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)


def risk_badge(niveau: str):
    """Retourne le HTML d'un badge de risque."""
    colors = {
        "Élevé": ("🔴", "#FDE8E8", "#C0392B"),
        "Moyen": ("🟡", "#FEF3CD", "#856404"),
        "Faible": ("🟢", "#D4EDDA", "#155724"),
    }
    icon, bg, txt = colors.get(niveau, ("⚪", "#F5F5F5", "#333"))
    return f'<span style="background:{bg};color:{txt};border-radius:20px;padding:3px 12px;font-size:0.82rem;font-weight:600">{icon} {niveau}</span>'


def priority_badge(priorite: str):
    """Badge de priorité HTML."""
    cls_map = {"Critique": "badge-critique", "Haute": "badge-haute",
               "Moyenne": "badge-moyenne", "Basse": "badge-basse"}
    return f'<span class="{cls_map.get(priorite, "badge-basse")}">{priorite}</span>'


def sidebar_logo():
    """Affiche le logo/titre dans la sidebar."""
    st.sidebar.markdown("""
    <div style="text-align:center; padding: 1.5rem 0 1rem 0;">
        <div style="font-size:3rem; margin-bottom:0.3rem;">💧</div>
        <div style="font-size:1.4rem; font-weight:800; color:white; letter-spacing:0.02em">AquaPredict AI</div>
        <div style="font-size:0.75rem; color:#90CAF9; margin-top:0.2rem">Gestion Intelligente des Réseaux</div>
        <hr style="border:1px solid rgba(255,255,255,0.2); margin:1rem 0 0 0">
    </div>
    """, unsafe_allow_html=True)


def user_info_sidebar(user: dict):
    """Affiche les informations utilisateur dans la sidebar."""
    role_icons = {"Admin": "👑", "Ingénieur": "🔬", "Technicien": "🔧"}
    icon = role_icons.get(user.get("role", ""), "👤")
    st.sidebar.markdown(f"""
    <div style="background:rgba(255,255,255,0.12); border-radius:10px; padding:0.8rem; margin:0.5rem 0; text-align:center">
        <div style="font-size:1.6rem">{icon}</div>
        <div style="font-weight:700; font-size:0.95rem; color:white">{user.get('full_name', user.get('username',''))}</div>
        <div style="font-size:0.75rem; color:#B3D4F0; background:rgba(255,255,255,0.15); border-radius:12px; padding:2px 10px; display:inline-block; margin-top:4px">{user.get('role','')}</div>
    </div>
    """, unsafe_allow_html=True)


def show_login_form():
    """Affiche le formulaire de connexion centré."""
    st.markdown("""
    <div style="text-align:center; padding: 2rem 0 1rem 0;">
        <div style="font-size:4rem">💧</div>
        <h1 style="color:#1565C0; font-size:2.5rem; font-weight:800; margin:0">AquaPredict AI</h1>
        <p style="color:#64748B; font-size:1.1rem; margin:0.5rem 0 0 0">
            Système Intelligent de Prédiction des Fuites d'Eau
        </p>
        <p style="color:#94A3B8; font-size:0.85rem;">Master 2 Intelligence Artificielle</p>
    </div>
    """, unsafe_allow_html=True)


def success_box(msg: str):
    st.markdown(f"""
    <div style="background:#D4EDDA;border:1px solid #C3E6CB;border-radius:10px;padding:0.8rem 1.2rem;color:#155724;font-weight:500;margin:0.5rem 0">
    ✅ {msg}
    </div>""", unsafe_allow_html=True)


def error_box(msg: str):
    st.markdown(f"""
    <div style="background:#FDE8E8;border:1px solid #F5C6C6;border-radius:10px;padding:0.8rem 1.2rem;color:#C0392B;font-weight:500;margin:0.5rem 0">
    ❌ {msg}
    </div>""", unsafe_allow_html=True)


def info_box(msg: str):
    st.markdown(f"""
    <div style="background:#E3F2FD;border:1px solid #BBDEFB;border-radius:10px;padding:0.8rem 1.2rem;color:#1565C0;font-weight:500;margin:0.5rem 0">
    ℹ️ {msg}
    </div>""", unsafe_allow_html=True)


def divider():
    st.markdown('<hr class="aqua-divider">', unsafe_allow_html=True)
