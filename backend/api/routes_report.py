"""
api/routes_report.py
=====================
Endpoint de generation de rapport PDF professionnel.
POST /report/pdf
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from loguru import logger

router = APIRouter()

class ReportRequest(BaseModel):
    formulation:      Dict[str, float]
    batch_kg:         float = Field(10.0, gt=0, description="Taille du batch en kg")
    formulation_name: str   = "Ma Formulation"
    company_name:     str   = "Mon Entreprise"
    prepared_by:      str   = ""
    application:      str   = "cosmetique"
    include_analysis: bool  = True


@router.post("/report/pdf",
             summary="Generer un rapport PDF professionnel",
             description=(
                 "Genere un rapport PDF complet incluant :\n"
                 "- Page de garde avec branding CI\n"
                 "- Tableau de composition avec barres visuelles\n"
                 "- Analyse economique detaillee en FCFA\n"
                 "- Fournisseurs locaux Abidjan\n"
                 "- Proprietes estimees + note climat CI\n"
                 "- Conformite reglementaire (CODINORM, AIPS)"
             ))
async def generate_pdf(req: ReportRequest):
    logger.info(f"POST /report/pdf  form='{req.formulation_name}'  batch={req.batch_kg}kg")
    try:
        from engine.formulation_engine import validate_formulation_full
        from data.ci_materials_db      import estimate_cost_fcfa
        from utils.report_generator    import generate_report_pdf

        # Validation + enrichissement
        enriched = validate_formulation_full(req.formulation)

        # Cout FCFA
        fcfa_detail = estimate_cost_fcfa(req.formulation, req.batch_kg)

        # Analyse IA (optionnelle)
        analysis = None
        if req.include_analysis:
            try:
                from engine.ai_advisor import analyze_formulation
                analysis = analyze_formulation(req.formulation, application=req.application)
            except Exception as e:
                logger.warning(f"Analyse IA ignoree: {e}")

        # Génération PDF
        pdf_bytes = generate_report_pdf(
            formulation=      req.formulation,
            enriched=         enriched,
            fcfa_detail=      fcfa_detail,
            analysis=         analysis,
            company_name=     req.company_name,
            formulation_name= req.formulation_name,
            batch_kg=         req.batch_kg,
            application=      req.application,
            prepared_by=      req.prepared_by,
        )

        filename = req.formulation_name.replace(" ", "_")[:40] + "_rapport.pdf"
        return Response(
            content=     pdf_bytes,
            media_type=  "application/pdf",
            headers=     {
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length":      str(len(pdf_bytes)),
            },
        )

    except ImportError as e:
        raise HTTPException(503,
            f"fpdf2 non installe. Ajouter 'fpdf2' a requirements.txt : {e}")
    except Exception as e:
        logger.error(f"Erreur generation PDF: {e}")
        raise HTTPException(500, str(e))
