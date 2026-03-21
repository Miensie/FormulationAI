"""
engine/optimization_engine.py
==============================
Optimisation de formulations :
  - Minimisation de cout
  - Maximisation d'une propriete cible
  - Optimisation multi-objectifs (Pareto)
"""

from __future__ import annotations
import numpy as np
from scipy.optimize import differential_evolution, minimize
from typing import List, Dict, Any, Callable, Optional
from loguru import logger
from data.materials_db import MATERIALS, estimate_blend_cost, estimate_blend_density
from engine.formulation_engine import ComponentConstraint, validate_constraints, _enrich


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _build_bounds_and_eq(components: List[ComponentConstraint]):
    """Retourne bounds pour scipy + contrainte d'egalite sum=100."""
    ids  = [c["id"] for c in components]
    mins = [c.get("min", 0.0) for c in components]
    maxs = [c.get("max", 100.0) for c in components]
    bounds = list(zip(mins, maxs))
    eq_constraint = {"type": "eq", "fun": lambda x: x.sum() - 100.0}
    return ids, bounds, eq_constraint


def _vec_to_formulation(ids: List[str], x: np.ndarray) -> Dict[str, float]:
    return {ids[i]: round(float(x[i]), 6) for i in range(len(ids))}


# ─────────────────────────────────────────────────────────────────────────────
# Objectifs
# ─────────────────────────────────────────────────────────────────────────────

def _objective_cost(x: np.ndarray, ids: List[str]) -> float:
    formulation = _vec_to_formulation(ids, x)
    return estimate_blend_cost(formulation)


def _objective_maximize_prop(x: np.ndarray, ids: List[str],
                               prop_fn: Callable) -> float:
    formulation = _vec_to_formulation(ids, x)
    return -prop_fn(formulation)  # negate pour maximiser


def _objective_custom(x: np.ndarray, ids: List[str],
                        weights: Dict[str, float]) -> float:
    """
    Objectif composite : minimise une combinaison ponderee de :
    - cost : cout
    - density : ecart par rapport a cible
    - HLB : ecart par rapport a cible
    """
    formulation = _vec_to_formulation(ids, x)
    cost    = estimate_blend_cost(formulation)
    density = estimate_blend_density(formulation)

    value = 0.0
    if "cost" in weights:
        value += weights["cost"] * cost / 100.0

    if "target_density" in weights:
        target = weights["target_density"]
        value += weights.get("w_density", 1.0) * abs(density - target)

    if "target_HLB" in weights:
        target = weights["target_HLB"]
        hlb_num = hlb_den = 0.0
        for mat_id, pct in formulation.items():
            mat = MATERIALS.get(mat_id, {})
            if "HLB" in mat:
                hlb_num += mat["HLB"] * pct; hlb_den += pct
        if hlb_den > 0:
            hlb = hlb_num / hlb_den
            value += weights.get("w_HLB", 1.0) * abs(hlb - target) / 20.0

    return value


# ─────────────────────────────────────────────────────────────────────────────
# FONCTIONS PUBLIQUES
# ─────────────────────────────────────────────────────────────────────────────

def optimize_cost(
    components: List[ComponentConstraint],
    method: str = "differential_evolution",
    seed: int = 42,
) -> Dict[str, Any]:
    """Minimise le cout de la formulation sous contraintes."""
    logger.info(f"optimize_cost — {len(components)} composants, method={method}")

    val = validate_constraints(components)
    if not val["valid"]:
        return {"status": "error", "errors": val["errors"]}

    ids, bounds, eq_con = _build_bounds_and_eq(components)

    if method == "differential_evolution":
        def obj_penalized(x):
            penalty = abs(x.sum() - 100.0) * 1000
            return _objective_cost(x, ids) + penalty

        result = differential_evolution(
            obj_penalized, bounds, seed=seed,
            maxiter=500, tol=1e-8, workers=1, popsize=20,
        )
    else:
        x0 = np.array([(c.get("min",0)+c.get("max",100))/2 for c in components])
        x0 = x0 * 100.0 / x0.sum()
        result = minimize(
            _objective_cost, x0, args=(ids,),
            method="SLSQP", bounds=bounds, constraints=[eq_con],
            options={"maxiter": 1000},
        )

    x_opt = np.clip(result.x, [b[0] for b in bounds], [b[1] for b in bounds])
    x_opt = x_opt * 100.0 / x_opt.sum()
    formulation = _vec_to_formulation(ids, x_opt)
    enriched    = _enrich(formulation)

    return {
        "status":         "ok",
        "objective":      "minimize_cost",
        "optimal_cost":   round(float(result.fun if result.fun < 1e9 else enriched["cost_index"]), 4),
        "converged":      bool(result.success),
        "n_iterations":   int(getattr(result, "nit", -1)),
        **enriched,
    }


