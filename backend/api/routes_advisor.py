from fastapi import APIRouter, HTTPException
from loguru import logger
from api.schemas import RecommendRequest, AnalyzeFormulationRequest
from engine.ai_advisor import recommend, analyze_formulation, check_compatibility

router = APIRouter()

@router.post("/recommend", summary="Recommandations IA intelligentes")
async def ai_recommend(req: RecommendRequest):
    logger.info(f"POST /recommend app={req.application}")
    try:
        return recommend(req.target_properties, req.application,
                         req.current_components, req.constraints, req.budget_level)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/recommend/analyze", summary="Analyser une formulation existante")
async def analyze(req: AnalyzeFormulationRequest):
    logger.info("POST /recommend/analyze")
    try:
        return analyze_formulation(req.formulation, req.target_properties, req.application)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/recommend/compatibility", summary="Verifier la compatibilite")
async def compat(req: AnalyzeFormulationRequest):
    try:
        return check_compatibility(list(req.formulation.keys()))
    except Exception as e: raise HTTPException(500, str(e))
