"""
engine/formulation_engine.py
==============================
Moteur de generation de formulations :
  - Generation aleatoire avec contraintes
  - Latin Hypercube Sampling
  - Generation basee sur regles de formulation
  - Validation et normalisation
"""

from __future__ import annotations
import numpy as np
from typing import List, Dict, Any, Optional
from loguru import logger
from data.materials_db import MATERIALS, estimate_blend_cost, estimate_blend_density


# ─────────────────────────────────────────────────────────────────────────────
# Types
# ─────────────────────────────────────────────────────────────────────────────

ComponentConstraint = Dict[str, Any]
# { "id": str, "min": float, "max": float, "fixed": bool }

Formulation = Dict[str, float]
# { material_id: percentage, ... }


# ─────────────────────────────────────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────────────────────────────────────

def validate_constraints(components: List[ComponentConstraint]) -> Dict[str, Any]:
    """
    Verifie que les contraintes sont coherentes :
    - sum(min) <= 100 <= sum(max)
    - min <= max pour chaque composant
    - identifiants existent dans la BD
    """
    errors = []
    warnings = []

    sum_min = sum(c.get("min", 0) for c in components)
    sum_max = sum(c.get("max", 100) for c in components)

    if sum_min > 100:
        errors.append(f"sum(min) = {sum_min:.2f} > 100 — infaisable")
    if sum_max < 100:
        errors.append(f"sum(max) = {sum_max:.2f} < 100 — infaisable")

    for c in components:
        mat_id = c.get("id", "")
        if mat_id not in MATERIALS:
            warnings.append(f"Materiau '{mat_id}' non trouve dans la BD — utilise quand meme")
        lo, hi = c.get("min", 0), c.get("max", 100)
        if lo > hi:
            errors.append(f"{mat_id}: min ({lo}) > max ({hi})")
        if lo < 0 or hi > 100:
            errors.append(f"{mat_id}: valeurs hors [0, 100]")

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def normalize_formulation(formulation: Dict[str, float]) -> Dict[str, float]:
    """Normalise une formulation pour que la somme = 100%."""
    total = sum(formulation.values())
    if total <= 0:
        return formulation
    return {k: round(v * 100.0 / total, 6) for k, v in formulation.items()}


# ─────────────────────────────────────────────────────────────────────────────
# Generation aleatoire
# ─────────────────────────────────────────────────────────────────────────────

def _random_in_simplex(components: List[ComponentConstraint],
                        rng: np.random.Generator) -> Optional[Dict[str, float]]:
    """
    Tire un point aleatoire dans le simplexe defini par les contraintes.
    Methode : Dirichlet tronque + rejection sampling.
    """
    ids  = [c["id"] for c in components]
    mins = np.array([c.get("min", 0.0) for c in components])
    maxs = np.array([c.get("max", 100.0) for c in components])

    # Verifier faisabilite rapide
    residual = 100.0 - mins.sum()
    if residual < 0:
        return None

    # Dirichlet sur l'espace residuel
    for _ in range(500):  # max tentatives
        alpha = np.ones(len(components))
        sample = rng.dirichlet(alpha) * residual + mins
        if np.all(sample >= mins - 1e-9) and np.all(sample <= maxs + 1e-9):
            sample = np.clip(sample, mins, maxs)
            # Re-normaliser si necessaire
            total = sample.sum()
            if abs(total - 100.0) > 0.01:
                sample = sample * 100.0 / total
            return {ids[i]: round(float(sample[i]), 4) for i in range(len(ids))}
    return None


def _lhs_samples(components: List[ComponentConstraint],
                  n: int, rng: np.random.Generator) -> List[Dict[str, float]]:
    """Latin Hypercube Sampling dans l'espace contraint."""
    ids  = [c["id"] for c in components]
    mins = np.array([c.get("min", 0.0) for c in components])
    maxs = np.array([c.get("max", 100.0) for c in components])
    k    = len(components)

    # LHS : diviser chaque dimension en n intervalles
    cut  = np.linspace(0, 1, n + 1)
    u    = np.zeros((n, k))
    for j in range(k):
        u[:, j] = rng.permutation([rng.uniform(cut[i], cut[i+1]) for i in range(n)])

    # Mapper sur les bornes
    raw = mins + u * (maxs - mins)

    results = []
    for row in raw:
        total = row.sum()
        if total <= 0:
            continue
        row = row * 100.0 / total
        row = np.clip(row, mins, maxs)
        total = row.sum()
        row = row * 100.0 / total
        results.append({ids[i]: round(float(row[i]), 4) for i in range(k)})
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Enrichissement d'une formulation
# ─────────────────────────────────────────────────────────────────────────────

