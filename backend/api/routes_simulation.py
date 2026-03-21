import numpy as np
from fastapi import APIRouter, HTTPException
from loguru import logger
from api.schemas import (SimulateViscosityRequest, SimulateReleaseRequest,
                          SimulateStabilityRequest, CompareFormulationsRequest)
from engine.simulation_engine import (simulate_viscosity_vs_temperature,
    simulate_release_profile, simulate_stability, compare_formulations)

router = APIRouter()

@router.post("/simulate/viscosity", summary="Simuler viscosite vs temperature")
async def sim_viscosity(req: SimulateViscosityRequest):
    try: return simulate_viscosity_vs_temperature(req.formulation, req.T_range, req.ref_viscosity)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/simulate/release", summary="Simuler profil de liberation")
async def sim_release(req: SimulateReleaseRequest):
    try: return simulate_release_profile(req.formulation, req.time_hours, req.api_id, req.dissolution_medium)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/simulate/stability", summary="Simuler stabilite dans le temps")
async def sim_stability(req: SimulateStabilityRequest):
    try: return simulate_stability(req.formulation, req.time_months, req.temperature_C, req.humidity_pct)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/simulate/compare", summary="Comparer plusieurs formulations")
async def sim_compare(req: CompareFormulationsRequest):
    try: return compare_formulations(req.formulations, req.labels, req.properties_to_compare)
    except Exception as e: raise HTTPException(500, str(e))
