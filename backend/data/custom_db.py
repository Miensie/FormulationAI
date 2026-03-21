"""
data/custom_db.py
==================
Base de donnees personnalisee — stockage en memoire des materiaux
et proprietes ajoutes par l'utilisateur pendant la session.

Pour persistance entre sessions : exporter via /db/export
et reimporter via /db/import au demarrage.
"""

from __future__ import annotations
import json, os
from typing import Dict, Any, List, Optional
from loguru import logger

# ── Stockage en memoire (session) ─────────────────────────────────────────────
_CUSTOM_MATERIALS:  Dict[str, Dict[str, Any]] = {}
_CUSTOM_PROPERTIES: Dict[str, Dict[str, Any]] = {}

# Chemin du fichier de persistance local (optionnel)
_PERSIST_FILE = os.path.join(os.path.dirname(__file__), "custom_data.json")


# ─────────────────────────────────────────────────────────────────────────────
# Chargement au démarrage
# ─────────────────────────────────────────────────────────────────────────────

def load_from_file():
    """Charge les donnees personnalisees depuis le fichier JSON si present."""
    global _CUSTOM_MATERIALS, _CUSTOM_PROPERTIES
    if os.path.exists(_PERSIST_FILE):
        try:
            with open(_PERSIST_FILE, encoding="utf-8") as f:
                data = json.load(f)
            _CUSTOM_MATERIALS  = data.get("materials", {})
            _CUSTOM_PROPERTIES = data.get("properties", {})
            logger.info(f"BD custom chargee : {len(_CUSTOM_MATERIALS)} materiaux, "
                        f"{len(_CUSTOM_PROPERTIES)} proprietes")
        except Exception as e:
            logger.warning(f"Impossible de charger custom_data.json : {e}")


def save_to_file():
    """Sauvegarde les donnees personnalisees dans le fichier JSON."""
    try:
        with open(_PERSIST_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "materials":  _CUSTOM_MATERIALS,
                "properties": _CUSTOM_PROPERTIES,
            }, f, indent=2, ensure_ascii=False)
        logger.info(f"BD custom sauvegardee : {_PERSIST_FILE}")
        return True
    except Exception as e:
        logger.error(f"Sauvegarde echouee : {e}")
        return False


# Charger au démarrage du module
load_from_file()


# ─────────────────────────────────────────────────────────────────────────────
# MATERIAUX — CRUD
# ─────────────────────────────────────────────────────────────────────────────

def add_material(material_id: str, data: Dict[str, Any],
                 persist: bool = True) -> Dict[str, Any]:
    """
    Ajoute ou met a jour un materiau personnalise.

    Champs minimaux requis : name, category
    Champs optionnels : cas, molar_mass, density, HLB, cost_rel,
                        min_pct, max_pct, function, compatible_with,
                        solubility, properties, ...
    """
    required = {"name", "category"}
    missing  = required - set(data.keys())
    if missing:
        return {"status": "error", "error": f"Champs requis manquants : {missing}"}

    # Valider la categorie
    valid_cats = ["polymer","surfactant","solvent","oil","wax",
                  "excipient","api","preservative","plasticizer","pigment","other"]
    if data.get("category") not in valid_cats:
        data["category"] = "other"

    # Valider min/max
    if data.get("min_pct", 0) > data.get("max_pct", 100):
        return {"status": "error", "error": "min_pct > max_pct"}

    _CUSTOM_MATERIALS[material_id] = {
        "name":           data.get("name"),
        "category":       data.get("category", "other"),
        "cas":            data.get("cas", ""),
        "molar_mass":     data.get("molar_mass"),
        "density":        data.get("density", 1.0),
        "HLB":            data.get("HLB"),
        "pKa":            data.get("pKa"),
        "cost_rel":       data.get("cost_rel", 10.0),
        "min_pct":        data.get("min_pct", 0.0),
        "max_pct":        data.get("max_pct", 100.0),
        "melting_point":  data.get("melting_point"),
        "boiling_point":  data.get("boiling_point"),
        "function":       data.get("function", []),
        "compatible_with":data.get("compatible_with", []),
        "solubility":     data.get("solubility", {}),
        "properties":     data.get("properties", {}),
        "_custom":        True,   # marque pour distinguer des materiaux BD
        "_source":        data.get("source", "user"),
    }

    if persist:
        save_to_file()

    logger.info(f"Materiau '{material_id}' ajoute/mis a jour")
    return {"status": "ok", "id": material_id, "data": _CUSTOM_MATERIALS[material_id]}