def _enrich(formulation: Dict[str, float]) -> Dict[str, Any]:
    """Ajoute les proprietes calculables a une formulation."""
    from data.ci_materials_db import estimate_cost_fcfa
    cost    = estimate_blend_cost(formulation)
    density = estimate_blend_density(formulation)
    # Cout FCFA pour 1 kg
    fcfa = 0.0
    for mat_id, pct in formulation.items():
        fcfa    += estimate_cost_fcfa(mat_id, pct)

    # HLB moyen pondere
    hlb_num = 0.0; hlb_den = 0.0
    for mat_id, pct in formulation.items():
        mat = MATERIALS.get(mat_id, {})
        if "HLB" in mat:
            hlb_num += mat["HLB"] * pct
            hlb_den += pct
    hlb_avg = round(hlb_num / hlb_den, 2) if hlb_den > 0 else None

    # Categories presentes
    categories = list(set(
        MATERIALS[m]["category"] for m in formulation if m in MATERIALS
    ))

    return {
        "composition":      formulation,
        "total_pct":        round(sum(formulation.values()), 4),
        "cost_index":       cost,
        "cost_fcfa_per_kg": fcfa,
        "density_est":      density,
        "HLB_avg":          hlb_avg,
        "categories":       categories,
        "n_components":     len(formulation),
    }


# ─────────────────────────────────────────────────────────────────────────────
# FONCTIONS PUBLIQUES
# ─────────────────────────────────────────────────────────────────────────────

def generate_formulation(
    components: List[ComponentConstraint],
    n_formulations: int = 5,
    method: str = "lhs",
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Genere n formulations respectant les contraintes min/max.

    Parameters
    ----------
    components : liste de {id, min, max, fixed}
    n_formulations : nombre de formulations a generer
    method : "random" | "lhs" (Latin Hypercube Sampling)
    seed : graine aleatoire pour reproducibilite

    Returns
    -------
    dict avec formulations, validation, statistiques
    """
    logger.info(f"generate_formulation — {len(components)} composants, n={n_formulations}, method={method}")

    # Validation des contraintes
    val = validate_constraints(components)
    if not val["valid"]:
        return {"status": "error", "errors": val["errors"]}

    rng = np.random.default_rng(seed)

    # Composants fixes
    fixed   = {c["id"]: c["min"] for c in components if c.get("fixed", False)}
    free    = [c for c in components if not c.get("fixed", False)]
    fixed_sum = sum(fixed.values())

    # Ajuster les composants libres
    free_adj = []
    for c in free:
        new_max = min(c.get("max", 100), 100 - fixed_sum - sum(f.get("min",0) for f in free if f["id"] != c["id"]))
        free_adj.append({**c, "max": max(c.get("min",0), new_max)})

    # Generation
    formulations_raw = []
    if method == "lhs":
        formulations_raw = _lhs_samples(free_adj, n_formulations, rng)
    else:
        for _ in range(n_formulations * 5):
            f = _random_in_simplex(free_adj, rng)
            if f:
                formulations_raw.append(f)
            if len(formulations_raw) >= n_formulations:
                break

    # Ajouter les fixes + enrichir
    results = []
    for f in formulations_raw[:n_formulations]:
        full = {**f, **fixed}
        total = sum(full.values())
        if abs(total - 100.0) > 0.5:
            full = normalize_formulation(full)
        results.append(_enrich(full))

    # Statistiques sur l'ensemble genere
    if results:
        costs   = [r["cost_index"] for r in results]
        density = [r["density_est"] for r in results]
        stats   = {
            "cost_min":    round(min(costs), 4),
            "cost_max":    round(max(costs), 4),
            "cost_mean":   round(float(np.mean(costs)), 4),
            "fcfa_mean":   round(float(np.mean([r["cost_fcfa_per_kg"] for r in results])), 3),
            "density_mean":round(float(np.mean(density)), 4),
        }
    else:
        stats = {}

    logger.info(f"  → {len(results)} formulations generees")
    return {
        "status":       "ok",
        "method":       method,
        "n_generated":  len(results),
        "formulations": results,
        "statistics":   stats,
        "validation":   val,
    }


def validate_formulation_full(formulation: Dict[str, float]) -> Dict[str, Any]:
    """
    Validation complete d'une formulation existante :
    compatibilite, somme, BD lookup.
    """
    issues = []
    total  = sum(formulation.values())
    if abs(total - 100.0) > 0.1:
        issues.append(f"Somme = {total:.2f}% (attendu 100%)")

    # Verifications chimiques
    materials_info = []
    for mat_id, pct in formulation.items():
        mat = MATERIALS.get(mat_id)
        if not mat:
            issues.append(f"'{mat_id}' non trouve dans la BD")
            continue
        lo, hi = mat.get("min_pct", 0), mat.get("max_pct", 100)
        status = "ok"
        if pct < lo:
            issues.append(f"{mat_id}: {pct}% < min recommande {lo}%")
            status = "low"
        elif pct > hi:
            issues.append(f"{mat_id}: {pct}% > max recommande {hi}%")
            status = "high"
        materials_info.append({
            "id": mat_id, "name": mat["name"],
            "category": mat["category"], "pct": pct, "status": status,
        })

    enriched = _enrich(formulation)
    return {
        "valid":    len(issues) == 0,
        "issues":   issues,
        "materials":materials_info,
        **enriched,
    }
