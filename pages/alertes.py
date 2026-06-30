"""
AquaPredict AI - Alertes
"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_manager import get_alertes, resolve_alerte, add_alerte, get_all_canalisations
from utils.ui_helpers import section_header, divider, success_box


def render():
    section_header("Système d'Alertes", "Surveillance et gestion des alertes en temps réel", "🚨")

    tab1, tab2, tab3 = st.tabs(["⚡ Alertes Actives", "✅ Alertes Résolues", "➕ Nouvelle Alerte"])

    with tab1:
        alertes = get_alertes(resolues=False)
        st.markdown(f"**{len(alertes)} alerte(s) active(s)**")

        if alertes:
            for a in alertes:
                p = a.get("priorite", "Basse")
                colors = {"Critique": ("#FDE8E8", "#E74C3C"), "Haute": ("#FFF3CD", "#F39C12"),
                          "Moyenne": ("#D1ECF1", "#0288D1"), "Basse": ("#D4EDDA", "#27AE60")}
                bg, border = colors.get(p, ("#F5F5F5", "#888"))
                icons = {"Critique": "🔴", "Haute": "🟠", "Moyenne": "🟡", "Basse": "🟢"}

                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"""
                    <div style="background:{bg};border-left:5px solid {border};border-radius:8px;
                                padding:0.8rem 1.2rem;margin:0.4rem 0">
                        <div style="font-weight:700;font-size:0.95rem">{icons.get(p,'⚪')} {a.get('type_alerte','')} — Priorité {p}</div>
                        <div style="color:#64748B;font-size:0.85rem">
                            📍 {a.get('zone','N/A')} ({a.get('canalisation_code','N/A')}) &nbsp;|&nbsp;
                            📅 {str(a.get('created_at',''))[:16]}
                        </div>
                        <div style="font-size:0.88rem;margin-top:0.3rem">{a.get('message','')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("✅ Résoudre", key=f"res_{a['id']}", type="secondary", use_container_width=True):
                        resolve_alerte(a["id"])
                        st.rerun()
        else:
            st.success("✅ Aucune alerte active — réseau nominal")

    with tab2:
        alertes_res = get_alertes(resolues=True)
        if alertes_res:
            df = pd.DataFrame(alertes_res)
            cols = ["type_alerte", "priorite", "zone", "message", "created_at", "resolved_at"]
            cols = [c for c in cols if c in df.columns]
            st.dataframe(df[cols], use_container_width=True, hide_index=True)
        else:
            st.info("Aucune alerte résolue.")

    with tab3:
        canalisations = get_all_canalisations()
        with st.form("form_alerte"):
            can_opts = {f"{c['code']} — {c['zone']}": c["id"] for c in canalisations}
            sel = st.selectbox("Canalisation", list(can_opts.keys()))
            type_alerte = st.selectbox("Type d'alerte", ["Pression anormale", "Débit anormal",
                                                          "Fuite détectée", "Maintenance requise", "Autre"])
            priorite = st.selectbox("Priorité", ["Basse", "Moyenne", "Haute", "Critique"])
            message = st.text_area("Message / Description")
            if st.form_submit_button("➕ Créer l'alerte", type="primary", use_container_width=True):
                add_alerte(can_opts[sel], type_alerte, priorite, message)
                success_box("Alerte créée avec succès !")
                st.rerun()
