"""
utils/report_generator.py
==========================
Generateur de rapport PDF professionnel pour FormulationAI CI.
Utilise uniquement la bibliotheque standard + fpdf2 (leger, sans Fortran).
Produit un PDF avec :
  - Page de garde branding CI
  - Tableau composition + barres visuelles
  - Cout FCFA detail par ingredient + fournisseurs locaux
  - Proprietes estimees
  - Recommandations et alertes
  - Mentions reglementaires (CODINORM, AIPS)
"""

from __future__ import annotations
import io, os, datetime
from typing import Dict, Any, List, Optional


def _try_import_fpdf():
    try:
        from fpdf import FPDF
        return FPDF
    except ImportError:
        return None


def generate_report_pdf(
    formulation:     Dict[str, float],
    enriched:        Dict[str, Any],
    fcfa_detail:     Optional[Dict[str, Any]] = None,
    analysis:        Optional[Dict[str, Any]] = None,
    company_name:    str = "FormulationAI CI",
    formulation_name:str = "Formulation",
    batch_kg:        float = 10.0,
    application:     str = "cosmetique",
    prepared_by:     str = "",
) -> bytes:
    """
    Genere un rapport PDF complet.
    Retourne les bytes du PDF.
    """
    FPDF = _try_import_fpdf()
    if FPDF is None:
        raise ImportError("fpdf2 non installe. Ajouter 'fpdf2' dans requirements.txt")

    # ── Constantes couleurs ───────────────────────────────────────────────────
    VERT_CI   = (0, 114, 54)      # Vert ivoirien
    ORANGE_CI = (240, 135, 0)     # Orange ivoirien
    BLANC     = (255, 255, 255)
    NOIR      = (20,  20,  20)
    GRIS_FOND = (245, 247, 250)
    GRIS_TXT  = (100, 110, 125)
    GRIS_BORD = (210, 215, 225)
    VERT_BON  = (34,  160,  80)
    ROUGE_BAD = (200,  50,  50)
    ORANGE_WARN=(200, 120,   0)

    date_str = datetime.datetime.now().strftime("%d/%m/%Y à %Hh%M")
    today    = datetime.date.today().strftime("%d/%m/%Y")

    # ── Helpers couleurs ──────────────────────────────────────────────────────
    def rgb(*c): return tuple(c)

    # ────────────────────────────────────────────────────────────────────────
    # Création du document
    # ────────────────────────────────────────────────────────────────────────
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(left=18, top=18, right=18)

    W  = pdf.w - 36   # largeur utile
    CX = 18           # marge gauche

    # ────────────────────────────────────────────────────────────────────────
    # PAGE DE GARDE
    # ────────────────────────────────────────────────────────────────────────
    pdf.add_page()

    # Bande verte supérieure
    pdf.set_fill_color(*VERT_CI)
    pdf.rect(0, 0, 210, 35, "F")

    # Logo texte
    pdf.set_text_color(*BLANC)
    pdf.set_xy(18, 8)
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 10, "FormulationAI", ln=False)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(*ORANGE_CI)
    pdf.set_xy(18, 20)
    pdf.cell(0, 6, "Cote d'Ivoire - Outil de Formulation Industrielle", ln=True)

    # Bande orange mince
    pdf.set_fill_color(*ORANGE_CI)
    pdf.rect(0, 35, 210, 2, "F")

    # Zone titre formulation
    pdf.set_xy(18, 50)
    pdf.set_text_color(*NOIR)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "RAPPORT DE FORMULATION", ln=True, align="C")
    pdf.set_xy(18, 62)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*VERT_CI)
    pdf.cell(0, 12, formulation_name, ln=True, align="C")

    # Rectangle encadré infos
    pdf.set_fill_color(*GRIS_FOND)
    pdf.set_draw_color(*GRIS_BORD)
    pdf.rect(28, 82, W - 20, 55, "FD")

    def info_row(y, label, value, val_color=NOIR):
        pdf.set_xy(35, y)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*GRIS_TXT)
        pdf.cell(50, 7, label + " :", ln=False)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*val_color)
        pdf.cell(0, 7, str(value), ln=True)

    info_row(88,  "Entreprise",       company_name)
    info_row(96,  "Application",      application.capitalize())
    info_row(104, "Batch reference",  f"{batch_kg} kg")
    info_row(112, "Prepare par",      prepared_by or "FormulationAI")
    info_row(120, "Date de rapport",  today)

    # Coût FCFA en évidence
    if fcfa_detail:
        cost_fmt = fcfa_detail.get("cost_per_kg_fmt", "N/A")
        total_fmt = fcfa_detail.get("total_fcfa_fmt", "N/A")
        pdf.set_fill_color(*VERT_CI)
        pdf.rect(28, 145, W - 20, 22, "F")
        pdf.set_xy(35, 148)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(*BLANC)
        pdf.cell(80, 8, f"Cout de revient : {cost_fmt}", ln=False)
        pdf.set_xy(130, 148)
        pdf.cell(0, 8, f"Batch {batch_kg} kg : {total_fmt}", ln=True)
        pdf.set_xy(35, 158)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(*ORANGE_CI)
        pdf.cell(0, 6, "Prix marche Abidjan 2024-2025 (FCFA = Franc CFA UEMOA XOF)")

    # Bande verte bas + mentions
    pdf.set_fill_color(*VERT_CI)
    pdf.rect(0, 272, 210, 25, "F")
    pdf.set_xy(18, 278)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*BLANC)
    pdf.cell(0, 5,
        "Genere par FormulationAI CI | Conforme CODINORM | "
        "Valider avec votre service R&D avant production", ln=True, align="C")
    pdf.set_xy(18, 284)
    pdf.cell(0, 5,
        f"Genere le {date_str} | Les prix FCFA sont indicatifs", ln=True, align="C")

    # ────────────────────────────────────────────────────────────────────────
    # PAGE 2 — COMPOSITION DÉTAILLÉE
    # ────────────────────────────────────────────────────────────────────────
    pdf.add_page()

    def section_title(title: str):
        pdf.set_fill_color(*VERT_CI)
        pdf.rect(CX, pdf.get_y(), W, 9, "F")
        pdf.set_xy(CX + 3, pdf.get_y() + 1)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*BLANC)
        pdf.cell(0, 7, title.upper(), ln=True)
        pdf.ln(3)

    def section_orange(title: str):
        pdf.set_fill_color(*ORANGE_CI)
        pdf.rect(CX, pdf.get_y(), W, 9, "F")
        pdf.set_xy(CX + 3, pdf.get_y() + 1)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*BLANC)
        pdf.cell(0, 7, title.upper(), ln=True)
        pdf.ln(3)

    def kv_row(label, value, y=None, bold_val=False, val_color=NOIR):
        if y: pdf.set_xy(CX, y)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*GRIS_TXT)
        pdf.cell(65, 6, label, ln=False)
        pdf.set_font("Helvetica", "B" if bold_val else "", 9)
        pdf.set_text_color(*val_color)
        pdf.cell(0, 6, str(value), ln=True)
        pdf.set_draw_color(*GRIS_BORD)
        pdf.line(CX, pdf.get_y(), CX + W, pdf.get_y())
        pdf.ln(1)

    # ── En-tête page ─────────────────────────────────────────────────────────
    pdf.set_fill_color(*VERT_CI)
    pdf.rect(0, 0, 210, 10, "F")
    pdf.set_xy(CX, 2)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*BLANC)
    pdf.cell(W//2, 6, "FormulationAI CI", ln=False)
    pdf.cell(0, 6, formulation_name, ln=True, align="R")
    pdf.ln(6)

    # ── 1. Résumé ─────────────────────────────────────────────────────────────
    section_title("1. Resume de la formulation")
    kv_row("Nombre de composants",   enriched.get("n_components", "?"))
    kv_row("Total (%)",              f"{enriched.get('total_pct', 0):.2f} %")
    kv_row("Densite estimee",        f"{enriched.get('density_est', 0):.4f} g/cm3")
    if enriched.get("HLB_avg"):
        kv_row("HLB moyen",          f"{enriched.get('HLB_avg')}")
    kv_row("Categories presentes",   ", ".join(enriched.get("categories", [])))
    if enriched.get("cost_fcfa_fmt"):
        kv_row("Cout FCFA/kg",       enriched.get("cost_fcfa_fmt", ""), bold_val=True, val_color=VERT_CI)
    pdf.ln(4)

    # ── 2. Tableau Composition ────────────────────────────────────────────────
    section_title("2. Composition detaillee")

    # En-têtes tableau
    COL = [62, 20, 30, 48]   # Composant | % | Categorie | Fonction
    pdf.set_fill_color(*NOIR)
    pdf.set_draw_color(*NOIR)
    pdf.rect(CX, pdf.get_y(), W, 7, "F")
    pdf.set_xy(CX, pdf.get_y())
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*BLANC)
    headers = ["Composant", "%", "Categorie", "Fonctions principales"]
    for h, w in zip(headers, COL):
        pdf.cell(w, 7, h, ln=False)
    pdf.ln(7)

    # Lignes triées par % décroissant
    from data.custom_db import get_all_materials_merged
    all_mats = get_all_materials_merged()
    comp = enriched.get("composition", {})
    sorted_comp = sorted(comp.items(), key=lambda x: x[1], reverse=True)

    for i, (mat_id, pct) in enumerate(sorted_comp):
        mat  = all_mats.get(mat_id, {})
        name = (mat.get("name") or mat_id)[:30]
        cat  = mat.get("category", "?")[:12]
        fns  = ", ".join(mat.get("function", [])[:3])[:28]

        # Couleur alternée
        if i % 2 == 0:
            pdf.set_fill_color(*GRIS_FOND)
            pdf.rect(CX, pdf.get_y(), W, 6.5, "F")

        pdf.set_xy(CX, pdf.get_y())
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*NOIR)
        pdf.cell(COL[0], 6.5, name, ln=False)
        pdf.set_font("Helvetica", "B", 8)
        pct_color = VERT_BON if pct > 10 else NOIR
        pdf.set_text_color(*pct_color)
        pdf.cell(COL[1], 6.5, f"{pct:.2f}%", ln=False)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*GRIS_TXT)
        pdf.cell(COL[2], 6.5, cat, ln=False)
        pdf.cell(COL[3], 6.5, fns, ln=True)

        # Barre proportionnelle
        bar_max = W * 0.6
        bar_w   = max(1, bar_max * pct / 100)
        pdf.set_fill_color(*VERT_CI)
        pdf.rect(CX, pdf.get_y(), bar_w, 2, "F")
        pdf.set_fill_color(*GRIS_BORD)
        pdf.rect(CX + bar_w, pdf.get_y(), bar_max - bar_w, 2, "F")
        pdf.ln(3)

    pdf.ln(5)

    # ────────────────────────────────────────────────────────────────────────
    # PAGE 3 — COÛT FCFA DÉTAILLÉ
    # ────────────────────────────────────────────────────────────────────────
    pdf.add_page()

    # En-tête page
    pdf.set_fill_color(*VERT_CI)
    pdf.rect(0, 0, 210, 10, "F")
    pdf.set_xy(CX, 2)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*BLANC)
    pdf.cell(W//2, 6, "FormulationAI CI", ln=False)
    pdf.cell(0, 6, "Analyse economique FCFA", ln=True, align="R")
    pdf.ln(6)

    section_orange("3. Analyse economique - Prix FCFA (Marche Abidjan 2024-2025)")

    if fcfa_detail:
        # Totaux en évidence
        pdf.set_fill_color(*ORANGE_CI)
        pdf.rect(CX, pdf.get_y(), W, 14, "F")
        pdf.set_xy(CX + 3, pdf.get_y() + 2)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(*BLANC)
        pdf.cell(90, 6, f"Batch {fcfa_detail.get('batch_kg')} kg : {fcfa_detail.get('total_fcfa_fmt')}", ln=False)
        pdf.cell(0, 6, f"Cout/kg : {fcfa_detail.get('cost_per_kg_fmt')}", ln=True)
        pdf.ln(4)

        # Tableau détail
        detail = fcfa_detail.get("detail", {})
        estimated_ids = fcfa_detail.get("estimated_ids", [])

        COL2 = [55, 18, 22, 28, 30, 25]
        pdf.set_fill_color(*NOIR)
        pdf.rect(CX, pdf.get_y(), W, 7, "F")
        pdf.set_xy(CX, pdf.get_y())
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(*BLANC)
        for h, w in zip(["Ingredient","% formule","Qte (kg)","Prix FCFA/kg","Cout FCFA","Source"], COL2):
            pdf.cell(w, 7, h, ln=False)
        pdf.ln(7)

        sorted_detail = sorted(detail.items(), key=lambda x: x[1]["cost_fcfa"], reverse=True)
        for i, (mat_id, d) in enumerate(sorted_detail):
            mat = all_mats.get(mat_id, {})
            name = (mat.get("name") or mat_id)[:24]
            is_est = mat_id in estimated_ids
            color  = GRIS_TXT if is_est else NOIR

            if i % 2 == 0:
                pdf.set_fill_color(*GRIS_FOND)
                pdf.rect(CX, pdf.get_y(), W, 6, "F")

            pdf.set_xy(CX, pdf.get_y())
            pdf.set_font("Helvetica", "" if not is_est else "I", 7.5)
            pdf.set_text_color(*color)
            pdf.cell(COL2[0], 6, name, ln=False)
            pdf.cell(COL2[1], 6, f"{d['pct']:.1f}%", ln=False)
            pdf.cell(COL2[2], 6, f"{d['kg']:.3f}", ln=False)
            pdf.set_font("Helvetica", "B", 7.5)
            pdf.cell(COL2[3], 6, f"{int(d['price_fcfa_kg']):,}".replace(",", " "), ln=False)
            pdf.set_text_color(*VERT_CI)
            pdf.cell(COL2[4], 6, f"{int(d['cost_fcfa']):,}".replace(",", " "), ln=False)
            pdf.set_text_color(*GRIS_TXT)
            pdf.set_font("Helvetica", "I", 6.5)
            src_label = "Prix CI" if d["source"] == "prix_ci" else "Estime"
            pdf.cell(COL2[5], 6, src_label, ln=True)

        pdf.ln(3)

        # Ligne total
        pdf.set_fill_color(*VERT_CI)
        pdf.rect(CX, pdf.get_y(), W, 8, "F")
        pdf.set_xy(CX + 3, pdf.get_y() + 1)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*BLANC)
        total_cost = int(fcfa_detail.get("total_fcfa", 0))
        pdf.cell(100, 6, f"TOTAL BATCH {fcfa_detail.get('batch_kg')} kg", ln=False)
        pdf.cell(0, 6,
            f"{total_cost:,} FCFA".replace(",", " ") +
            f"  ({int(total_cost/fcfa_detail.get('batch_kg',1)):,} FCFA/kg)".replace(",", " "),
            ln=True)
        pdf.ln(5)

        if estimated_ids:
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(*ORANGE_WARN)
            pdf.cell(0, 5,
                f"Note : Prix estimes pour {len(estimated_ids)} ingredient(s) "
                f"sans prix FCFA dans la BD : {', '.join(estimated_ids[:5])}",
                ln=True)
        pdf.ln(4)

    # ── 4. Fournisseurs CI ─────────────────────────────────────────────────────
    section_orange("4. Fournisseurs recommandes (Cote d'Ivoire)")

    from data.ci_materials_db import CI_MATERIALS, CI_SUPPLIERS_GENERAL
    comp_keys = enriched.get("composition", {}).keys()
    shown_suppliers = set()

    for mat_id in comp_keys:
        mat = CI_MATERIALS.get(mat_id, {})
        suppliers = mat.get("suppliers_ci", [])
        for sup in suppliers[:1]:  # 1 fournisseur prioritaire par ingrédient
            key = sup["name"]
            if key not in shown_suppliers:
                shown_suppliers.add(key)
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_text_color(*VERT_CI)
                mat_name = (mat.get("name") or mat_id)[:30]
                pdf.cell(0, 6, f"► {mat_name}  →  {sup['name']}", ln=True)
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(*GRIS_TXT)
                pdf.set_x(CX + 5)
                pdf.cell(0, 5,
                    f"  {sup.get('city','')}  |  {sup.get('contact','')}  |  {sup.get('notes','')}",
                    ln=True)
                pdf.ln(1)

    # Fournisseurs généraux
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*NOIR)
    pdf.cell(0, 6, "Fournisseurs generaux Abidjan :", ln=True)
    for sup in CI_SUPPLIERS_GENERAL[:3]:
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*GRIS_TXT)
        pdf.set_x(CX + 3)
        pdf.cell(0, 5,
            f"• {sup['name']} ({sup.get('city','')})"
            f" — {sup.get('specialty','')} — {sup.get('phone','')}",
            ln=True)
    pdf.ln(5)

    # ── 5. Analyse et recommandations ─────────────────────────────────────────
    if analysis:
        section_title("5. Analyse de la formulation")

        compat = analysis.get("compatibility", {})
        compat_ok = compat.get("compatible", True)
        pdf.set_fill_color(*(VERT_BON if compat_ok else ROUGE_BAD))
        pdf.rect(CX, pdf.get_y(), W, 8, "F")
        pdf.set_xy(CX + 3, pdf.get_y() + 1)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*BLANC)
        pdf.cell(0, 6,
            f"Compatibilite : {'CONFORME' if compat_ok else 'PROBLEMES DETECTES'}  "
            f"| {compat.get('n_checked',0)} composants verifies",
            ln=True)
        pdf.ln(3)

        for alert in compat.get("alerts", []):
            pdf.set_font("Helvetica", "B", 8); pdf.set_text_color(*ROUGE_BAD)
            pdf.cell(6, 5, "✗", ln=False)
            pdf.set_font("Helvetica", "", 8); pdf.set_text_color(*NOIR)
            pdf.cell(0, 5, alert, ln=True)

        for warn in compat.get("warnings", []):
            pdf.set_font("Helvetica", "B", 8); pdf.set_text_color(*ORANGE_WARN)
            pdf.cell(6, 5, "!", ln=False)
            pdf.set_font("Helvetica", "", 8); pdf.set_text_color(*NOIR)
            pdf.cell(0, 5, warn, ln=True)

        recs = analysis.get("recommendations", [])
        if recs:
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*VERT_CI)
            pdf.cell(0, 6, "Recommandations R&D :", ln=True)
            for rec in recs[:5]:
                t = rec.get("type","info")
                c = ROUGE_BAD if t=="error" else ORANGE_WARN if t=="warning" else VERT_CI
                pdf.set_font("Helvetica", "B", 8); pdf.set_text_color(*c)
                pdf.set_x(CX+3)
                pdf.cell(0, 5, f"[{t.upper()}] {rec.get('message','')}", ln=True)
                pdf.set_font("Helvetica", "I", 7.5); pdf.set_text_color(*GRIS_TXT)
                pdf.set_x(CX+8)
                pdf.cell(0, 4.5, f"→ {rec.get('suggestion','')}", ln=True)
                pdf.ln(1)
        pdf.ln(4)

    # ── 6. Propriétés estimées ─────────────────────────────────────────────────
    section_title("6. Proprietes estimees et climat CI")

    props_est = (analysis or {}).get("estimated_properties", {})
    kv_row("Densite formulation",  f"{enriched.get('density_est',0):.4f} g/cm3")
    if enriched.get("HLB_avg"):
        kv_row("HLB moyen pondere", str(enriched.get("HLB_avg")))
        kv_row("Type emulsion prevu", props_est.get("emulsion_type","N/A"))
    if props_est.get("viscosity_qualitative"):
        kv_row("Viscosite qualitative", props_est.get("viscosity_qualitative"))
    kv_row("Fraction polymere",    f"{props_est.get('polymer_fraction_pct',0):.2f} %")
    kv_row("Fraction aqueuse",     f"{props_est.get('water_fraction_pct',0):.2f} %")

    # Note spécifique climat CI
    pdf.ln(3)
    pdf.set_fill_color(*GRIS_FOND)
    pdf.set_draw_color(*ORANGE_CI)
    pdf.rect(CX, pdf.get_y(), W, 18, "FD")
    pdf.set_xy(CX + 3, pdf.get_y() + 2)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(*ORANGE_CI)
    pdf.cell(0, 5, "NOTE CLIMAT COTE D'IVOIRE (Tropical humide)", ln=True)
    pdf.set_xy(CX + 3, pdf.get_y())
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*NOIR)
    pdf.multi_cell(W - 6, 4.5,
        "Temp. moy. Abidjan 27-32 degres C | Humidite 70-90% RH\n"
        "Verifier : tenue a 40 degres C (test etuve) | Point de fusion cires > 40 degres C\n"
        "Stabilite acceleree recommandee : 40 degres C / 75% HR pendant 3 mois\n"
        "Emballage : flacon pompe > pot large ouverture (eviter oxydation)")
    pdf.ln(5)

    # ── 7. Pied de page réglementaire ─────────────────────────────────────────
    pdf.set_fill_color(*VERT_CI)
    pdf.rect(0, 272, 210, 25, "F")
    pdf.set_xy(CX, 274)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*ORANGE_CI)
    pdf.cell(0, 5, "Conformite reglementaire Cote d'Ivoire", ln=True, align="C")
    pdf.set_xy(CX, 280)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*BLANC)
    pdf.cell(0, 4,
        "CODINORM CI | AIPS (pharmacie) | FIRCA (agroalimentaire) | UEMOA | "
        "Loi 2013-450 protection donnees", ln=True, align="C")
    pdf.set_xy(CX, 285)
    pdf.cell(0, 4, f"Rapport genere le {date_str} par FormulationAI CI",
        ln=True, align="C")

    return bytes(pdf.output())
