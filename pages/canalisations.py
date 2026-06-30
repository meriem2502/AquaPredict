"""
AquaPredict AI - Gestion des Canalisations
CRUD complet avec recherche et filtrage
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.db_manager import (
    get_all_canalisations, add_canalisation, update_canalisation,
    delete_canalisation, get_canalisation_by_id
)
from utils.ui_helpers import section_header, divider, success_box, error_box


ZONES = ["Zone Nord", "Zone Sud", "Zone Est", "Zone Ouest", "Zone Centre", "Zone Industrielle"]
MATERIAUX = ["PVC", "Fonte", "Acier", "PEHD", "Amiante-Ciment", "Béton"]
ETATS = ["Bon", "Moyen", "Mauvais", "Critique"]


def render():   


      
    section_header("Gestion des Canalisations", "Ajouter, modifier, supprimer et consulter", "🔩")

    tab1, tab2, tab3 = st.tabs(["📋 Liste & Recherche", "➕ Ajouter", "✏️ Modifier / Supprimer"])

    # ── Tab 1 : Liste ────────────────────────────────────────
    with tab1:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search = st.text_input("🔍 Rechercher (code ou zone)", placeholder="Ex: CAN-0001 ou Zone Nord")
        with col2:
            filtre_zone = st.selectbox("Filtrer par Zone", ["Toutes"] + ZONES)
        with col3:
            filtre_etat = st.selectbox("Filtrer par État", ["Tous"] + ETATS)

        zone_filter = None if filtre_zone == "Toutes" else filtre_zone
        etat_filter = None if filtre_etat == "Tous" else filtre_etat
        canalisations = get_all_canalisations(zone=zone_filter, etat=etat_filter,
                                              search=search if search else None)

        st.markdown(f"**{len(canalisations)} canalisation(s) trouvée(s)**")

        if canalisations:
            df = pd.DataFrame(canalisations)
            display_cols = ["code", "zone", "materiau", "diametre", "longueur",
                            "date_installation", "age", "etat", "nb_reparations"]
            df_display = df[display_cols].copy()
            df_display.columns = ["Code", "Zone", "Matériau", "Diamètre (mm)",
                                   "Longueur (m)", "Date Install.", "Âge (ans)", "État", "Nb Rép."]

            def color_etat(val):
                colors = {"Bon": "background-color: #D4EDDA; color: #155724",
                          "Moyen": "background-color: #D1ECF1; color: #0C5460",
                          "Mauvais": "background-color: #FFF3CD; color: #856404",
                          "Critique": "background-color: #FDE8E8; color: #C0392B"}
                return colors.get(val, "")

            styled = df_display.style.applymap(color_etat, subset=["État"])
            st.dataframe(styled, use_container_width=True, hide_index=True)

            # Export CSV
            csv = df_display.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Exporter CSV", csv, "canalisations.csv", "text/csv")
        else:
            st.info("Aucune canalisation trouvée.")

    # ── Tab 2 : Ajouter ──────────────────────────────────────
    with tab2:
        st.markdown("### ➕ Ajouter une Canalisation")
        with st.form("form_add_can", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                code = st.text_input("Code *", placeholder="CAN-0051")
                zone = st.selectbox("Zone *", ZONES)
                materiau = st.selectbox("Matériau *", MATERIAUX)
                diametre = st.number_input("Diamètre (mm) *", min_value=50, max_value=1000, value=200, step=50)
                longueur = st.number_input("Longueur (m) *", min_value=1.0, max_value=5000.0, value=200.0)
            with c2:
                date_inst = st.date_input("Date d'installation *", value=date(2000, 1, 1))
                etat = st.selectbox("État", ETATS)
                pression = st.number_input("Pression nominale (bar)", 0.0, 20.0, 5.0, 0.5)
                debit = st.number_input("Débit nominal (m³/h)", 0.0, 1000.0, 100.0, 10.0)
                nb_rep = st.number_input("Nb réparations", 0, 100, 0)

            st.markdown("**Coordonnées GPS (optionnel)**")
            g1, g2 = st.columns(2)
            with g1:
                lat = st.number_input("Latitude", value=36.75, format="%.5f")
            with g2:
                lon = st.number_input("Longitude", value=3.04, format="%.5f")

            submitted = st.form_submit_button("✅ Ajouter la canalisation", type="primary",
                                               use_container_width=True)
            if submitted:
                if not code:
                    error_box("Le code est obligatoire.")
                else:
                    age = datetime.now().year - date_inst.year
                    add_canalisation({
                        "code": code, "zone": zone, "materiau": materiau,
                        "diametre": diametre, "longueur": longueur,
                        "date_installation": str(date_inst), "age": age, "etat": etat,
                        "pression_nominale": pression, "debit_nominal": debit,
                        "latitude": lat, "longitude": lon, "nb_reparations": nb_rep,
                    })
                    success_box(f"Canalisation **{code}** ajoutée avec succès !")
                    st.rerun()

    # ── Tab 3 : Modifier / Supprimer ─────────────────────────
    with tab3:
        canalisations_all = get_all_canalisations()
        canalisations = get_all_canalisations(
    zone=zone_filter,
    etat=etat_filter,
    search=search if search else None
)
        if not canalisations_all:
            st.info("Aucune canalisation disponible.")
            return

        options = {f"{c['code']} — {c['zone']}": c["id"] for c in canalisations_all}
        sel = st.selectbox("Sélectionner une canalisation", list(options.keys()))
        can_id = options[sel]
        can = get_canalisation_by_id(can_id)

        if not can:
            st.warning("Canalisation introuvable.")
            return

        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.markdown(f"#### Modifier : {can['code']}")
        with col_b:
            if st.button("🗑️ Supprimer", type="secondary", use_container_width=True):
                st.session_state["confirm_delete"] = can_id

        if st.session_state.get("confirm_delete") == can_id:
            st.warning(f"⚠️ Confirmer la suppression de **{can['code']}** ?")
            c_yes, c_no = st.columns(2)
            with c_yes:
                if st.button("✅ Confirmer suppression", type="primary"):
                    delete_canalisation(can_id)
                    del st.session_state["confirm_delete"]
                    success_box("Canalisation supprimée.")
                    st.rerun()
            with c_no:
                if st.button("❌ Annuler"):
                    del st.session_state["confirm_delete"]

        divider()

        with st.form("form_edit_can"):
            c1, c2 = st.columns(2)
            with c1:
                zone_edit = st.selectbox("Zone", ZONES, index=ZONES.index(can["zone"]) if can["zone"] in ZONES else 0)
                materiau_edit = st.selectbox("Matériau", MATERIAUX, index=MATERIAUX.index(can["materiau"]) if can["materiau"] in MATERIAUX else 0)
                diametre_edit = st.number_input("Diamètre (mm)", 50, 1000, int(can["diametre"] or 200), 50)
                longueur_edit = st.number_input("Longueur (m)", 1.0, 5000.0, float(can["longueur"] or 100.0))
                nb_rep_edit = st.number_input("Nb réparations", 0, 100, int(can["nb_reparations"] or 0))
            with c2:
                try:
                    d_val = date.fromisoformat(can["date_installation"])
                except Exception:
                    d_val = date(2000, 1, 1)
                date_edit = st.date_input("Date d'installation", value=d_val)
                etat_edit = st.selectbox("État", ETATS, index=ETATS.index(can["etat"]) if can["etat"] in ETATS else 0)
                pression_edit = st.number_input("Pression (bar)", 0.0, 20.0, float(can.get("pression_nominale") or 5.0), 0.5)
                debit_edit = st.number_input("Débit (m³/h)", 0.0, 1000.0, float(can.get("debit_nominal") or 100.0), 10.0)
                lat_edit = st.number_input("Latitude", value=float(can.get("latitude") or 36.75), format="%.5f")
                lon_edit = st.number_input("Longitude", value=float(can.get("longitude") or 3.04), format="%.5f")

            if st.form_submit_button("💾 Enregistrer les modifications", type="primary", use_container_width=True):
                age_edit = datetime.now().year - date_edit.year
                update_canalisation(can_id, {
                    "zone": zone_edit, "materiau": materiau_edit, "diametre": diametre_edit,
                    "longueur": longueur_edit, "date_installation": str(date_edit),
                    "age": age_edit, "etat": etat_edit, "pression_nominale": pression_edit,
                    "debit_nominal": debit_edit, "latitude": lat_edit, "longitude": lon_edit,
                    "nb_reparations": nb_rep_edit,
                })
                success_box(f"Canalisation **{can['code']}** mise à jour !")
                st.rerun()
