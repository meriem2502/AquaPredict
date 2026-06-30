"""
AquaPredict AI - Gestion des Données
Import CSV/Excel, nettoyage, aperçu
"""
import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_manager import get_connection
from utils.ui_helpers import section_header, divider, success_box, error_box, info_box


# Colonnes requises par type de fichier
SCHEMAS = {
    "canalisations": {
        "required": ["code", "zone", "materiau", "diametre", "longueur", "date_installation"],
        "optional": ["age", "etat", "pression_nominale", "debit_nominal",
                     "latitude", "longitude", "nb_reparations"],
        "table": "canalisations",
        "description": "Données des canalisations du réseau",
    },
    "reservoirs": {
        "required": ["code", "nom", "zone", "capacite"],
        "optional": ["niveau_actuel", "latitude", "longitude", "date_construction", "etat"],
        "table": "reservoirs",
        "description": "Données des réservoirs",
    },
    "mesures": {
        "required": ["canalisation_id", "pression", "debit"],
        "optional": ["temperature", "timestamp"],
        "table": "mesures",
        "description": "Mesures capteurs (pression, débit, température)",
    },
    "fuites": {
        "required": ["canalisation_id", "date_detection"],
        "optional": ["debit_perdu", "type_fuite", "cause", "est_reparee"],
        "table": "fuites",
        "description": "Historique des fuites détectées",
    },
}


