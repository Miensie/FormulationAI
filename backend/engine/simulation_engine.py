"""
engine/simulation_engine.py
=============================
Simulation virtuelle de formulations :
  - Simulation de viscosite vs temperature
  - Simulation de liberation (profils)
  - Test de stabilite accelee
  - Comparaison de formulations
"""

from __future__ import annotations
import numpy as np
from typing import List, Dict, Any
from loguru import logger
from data.materials_db import MATERIALS


def simulate_viscosity_vs_temperature(
    formulation: Dict[str, float],
    T_range: List[float],
    ref_viscosity: float = 1000.0,
) -> Dict[str, Any]:
    """
    Simule la viscosite en fonction de la temperature
    selon une loi d'Arrhenius modifiee.
    """
    logger.debug("simulate_viscosity_vs_temperature")
    T  = np.array(T_range, dtype=float)
    Ea = 25000.0  # J/mol approximatif pour systemes aqueux

    # Facteur de contribution des polymeres
    polymer_pct = sum(
        pct for mid, pct in formulation.items()
        if MATERIALS.get(mid, {}).get("category") == "polymer"
    )
    alpha = 1.0 + polymer_pct * 0.15

    # Viscosite via Arrhenius : eta(T) = eta_ref * exp(Ea/R * (1/T - 1/T_ref))
    R    = 8.314
    T_K  = T + 273.15
    T_ref = 298.15
    eta  = ref_viscosity * alpha * np.exp(Ea / R * (1/T_K - 1/T_ref))

    return {
        "model":        "viscosity_temperature",
        "temperature":  T.tolist(),
        "viscosity":    np.round(eta, 2).tolist(),
        "ref_viscosity":ref_viscosity,
        "polymer_pct":  round(polymer_pct, 2),
    }


def simulate_release_profile(
    formulation: Dict[str, float],
    time_hours: List[float],
    api_id: str = "Ibuprofen",
    dissolution_medium: str = "PBS_pH6.8",
) -> Dict[str, Any]:
    """
    Simule un profil de liberation in vitro.
    Modeles : Higuchi, Korsmeyer-Peppas, premier ordre.
    """
    logger.debug(f"simulate_release_profile — api={api_id}")
    t   = np.array(time_hours, dtype=float)
    api = MATERIALS.get(api_id, {})

    # Solubilite de l'API
    solubility  = api.get("solubility", {}).get("water", 10.0)
    log_P       = api.get("properties", {}).get("log_P", 2.0)

    # Teneur en polymere retardateur
    polymer_pct = sum(
        pct for mid, pct in formulation.items()
        if "controlled_release" in MATERIALS.get(mid, {}).get("function", [])
    )

    # Parametres Korsmeyer-Peppas : Q(t) = k*t^n
    if polymer_pct > 0:
        k_release = max(0.05, min(0.5, solubility / (polymer_pct * 10 * (1 + abs(log_P)))))
        n_exp     = min(1.0, 0.45 + polymer_pct * 0.05)
    else:
        k_release = min(1.0, solubility / 20.0)
        n_exp     = 0.5  # Higuchi

    Q_pct = np.clip(100.0 * k_release * np.power(t + 1e-9, n_exp), 0, 100)
    Q_pct = np.where(t == 0, 0, Q_pct)

    return {
        "model":             "korsmeyer_peppas",
        "time_hours":        t.tolist(),
        "release_pct":       np.round(Q_pct, 2).tolist(),
        "api":               api_id,
        "medium":            dissolution_medium,
        "k_release":         round(float(k_release), 4),
        "n_exponent":        round(float(n_exp), 4),
        "release_type":      ("Fickian" if n_exp <= 0.5 else
                              "anomalous" if n_exp < 1.0 else "case_II"),
        "t80_hours":         round(float(((0.80/k_release)**(1/n_exp)) - 1e-9), 2),
    }


def simulate_stability(
    formulation: Dict[str, float],
    time_months: List[float],
    temperature_C: float = 25.0,
    humidity_pct: float = 60.0,
) -> Dict[str, Any]:
    """
    Simule la stabilite de la formulation dans le temps.
    Modele de degradation du premier ordre.
    """
    logger.debug("simulate_stability")
    t = np.array(time_months, dtype=float)

    # Constante de degradation = f(T, HR, composition)
    k_base = 0.01  # mois-1

    # Contribution de la temperature via Arrhenius
    Ea = 70000.0; R = 8.314
    T_K = temperature_C + 273.15; T_ref = 298.15
    k_T = k_base * np.exp(Ea / R * (1/T_ref - 1/T_K))

    # Contribution de l'humidite
    k_H = k_T * (1 + humidity_pct / 200.0)

    # Antioxydants protegers
    has_antioxidant = any(
        "antioxidant" in MATERIALS.get(m, {}).get("function", [])
        for m in formulation
    )
    if has_antioxidant:
        k_H *= 0.5

    stability = 100.0 * np.exp(-k_H * t)
    degradation = 100.0 - stability

    return {
        "model":           "first_order_degradation",
        "time_months":     t.tolist(),
        "stability_pct":   np.round(stability, 2).tolist(),
        "degradation_pct": np.round(degradation, 2).tolist(),
        "temperature_C":   temperature_C,
        "humidity_pct":    humidity_pct,
        "k_degradation":   round(float(k_H), 6),
        "t90_months":      round(float(-np.log(0.9) / k_H), 2),
        "t_shelf_life":    round(float(-np.log(0.95) / k_H), 2),
        "antioxidant_effect": has_antioxidant,
    }


def compare_formulations(
    formulations: List[Dict[str, float]],
    labels: List[str],
    properties_to_compare: List[str],
) -> Dict[str, Any]:
    """
    Compare plusieurs formulations sur des proprietes calculables.
    """
    from data.materials_db import estimate_blend_cost, estimate_blend_density
    logger.debug(f"compare_formulations — {len(formulations)} formulations")

    results = []
    for i, (form, label) in enumerate(zip(formulations, labels)):
        props = {"label": label}

        if "cost" in properties_to_compare:
            props["cost_index"] = estimate_blend_cost(form)
        if "density" in properties_to_compare:
            props["density"] = estimate_blend_density(form)
        if "HLB" in properties_to_compare:
            hlb_n = hlb_d = 0.0
            for mid, pct in form.items():
                mat = MATERIALS.get(mid, {})
                if "HLB" in mat:
                    hlb_n += mat["HLB"] * pct; hlb_d += pct
            props["HLB"] = round(hlb_n / hlb_d, 2) if hlb_d > 0 else None
        if "n_components" in properties_to_compare:
            props["n_components"] = len(form)

        results.append(props)

    # Identifier le meilleur sur chaque critere
    best = {}
    for prop in properties_to_compare:
        vals = [(r["label"], r.get(prop)) for r in results if r.get(prop) is not None]
        if vals:
            if prop == "cost_index":
                best[prop] = min(vals, key=lambda x: x[1])[0]
            else:
                best[prop] = max(vals, key=lambda x: x[1])[0]

    return {
        "status":      "ok",
        "n_compared":  len(formulations),
        "results":     results,
        "best_per_property": best,
    }
