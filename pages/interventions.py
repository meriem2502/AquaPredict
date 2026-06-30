"""
AquaPredict AI - Gestion des Interventions
"""
import streamlit as st
import pandas as pd
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_manager import get_all_interventions, add_intervention, update_intervention_statut, get_all_canalisations, get_technicians
from utils.ui_helpers import section_header, divider, success_box


def render():
    section_header("Gestion des Interventions", "Planification et suivi des réparations", "🔧")

    tab1, tab2 = st.tabs(["📋 Liste des Interventions", "➕ Nouvelle Intervention"])

    with tab1:
        interventions = get_all_interventions()
        if interventions:
            # Résumé statuts
            df = pd.DataFrame(interventions)
            c1, c2, c3, c4 = st.columns(4)
            for col, statut, color in zip([c1, c2, c3, c4],
                                           ["Planifié", "En cours", "Terminé", "Annulé"],
                                           ["#1565C0", "#F39C12", "#27AE60", "#E74C3C"]):
                count = len(df[df["statut"] == statut]) if "statut" in df.columns else 0
                with col:
                    st.markdown(f"""
                    <div style="background:white;border-radius:10px;padding:0.8rem;text-align:center;
                                border-top:4px solid {color};box-shadow:0 2px 8px rgba(0,0,0,0.07)">
                        <div style="font-size:1.8rem;font-weight:800;color:{color}">{count}</div>
                        <div style="font-size:0.82rem;color:#64748B">{statut}</div>
                    </div>""", unsafe_allow_html=True)

            divider()

            for inter in interventions:
                statut = inter.get("statut", "Planifié")
                s_colors = {"Planifié": "#3498DB", "En cours": "#F39C12", "Terminé": "#27AE60", "Annulé": "#E74C3C"}
                color = s_colors.get(statut, "#888")

                col1, col2, col3 = st.columns([4, 2, 1])
                with col1:
                    st.markdown(f"""
                    <div style="background:white;border-radius:10px;padding:0.8rem 1.2rem;
                                border-left:5px solid {color};box-shadow:0 2px 6px rgba(0,0,0,0.06)">
                        <div style="font-weight:700">{inter.get('canalisation_code','N/A')} — {inter.get('zone','')}</div>
                        <div style="color:#64748B;font-size:0.85rem">
                            👷 {inter.get('technicien_nom','Non assigné')} &nbsp;|&nbsp;
                            📅 {inter.get('date_planifiee','N/A')} &nbsp;|&nbsp;
                            ⚡ {inter.get('priorite','')}
                        </div>
                        <div style="font-size:0.88rem;margin-top:0.2rem">{inter.get('description','')}</div>
                    </div>""", unsafe_allow_html=True)
                with col2:
                    new_statut = st.selectbox("Statut", ["Planifié", "En cours", "Terminé", "Annulé"],
                                               index=["Planifié", "En cours", "Terminé", "Annulé"].index(statut),
                                               key=f"st_{inter['id']}", label_visibility="collapsed")
                with col3:
                    if st.button("💾", key=f"save_{inter['id']}", use_container_width=True):
                        update_intervention_statut(inter["id"], new_statut)
                        st.rerun()
        else:
            st.info("Aucune intervention planifiée.")

    with tab2:
        canalisations = get_all_canalisations()
        techs = get_technicians()

        with st.form("form_intervention"):
            c1, c2 = st.columns(2)
            with c1:
                can_opts = {f"{c['code']} — {c['zone']}": c["id"] for c in canalisations}
                sel_can = st.selectbox("Canalisation *", list(can_opts.keys()))
                tech_opts = {f"{t['full_name']} ({t['username']})": t["id"] for t in techs}
                tech_opts["Non assigné"] = None
                sel_tech = st.selectbox("Technicien", list(tech_opts.keys()))
                priorite = st.selectbox("Priorité", ["Basse", "Moyenne", "Haute", "Critique"])
            with c2:
                date_plan = st.date_input("Date planifiée", value=date.today())
                statut = st.selectbox("Statut initial", ["Planifié", "En cours"])
                description = st.text_area("Description de l'intervention *")
                notes = st.text_area("Notes")

            if st.form_submit_button("🔧 Planifier l'intervention", type="primary", use_container_width=True):
                if not description:
                    st.error("La description est obligatoire.")
                else:
                    add_intervention({
                        "canalisation_id": can_opts[sel_can],
                        "technicien_id": tech_opts[sel_tech],
                        "description": description,
                        "statut": statut,
                        "priorite": priorite,
                        "date_planifiee": str(date_plan),
                        "notes": notes,
                    })
                    success_box("Intervention planifiée avec succès !")
                    st.rerun()
