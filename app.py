"""
╔══════════════════════════════════════════════════════════════════╗
║           AquaPredict AI — Application Principale               ║
║   Système Intelligent de Prédiction des Fuites dans les         ║
║   Réseaux de Distribution d'Eau                                 ║
║                                                                  ║
║   Technologies : Streamlit · SQLite · Scikit-Learn · Plotly     ║
║   Architecture : MVC multi-pages avec sidebar de navigation     ║
║   Auteur       : Master 2 Intelligence Artificielle             ║
║   Version      : 1.0.0                                          ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import sys
import os

# ── Résolution des chemins ────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

# ── Configuration Streamlit (DOIT être le 1er appel st.*) ────
st.set_page_config(
    page_title="AquaPredict AI",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "mailto:contact@aquapredict.dz",
        "Report a bug": "mailto:support@aquapredict.dz",
        "About": "**AquaPredict AI** v1.0 — Système Intelligent de Prédiction des Fuites\n\nMaster 2 Intelligence Artificielle",
    },
)

# ── Imports internes ──────────────────────────────────────────
from database.db_manager import init_database, verify_password
from utils.ui_helpers import inject_css, sidebar_logo, user_info_sidebar, show_login_form

# ── Initialisation base de données au démarrage ───────────────
@st.cache_resource(show_spinner="Initialisation de la base de données…")
def startup():
    """Initialise la BD une seule fois par session serveur."""
    init_database()
    return True

startup()


# ══════════════════════════════════════════════════════════════
#  AUTHENTIFICATION
# ══════════════════════════════════════════════════════════════

def render_login():
    """Page de connexion centrée et stylisée."""
    inject_css()
    show_login_form()

    # Carte de formulaire centrée
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("""
        <div style="background:white;border-radius:18px;padding:2rem 2.4rem;
                    box-shadow:0 8px 40px rgba(21,101,192,0.15);
                    border:1px solid #E3F2FD;margin-top:0.5rem">
            <h3 style="color:#1565C0;text-align:center;margin-bottom:1.5rem">🔐 Connexion</h3>
        </div>
        """, unsafe_allow_html=True)

        username = st.text_input("👤 Identifiant", placeholder="admin / ingenieur1 / tech1",
                                  key="login_user")
        password = st.text_input("🔑 Mot de passe", type="password",
                                  placeholder="Votre mot de passe", key="login_pass")

        if st.button("🚀 Se Connecter", type="primary", use_container_width=True):
            if not username or not password:
                st.error("Veuillez remplir tous les champs.")
            else:
                user = verify_password(username.strip(), password)
                if user:
                    st.session_state["user"] = user
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects ou compte désactivé.")

       
       
       
       
       
        st.markdown("""
        <div style="margin-top:1.2rem;padding:0.9rem;background:#F0F7FF;border-radius:10px;
                    font-size:0.82rem;color:#1565C0;text-align:center">
            <b>Comptes de démo :</b><br>
            👑 admin / admin123 &nbsp;|&nbsp;
            🔬 ingenieur1 / ing123 &nbsp;|&nbsp;
            🔧 tech1 / tech123
        </div>
        """, unsafe_allow_html=True)










# ══════════════════════════════════════════════════════════════
#  NAVIGATION SIDEBAR
# ══════════════════════════════════════════════════════════════

# Structure de navigation : (label, icon, module_path, rôles autorisés)
NAV_ITEMS = [
    # ── Tableau de bord ───────────────────────────────────────
    ("Dashboard",               "📊", "pages.dashboard",       ["Admin", "Ingénieur", "Technicien"]),
    # ── Gestion réseau ────────────────────────────────────────
    ("Canalisations",           "🔩", "pages.canalisations",   ["Admin", "Ingénieur", "Technicien"]),
    ("Réservoirs",              "🏗️", "pages.reservoirs",      ["Admin", "Ingénieur", "Technicien"]),
    # ── Machine Learning ──────────────────────────────────────
    ("ML — Entraînement",       "🤖", "pages.ml_training",     ["Admin", "Ingénieur"]),
    ("ML — Prédiction",         "🔮", "pages.prediction",      ["Admin", "Ingénieur", "Technicien"]),
    # ── Surveillance ─────────────────────────────────────────
    ("Alertes",                 "🚨", "pages.alertes",         ["Admin", "Ingénieur", "Technicien"]),
    ("Interventions",           "🔧", "pages.interventions",   ["Admin", "Ingénieur", "Technicien"]),
    # ── Carte & Analyses ─────────────────────────────────────
    ("Carte GIS",               "🗺️", "pages.carte",           ["Admin", "Ingénieur", "Technicien"]),
    ("Statistiques",            "📈", "pages.statistiques",    ["Admin", "Ingénieur"]),
    # ── Données & Rapports ────────────────────────────────────
    ("Gestion des Données",     "📂", "pages.data_management", ["Admin", "Ingénieur"]),
    ("Rapports",                "📄", "pages.rapports",        ["Admin", "Ingénieur"]),
    # ── Administration ────────────────────────────────────────
    ("Paramètres",              "⚙️", "pages.parametres",      ["Admin"]),
]

# Groupes pour affichage sidebar
NAV_GROUPS = {
    "📊 Tableau de Bord":   ["Dashboard"],
    "🔩 Réseau":            ["Canalisations", "Réservoirs"],
    "🤖 Machine Learning":  ["ML — Entraînement", "ML — Prédiction"],
    "🚨 Surveillance":      ["Alertes", "Interventions"],
    "🗺️ Analyse":           ["Carte GIS", "Statistiques"],
    "📂 Données":           ["Gestion des Données", "Rapports"],
    "⚙️ Admin":             ["Paramètres"],
}


def render_sidebar(user: dict) -> str:
    """Affiche la sidebar et retourne la page sélectionnée."""
    with st.sidebar:
        sidebar_logo()
        user_info_sidebar(user)
        st.sidebar.markdown("")

        user_role = user.get("role", "Technicien")
        page_label_map = {item[0]: item for item in NAV_ITEMS}

        # Si pas de page sélectionnée, défaut = Dashboard
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = "Dashboard"

        # Affichage groupé
        for group_title, items_in_group in NAV_GROUPS.items():
            visible_items = []
            for label in items_in_group:
                if label in page_label_map:
                    nav = page_label_map[label]
                    if user_role in nav[3]:           # contrôle d'accès par rôle
                        visible_items.append(nav)

            if not visible_items:
                continue

            st.markdown(f"""
            <div style="padding:0.25rem 0.6rem;margin:0.6rem 0 0.15rem 0;
                        font-size:0.7rem;font-weight:700;letter-spacing:0.09em;
                        color:rgba(255,255,255,0.45);text-transform:uppercase">
                {group_title}
            </div>""", unsafe_allow_html=True)

            for label, icon, _, _ in visible_items:
                is_active = (st.session_state["current_page"] == label)
                btn_style = """
                    background:rgba(255,255,255,0.18);border-radius:8px;
                    font-weight:700;border:1px solid rgba(255,255,255,0.25);
                """ if is_active else ""
                if st.sidebar.button(
                    f"{icon}  {label}",
                    key=f"nav_{label}",
                    use_container_width=True,
                    help=f"Aller à {label}",
                ):
                    st.session_state["current_page"] = label
                    st.rerun()

        # Pied de sidebar — déconnexion
        st.sidebar.markdown("""<div style="flex:1"></div>""", unsafe_allow_html=True)
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"""
        <div style="font-size:0.72rem;color:rgba(255,255,255,0.4);text-align:center;padding-bottom:0.3rem">
            AquaPredict AI v1.0<br>Master 2 IA · 2025
        </div>""", unsafe_allow_html=True)
        if st.sidebar.button("🚪  Se Déconnecter", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    return st.session_state.get("current_page", "Dashboard")


# ══════════════════════════════════════════════════════════════
#  CHARGEMENT DES PAGES
# ══════════════════════════════════════════════════════════════

def load_page(module_path: str, user: dict):
    """
    Importe dynamiquement le module de page et appelle render().
    Gère les erreurs d'import proprement.
    """
    try:
        import importlib
        module = importlib.import_module(module_path)
        # Recharger pour refléter les changements en dev
        importlib.reload(module)
        module.render()
    except ModuleNotFoundError as e:
        st.warning(f"⚠️ Module **{module_path}** introuvable. ({e})")
        st.info("Vérifiez que tous les fichiers `pages/` sont présents.")
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement de la page :")
        st.exception(e)


# ══════════════════════════════════════════════════════════════
#  POINT D'ENTRÉE PRINCIPAL
# ══════════════════════════════════════════════════════════════

def main():
    inject_css()

    # ── Vérification authentification ────────────────────────
    if not st.session_state.get("authenticated", False):
        render_login()
        return

    user = st.session_state.get("user", {})
    user_role = user.get("role", "Technicien")

    # ── Sidebar + sélection de page ──────────────────────────
    current_page = render_sidebar(user)

    # ── Contrôle d'accès ─────────────────────────────────────
    page_label_map = {item[0]: item for item in NAV_ITEMS}
    nav_item = page_label_map.get(current_page)

    if not nav_item:
        st.error("Page inconnue.")
        return

    _, _, module_path, allowed_roles = nav_item

    if user_role not in allowed_roles:
        st.markdown("""
        <div style="text-align:center;padding:4rem 0">
            <div style="font-size:4rem">🔒</div>
            <h2 style="color:#E74C3C">Accès Refusé</h2>
            <p style="color:#64748B">Vous n'avez pas les permissions nécessaires pour accéder à cette page.</p>
        </div>""", unsafe_allow_html=True)
        return

    # ── Rendu de la page ─────────────────────────────────────
    load_page(module_path, user)


# ── Lancement ────────────────────────────────────────────────
if __name__ == "__main__":
    main()
