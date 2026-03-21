"""
FormulationAI — Main FastAPI Application
Compatible Render.com + GitHub Pages.
"""

import os, sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from api.routes_formulation import router as form_router
from api.routes_optimization import router as opt_router
from api.routes_prediction   import router as pred_router
from api.routes_advisor      import router as adv_router
from api.routes_simulation   import router as sim_router
from api.routes_database     import router as db_router

# Logs
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logger.remove()
logger.add(sys.stderr, level=LOG_LEVEL,
           format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")
os.makedirs("logs", exist_ok=True)
logger.add("logs/formulationai.log", rotation="10 MB", retention="7 days", level="DEBUG")

# CORS
_raw = os.getenv("CORS_ORIGINS", "*")
CORS_ORIGINS = [o.strip() for o in _raw.split(",")] if _raw != "*" else ["*"]

app = FastAPI(
    title="FormulationAI API",
    description="Moteur de generation et optimisation de formulations chimiques assiste par IA.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

PREFIX = "/api/v1"
app.include_router(form_router, prefix=PREFIX, tags=["Formulation"])
app.include_router(opt_router,  prefix=PREFIX, tags=["Optimisation"])
app.include_router(pred_router, prefix=PREFIX, tags=["Prediction ML"])
app.include_router(adv_router,  prefix=PREFIX, tags=["IA Advisor"])
app.include_router(sim_router,  prefix=PREFIX, tags=["Simulation"])
app.include_router(db_router,   prefix=PREFIX, tags=["Base de donnees"])

@app.get("/", tags=["Sante"])
async def root():
    return {"status": "ok", "app": "FormulationAI", "version": "1.0.0"}

@app.get("/health", tags=["Sante"])
async def health():
    return {"status": "healthy"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Erreur non geree: {exc}")
    return JSONResponse(status_code=500, content={"error": str(exc)})

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"FormulationAI v1.0 → http://0.0.0.0:{port}/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