def _validate_dataframe(df: pd.DataFrame, schema: dict) -> tuple[bool, list]:
    """Valide un DataFrame contre un schéma. Retourne (valide, erreurs)."""
    errors = []
    missing = [c for c in schema["required"] if c not in df.columns]
    if missing:
        errors.append(f"Colonnes obligatoires manquantes : {', '.join(missing)}")

    if df.empty:
        errors.append("Le fichier est vide.")

    if df.duplicated().sum() > 0:
        errors.append(f"⚠️ {df.duplicated().sum()} ligne(s) dupliquée(s) détectée(s).")

    return len([e for e in errors if not e.startswith("⚠️")]) == 0, errors


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoyage de base : strip strings, NaN handling."""
    # Trim strings
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda c: c.str.strip())

    # Supprimer lignes entièrement vides
    df = df.dropna(how="all")

    # Remplir NaN numériques par 0
    num_cols = df.select_dtypes(include=np.number).columns
    df[num_cols] = df[num_cols].fillna(0)

    return df.reset_index(drop=True)


def _insert_dataframe(df: pd.DataFrame, table: str) -> tuple[int, int]:
    """Insère un DataFrame dans la table SQLite. Retourne (insérés, erreurs)."""
    conn = get_connection()
    inserted, errors = 0, 0
    for _, row in df.iterrows():
        try:
            cols = ", ".join(row.index.tolist())
            placeholders = ", ".join(["?" for _ in row])
            conn.execute(f"INSERT OR IGNORE INTO {table} ({cols}) VALUES ({placeholders})",
                         tuple(row.values))
            inserted += 1
        except Exception:
            errors += 1
    conn.commit()
    conn.close()
    return inserted, errors


def render():
    section_header("Gestion des Données", "Import CSV/Excel, nettoyage et validation", "📂")

    tab1, tab2, tab3 = st.tabs(["⬆️ Import de Données", "🔍 Aperçu Base de Données", "🧹 Nettoyage"])

    # ── Tab 1 : Import ───────────────────────────────────────
    with tab1:
        st.markdown("### Importer des Données")

        col1, col2 = st.columns(2)
        with col1:
            data_type = st.selectbox(
                "Type de données",
                list(SCHEMAS.keys()),
                format_func=lambda k: f"{k.capitalize()} — {SCHEMAS[k]['description']}",
            )
        with col2:
            file_format = st.selectbox("Format du fichier", ["CSV (séparateur virgule)",
                                                              "CSV (séparateur point-virgule)",
                                                              "Excel (.xlsx)"])

        schema = SCHEMAS[data_type]
        st.markdown(f"""
        <div style="background:#E3F2FD;border-radius:10px;padding:0.8rem 1.2rem;color:#1565C0;font-size:0.88rem;margin:0.5rem 0">
            📋 <b>Colonnes obligatoires :</b> {', '.join(f'<code>{c}</code>' for c in schema['required'])}<br>
            ➕ <b>Colonnes optionnelles :</b> {', '.join(f'<code>{c}</code>' for c in schema['optional'])}
        </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader(
            f"Sélectionner le fichier {data_type}",
            type=["csv", "xlsx", "xls"],
            help="Glisser-déposer ou cliquer pour sélectionner",
        )

        if uploaded:
            with st.spinner("Lecture du fichier..."):
                try:
                    if "Excel" in file_format:
                        df = pd.read_excel(uploaded)
                    elif "point-virgule" in file_format:
                        df = pd.read_csv(uploaded, sep=";", encoding="utf-8-sig")
                    else:
                        df = pd.read_csv(uploaded, encoding="utf-8-sig")
                except Exception as e:
                    error_box(f"Erreur de lecture : {e}")
                    return

            st.markdown(f"**Aperçu du fichier — {len(df)} lignes × {len(df.columns)} colonnes**")
            st.dataframe(df.head(10), use_container_width=True, hide_index=True)

            # Validation
            is_valid, errs = _validate_dataframe(df, schema)

            if errs:
                for err in errs:
                    if err.startswith("⚠️"):
                        st.warning(err)
                    else:
                        st.error(err)

            if is_valid:
                st.success("✅ Validation réussie — fichier conforme au schéma.")

                col_a, col_b = st.columns(2)
                with col_a:
                    auto_clean = st.checkbox("Nettoyage automatique avant import", value=True)
                with col_b:
                    st.metric("Lignes à importer", len(df))

                if st.button("⬆️ Importer dans la Base de Données", type="primary", use_container_width=True):
                    if auto_clean:
                        df = _clean_dataframe(df)

                    # Filtrer colonnes existantes dans la table
                    all_cols = schema["required"] + schema["optional"]
                    valid_cols = [c for c in all_cols if c in df.columns]
                    df_import = df[valid_cols].copy()

                    inserted, errors = _insert_dataframe(df_import, schema["table"])
                    if inserted > 0:
                        success_box(f"✅ **{inserted}** enregistrement(s) importé(s) avec succès !")
                    if errors > 0:
                        st.warning(f"⚠️ {errors} ligne(s) ignorée(s) (doublons ou erreurs).")
            else:
                st.error("❌ Correction requise avant l'import.")

        divider()

        # Templates à télécharger
        st.markdown("#### 📥 Télécharger des Templates CSV")
        tcol1, tcol2, tcol3, tcol4 = st.columns(4)

        templates = {
            "canalisations": pd.DataFrame([{
                "code": "CAN-0001", "zone": "Zone Nord", "materiau": "PVC",
                "diametre": 200, "longueur": 500.0, "date_installation": "2005-06-15",
                "age": 19, "etat": "Bon", "pression_nominale": 5.0,
                "debit_nominal": 120.0, "latitude": 36.75, "longitude": 3.04, "nb_reparations": 2,
            }]),
            "reservoirs": pd.DataFrame([{
                "code": "RES-001", "nom": "Réservoir Nord", "zone": "Zone Nord",
                "capacite": 5000, "niveau_actuel": 3800, "latitude": 36.78, "longitude": 3.02,
                "date_construction": "1990-01-01", "etat": "Opérationnel",
            }]),
            "mesures": pd.DataFrame([{
                "canalisation_id": 1, "pression": 5.2, "debit": 120.5,
                "temperature": 18.3, "timestamp": "2025-01-15 08:30:00",
            }]),
            "fuites": pd.DataFrame([{
                "canalisation_id": 1, "date_detection": "2024-03-10",
                "debit_perdu": 12.5, "type_fuite": "Micro-fissure",
                "cause": "Corrosion", "est_reparee": 0,
            }]),
        }

        for col, (name, df_tmpl) in zip([tcol1, tcol2, tcol3, tcol4], templates.items()):
            with col:
                csv = df_tmpl.to_csv(index=False).encode("utf-8")
                st.download_button(
                    f"📄 {name.capitalize()}",
                    csv, f"template_{name}.csv", "text/csv",
                    use_container_width=True,
                )

    # ── Tab 2 : Aperçu BD ────────────────────────────────────
    with tab2:
        st.markdown("### Aperçu de la Base de Données")

        table_choice = st.selectbox("Table", ["canalisations", "reservoirs", "mesures",
                                               "fuites", "alertes", "predictions",
                                               "interventions", "users", "logs_systeme"])
        limit = st.slider("Nombre de lignes", 10, 500, 50)

        try:
            conn = get_connection()
            df_view = pd.read_sql_query(f"SELECT * FROM {table_choice} LIMIT {limit}", conn)
            conn.close()

            st.markdown(f"**{len(df_view)} lignes affichées** — Table `{table_choice}`")
            st.dataframe(df_view, use_container_width=True, hide_index=True)

            csv = df_view.to_csv(index=False).encode("utf-8")
            st.download_button(f"📥 Exporter {table_choice}.csv", csv,
                               f"{table_choice}_export.csv", "text/csv")

            # Stats rapides
            if not df_view.empty:
                with st.expander("📊 Statistiques descriptives"):
                    st.dataframe(df_view.describe(include="all").round(2), use_container_width=True)

        except Exception as e:
            error_box(f"Erreur d'accès à la table : {e}")

    # ── Tab 3 : Nettoyage ────────────────────────────────────
    with tab3:
        st.markdown("### Outils de Nettoyage")

        uploaded_clean = st.file_uploader("Charger un fichier à nettoyer", type=["csv", "xlsx"],
                                           key="clean_upload")
        if uploaded_clean:
            if uploaded_clean.name.endswith(".xlsx"):
                df_c = pd.read_excel(uploaded_clean)
            else:
                df_c = pd.read_csv(uploaded_clean, encoding="utf-8-sig")

            st.markdown(f"**Fichier original : {len(df_c)} lignes × {len(df_c.columns)} colonnes**")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Valeurs manquantes", df_c.isnull().sum().sum())
            with col2:
                st.metric("Doublons", df_c.duplicated().sum())
            with col3:
                st.metric("Colonnes", len(df_c.columns))

            st.dataframe(df_c.head(5), use_container_width=True, hide_index=True)

            options = st.multiselect("Opérations de nettoyage", [
                "Supprimer doublons",
                "Supprimer lignes vides",
                "Remplir NaN numériques par 0",
                "Remplir NaN texte par 'N/A'",
                "Trimmer les espaces (texte)",
                "Convertir colonnes numériques",
            ], default=["Supprimer doublons", "Supprimer lignes vides", "Trimmer les espaces (texte)"])

            if st.button("🧹 Appliquer le Nettoyage", type="primary", use_container_width=True):
                df_clean = df_c.copy()
                log = []

                if "Supprimer doublons" in options:
                    before = len(df_clean)
                    df_clean = df_clean.drop_duplicates()
                    log.append(f"✅ Doublons supprimés : {before - len(df_clean)}")

                if "Supprimer lignes vides" in options:
                    before = len(df_clean)
                    df_clean = df_clean.dropna(how="all")
                    log.append(f"✅ Lignes vides supprimées : {before - len(df_clean)}")

                if "Remplir NaN numériques par 0" in options:
                    num_cols = df_clean.select_dtypes(include=np.number).columns
                    n_filled = df_clean[num_cols].isnull().sum().sum()
                    df_clean[num_cols] = df_clean[num_cols].fillna(0)
                    log.append(f"✅ NaN numériques remplacés par 0 : {n_filled}")

                if "Remplir NaN texte par 'N/A'" in options:
                    obj_cols = df_clean.select_dtypes(include="object").columns
                    n_filled = df_clean[obj_cols].isnull().sum().sum()
                    df_clean[obj_cols] = df_clean[obj_cols].fillna("N/A")
                    log.append(f"✅ NaN texte remplacés par 'N/A' : {n_filled}")

                if "Trimmer les espaces (texte)" in options:
                    obj_cols = df_clean.select_dtypes(include="object").columns
                    df_clean[obj_cols] = df_clean[obj_cols].apply(lambda c: c.str.strip())
                    log.append("✅ Espaces superflus supprimés")

                if "Convertir colonnes numériques" in options:
                    for col in df_clean.columns:
                        try:
                            df_clean[col] = pd.to_numeric(df_clean[col], errors="ignore")
                        except Exception:
                            pass
                    log.append("✅ Conversion numérique appliquée")

                st.markdown("**Rapport de nettoyage :**")
                for entry in log:
                    st.markdown(f"- {entry}")

                st.markdown(f"**Résultat : {len(df_clean)} lignes × {len(df_clean.columns)} colonnes**")
                st.dataframe(df_clean.head(10), use_container_width=True, hide_index=True)

                csv_out = df_clean.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Télécharger fichier nettoyé", csv_out,
                                   f"cleaned_{uploaded_clean.name.replace('.xlsx','.csv')}",
                                   "text/csv", use_container_width=True)
