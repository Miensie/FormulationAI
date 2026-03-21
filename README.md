# ⚗ FormulationAI

> **Generateur et optimiseur de formulations chimiques assiste par IA**
> Excel Web Add-in (Office.js) + Backend Python FastAPI

---

## Architecture

```
formulationai/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── api/
│   │   ├── schemas.py
│   │   ├── routes_formulation.py   POST /generate_formulation, /validate
│   │   ├── routes_optimization.py  POST /optimize/cost, /optimize, /optimize/pareto
│   │   ├── routes_prediction.py    POST /predict/train, /predict, /predict/quick
│   │   ├── routes_advisor.py       POST /recommend, /recommend/analyze
│   │   ├── routes_simulation.py    POST /simulate/viscosity|release|stability|compare
│   │   └── routes_database.py      GET  /db/materials, /db/properties, /db/categories
│   ├── engine/
│   │   ├── formulation_engine.py   Generation LHS + aleatoire
│   │   ├── optimization_engine.py  Minimisation cout + Pareto
│   │   ├── prediction_engine.py    ML: RF, GBM, SVR, Ridge
│   │   ├── ai_advisor.py           Compatibilite + recommandations
│   │   └── simulation_engine.py    Viscosite, liberation, stabilite
│   └── data/
│       ├── materials_db.py         30 matieres premieres
│       └── properties_db.py        10 proprietes mesurables
└── frontend/
    ├── manifest.xml
    ├── taskpane.html               6 onglets
    ├── css/taskpane.css
    └── js/
        ├── config.js               URL API
        └── taskpane.js             Logique complete
```

## Installation locale

```bash
cd backend
pip install -r requirements.txt
python main.py
# API : http://localhost:8000/docs
```

## Deploiement GitHub + Render

```bash
# 1. Pusher sur GitHub
git init && git add . && git commit -m "FormulationAI v1"
git remote add origin https://github.com/miensie/FormulationAI.git
git push -u origin main

# 2. Render : New > Web Service > backend/
#    Build: pip install -r requirements.txt
#    Start: uvicorn main:app --host 0.0.0.0 --port $PORT

# 3. Modifier frontend/js/config.js → RENDER_API_URL
# 4. git push → redeploi automatique
```

## Endpoints principaux

| Methode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/v1/generate_formulation` | Generer N formulations |
| POST | `/api/v1/optimize/cost` | Minimiser le cout |
| POST | `/api/v1/optimize` | Optimiser propriete |
| POST | `/api/v1/optimize/pareto` | Front de Pareto |
| POST | `/api/v1/predict/train` | Entrainer ML |
| POST | `/api/v1/predict` | Predire propriete |
| POST | `/api/v1/recommend` | Recommandations IA |
| POST | `/api/v1/simulate/viscosity` | Viscosite vs T |
| POST | `/api/v1/simulate/release` | Profil liberation |
| POST | `/api/v1/simulate/stability` | Stabilite temps |
| GET  | `/api/v1/db/materials` | Base materiaux |
| GET  | `/api/v1/db/properties` | Base proprietes |

## Exemple : Generer une formulation cosmetique

```bash
curl -X POST http://localhost:8000/api/v1/generate_formulation \
  -H "Content-Type: application/json" \
  -d '{
    "components": [
      {"id":"Water",        "min":50, "max":80},
      {"id":"Glycerol",     "min":5,  "max":20},
      {"id":"HPMC_E5",      "min":0.5,"max":3},
      {"id":"Tween_80",     "min":0.5,"max":3},
      {"id":"Phenoxyethanol","min":0.5,"max":1,"fixed":true}
    ],
    "n_formulations": 5,
    "method": "lhs"
  }'
```
