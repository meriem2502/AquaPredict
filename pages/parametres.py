"""
AquaPredict AI - Paramètres & Administration
Gestion des utilisateurs, sauvegarde, configuration
"""
import streamlit as st
import sqlite3
import shutil
import os
import json
from datetime import datetime
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_manager import (
    get_all_users, add_user, toggle_user_active, get_connection,
    DB_PATH
)
from utils.ui_helpers import section_header, divider, success_box, error_box, info_box


def render():
    section_header("Paramètres & Administration", "Gestion des utilisateurs, sauvegardes, configuration système", "⚙️")

    tab1, tab2, tab3, tab4 = st.tabs(["👥 Utilisateurs", "💾 Sauvegarde", "🔧 Configuration", "📋 Logs Système"])

    # ── Tab 1 : Utilisateurs ─────────────────────────────────
    with tab1:
        st.markdown("### 👥 Gestion des Utilisateurs")

        users = get_all_users()
        if users:
            for u in users:
                role_icon = {"Admin": "👑", "Ingénieur": "🔬", "Technicien": "🔧"}.get(u["role"], "👤")
                status_color = "#27AE60" if u["is_active"] else "#E74C3C"
                status_text = "Actif" if u["is_active"] else "Inactif"

                col1, col2, col3 = st.columns([4, 2, 1])
                with col1:
                    st.markdown(f"""
                    <div style="background:white;border-radius:10px;padding:0.8rem 1.2rem;
                                box-shadow:0 2px 6px rgba(0,0,0,0.06);
                                border-left:4px solid {status_color}">
                        <div style="font-weight:700">{role_icon} {u.get('full_name','N/A')} <code style="font-size:0.8rem">@{u['username']}</code></div>
                        <div style="color:#64748B;font-size:0.82rem">
                            🎭 {u['role']} &nbsp;|&nbsp; 📧 {u.get('email','N/A')} &nbsp;|&nbsp;
                            🕐 Dernière connexion: {str(u.get('last_login','Jamais'))[:16]}
                        </div>
                    </div>""", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;height:100%;padding-top:0.8rem">
                        <span style="background:{'#D4EDDA' if u['is_active'] else '#FDE8E8'};
                                     color:{status_color};border-radius:20px;padding:3px 12px;
                                     font-size:0.82rem;font-weight:600">● {status_text}</span>
                    </div>""", unsafe_allow_html=True)
                with col3:
                    # Ne pas désactiver l'admin principal
                    if u["username"] != "admin":
                        btn_label = "🔴 Désactiver" if u["is_active"] else "🟢 Activer"
                        if st.button(btn_label, key=f"toggle_{u['id']}", use_container_width=True):
                            toggle_user_active(u["id"], 0 if u["is_active"] else 1)
                            st.rerun()

        divider()

        # Ajouter un utilisateur
        st.markdown("### ➕ Ajouter un Utilisateur")
        with st.form("form_add_user"):
            c1, c2 = st.columns(2)
            with c1:
                username = st.text_input("Identifiant *")
                password = st.text_input("Mot de passe *", type="password")
                role = st.selectbox("Rôle *", ["Technicien", "Ingénieur", "Admin"])
            with c2:
                full_name = st.text_input("Nom complet")
                email = st.text_input("Email")

            if st.form_submit_button("✅ Créer l'utilisateur", type="primary", use_container_width=True):
                if not username or not password:
                    st.error("Identifiant et mot de passe obligatoires.")
                else:
                    try:
                        add_user({"username": username, "password": password,
                                  "role": role, "full_name": full_name, "email": email})
                        success_box(f"Utilisateur **{username}** créé avec succès !")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        error_box(f"L'identifiant **{username}** existe déjà.")

    # ── Tab 2 : Sauvegarde ───────────────────────────────────
    with tab2:
        st.markdown("### 💾 Sauvegarde de la Base de Données")

        if os.path.exists(DB_PATH):
            db_size = os.path.getsize(DB_PATH) / 1024
            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:1.2rem;box-shadow:0 2px 8px rgba(0,0,0,0.07);margin-bottom:1rem">
                <b>📂 Fichier DB :</b> <code>{DB_PATH}</code><br>
                <b>📦 Taille :</b> {db_size:.1f} Ko &nbsp;|&nbsp;
                <b>🕐 Modifié :</b> {datetime.fromtimestamp(os.path.getmtime(DB_PATH)).strftime('%d/%m/%Y %H:%M')}
            </div>""", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Télécharger la Base de Données", type="primary", use_container_width=True):
                    with open(DB_PATH, "rb") as f:
                        db_bytes = f.read()
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        "⬇️ Sauvegarder aquapredict.db",
                        db_bytes,
                        f"aquapredict_backup_{timestamp}.db",
                        "application/octet-stream",
                        use_container_width=True,
                    )
            with col2:
                backup_dir = os.path.join(os.path.dirname(DB_PATH), "backups")
                if st.button("🗂️ Créer Sauvegarde Locale", use_container_width=True):
                    os.makedirs(backup_dir, exist_ok=True)
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dest = os.path.join(backup_dir, f"backup_{ts}.db")
                    shutil.copy2(DB_PATH, dest)
                    success_box(f"Sauvegarde créée : `backup_{ts}.db`")

            # Lister les backups locaux
            if os.path.exists(backup_dir):
                backups = sorted(os.listdir(backup_dir), reverse=True)
                if backups:
                    st.markdown(f"**Sauvegardes locales disponibles : {len(backups)}**")
                    for bk in backups[:10]:
                        bk_path = os.path.join(backup_dir, bk)
                        bk_size = os.path.getsize(bk_path) / 1024
                        st.markdown(f"- `{bk}` — {bk_size:.1f} Ko")
        else:
            st.warning("Base de données non trouvée.")

    # ── Tab 3 : Configuration ────────────────────────────────
    with tab3:
        st.markdown("### 🔧 Configuration du Système")

        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "config.json")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        # Charger config existante ou défauts
        default_config = {
            "seuil_risque_eleve": 66,
            "seuil_risque_moyen": 33,
            "age_max_acceptable": 40,
            "pression_max_bar": 10.0,
            "alertes_auto": True,
            "nb_predictions_historique": 100,
            "intervalle_rafraichissement_min": 5,
            "nom_organisme": "Direction de l'Hydraulique",
            "ville": "Alger",
            "version": "1.0.0",
        }
        if os.path.exists(config_path):
            try:
                with open(config_path) as f:
                    config = json.load(f)
            except Exception:
                config = default_config
        else:
            config = default_config

        st.markdown("#### Seuils ML")
        c1, c2, c3 = st.columns(3)
        with c1:
            config["seuil_risque_eleve"] = st.slider("Seuil Risque Élevé (%)", 50, 90,
                                                       config.get("seuil_risque_eleve", 66))
        with c2:
            config["seuil_risque_moyen"] = st.slider("Seuil Risque Moyen (%)", 10, 50,
                                                       config.get("seuil_risque_moyen", 33))
        with c3:
            config["age_max_acceptable"] = st.slider("Âge max acceptable (ans)", 20, 60,
                                                       config.get("age_max_acceptable", 40))

        st.markdown("#### Paramètres Réseau")
        c4, c5 = st.columns(2)
        with c4:
            config["pression_max_bar"] = st.number_input("Pression max (bar)", 5.0, 20.0,
                                                           config.get("pression_max_bar", 10.0), 0.5)
            config["alertes_auto"] = st.checkbox("Alertes automatiques ML", config.get("alertes_auto", True))
        with c5:
            config["nom_organisme"] = st.text_input("Nom organisme", config.get("nom_organisme", ""))
            config["ville"] = st.text_input("Ville", config.get("ville", "Alger"))

        if st.button("💾 Sauvegarder la Configuration", type="primary", use_container_width=True):
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            success_box("Configuration sauvegardée avec succès !")

        with st.expander("🔍 Voir le JSON de configuration"):
            st.json(config)

    # ── Tab 4 : Logs ─────────────────────────────────────────
    with tab4:
        st.markdown("### 📋 Logs Système")
        try:
            conn = get_connection()
            import pandas as pd
            df_logs = pd.read_sql_query("""
                SELECT l.id, u.username, l.action, l.details, l.timestamp
                FROM logs_systeme l LEFT JOIN users u ON l.user_id = u.id
                ORDER BY l.timestamp DESC LIMIT 100
            """, conn)
            conn.close()

            if not df_logs.empty:
                df_logs.columns = ["ID", "Utilisateur", "Action", "Détails", "Horodatage"]
                st.dataframe(df_logs, use_container_width=True, hide_index=True)
                csv = df_logs.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Exporter les logs", csv, "logs_systeme.csv", "text/csv")
            else:
                info_box("Aucun log système enregistré.")
        except Exception as e:
            error_box(f"Erreur lecture logs : {e}")