def optimize_property(
    components: List[ComponentConstraint],
    target_property: str,
    target_value: Optional[float] = None,
    maximize: bool = True,
    weights: Optional[Dict[str, float]] = None,
    method: str = "differential_evolution",
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Optimise une propriete de la formulation.
    Si target_value est donne, minimise |prop - target|.
    Sinon, maximise (ou minimise) la propriete estimee.
    """
    logger.info(f"optimize_property — prop={target_property}, maximize={maximize}")

    val = validate_constraints(components)
    if not val["valid"]:
        return {"status": "error", "errors": val["errors"]}

    ids, bounds, eq_con = _build_bounds_and_eq(components)
    w = weights or {}

    def obj(x):
        penalty = abs(x.sum() - 100.0) * 1000
        # Objectif composite
        form = _vec_to_formulation(ids, x)
        val_obj = _objective_custom(x, ids, w)
        return val_obj + penalty

    if method == "differential_evolution":
        result = differential_evolution(
            obj, bounds, seed=seed, maxiter=500, tol=1e-8,
            workers=1, popsize=15,
        )
    else:
        x0 = np.array([(b[0]+b[1])/2 for b in bounds])
        x0 = x0 * 100.0 / x0.sum()
        result = minimize(obj, x0, method="SLSQP", bounds=bounds,
                          constraints=[eq_con], options={"maxiter":1000})

    x_opt = np.clip(result.x, [b[0] for b in bounds], [b[1] for b in bounds])
    x_opt = x_opt * 100.0 / x_opt.sum()
    formulation = _vec_to_formulation(ids, x_opt)
    enriched    = _enrich(formulation)

    return {
        "status":          "ok",
        "objective":       f"{'maximize' if maximize else 'minimize'}_{target_property}",
        "converged":       bool(result.success),
        "n_iterations":    int(getattr(result, "nit", -1)),
        "objective_value": round(float(result.fun), 6),
        **enriched,
    }


def pareto_optimization(
    components: List[ComponentConstraint],
    n_solutions: int = 20,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Optimisation bi-objectifs : cout vs densite.
    Genere un front de Pareto par variation du parametre de ponderation.
    """
    logger.info(f"pareto_optimization — {n_solutions} solutions")

    val = validate_constraints(components)
    if not val["valid"]:
        return {"status": "error", "errors": val["errors"]}

    ids, bounds, eq_con = _build_bounds_and_eq(components)
    rng = np.random.default_rng(seed)

    pareto_solutions = []
    lambdas = np.linspace(0, 1, n_solutions)

    for lam in lambdas:
        def obj(x, lam=lam):
            penalty = abs(x.sum() - 100.0) * 1000
            form = _vec_to_formulation(ids, x)
            cost    = estimate_blend_cost(form) / 100.0
            density = estimate_blend_density(form)
            return lam * cost + (1 - lam) * density + penalty

        x0 = rng.uniform([b[0] for b in bounds], [b[1] for b in bounds])
        x0 = x0 * 100.0 / x0.sum()

        try:
            res = minimize(obj, x0, method="SLSQP", bounds=bounds,
                           constraints=[eq_con], options={"maxiter":500})
            x_opt = np.clip(res.x, [b[0] for b in bounds], [b[1] for b in bounds])
            x_opt = x_opt * 100.0 / x_opt.sum()
            form  = _vec_to_formulation(ids, x_opt)
            enr   = _enrich(form)
            pareto_solutions.append({
                "lambda":     round(float(lam), 3),
                "cost":       enr["cost_index"],
                "density":    enr["density_est"],
                "composition":enr["composition"],
            })
        except Exception as e:
            logger.debug(f"Pareto lam={lam:.2f} echoue: {e}")

    # Trier par cout croissant
    pareto_solutions.sort(key=lambda s: s["cost"])

    costs    = [s["cost"]    for s in pareto_solutions]
    densities= [s["density"] for s in pareto_solutions]

    return {
        "status":    "ok",
        "objective": "pareto_cost_vs_density",
        "n_solutions": len(pareto_solutions),
        "solutions": pareto_solutions,
        "chart_data": {"cost": costs, "density": densities},
    }
