"""
engine/ai_advisor.py
=====================
Conseiller IA pour la formulation :
  - Analyse des contraintes utilisateur
  - Recommandation de composants
  - Suggestion de methode d'optimisation
  - Alertes de compatibilite
"""

from __future__ import annotations
import numpy as np
from typing import List, Dict, Any, Optional
from loguru import logger
from data.materials_db import MATERIALS, get_by_category, search_by_function, get_compatible
from data.properties_db import PROPERTIES, get_key_factors


# ─────────────────────────────────────────────────────────────────────────────
# Analyse de compatibilite
# ─────────────────────────────────────────────────────────────────────────────

def check_compatibility(component_ids: List[str]) -> Dict[str, Any]:
    """
    Verifie la compatibilite entre les composants selectionnes.
    Retourne les paires incompatibles et les alertes.
    """
    alerts   = []
    warnings = []

    # Regles de compatibilite categorie-categorie
    INCOMPATIBLE_RULES = [
        ("cationic", "anionic",  "Tensioactifs cationique + anionique : precipitation possible"),
        ("api",      "oxidizing","API + oxydant : degradation possible"),
    ]

    # Verifier les types de tensioactifs
    has_cationic = any(
        MATERIALS.get(m, {}).get("properties", {}).get("type") == "cationic"
        for m in component_ids
    )
    has_anionic = any(
        MATERIALS.get(m, {}).get("properties", {}).get("type") == "anionic"
        for m in component_ids
    )
    if has_cationic and has_anionic:
        alerts.append("Melange tensioactif cationique + anionique detecte — risque de precipitation")

    # pH et stabilite polymere
    for mat_id in component_ids:
        mat = MATERIALS.get(mat_id, {})
        ph_range = mat.get("properties", {}).get("pH_stability")
        if ph_range:
            warnings.append(f"{mat_id} stable seulement a pH [{ph_range[0]}-{ph_range[1]}]")

    # Sensibilite a la lumiere
    light_sensitive = [
        m for m in component_ids
        if MATERIALS.get(m, {}).get("properties", {}).get("light_sensitive")
    ]
    if light_sensitive:
        warnings.append(f"Composants photosensibles detectes : {light_sensitive} — conditionnement opaque requis")

    # Ingredients ignifuges
    flammable = [
        m for m in component_ids
        if MATERIALS.get(m, {}).get("properties", {}).get("flammable")
    ]
    if flammable:
        warnings.append(f"Composants inflammables : {flammable} — securite incendie")

    return {
        "compatible":  len(alerts) == 0,
        "alerts":      alerts,
        "warnings":    warnings,
        "n_checked":   len(component_ids),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Recommandation de composants
# ─────────────────────────────────────────────────────────────────────────────

def recommend_components(
    target_properties: List[str],
    application: str,
    excluded_ids: Optional[List[str]] = None,
    max_suggestions: int = 10,
) -> Dict[str, Any]:
    """
    Recommande des composants selon les proprietes cibles et l'application.
    """
    logger.info(f"recommend_components — props={target_properties}, app={application}")
    excluded = set(excluded_ids or [])
    scores: Dict[str, float] = {}

    for prop_id in target_properties:
        key_factors = get_key_factors(prop_id)
        for factor in key_factors:
            # Mapper facteur -> fonction de materiau
            factor_to_function = {
                "polymer_conc":  "thickener",
                "surfactant_HLB":"emulsifier",
                "antioxidant":   "antioxidant",
                "buffer_capacity":"buffer",
                "solvent_ratio": "solvent",
                "emollient_type":"emollient",
                "wax_ratio":     "wax",
                "particle_size": "milling",
            }
            fn = factor_to_function.get(factor, factor)
            for mat_id, mat in search_by_function(fn).items():
                if mat_id not in excluded:
                    scores[mat_id] = scores.get(mat_id, 0) + 1

    # Appliquer bonus selon l'application
    app_preferences = {
        "cosmetic":      ["emollient", "humectant", "film_former"],
        "pharmaceutical":["binder", "disintegrant", "controlled_release"],
        "food":          ["thickener", "emulsifier", "preservative"],
        "industrial":    ["solvent", "lubricant", "binder"],
    }
    for fn in app_preferences.get(application, []):
        for mat_id in search_by_function(fn):
            if mat_id not in excluded:
                scores[mat_id] = scores.get(mat_id, 0) + 0.5

    # Trier et formater
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:max_suggestions]
    suggestions = []
    for mat_id, score in ranked:
        mat = MATERIALS.get(mat_id, {})
        suggestions.append({
            "id":        mat_id,
            "name":      mat.get("name", mat_id),
            "category":  mat.get("category", "?"),
            "function":  mat.get("function", []),
            "min_pct":   mat.get("min_pct", 0),
            "max_pct":   mat.get("max_pct", 100),
            "cost_rel":  mat.get("cost_rel", 0),
            "relevance": round(score, 2),
            "reason":    f"Pertinent pour : {', '.join(mat.get('function', [])[:3])}",
        })

    return {
        "status":       "ok",
        "application":  application,
        "target_props": target_properties,
        "suggestions":  suggestions,
        "n_found":      len(suggestions),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Analyse de formulation existante
# ─────────────────────────────────────────────────────────────────────────────

def analyze_formulation(
    formulation: Dict[str, float],
    target_properties: Optional[List[str]] = None,
    application: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyse complete d'une formulation :
    - Compatibilite
    - Balance fonctionnelle
    - Recommandations d'amelioration
    - Estimation proprietes attendues
    """
    logger.info(f"analyze_formulation — {len(formulation)} composants")

    component_ids = list(formulation.keys())

    # 1. Compatibilite
    compat = check_compatibility(component_ids)

    # 2. Balance des fonctions
    function_coverage: Dict[str, List[str]] = {}
    for mat_id, pct in formulation.items():
        mat = MATERIALS.get(mat_id, {})
        for fn in mat.get("function", []):
            function_coverage.setdefault(fn, []).append(f"{mat_id}({pct:.1f}%)")

    # 3. Proprietes estimees
    estimated = {}
    total_pct = sum(formulation.values())

    # HLB moyen
    hlb_n = hlb_d = 0.0
    for mat_id, pct in formulation.items():
        mat = MATERIALS.get(mat_id, {})
        if "HLB" in mat:
            hlb_n += mat["HLB"] * pct; hlb_d += pct
    if hlb_d > 0:
        estimated["HLB_avg"] = round(hlb_n / hlb_d, 2)
        if estimated["HLB_avg"] < 6:
            estimated["emulsion_type"] = "W/O probable"
        elif estimated["HLB_avg"] > 10:
            estimated["emulsion_type"] = "O/W probable"
        else:
            estimated["emulsion_type"] = "Zone intermediaire"

    # Fraction aqueuse
    water_frac = sum(
        pct for mat_id, pct in formulation.items()
        if MATERIALS.get(mat_id, {}).get("category") in ("solvent",)
        and MATERIALS.get(mat_id, {}).get("cas") == "7732-18-5"
    )
    estimated["water_fraction_pct"] = round(water_frac, 2)

    # Teneur en polymere
    polymer_frac = sum(
        pct for mat_id, pct in formulation.items()
        if MATERIALS.get(mat_id, {}).get("category") == "polymer"
    )
    estimated["polymer_fraction_pct"] = round(polymer_frac, 2)
    if polymer_frac < 0.5:
        estimated["viscosity_qualitative"] = "Faible (< 0.5% polymere)"
    elif polymer_frac < 2.0:
        estimated["viscosity_qualitative"] = "Moderee (0.5-2% polymere)"
    else:
        estimated["viscosity_qualitative"] = "Elevee (> 2% polymere)"

    # 4. Recommandations
    recommendations = []
    if not any("preservative" in MATERIALS.get(m,{}).get("function",[]) for m in component_ids):
        if water_frac > 20:
            recommendations.append({
                "type": "warning",
                "message": "Formulation aqueuse sans conservateur detecte — risque microbiologique",
                "suggestion": "Ajouter Phenoxyethanol (0.5-1%) ou Parabens_Mix (0.1-0.3%)",
            })

    if not any("antioxidant" in MATERIALS.get(m,{}).get("function",[]) for m in component_ids):
        has_sensitive = any(
            MATERIALS.get(m,{}).get("properties",{}).get("log_P", 0) > 4
            for m in component_ids
        )
        if has_sensitive:
            recommendations.append({
                "type": "info",
                "message": "Actif lipophile sans antioxydant — risque d'oxydation",
                "suggestion": "Ajouter Vitamin_C (0.1-0.5%) ou BHT (0.01-0.1%)",
            })

    if total_pct < 99 or total_pct > 101:
        recommendations.append({
            "type": "error",
            "message": f"Somme des % = {total_pct:.2f}% — doit etre 100%",
            "suggestion": "Reequilibrer les pourcentages",
        })

    return {
        "status":             "ok",
        "compatibility":      compat,
        "function_coverage":  function_coverage,
        "estimated_properties": estimated,
        "recommendations":    recommendations,
        "n_recommendations":  len(recommendations),
    }


# ─────────────────────────────────────────────────────────────────────────────
# FONCTION PRINCIPALE — Point d'entree /recommend
# ─────────────────────────────────────────────────────────────────────────────

def recommend(
    target_properties: List[str],
    application: str,
    current_components: Optional[List[str]] = None,
    constraints: Optional[Dict[str, Any]] = None,
    budget_level: str = "medium",
) -> Dict[str, Any]:
    """
    Recommandation complete :
    1. Composants suggeres
    2. Methode d'optimisation conseillee
    3. Points de vigilance
    """
    logger.info(f"recommend — app={application}, props={target_properties}, budget={budget_level}")

    # Composants recommandes
    comp_recs = recommend_components(
        target_properties, application,
        excluded_ids=current_components, max_suggestions=8
    )

    # Filtrer par budget
    budget_limits = {"low": 20, "medium": 50, "high": 100}
    max_cost = budget_limits.get(budget_level, 50)
    filtered = [s for s in comp_recs["suggestions"] if s["cost_rel"] <= max_cost]

    # Methode d'optimisation conseillee
    n_targets = len(target_properties)
    if n_targets == 1:
        if "cost" in target_properties:
            opt_method = "optimize_cost"
            opt_reason = "Un seul objectif economique — minimisation directe"
        else:
            opt_method = "optimize_property"
            opt_reason = "Un seul objectif technique — optimisation avec differential_evolution"
    else:
        opt_method = "pareto_optimization"
        opt_reason = f"Objectifs multiples ({n_targets}) — front de Pareto recommande"

    # Alertes generales
    general_alerts = []
    if "stability_index" in target_properties:
        general_alerts.append("Tester la stabilite acceleree : 40°C/75%HR, 3 et 6 mois")
    if "release_rate_2h" in target_properties:
        general_alerts.append("Valider la liberation in vitro : dissolution USP II, milieu pH 6.8")
    if application == "pharmaceutical":
        general_alerts.append("Soumettre a validation GMP et dossier reglementaire (ICH Q8/Q9/Q10)")
    if application == "cosmetic":
        general_alerts.append("Tester la tolerance cutanee (patch test) et l'efficacite clinique")

    return {
        "status":                 "ok",
        "application":            application,
        "target_properties":      target_properties,
        "budget_level":           budget_level,
        "suggested_components":   filtered[:6],
        "all_suggestions":        comp_recs["suggestions"],
        "recommended_method":     opt_method,
        "method_reason":          opt_reason,
        "general_alerts":         general_alerts,
        "priority_action": (
            f"Commencer par : {filtered[0]['name']} ({filtered[0]['category']}) "
            f"si disponible, puis {opt_method}"
            if filtered else f"Lancer {opt_method} avec les composants actuels"
        ),
    }
