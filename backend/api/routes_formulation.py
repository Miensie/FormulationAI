from fastapi import APIRouter, HTTPException
from loguru import logger
from api.schemas import GenerateRequest, ValidateFormulationRequest
from engine.formulation_engine import generate_formulation, validate_formulation_full

router = APIRouter()

@router.post("/generate_formulation", summary="Generer des formulations")
async def generate(req: GenerateRequest):
    logger.info(f"POST /generate_formulation n={req.n_formulations}")
    try:
        result = generate_formulation(
            [c.model_dump() for c in req.components],
            req.n_formulations, req.method, req.seed,
        )
        if result.get("status") == "error":
            raise HTTPException(400, detail=result.get("errors"))
        return result
    except HTTPException: raise
    except Exception as e:
        logger.error(f"generate_formulation error: {e}")
        raise HTTPException(500, str(e))

@router.post("/validate", summary="Valider une formulation")
async def validate(req: ValidateFormulationRequest):
    try:
        return validate_formulation_full(req.formulation)
    except Exception as e:
        raise HTTPException(500, str(e))
