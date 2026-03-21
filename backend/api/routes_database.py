from fastapi import APIRouter, HTTPException, Query
from data.materials_db import (get_all_materials, get_by_category, get_categories,
    get_material, search_by_function, get_material_ids)
from data.properties_db import get_all_properties, get_property, get_property_ids

router = APIRouter()

@router.get("/db/materials", summary="Tous les materiaux")
async def get_materials(category: str = Query(None)):
    if category:
        return {"materials": get_by_category(category), "category": category}
    return {"materials": get_all_materials()}

@router.get("/db/materials/{material_id}", summary="Un materiau")
async def get_mat(material_id: str):
    mat = get_material(material_id)
    if not mat: raise HTTPException(404, f"Materiau '{material_id}' non trouve")
    return {"id": material_id, **mat}

@router.get("/db/categories", summary="Categories disponibles")
async def get_cats():
    return {"categories": get_categories()}

@router.get("/db/materials/search/function", summary="Recherche par fonction")
async def search_fn(function: str = Query(...)):
    return {"results": search_by_function(function), "function": function}

@router.get("/db/properties", summary="Toutes les proprietes")
async def get_props():
    return {"properties": get_all_properties()}

@router.get("/db/properties/{prop_id}", summary="Une propriete")
async def get_prop(prop_id: str):
    prop = get_property(prop_id)
    if not prop: raise HTTPException(404, f"Propriete '{prop_id}' non trouvee")
    return {"id": prop_id, **prop}

@router.get("/db/ids", summary="Tous les IDs disponibles")
async def get_ids():
    return {"materials": get_material_ids(), "properties": get_property_ids()}
