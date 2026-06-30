"""
AquaPredict AI - Générateur de Rapports PDF
Utilise ReportLab pour créer des rapports professionnels
"""

import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.colors import HexColor

# Couleurs AquaPredict
BLUE_DARK = HexColor("#1565C0")
BLUE_MED = HexColor("#0288D1")
BLUE_LIGHT = HexColor("#E3F2FD")
GREEN = HexColor("#27AE60")
ORANGE = HexColor("#F39C12")
RED = HexColor("#E74C3C")
GRAY = HexColor("#64748B")
WHITE = colors.white


def _header_style():
    return ParagraphStyle("header", fontName="Helvetica-Bold", fontSize=20,
                          textColor=BLUE_DARK, spaceAfter=6)


def _title_style():
    return ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=13,
                          textColor=BLUE_DARK, spaceBefore=14, spaceAfter=6)


def _body_style():
    return ParagraphStyle("body", fontName="Helvetica", fontSize=10,
                          textColor=HexColor("#1A2332"), spaceAfter=4, leading=14)


def _caption_style():
    return ParagraphStyle("caption", fontName="Helvetica", fontSize=9,
                          textColor=GRAY, spaceAfter=4)


def _table_header_style():
    return [
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, BLUE_LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CBD5E0")),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]


def _risk_color(niveau):
    return {"Faible": GREEN, "Moyen": ORANGE, "Élevé": RED}.get(niveau, GRAY)


def generate_rapport_journalier(stats: dict, canalisations: list, alertes: list,
                                 predictions: list, user_name: str = "Système") -> bytes:
    """Génère un rapport journalier complet en PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                             rightMargin=2*cm, leftMargin=2*cm,
                             topMargin=2.5*cm, bottomMargin=2*cm)
    story = []

    # ── En-tête ──────────────────────────────────────────────
    story.append(Paragraph("🌊 AquaPredict AI", _header_style()))
    story.append(Paragraph("Système Intelligent de Prédiction des Fuites", _caption_style()))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE_DARK, spaceAfter=8))

    story.append(Paragraph("RAPPORT JOURNALIER", ParagraphStyle(
        "rtype", fontName="Helvetica-Bold", fontSize=14, textColor=BLUE_MED)))
    story.append(Paragraph(
        f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} | Par: {user_name}",
        _caption_style()
    ))
    story.append(Spacer(1, 0.4*cm))

    # ── KPI Cards (tableau) ──────────────────────────────────
    story.append(Paragraph("Indicateurs Clés", _title_style()))
    kpi_data = [
        ["Indicateur", "Valeur", "Statut"],
        ["Canalisations surveillées", str(stats.get("nb_canalisations", 0)), "✅"],
        ["Alertes actives", str(stats.get("nb_alertes", 0)),
         "⚠️" if stats.get("nb_alertes", 0) > 0 else "✅"],
        ["Alertes critiques", str(stats.get("nb_alertes_critiques", 0)),
         "🔴" if stats.get("nb_alertes_critiques", 0) > 0 else "✅"],
        ["Fuites non réparées", str(stats.get("nb_fuites", 0)),
         "⚠️" if stats.get("nb_fuites", 0) > 0 else "✅"],
        ["Score de risque moyen", f"{stats.get('risque_moyen', 0):.1f}%",
         "🔴" if stats.get("risque_moyen", 0) > 60 else ("⚠️" if stats.get("risque_moyen", 0) > 30 else "✅")],
        ["Interventions en cours", str(stats.get("nb_interventions_en_cours", 0)), "🔧"],
    ]
    t = Table(kpi_data, colWidths=[8*cm, 4*cm, 3*cm])
    t.setStyle(TableStyle(_table_header_style()))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    # ── Alertes récentes ─────────────────────────────────────
    if alertes:
        story.append(Paragraph("Alertes Actives", _title_style()))
        alert_data = [["#", "Zone", "Type", "Priorité", "Date"]]
        for i, a in enumerate(alertes[:10], 1):
            alert_data.append([
                str(i),
                a.get("zone", "N/A"),
                a.get("type_alerte", ""),
                a.get("priorite", ""),
                str(a.get("created_at", ""))[:16],
            ])
        t2 = Table(alert_data, colWidths=[1.2*cm, 4*cm, 4.5*cm, 3*cm, 4*cm])
        t2.setStyle(TableStyle(_table_header_style()))
        story.append(t2)
        story.append(Spacer(1, 0.5*cm))

    # ── Prédictions récentes ─────────────────────────────────
    if predictions:
        story.append(Paragraph("Dernières Prédictions ML", _title_style()))
        pred_data = [["Canalisation", "Zone", "Risque", "Score (%)", "Date"]]
        for p in predictions[:10]:
            pred_data.append([
                p.get("canalisation_code", "N/A"),
                p.get("zone", "N/A"),
                p.get("risque_niveau", ""),
                f"{p.get('score_risque', 0):.1f}%",
                str(p.get("timestamp", ""))[:16],
            ])
        t3 = Table(pred_data, colWidths=[3.5*cm, 4*cm, 3*cm, 3*cm, 4*cm])
        t3.setStyle(TableStyle(_table_header_style()))
        story.append(t3)
        story.append(Spacer(1, 0.5*cm))

    # ── État des canalisations ───────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("État du Réseau", _title_style()))
    if canalisations:
        from collections import Counter
        etats = Counter(c.get("etat", "Bon") for c in canalisations)
        zones = Counter(c.get("zone", "") for c in canalisations)

        etat_data = [["État", "Nombre", "Pourcentage"]]
        total = len(canalisations)
        for etat, count in sorted(etats.items()):
            etat_data.append([etat, str(count), f"{count/total*100:.1f}%"])
        etat_data.append(["TOTAL", str(total), "100%"])

        t4 = Table(etat_data, colWidths=[6*cm, 4*cm, 4*cm])
        t4.setStyle(TableStyle(_table_header_style()))
        story.append(t4)

    # ── Pied de page ─────────────────────────────────────────
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE_MED))
    story.append(Paragraph(
        "AquaPredict AI © 2025 | Système développé dans le cadre d'un Master 2 Intelligence Artificielle | Confidentiel",
        ParagraphStyle("footer", fontName="Helvetica", fontSize=8, textColor=GRAY, alignment=1)
    ))

    doc.build(story)
    return buffer.getvalue()


def generate_rapport_prediction(prediction_result: dict, canalisation: dict, user_name: str = "") -> bytes:
    """Génère un rapport de prédiction individuel."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                             rightMargin=2*cm, leftMargin=2*cm,
                             topMargin=2.5*cm, bottomMargin=2*cm)
    story = []

    story.append(Paragraph("🌊 AquaPredict AI — Rapport de Prédiction", _header_style()))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE_DARK, spaceAfter=8))
    story.append(Paragraph(
        f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Analyste: {user_name}",
        _caption_style()
    ))
    story.append(Spacer(1, 0.3*cm))

    # Résultat principal
    risque = prediction_result.get("risque_niveau", "N/A")
    score = prediction_result.get("score_risque", 0)
    risk_color = _risk_color(risque)

    result_style = ParagraphStyle("result", fontName="Helvetica-Bold", fontSize=22,
                                   textColor=risk_color, alignment=1, spaceBefore=10, spaceAfter=10)
    story.append(Paragraph(f"Niveau de Risque: {risque}", result_style))
    story.append(Paragraph(f"Score de Risque: {score:.1f}%", ParagraphStyle(
        "score", fontName="Helvetica-Bold", fontSize=16, textColor=risk_color, alignment=1)))
    story.append(Spacer(1, 0.5*cm))

    # Probabilités
    probs = prediction_result.get("probabilities", {})
    if probs:
        story.append(Paragraph("Probabilités par Niveau", _title_style()))
        prob_data = [["Niveau", "Probabilité"]]
        for niveau, prob in probs.items():
            prob_data.append([niveau, f"{prob:.1f}%"])
        t = Table(prob_data, colWidths=[8*cm, 6*cm])
        t.setStyle(TableStyle(_table_header_style()))
        story.append(t)

    # Infos canalisation
    if canalisation:
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("Informations Canalisation", _title_style()))
        can_data = [
            ["Code", canalisation.get("code", "N/A")],
            ["Zone", canalisation.get("zone", "N/A")],
            ["Matériau", canalisation.get("materiau", "N/A")],
            ["Âge", f"{canalisation.get('age', 0)} ans"],
            ["Diamètre", f"{canalisation.get('diametre', 0)} mm"],
            ["Nb Réparations", str(canalisation.get("nb_reparations", 0))],
        ]
        t2 = Table(can_data, colWidths=[6*cm, 8*cm])
        t2.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (0, -1), BLUE_LIGHT),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CBD5E0")),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BLUE_LIGHT, WHITE]),
        ]))
        story.append(t2)

    # Recommandations
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Recommandations", _title_style()))
    recs = {
        "Faible": "La canalisation est en bon état. Continuer la surveillance périodique standard.",
        "Moyen": "Surveillance renforcée recommandée. Planifier une inspection dans les 30 jours.",
        "Élevé": "INTERVENTION URGENTE REQUISE. Planifier une intervention dans les 7 jours. Risque de rupture élevé.",
    }
    story.append(Paragraph(recs.get(risque, "Consulter l'équipe technique."), _body_style()))

    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE_MED))
    story.append(Paragraph("AquaPredict AI © 2025 | Rapport généré automatiquement par le système ML",
                            ParagraphStyle("footer", fontName="Helvetica", fontSize=8, textColor=GRAY, alignment=1)))

    doc.build(story)
    return buffer.getvalue()
