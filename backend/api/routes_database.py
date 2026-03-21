"""
api/routes_database.py
=======================
Endpoints pour la BD principale (lecture seule) + BD personnalisee (CRUD complet).
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from data.materials_db   import (get_all_materials, get_by_category,
                                   get_categories, get_material,
                                   search_by_function, get_material_ids)
from data.properties_db  import (get_all_properties, get_property, get_property_ids)
from data.custom_db      import (add_material, update_material, delete_material,
                                   add_property, delete_property,
                                   get_custom_materials, get_custom_properties,
                                   get_all_materials_merged, get_all_properties_merged,
                                   export_custom_db, import_custom_db, clear_custom_db,
                                   validate_material_data)

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# Schemas pour la BD personnalisee
# ─────────────────────────────────────────────────────────────────────────────

class MaterialInput(BaseModel):
    name:           str
    category:       str = Field(..., description="polymer|surfactant|solvent|oil|wax|excipient|api|preservative|plasticizer|pigment|other")
    cas:            Optional[str]   = None
    molar_mass:     Optional[float] = None
    density:        Optional[float] = 1.0
    HLB:            Optional[float] = None
    pKa:            Optional[float] = None
    cost_rel:       float           = Field(10.0, description="Cout relatif (1=eau, 100=premium)")
    min_pct:        float           = Field(0.0,  ge=0, le=100)
    max_pct:        float           = Field(100.0,ge=0, le=100)
    melting_point:  Optional[float] = None
    boiling_point:  Optional[float] = None
    function:       List[str]       = []
    compatible_with:List[str]       = []
    solubility:     Dict[str, float]= {}
    properties:     Dict[str, Any]  = {}
    source:         str             = "user"

class PropertyInput(BaseModel):
    name:            str
    unit:            str
    range:           List[float]         = [0.0, 1e9]
    log_scale:       bool                = False
    method:          str                 = ""
    target_ranges:   Dict[str, List[float]] = {}
    key_factors:     List[str]           = []
    prediction_model:str                 = "random_forest"
    source:          str                 = "user"

class ImportPayload(BaseModel):
    materials:  Dict[str, Any] = {}
    properties: Dict[str, Any] = {}
    mode:       str = Field("merge", description="merge|replace")


# ─────────────────────────────────────────────────────────────────────────────
# BD PRINCIPALE — lecture seule
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/db/materials",
            summary="Tous les materiaux (BD principale + custom)")
async def get_materials(
    category: str = Query(None, description="Filtrer par categorie"),
    custom_only: bool = Query(False, description="Uniquement les materiaux personnalises"),
):
    if custom_only:
        data = get_custom_materials()
    elif category:
        # Fusion BD principale + custom, filtree par categorie
        merged = get_all_materials_merged()
        data   = {k: v for k, v in merged.items() if v.get("category") == category}
    else:
        data = get_all_materials_merged()
    return {"materials": data, "n": len(data)}


@router.get("/db/materials/{material_id}",
            summary="Detail d'un materiau")
async def get_mat(material_id: str):
    # Chercher d'abord dans la BD custom, puis dans la principale
    from data.custom_db import get_custom_material
    mat = get_custom_material(material_id) or get_material(material_id)
    if not mat:
        raise HTTPException(404, f"Materiau '{material_id}' non trouve")
    return {"id": material_id, **mat}


@router.get("/db/categories",
            summary="Toutes les categories disponibles")
async def get_cats():
    # Fusionner categories BD + custom
    from data.custom_db import get_custom_materials
    all_mats  = {**get_all_materials_merged()}
    cats      = sorted(set(v.get("category","other") for v in all_mats.values()))
    return {"categories": cats}


@router.get("/db/materials/search/function",
            summary="Recherche par fonction")
async def search_fn(function: str = Query(...)):
    merged  = get_all_materials_merged()
    results = {k: v for k, v in merged.items()
               if function in v.get("function", [])}
    return {"results": results, "function": function, "n": len(results)}


@router.get("/db/properties",
            summary="Toutes les proprietes (BD principale + custom)")
async def get_props(custom_only: bool = Query(False)):
    data = get_custom_properties() if custom_only else get_all_properties_merged()
    return {"properties": data, "n": len(data)}


@router.get("/db/properties/{prop_id}",
            summary="Detail d'une propriete")
async def get_prop(prop_id: str):
    from data.custom_db import get_custom_properties
    merged = get_all_properties_merged()
    prop   = merged.get(prop_id)
    if not prop:
        raise HTTPException(404, f"Propriete '{prop_id}' non trouvee")
    return {"id": prop_id, **prop}


@router.get("/db/ids",
            summary="Tous les identifiants disponibles")
async def get_ids():
    return {
        "materials":  list(get_all_materials_merged().keys()),
        "properties": list(get_all_properties_merged().keys()),
        "custom_materials":  list(get_custom_materials().keys()),
        "custom_properties": list(get_custom_properties().keys()),
    }


# ─────────────────────────────────────────────────────────────────────────────
# BD PERSONNALISEE — CRUD MATERIAUX
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/db/materials/custom",
             summary="Ajouter un nouveau materiau",
             description="Ajoute un materiau personnalise dans la BD. Persiste entre les redemarrages.")
async def add_mat(material_id: str = Query(..., description="Identifiant unique ex: MyPolymer_X"),
                  data: MaterialInput = ...):
    # Verifier unicite
    if material_id in get_all_materials_merged():
        raise HTTPException(409,
            f"'{material_id}' existe deja. Utilisez PUT pour mettre a jour.")

    # Valider
    val = validate_material_data(data.model_dump())
    if not val["valid"]:
        raise HTTPException(400, detail={"errors": val["errors"]})

    result = add_material(material_id, data.model_dump())
    if result.get("status") == "error":
        raise HTTPException(400, result["error"])
    return {**result, "validation": val}


@router.put("/db/materials/custom/{material_id}",
            summary="Mettre a jour un materiau personnalise")
async def update_mat(material_id: str, updates: Dict[str, Any]):
    result = update_material(material_id, updates)
    if result.get("status") == "error":
        raise HTTPException(404, result["error"])
    return result


@router.delete("/db/materials/custom/{material_id}",
               summary="Supprimer un materiau personnalise")
async def delete_mat(material_id: str):
    result = delete_material(material_id)
    if result.get("status") == "error":
        raise HTTPException(404, result["error"])
    return result


@router.post("/db/materials/validate",
             summary="Valider les donnees avant ajout")
async def validate_mat(data: MaterialInput):
    return validate_material_data(data.model_dump())


# ─────────────────────────────────────────────────────────────────────────────
# BD PERSONNALISEE — CRUD PROPRIETES
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/db/properties/custom",
             summary="Ajouter une nouvelle propriete")
async def add_prop(prop_id: str = Query(..., description="Ex: my_hardness"),
                   data: PropertyInput = ...):
    if prop_id in get_all_properties_merged():
        raise HTTPException(409, f"'{prop_id}' existe deja.")
    result = add_property(prop_id, data.model_dump())
    if result.get("status") == "error":
        raise HTTPException(400, result["error"])
    return result


@router.delete("/db/properties/custom/{prop_id}",
               summary="Supprimer une propriete personnalisee")
async def delete_prop(prop_id: str):
    result = delete_property(prop_id)
    if result.get("status") == "error":
        raise HTTPException(404, result["error"])
    return result


# ─────────────────────────────────────────────────────────────────────────────
# EXPORT / IMPORT / RESET
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/db/custom/export",
            summary="Exporter la BD personnalisee en JSON")
async def export_db():
    return export_custom_db()


@router.post("/db/custom/import",
             summary="Importer une BD personnalisee",
             description="mode='merge' fusionne, mode='replace' remplace tout.")
async def import_db(payload: ImportPayload):
    return import_custom_db(payload.model_dump())


@router.delete("/db/custom/clear",
               summary="Supprimer toutes les entrees personnalisees")
async def clear_db():
    return clear_custom_db()


@router.get("/db/stats",
            summary="Statistiques de la BD")
async def db_stats():
    all_mats   = get_all_materials_merged()
    all_props  = get_all_properties_merged()
    custom_m   = get_custom_materials()
    custom_p   = get_custom_properties()

    from data.materials_db import get_categories
    cats = {}
    for v in all_mats.values():
        c = v.get("category", "other")
        cats[c] = cats.get(c, 0) + 1

    return {
        "total_materials":    len(all_mats),
        "builtin_materials":  len(all_mats) - len(custom_m),
        "custom_materials":   len(custom_m),
        "total_properties":   len(all_props),
        "builtin_properties": len(all_props) - len(custom_p),
        "custom_properties":  len(custom_p),
        "by_category":        cats,
        "custom_material_ids":list(custom_m.keys()),
    }


# ─────────────────────────────────────────────────────────────────────────────
# BD LOCALE CÔTE D'IVOIRE
# ─────────────────────────────────────────────────────────────────────────────

from pydantic import BaseModel as _BM
class CostFCFARequest(_BM):
    formulation: Dict[str, float]
    batch_kg:    float = 1.0

@router.get("/db/ci/materials",
            summary="Matieres premieres locales Cote d'Ivoire")
async def get_ci_mats(local_only: bool = False):
    from data.ci_materials_db import CI_MATERIALS, get_ci_by_origin
    data = get_ci_by_origin(True) if local_only else CI_MATERIALS
    return {"materials": data, "n": len(data), "country": "Cote d'Ivoire"}

@router.get("/db/ci/suppliers",
            summary="Fournisseurs locaux Abidjan")
async def get_ci_suppliers():
    from data.ci_materials_db import CI_SUPPLIERS_GENERAL
    return {"suppliers": CI_SUPPLIERS_GENERAL, "n": len(CI_SUPPLIERS_GENERAL)}

@router.post("/db/ci/cost_fcfa",
             summary="Calculer le cout en FCFA",
             description="Retourne le cout reel en FCFA pour un batch donne, selon les prix marche Abidjan.")
async def calc_cost_fcfa(req: CostFCFARequest):
    from data.ci_materials_db import estimate_cost_fcfa
    try:
        return estimate_cost_fcfa(req.formulation, req.batch_kg)
    except Exception as e:
        raise HTTPException(500, str(e))


# ─────────────────────────────────────────────────────────────────────────────
# DEVISES — nouveaux endpoints
# ─────────────────────────────────────────────────────────────────────────────

class PriceFormulationRequest(BaseModel):
    formulation: Dict[str, float]
    currency:    str = Field("FCFA", description="FCFA|EUR|USD")

class UpdateRateRequest(BaseModel):
    usd_rate: float = Field(..., gt=0, description="Nouveau taux USD/FCFA")


@router.get("/currency/rates",
            summary="Taux de change disponibles")
async def get_rates():
    from utils.currency import get_exchange_rates
    return get_exchange_rates()


@router.post("/currency/price",
             summary="Calculer le prix d'une formulation dans une devise")
async def price_formulation(req: PriceFormulationRequest):
    from utils.currency import price_formulation as pf
    try:
        return pf(req.formulation, req.currency)
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/currency/update_usd",
             summary="Mettre a jour le taux USD/FCFA")
async def update_usd(req: UpdateRateRequest):
    from utils.currency import update_usd_rate, EXCHANGE_RATES
    update_usd_rate(req.usd_rate)
    return {"status": "ok", "new_rate": req.usd_rate,
            "message": f"1 USD = {req.usd_rate} FCFA"}


@router.get("/db/ci_materials",
            summary="Matieres premieres locales Cote d'Ivoire")
async def get_ci_mats():
    from data.ci_materials_db import CI_MATERIALS, CI_MATERIALS_META
    return {"materials": CI_MATERIALS, "meta": CI_MATERIALS_META,
            "n": len(CI_MATERIALS)}
