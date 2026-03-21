from fastapi import APIRouter, HTTPException
from loguru import logger
from api.schemas import OptimizeCostRequest, OptimizePropertyRequest, ParetoRequest
from engine.optimization_engine import optimize_cost, optimize_property, pareto_optimization

router = APIRouter()

@router.post("/optimize/cost", summary="Minimiser le cout")
async def opt_cost(req: OptimizeCostRequest):
    logger.info("POST /optimize/cost")
    try:
        r = optimize_cost([c.model_dump() for c in req.components], req.method, req.seed)
        if r.get("status") == "error": raise HTTPException(400, r.get("errors"))
        return r
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/optimize", summary="Optimiser une propriete")
async def opt_prop(req: OptimizePropertyRequest):
    logger.info(f"POST /optimize prop={req.target_property}")
    try:
        r = optimize_property(
            [c.model_dump() for c in req.components],
            req.target_property, req.target_value, req.maximize,
            req.weights, req.method, req.seed,
        )
        if r.get("status") == "error": raise HTTPException(400, r.get("errors"))
        return r
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/optimize/pareto", summary="Front de Pareto")
async def opt_pareto(req: ParetoRequest):
    logger.info("POST /optimize/pareto")
    try:
        r = pareto_optimization([c.model_dump() for c in req.components], req.n_solutions, req.seed)
        if r.get("status") == "error": raise HTTPException(400, r.get("errors"))
        return r
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))
