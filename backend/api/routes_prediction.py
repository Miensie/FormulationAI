from fastapi import APIRouter, HTTPException
from loguru import logger
from api.schemas import TrainRequest, PredictRequest, QuickPredictRequest
from engine.prediction_engine import train_predictor, predict_property, quick_estimate, list_trained_models

router = APIRouter()

@router.post("/predict/train", summary="Entrainer un modele ML")
async def train(req: TrainRequest):
    logger.info(f"POST /predict/train prop={req.target_property}")
    try:
        return train_predictor(req.formulations, req.target_values, req.component_ids,
                               req.target_property, req.model_type, req.n_estimators)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/predict", summary="Predire une propriete")
async def predict(req: PredictRequest):
    logger.info(f"POST /predict key={req.model_cache_key}")
    try:
        r = predict_property(req.formulations, req.component_ids, req.model_cache_key)
        if r.get("status") == "error": raise HTTPException(404, r.get("error"))
        return r
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/predict/quick", summary="Entrainer et predire en une etape")
async def quick(req: QuickPredictRequest):
    logger.info("POST /predict/quick")
    try:
        return quick_estimate(req.train_formulations, req.target_values, req.component_ids,
                              req.new_formulations, req.target_property, req.model_type)
    except Exception as e: raise HTTPException(500, str(e))

@router.get("/predict/models", summary="Lister les modeles entraines")
async def get_models():
    return {"models": list_trained_models()}
