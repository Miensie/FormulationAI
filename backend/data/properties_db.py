"""
data/properties_db.py
======================
Base de donnees des proprietes mesurables de formulations.
Inclut : methodes de mesure, plages cibles, unites, modeles ML pre-configures.
"""

from __future__ import annotations
from typing import Dict, Any, List

PROPERTIES: Dict[str, Dict[str, Any]] = {

    "viscosity": {
        "name":         "Viscosite dynamique",
        "unit":         "mPa.s",
        "range":        [1.0, 1000000.0],
        "log_scale":    True,
        "method":       "Rheometre / Viscosimetre Brookfield",
        "target_ranges": {
            "lotion":     [100, 5000],
            "gel":        [5000, 100000],
            "cream":      [20000, 200000],
            "serum":      [50, 2000],
            "suspension": [500, 10000],
            "syrup":      [300, 3000],
        },
        "key_factors":  ["polymer_conc", "temperature", "pH", "shear_rate"],
        "prediction_model": "random_forest",
    },
    "pH": {
        "name":         "pH",
        "unit":         "—",
        "range":        [1.0, 14.0],
        "log_scale":    False,
        "method":       "pH-metre calibre",
        "target_ranges": {
            "skin_care":  [4.5, 6.5],
            "oral":       [5.0, 8.0],
            "ophthalmic": [6.5, 8.5],
            "vaginal":    [3.8, 4.5],
        },
        "key_factors":  ["acid_base_ratio", "buffer_capacity", "CO2"],
        "prediction_model": "ridge",
    },
    "stability_index": {
        "name":         "Indice de stabilite",
        "unit":         "% (100=stable)",
        "range":        [0.0, 100.0],
        "log_scale":    False,
        "method":       "Stockage accelere 40°C/75%HR 3 mois",
        "target_ranges": {
            "excellent":  [90, 100],
            "good":       [75, 90],
            "acceptable": [60, 75],
        },
        "key_factors":  ["surfactant_HLB", "phase_ratio", "temperature", "antioxidant"],
        "prediction_model": "gradient_boosting",
    },
    "spreadability": {
        "name":         "Etalement / Texture",
        "unit":         "cm2/g",
        "range":        [1.0, 50.0],
        "log_scale":    False,
        "method":       "Test d'etalement (parallele plate)",
        "target_ranges": {
            "body_lotion": [15, 35],
            "face_cream":  [10, 25],
            "ointment":    [5, 15],
        },
        "key_factors":  ["emollient_type", "wax_ratio", "water_content"],
        "prediction_model": "random_forest",
    },
    "solubility_api": {
        "name":         "Solubilite de l'actif",
        "unit":         "mg/mL",
        "range":        [0.001, 1000.0],
        "log_scale":    True,
        "method":       "Equilibrium solubility (shake flask)",
        "key_factors":  ["solvent_ratio", "surfactant_conc", "pH", "temperature"],
        "prediction_model": "random_forest",
    },
    "zeta_potential": {
        "name":         "Potentiel Zeta",
        "unit":         "mV",
        "range":        [-100.0, 100.0],
        "log_scale":    False,
        "method":       "DLS / Diffusion de la lumiere",
        "target_ranges": {
            "stable_neg":  [-60, -30],
            "stable_pos":  [30, 60],
            "unstable":    [-30, 30],
        },
        "key_factors":  ["surfactant_type", "ionic_strength", "pH"],
        "prediction_model": "svr",
    },
    "release_rate_2h": {
        "name":         "Taux de liberation a 2h",
        "unit":         "%",
        "range":        [0.0, 100.0],
        "log_scale":    False,
        "method":       "Dissolution USP II (paddles)",
        "target_ranges": {
            "immediate":   [75, 100],
            "modified":    [20, 60],
            "sustained":   [10, 40],
        },
        "key_factors":  ["polymer_type", "polymer_conc", "solubility_api", "particle_size"],
        "prediction_model": "random_forest",
    },
    "cost_index": {
        "name":         "Indice de cout",
        "unit":         "UA/kg",
        "range":        [1.0, 100.0],
        "log_scale":    False,
        "method":       "Calcul economique",
        "key_factors":  ["raw_material_costs", "process_complexity"],
        "prediction_model": "linear",
    },
    "HLB_required": {
        "name":         "HLB optimal pour l'emulsion",
        "unit":         "—",
        "range":        [1.0, 20.0],
        "log_scale":    False,
        "method":       "Test de stabilite emulsion",
        "target_ranges": {
            "W/O_emulsion":   [3, 6],
            "O/W_emulsion":   [8, 18],
            "microemulsion":  [12, 18],
        },
        "key_factors":  ["oil_type", "water_fraction", "temperature"],
        "prediction_model": "ridge",
    },
    "drug_content_uniformity": {
        "name":         "Uniformite de teneur",
        "unit":         "% (CV)",
        "range":        [0.0, 30.0],
        "log_scale":    False,
        "method":       "USP <905>",
        "target_ranges": {
            "excellent":  [0, 2],
            "acceptable": [2, 6],
            "borderline": [6, 15],
        },
        "key_factors":  ["mixing_time", "particle_size", "density_match"],
        "prediction_model": "random_forest",
    },
    
    "glass_transition_temp": {
        "name":         "Temperature de transition vitreuse (Tg)",
        "unit":         "°C",
        "range":        [-100.0, 250.0],
        "log_scale":    False,
        "method":       "DSC (Differential Scanning Calorimetry)",
        "target_ranges": {
            "flexible_polymer": [-50, 20],
            "rigid_polymer":    [60, 150],
        },
        "key_factors":  ["polymer_type", "plasticizer_conc"],
        "prediction_model": "ridge",
    },

    "melting_point_mix": {
        "name":         "Point de fusion du systeme",
        "unit":         "°C",
        "range":        [0.0, 400.0],
        "log_scale":    False,
        "method":       "DSC",
        "key_factors":  ["component_ratio", "crystallinity"],
        "prediction_model": "random_forest",
    },

    "thermal_degradation_temp": {
        "name":         "Temperature de degradation thermique",
        "unit":         "°C",
        "range":        [50.0, 600.0],
        "log_scale":    False,
        "method":       "TGA (Thermogravimetric Analysis)",
        "target_ranges": {
            "low_stability":  [50, 200],
            "medium":         [200, 350],
            "high":           [350, 600],
        },
        "key_factors":  ["stabilizer_conc", "polymer_type"],
        "prediction_model": "gradient_boosting",
    },

    "mechanical_strength": {
        "name":         "Resistance mecanique",
        "unit":         "MPa",
        "range":        [0.1, 200.0],
        "log_scale":    False,
        "method":       "Essai traction (ISO 527)",
        "target_ranges": {
            "soft":   [0.1, 5],
            "medium": [5, 50],
            "rigid":  [50, 200],
        },
        "key_factors":  ["filler_content", "polymer_type", "plasticizer"],
        "prediction_model": "random_forest",
    },

    "elongation_at_break": {
        "name":         "Allongement a la rupture",
        "unit":         "%",
        "range":        [1.0, 1000.0],
        "log_scale":    True,
        "method":       "Essai traction",
        "target_ranges": {
            "brittle":   [1, 10],
            "ductile":   [50, 300],
            "elastic":   [300, 1000],
        },
        "key_factors":  ["plasticizer_conc", "polymer_type"],
        "prediction_model": "svr",
    },

    "water_absorption": {
        "name":         "Absorption d'eau",
        "unit":         "%",
        "range":        [0.0, 100.0],
        "log_scale":    False,
        "method":       "ISO 62",
        "target_ranges": {
            "low":   [0, 1],
            "medium":[1, 5],
            "high":  [5, 100],
        },
        "key_factors":  ["polymer_polarity", "filler_type"],
        "prediction_model": "random_forest",
    },

    "permeability": {
        "name":         "Permeabilite gaz/liquide",
        "unit":         "cm3·mm/m2·day·atm",
        "range":        [0.001, 1000.0],
        "log_scale":    True,
        "method":       "Test permeabilite ASTM",
        "target_ranges": {
            "barrier": [0.001, 1],
            "medium":  [1, 100],
            "high":    [100, 1000],
        },
        "key_factors":  ["crystallinity", "polymer_type"],
        "prediction_model": "gradient_boosting",
    },

    "surface_tension": {
        "name":         "Tension superficielle",
        "unit":         "mN/m",
        "range":        [10.0, 80.0],
        "log_scale":    False,
        "method":       "Tensiometre (Du Noüy)",
        "target_ranges": {
            "low":   [10, 30],
            "medium":[30, 50],
            "high":  [50, 80],
        },
        "key_factors":  ["surfactant_conc", "temperature"],
        "prediction_model": "ridge",
    },

    "particle_size": {
        "name":         "Taille des particules",
        "unit":         "µm",
        "range":        [0.001, 1000.0],
        "log_scale":    True,
        "method":       "DLS / Laser diffraction",
        "target_ranges": {
            "nano":   [0.001, 0.1],
            "micro":  [0.1, 100],
        },
        "key_factors":  ["mixing_speed", "surfactant"],
        "prediction_model": "random_forest",
    },

    "hardness": {
        "name":         "Durete",
        "unit":         "Shore A/D",
        "range":        [0, 100],
        "log_scale":    False,
        "method":       "Durometre",
        "target_ranges": {
            "soft":  [0, 40],
            "medium":[40, 70],
            "hard":  [70, 100],
        },
        "key_factors":  ["plasticizer", "filler"],
        "prediction_model": "random_forest",
    },

    "processability_index": {
        "name":         "Indice de transformabilite",
        "unit":         "—",
        "range":        [0.0, 100.0],
        "log_scale":    False,
        "method":       "Score empirique (extrusion/injection)",
        "target_ranges": {
            "poor": [0, 40],
            "good": [40, 70],
            "excellent": [70, 100],
        },
        "key_factors":  ["viscosity", "lubricant", "temperature"],
        "prediction_model": "gradient_boosting",
    },

    "aging_resistance": {
        "name":         "Resistance au vieillissement",
        "unit":         "% retention",
        "range":        [0.0, 100.0],
        "log_scale":    False,
        "method":       "UV + chaleur (accelerated aging)",
        "target_ranges": {
            "poor": [0, 50],
            "good": [50, 80],
            "excellent": [80, 100],
        },
        "key_factors":  ["antioxidant", "UV_stabilizer"],
        "prediction_model": "gradient_boosting",
    },

    "electrical_resistivity": {
        "name":         "Resistivite electrique",
        "unit":         "Ohm·cm",
        "range":        [1e-6, 1e16],
        "log_scale":    True,
        "method":       "Test ASTM D257",
        "target_ranges": {
            "conductive": [1e-6, 1e2],
            "semiconductive": [1e2, 1e6],
            "insulator": [1e6, 1e16],
        },
        "key_factors":  ["filler_type", "carbon_black"],
        "prediction_model": "svr",
    }
}


# ─────────────────────────────────────────────────────────────────────────────
# Fonctions d'acces
# ─────────────────────────────────────────────────────────────────────────────

def get_property(prop_id: str):
    return PROPERTIES.get(prop_id)

def get_all_properties():
    return PROPERTIES

def get_property_ids() -> List[str]:
    return list(PROPERTIES.keys())

def get_target_range(prop_id: str, application: str):
    prop = PROPERTIES.get(prop_id, {})
    ranges = prop.get("target_ranges", {})
    return ranges.get(application)

def get_key_factors(prop_id: str) -> List[str]:
    return PROPERTIES.get(prop_id, {}).get("key_factors", [])

def validate_property_value(prop_id: str, value: float) -> Dict[str, Any]:
    prop = PROPERTIES.get(prop_id, {})
    lo, hi = prop.get("range", [0, 1e9])
    in_range = lo <= value <= hi
    quality = "unknown"
    for label, (tlo, thi) in prop.get("target_ranges", {}).items():
        if tlo <= value <= thi:
            quality = label
            break
    return {"in_range": in_range, "quality": quality, "unit": prop.get("unit", "")}