def update_material(material_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Met a jour des champs specifiques d'un materiau existant."""
    if material_id not in _CUSTOM_MATERIALS:
        return {"status": "error", "error": f"'{material_id}' non trouve dans la BD custom"}
    _CUSTOM_MATERIALS[material_id].update(updates)
    save_to_file()
    return {"status": "ok", "id": material_id, "data": _CUSTOM_MATERIALS[material_id]}


def delete_material(material_id: str) -> Dict[str, Any]:
    """Supprime un materiau personnalise."""
    if material_id not in _CUSTOM_MATERIALS:
        return {"status": "error", "error": f"'{material_id}' non trouve"}
    del _CUSTOM_MATERIALS[material_id]
    save_to_file()
    return {"status": "ok", "deleted": material_id}


def get_custom_materials() -> Dict[str, Dict[str, Any]]:
    return _CUSTOM_MATERIALS.copy()


def get_custom_material(material_id: str) -> Optional[Dict[str, Any]]:
    return _CUSTOM_MATERIALS.get(material_id)


# ─────────────────────────────────────────────────────────────────────────────
# PROPRIETES — CRUD
# ─────────────────────────────────────────────────────────────────────────────

def add_property(prop_id: str, data: Dict[str, Any],
                 persist: bool = True) -> Dict[str, Any]:
    """
    Ajoute ou met a jour une propriete personnalisee.

    Champs minimaux : name, unit
    """
    if "name" not in data or "unit" not in data:
        return {"status": "error", "error": "Champs requis : name, unit"}

    _CUSTOM_PROPERTIES[prop_id] = {
        "name":           data["name"],
        "unit":           data["unit"],
        "range":          data.get("range", [0, 1e9]),
        "log_scale":      data.get("log_scale", False),
        "method":         data.get("method", ""),
        "target_ranges":  data.get("target_ranges", {}),
        "key_factors":    data.get("key_factors", []),
        "prediction_model": data.get("prediction_model", "random_forest"),
        "_custom":        True,
        "_source":        data.get("source", "user"),
    }

    if persist:
        save_to_file()

    logger.info(f"Propriete '{prop_id}' ajoutee/mise a jour")
    return {"status": "ok", "id": prop_id, "data": _CUSTOM_PROPERTIES[prop_id]}


def delete_property(prop_id: str) -> Dict[str, Any]:
    if prop_id not in _CUSTOM_PROPERTIES:
        return {"status": "error", "error": f"'{prop_id}' non trouve"}
    del _CUSTOM_PROPERTIES[prop_id]
    save_to_file()
    return {"status": "ok", "deleted": prop_id}


def get_custom_properties() -> Dict[str, Dict[str, Any]]:
    return _CUSTOM_PROPERTIES.copy()


# ─────────────────────────────────────────────────────────────────────────────
# FUSION avec la BD principale
# ─────────────────────────────────────────────────────────────────────────────

def get_all_materials_merged() -> Dict[str, Dict[str, Any]]:
    """Retourne la BD principale + les materiaux personnalises."""
    from data.materials_db import MATERIALS
    return {**MATERIALS, **_CUSTOM_MATERIALS}


def get_all_properties_merged() -> Dict[str, Dict[str, Any]]:
    """Retourne la BD principale + les proprietes personnalisees."""
    from data.properties_db import PROPERTIES
    return {**PROPERTIES, **_CUSTOM_PROPERTIES}


# ─────────────────────────────────────────────────────────────────────────────
# EXPORT / IMPORT JSON
# ─────────────────────────────────────────────────────────────────────────────

def export_custom_db() -> Dict[str, Any]:
    """Exporte toute la BD personnalisee en JSON."""
    return {
        "version":    "1.0",
        "n_materials":  len(_CUSTOM_MATERIALS),
        "n_properties": len(_CUSTOM_PROPERTIES),
        "materials":  _CUSTOM_MATERIALS,
        "properties": _CUSTOM_PROPERTIES,
    }


def import_custom_db(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Importe une BD personnalisee exportee.
    mode="replace" : remplace tout
    mode="merge"   : fusionne (les nouveaux ecrasent les existants)
    """
    global _CUSTOM_MATERIALS, _CUSTOM_PROPERTIES
    mode = data.get("mode", "merge")

    mats  = data.get("materials", {})
    props = data.get("properties", {})

    if mode == "replace":
        _CUSTOM_MATERIALS  = mats
        _CUSTOM_PROPERTIES = props
    else:
        _CUSTOM_MATERIALS.update(mats)
        _CUSTOM_PROPERTIES.update(props)

    save_to_file()
    return {
        "status":         "ok",
        "mode":           mode,
        "n_materials":    len(_CUSTOM_MATERIALS),
        "n_properties":   len(_CUSTOM_PROPERTIES),
    }


def clear_custom_db() -> Dict[str, Any]:
    """Supprime toutes les entrees personnalisees."""
    global _CUSTOM_MATERIALS, _CUSTOM_PROPERTIES
    n_mat  = len(_CUSTOM_MATERIALS)
    n_prop = len(_CUSTOM_PROPERTIES)
    _CUSTOM_MATERIALS  = {}
    _CUSTOM_PROPERTIES = {}
    save_to_file()
    return {"status": "ok", "deleted_materials": n_mat, "deleted_properties": n_prop}


# ─────────────────────────────────────────────────────────────────────────────
# VALIDATION D'UN MATERIAU AVANT AJOUT
# ─────────────────────────────────────────────────────────────────────────────

def validate_material_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valide les donnees d'un nouveau materiau.
    Retourne les erreurs et suggestions.
    """
    errors   = []
    warnings = []
    suggestions = []

    if not data.get("name"):
        errors.append("Le champ 'name' est obligatoire")
    if not data.get("category"):
        errors.append("Le champ 'category' est obligatoire")

    cost = data.get("cost_rel")
    if cost and cost > 100:
        warnings.append("cost_rel > 100 : verifier l'echelle (1=eau, 100=ingredient premium)")

    if data.get("min_pct", 0) > data.get("max_pct", 100):
        errors.append("min_pct > max_pct")

    if not data.get("function"):
        suggestions.append("Ajouter au moins une fonction (thickener, emulsifier, solvent...)")
    if not data.get("cas"):
        suggestions.append("Ajouter le numero CAS pour identification unique")
    if not data.get("density"):
        suggestions.append("Ajouter la densite pour les calculs de formulation")

    return {
        "valid":       len(errors) == 0,
        "errors":      errors,
        "warnings":    warnings,
        "suggestions": suggestions,
    }
