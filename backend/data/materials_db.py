"""
data/materials_db.py
====================
Base de donnees complete des matieres premieres chimiques.
Chaque materiau possede : proprietes physico-chimiques, compatibilites,
plages d'utilisation, cout relatif.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional

# ─────────────────────────────────────────────────────────────────────────────
# STRUCTURE D'UN MATERIAU
# ─────────────────────────────────────────────────────────────────────────────
# {
#   "name":          str     — nom complet
#   "category":      str     — categorie (polymer, surfactant, solvent, ...)
#   "cas":           str     — numero CAS
#   "molar_mass":    float   — masse molaire (g/mol)
#   "density":       float   — densite (g/cm3)
#   "solubility":    dict    — solubilite (g/L) dans differents solvants
#   "pKa":           float   — pKa si pertinent
#   "HLB":           float   — valeur HLB (tensioactifs)
#   "viscosity_ref": float   — viscosite de reference (mPa.s)
#   "melting_point": float   — point de fusion (°C)
#   "boiling_point": float   — point d'ebullition (°C)
#   "cost_rel":      float   — cout relatif (1=eau, echelle 1-100)
#   "min_pct":       float   — % min typique en formulation
#   "max_pct":       float   — % max typique en formulation
#   "function":      List[str] — fonctions dans une formulation
#   "compatible_with": List[str] — categories compatibles
#   "properties":    dict    — proprietes additionnelles
# }

MATERIALS: Dict[str, Dict[str, Any]] = {

    # ═══════════════════════════════════════════════════════════════════════
    # POLYMERES & EPAISSISSANTS
    # ═══════════════════════════════════════════════════════════════════════

    "HPMC_E5": {
        "name": "Hydroxypropyl Methylcellulose E5",
        "category": "polymer",
        "cas": "9004-65-3",
        "molar_mass": 86000.0,
        "density": 1.39,
        "solubility": {"water": 50.0, "ethanol": 2.0},
        "viscosity_ref": 5.0,
        "melting_point": 190.0,
        "cost_rel": 25.0,
        "min_pct": 0.5, "max_pct": 5.0,
        "function": ["thickener", "film_former", "binder", "stabilizer"],
        "compatible_with": ["solvent", "surfactant", "polymer", "api"],
        "properties": {"pH_stability": [3, 11], "gel_temp": 60},
    },
    "HPMC_K100M": {
        "name": "Hydroxypropyl Methylcellulose K100M",
        "category": "polymer",
        "cas": "9004-65-3",
        "molar_mass": 1300000.0,
        "density": 1.39,
        "solubility": {"water": 50.0},
        "viscosity_ref": 100000.0,
        "cost_rel": 35.0,
        "min_pct": 0.1, "max_pct": 3.0,
        "function": ["thickener", "controlled_release", "matrix_former"],
        "compatible_with": ["solvent", "api", "excipient"],
        "properties": {"pH_stability": [3, 11]},
    },
    "Carbopol_971P": {
        "name": "Carbopol 971P (Carbomer)",
        "category": "polymer",
        "cas": "9007-20-9",
        "molar_mass": 1000000.0,
        "density": 1.41,
        "solubility": {"water": 5.0},
        "viscosity_ref": 40000.0,
        "pKa": 6.0,
        "cost_rel": 40.0,
        "min_pct": 0.1, "max_pct": 2.0,
        "function": ["thickener", "gelling_agent", "bioadhesive"],
        "compatible_with": ["solvent", "surfactant", "api"],
        "properties": {"pH_optimal": [6.0, 9.0], "neutralization": "required"},
    },
    "PVA": {
        "name": "Polyvinyl Alcohol",
        "category": "polymer",
        "cas": "9002-89-5",
        "molar_mass": 85000.0,
        "density": 1.27,
        "solubility": {"water": 100.0},
        "viscosity_ref": 25.0,
        "cost_rel": 20.0,
        "min_pct": 1.0, "max_pct": 15.0,
        "function": ["film_former", "binder", "emulsifier"],
        "compatible_with": ["solvent", "polymer", "pigment"],
        "properties": {"crystallinity": 70},
    },
    "PVC": {
        "name": "Polyvinyl Chloride",
        "category": "polymer",
        "cas": "9002-86-2",
        "molar_mass": "null",
        "density": 1.38,
       "solubility": {
            "water": 0,
            "ethanol": 0,
            "acetone": "insoluble (gonfle légèrement)",
            "chloroform": "faible gonflement",
            "THF": "soluble",
            "cyclohexanone": "soluble"
        },
        "pKa": "null",
        "HLB": "null",
        "viscosity_ref": "null",
        "melting_point": 160,
        "boiling_point": "null",
        "cost_rel": 20,
        "min_pct": 10,
        "max_pct": 100,
        "function": [
            "matrice polymere",
            "materiau structurel",
            "barriere chimique",
            "isolant electrique",
            "support de formulation solide"
        ],
        "compatible_with": [
            "plasticizers",
            "stabilizers",
            "fillers",
            "lubricants",
            "pigments",
            "flame_retardants"
        ],
        "properties": {
            "type": "thermoplastique amorphe",
            "glass_transition_temp_C": 80,
            "thermal_stability": "faible sans stabilisant",
            "flammability": "auto-extinguible",
            "mechanical_behavior": "rigide (PVC-U) ou flexible (PVC plastifie)",
            "weather_resistance": "bonne avec additifs",
            "chemical_resistance": "excellente aux acides, bases et sels",
            "electrical_insulation": "excellente",
            "processability": [
            "extrusion",
            "injection",
            "calandrage"
            ],
            "notes": "Necessite stabilisants thermiques pour eviter degradation (HCl)"
        }
    },

    "PEG_4000": {
        "name": "Polyethylene Glycol 4000",
        "category": "polymer",
        "cas": "25322-68-3",
        "molar_mass": 4000.0,
        "density": 1.21,
        "solubility": {"water": 500.0, "ethanol": 200.0},
        "melting_point": 54.0,
        "cost_rel": 15.0,
        "min_pct": 1.0, "max_pct": 40.0,
        "function": ["plasticizer", "lubricant", "solubilizer", "base"],
        "compatible_with": ["polymer", "api", "wax", "excipient"],
        "properties": {},
    },
    "Xanthan_Gum": {
        "name": "Xanthan Gum",
        "category": "polymer",
        "cas": "11138-66-2",
        "molar_mass": 1000000.0,
        "density": 1.50,
        "solubility": {"water": 15.0},
        "viscosity_ref": 1200.0,
        "cost_rel": 30.0,
        "min_pct": 0.1, "max_pct": 1.0,
        "function": ["thickener", "stabilizer", "suspending_agent"],
        "compatible_with": ["solvent", "surfactant", "api"],
        "properties": {"pH_stability": [3, 9], "shear_thinning": True},
    },
    "CMC_7HF": {
        "name": "Carboxymethylcellulose Sodium 7HF",
        "category": "polymer",
        "cas": "9004-32-4",
        "molar_mass": 250000.0,
        "density": 1.60,
        "solubility": {"water": 25.0},
        "viscosity_ref": 2000.0,
        "cost_rel": 18.0,
        "min_pct": 0.1, "max_pct": 3.0,
        "function": ["thickener", "stabilizer", "binder"],
        "compatible_with": ["solvent", "api", "excipient"],
        "properties": {"pH_stability": [4, 10]},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # TENSIOACTIFS / SURFACTANTS
    # ═══════════════════════════════════════════════════════════════════════

    "Tween_80": {
        "name": "Polysorbate 80 (Tween 80)",
        "category": "surfactant",
        "cas": "9005-65-6",
        "molar_mass": 1310.0,
        "density": 1.08,
        "solubility": {"water": 500.0, "ethanol": 500.0},
        "HLB": 15.0,
        "cost_rel": 20.0,
        "min_pct": 0.1, "max_pct": 5.0,
        "function": ["emulsifier", "solubilizer", "wetting_agent"],
        "compatible_with": ["polymer", "solvent", "api", "oil"],
        "properties": {"CMC": 0.014, "type": "nonionic"},
    },
    "Span_80": {
        "name": "Sorbitan Monooleate (Span 80)",
        "category": "surfactant",
        "cas": "1338-43-8",
        "molar_mass": 428.6,
        "density": 0.99,
        "solubility": {"ethanol": 200.0, "oil": 500.0},
        "HLB": 4.3,
        "cost_rel": 18.0,
        "min_pct": 0.5, "max_pct": 10.0,
        "function": ["emulsifier", "w/o_emulsifier"],
        "compatible_with": ["oil", "polymer", "wax"],
        "properties": {"type": "nonionic"},
    },
    "SDS": {
        "name": "Sodium Dodecyl Sulfate (SDS/SLS)",
        "category": "surfactant",
        "cas": "151-21-3",
        "molar_mass": 288.4,
        "density": 1.01,
        "solubility": {"water": 100.0},
        "HLB": 40.0,
        "cost_rel": 8.0,
        "min_pct": 0.1, "max_pct": 3.0,
        "function": ["surfactant", "emulsifier", "solubilizer", "foaming"],
        "compatible_with": ["solvent", "polymer", "api"],
        "properties": {"CMC": 2.4, "type": "anionic"},
    },
    "CTAB": {
        "name": "Cetyltrimethylammonium Bromide",
        "category": "surfactant",
        "cas": "57-09-0",
        "molar_mass": 364.5,
        "density": 1.00,
        "solubility": {"water": 100.0},
        "HLB": 16.0,
        "cost_rel": 35.0,
        "min_pct": 0.01, "max_pct": 1.0,
        "function": ["emulsifier", "antimicrobial", "conditioner"],
        "compatible_with": ["solvent", "polymer"],
        "properties": {"CMC": 0.92, "type": "cationic"},
    },
    "Lecithin": {
        "name": "Soy Lecithin",
        "category": "surfactant",
        "cas": "8002-43-5",
        "molar_mass": 770.0,
        "density": 1.03,
        "solubility": {"ethanol": 300.0, "oil": 200.0},
        "HLB": 8.0,
        "cost_rel": 15.0,
        "min_pct": 0.5, "max_pct": 5.0,
        "function": ["emulsifier", "phospholipid", "biocompatible"],
        "compatible_with": ["oil", "polymer", "api"],
        "properties": {"type": "amphoteric"},
    },
    "Cremophor_EL": {
        "name": "Cremophor EL (PEG-35 Castor Oil)",
        "category": "surfactant",
        "cas": "61791-12-6",
        "molar_mass": 1630.0,
        "density": 1.05,
        "solubility": {"water": 1000.0, "ethanol": 1000.0},
        "HLB": 12.0,
        "cost_rel": 45.0,
        "min_pct": 1.0, "max_pct": 20.0,
        "function": ["solubilizer", "emulsifier"],
        "compatible_with": ["oil", "api", "solvent"],
        "properties": {"type": "nonionic"},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # SOLVANTS
    # ═══════════════════════════════════════════════════════════════════════

    "Water": {
        "name": "Purified Water",
        "category": "solvent",
        "cas": "7732-18-5",
        "molar_mass": 18.02,
        "density": 1.00,
        "solubility": {"water": 1000.0},
        "viscosity_ref": 1.0,
        "boiling_point": 100.0,
        "cost_rel": 1.0,
        "min_pct": 0.0, "max_pct": 99.0,
        "function": ["solvent", "vehicle", "diluent"],
        "compatible_with": ["polymer", "surfactant", "api", "excipient"],
        "properties": {"polarity": 9.0, "dielectric": 80.0},
    },
    "Ethanol_96": {
        "name": "Ethanol 96%",
        "category": "solvent",
        "cas": "64-17-5",
        "molar_mass": 46.07,
        "density": 0.789,
        "solubility": {"water": 1000.0},
        "viscosity_ref": 1.07,
        "boiling_point": 78.4,
        "cost_rel": 12.0,
        "min_pct": 1.0, "max_pct": 80.0,
        "function": ["solvent", "preservative", "antiseptic"],
        "compatible_with": ["polymer", "surfactant", "api"],
        "properties": {"polarity": 5.2, "flammable": True},
    },
    "Glycerol": {
        "name": "Glycerol (Glycerin)",
        "category": "solvent",
        "cas": "56-81-5",
        "molar_mass": 92.09,
        "density": 1.261,
        "solubility": {"water": 1000.0},
        "viscosity_ref": 1412.0,
        "boiling_point": 290.0,
        "cost_rel": 8.0,
        "min_pct": 1.0, "max_pct": 50.0,
        "function": ["humectant", "solvent", "plasticizer", "sweetener"],
        "compatible_with": ["polymer", "surfactant", "api", "water"],
        "properties": {"hygroscopic": True},
    },
    "Propylene_Glycol": {
        "name": "Propylene Glycol",
        "category": "solvent",
        "cas": "57-55-6",
        "molar_mass": 76.09,
        "density": 1.036,
        "solubility": {"water": 1000.0, "ethanol": 1000.0},
        "viscosity_ref": 56.0,
        "boiling_point": 188.2,
        "cost_rel": 10.0,
        "min_pct": 1.0, "max_pct": 50.0,
        "function": ["humectant", "solvent", "preservative", "plasticizer"],
        "compatible_with": ["polymer", "surfactant", "api", "water"],
        "properties": {},
    },
    "PEG_400": {
        "name": "Polyethylene Glycol 400",
        "category": "solvent",
        "cas": "25322-68-3",
        "molar_mass": 400.0,
        "density": 1.127,
        "solubility": {"water": 1000.0, "ethanol": 1000.0},
        "viscosity_ref": 90.0,
        "cost_rel": 12.0,
        "min_pct": 1.0, "max_pct": 60.0,
        "function": ["solvent", "plasticizer", "humectant"],
        "compatible_with": ["polymer", "api", "surfactant"],
        "properties": {},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # HUILES & CIRES
    # ═══════════════════════════════════════════════════════════════════════

    "Vaseline": {
        "name": "White Petrolatum (Vaseline)",
        "category": "oil",
        "cas": "8009-03-8",
        "density": 0.84,
        "solubility": {"ethanol": 5.0, "oil": 500.0},
        "cost_rel": 5.0,
        "min_pct": 1.0, "max_pct": 80.0,
        "function": ["emollient", "occlusive", "base", "lubricant"],
        "compatible_with": ["oil", "wax", "surfactant"],
        "properties": {"polarity": "nonpolar"},
    },
    "Beeswax": {
        "name": "Beeswax",
        "category": "wax",
        "cas": "8012-89-3",
        "density": 0.96,
        "melting_point": 63.0,
        "cost_rel": 30.0,
        "min_pct": 1.0, "max_pct": 20.0,
        "function": ["wax", "thickener", "emulsifier", "film_former"],
        "compatible_with": ["oil", "polymer", "surfactant"],
        "properties": {},
    },
    "Carnauba_Wax": {
        "name": "Carnauba Wax",
        "category": "wax",
        "cas": "8015-86-9",
        "density": 0.99,
        "melting_point": 85.0,
        "cost_rel": 50.0,
        "min_pct": 0.5, "max_pct": 10.0,
        "function": ["wax", "coating", "film_former", "lubricant"],
        "compatible_with": ["wax", "oil", "polymer"],
        "properties": {},
    },
    "Mineral_Oil": {
        "name": "Light Mineral Oil",
        "category": "oil",
        "cas": "8012-95-1",
        "density": 0.85,
        "viscosity_ref": 15.0,
        "cost_rel": 4.0,
        "min_pct": 1.0, "max_pct": 80.0,
        "function": ["emollient", "lubricant", "vehicle", "occlusive"],
        "compatible_with": ["oil", "wax", "surfactant"],
        "properties": {},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # EXCIPIENTS PHARMACEUTIQUES / ALIMENTAIRES
    # ═══════════════════════════════════════════════════════════════════════

    "MCC_102": {
        "name": "Microcrystalline Cellulose PH102",
        "category": "excipient",
        "cas": "9004-34-6",
        "density": 1.52,
        "solubility": {"water": 0.0},
        "cost_rel": 10.0,
        "min_pct": 5.0, "max_pct": 80.0,
        "function": ["filler", "binder", "disintegrant", "flow_agent"],
        "compatible_with": ["api", "excipient", "polymer"],
        "properties": {},
    },
    "Lactose_Mono": {
        "name": "Lactose Monohydrate",
        "category": "excipient",
        "cas": "64044-51-5",
        "molar_mass": 360.3,
        "density": 1.54,
        "solubility": {"water": 195.0},
        "cost_rel": 6.0,
        "min_pct": 5.0, "max_pct": 80.0,
        "function": ["filler", "diluent", "carrier"],
        "compatible_with": ["api", "excipient", "polymer"],
        "properties": {},
    },
    "Starch_Corn": {
        "name": "Corn Starch",
        "category": "excipient",
        "cas": "9005-25-8",
        "density": 1.50,
        "solubility": {"water": 0.0},
        "gelatinization_temp": 70.0,
        "cost_rel": 4.0,
        "min_pct": 3.0, "max_pct": 30.0,
        "function": ["binder", "disintegrant", "filler", "thickener"],
        "compatible_with": ["api", "excipient", "polymer"],
        "properties": {},
    },
    "Magnesium_Stearate": {
        "name": "Magnesium Stearate",
        "category": "excipient",
        "cas": "557-04-0",
        "molar_mass": 591.2,
        "density": 1.04,
        "cost_rel": 12.0,
        "min_pct": 0.1, "max_pct": 2.0,
        "function": ["lubricant", "anti_adherent", "glidant"],
        "compatible_with": ["api", "excipient"],
        "properties": {},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # CONSERVATEURS
    # ═══════════════════════════════════════════════════════════════════════

    "Benzalkonium_Chloride": {
        "name": "Benzalkonium Chloride",
        "category": "preservative",
        "cas": "8001-54-5",
        "molar_mass": 360.0,
        "density": 0.98,
        "solubility": {"water": 100.0, "ethanol": 100.0},
        "HLB": 30.0,
        "cost_rel": 25.0,
        "min_pct": 0.001, "max_pct": 0.1,
        "function": ["preservative", "antimicrobial", "surfactant"],
        "compatible_with": ["solvent", "polymer"],
        "properties": {"spectrum": "broad", "type": "cationic"},
    },
    "Phenoxyethanol": {
        "name": "Phenoxyethanol",
        "category": "preservative",
        "cas": "122-99-6",
        "molar_mass": 138.2,
        "density": 1.107,
        "solubility": {"water": 27.0, "ethanol": 1000.0},
        "cost_rel": 20.0,
        "min_pct": 0.5, "max_pct": 1.0,
        "function": ["preservative", "antimicrobial"],
        "compatible_with": ["solvent", "surfactant", "polymer"],
        "properties": {},
    },
    "Parabens_Mix": {
        "name": "Methylparaben + Propylparaben Mix",
        "category": "preservative",
        "cas": "99-76-3",
        "molar_mass": 152.2,
        "cost_rel": 12.0,
        "min_pct": 0.02, "max_pct": 0.5,
        "function": ["preservative", "antimicrobial"],
        "compatible_with": ["solvent", "polymer", "api"],
        "properties": {},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # ACTIFS / INGREDIENTS ACTIFS
    # ═══════════════════════════════════════════════════════════════════════

    "Ibuprofen": {
        "name": "Ibuprofen",
        "category": "api",
        "cas": "15687-27-1",
        "molar_mass": 206.3,
        "density": 1.03,
        "solubility": {"water": 0.021, "ethanol": 300.0},
        "pKa": 4.43,
        "melting_point": 76.0,
        "cost_rel": 40.0,
        "min_pct": 1.0, "max_pct": 20.0,
        "function": ["api", "anti_inflammatory", "analgesic"],
        "compatible_with": ["polymer", "excipient", "solvent"],
        "properties": {"BCS_class": 2, "log_P": 3.97},
    },
    "Caffeine": {
        "name": "Caffeine",
        "category": "api",
        "cas": "58-08-2",
        "molar_mass": 194.2,
        "density": 1.23,
        "solubility": {"water": 21.7, "ethanol": 15.0},
        "melting_point": 238.0,
        "cost_rel": 30.0,
        "min_pct": 0.1, "max_pct": 5.0,
        "function": ["api", "stimulant", "synergist"],
        "compatible_with": ["solvent", "excipient", "polymer"],
        "properties": {"BCS_class": 1, "log_P": -0.07},
    },
    "Vitamin_C": {
        "name": "Ascorbic Acid (Vitamin C)",
        "category": "api",
        "cas": "50-81-7",
        "molar_mass": 176.1,
        "density": 1.65,
        "solubility": {"water": 330.0, "ethanol": 20.0},
        "pKa": 4.17,
        "melting_point": 190.0,
        "cost_rel": 15.0,
        "min_pct": 0.1, "max_pct": 10.0,
        "function": ["api", "antioxidant", "vitamin"],
        "compatible_with": ["solvent", "excipient"],
        "properties": {"reducing_agent": True},
    },
    "Retinol": {
        "name": "Retinol (Vitamin A)",
        "category": "api",
        "cas": "68-26-8",
        "molar_mass": 286.5,
        "density": 0.95,
        "solubility": {"water": 0.0, "ethanol": 200.0, "oil": 300.0},
        "melting_point": 63.0,
        "cost_rel": 80.0,
        "min_pct": 0.01, "max_pct": 0.1,
        "function": ["api", "anti_aging", "vitamin"],
        "compatible_with": ["oil", "polymer", "surfactant"],
        "properties": {"light_sensitive": True, "log_P": 6.1},
    },
    "Hyaluronic_Acid": {
        "name": "Hyaluronic Acid (HA) 1.8MDa",
        "category": "api",
        "cas": "9004-61-9",
        "molar_mass": 1800000.0,
        "density": 1.50,
        "solubility": {"water": 10.0},
        "cost_rel": 90.0,
        "min_pct": 0.01, "max_pct": 2.0,
        "function": ["api", "humectant", "filler", "anti_aging"],
        "compatible_with": ["solvent", "polymer"],
        "properties": {"viscoelastic": True},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # PLASTIFIANTS & ADDITIFS
    # ═══════════════════════════════════════════════════════════════════════

    "Triethyl_Citrate": {
        "name": "Triethyl Citrate (TEC)",
        "category": "plasticizer",
        "cas": "77-93-0",
        "molar_mass": 276.3,
        "density": 1.135,
        "solubility": {"water": 65.0, "ethanol": 1000.0},
        "cost_rel": 20.0,
        "min_pct": 0.5, "max_pct": 30.0,
        "function": ["plasticizer", "solubilizer"],
        "compatible_with": ["polymer", "api"],
        "properties": {},
    },
    "Calcium Carbonate": {
        "name": "Calcium Carbonate",
        "category": "filler",
        "cas": "471-34-1",
        "molar_mass": 100.09,
        "density": 2.7,
        "solubility": {"water": 0.013},
        "pKa": "null",
        "HLB": "null",
        "viscosity_ref": "null",
        "melting_point": 825,
        "boiling_point": "null",
        "cost_rel": 5,
        "min_pct": 5,
        "max_pct": 70,
        "function": ["charge economique", "rigidite", "reduction cout"],
        "compatible_with": ["polymer"],
        "properties": {
        "type": "mineral",
        "particle_size": "variable",
        "reinforcement": "faible"
        }
    },
    "Talc": {
        "name": "Talc",
        "category": "filler",
        "cas": "14807-96-6",
        "molar_mass": 379.27,
        "density": 2.75,
        "solubility": {"water": 0},
        "cost_rel": 8,
        "min_pct": 5,
        "max_pct": 40,
        "function": ["rigidite", "stabilite thermique", "ameliore surface"],
        "compatible_with": ["polymer"],
        "properties": {
        "type": "mineral lamellaire",
        "reinforcement": "modere"
        }
    },
    "Silica": {
        "name": "Silica",
        "category": "filler",
        "cas": "7631-86-9",
        "molar_mass": 60.08,
        "density": 2.2,
        "solubility": {"water": 0},
        "cost_rel": 15,
        "min_pct": 1,
        "max_pct": 20,
        "function": ["renforcement", "controle viscosite"],
        "compatible_with": ["polymer"],
        "properties": {
        "type": "amorphe",
        "surface_area": "elevee"
        }
    },
    "Titanium_Dioxide": {
        "name": "Titanium Dioxide",
        "category": "pigment",
        "cas": "13463-67-7",
        "molar_mass": 79.9,
        "density": 4.23,
        "solubility": {"water": 0.0},
        "cost_rel": 15.0,
        "min_pct": 0.1, "max_pct": 5.0,
        "function": ["opacifier", "pigment", "UV_filter"],
        "compatible_with": ["polymer", "solvent", "excipient"],
        "properties": {"refractive_index": 2.7},
    },
    "Calcium Zinc Stabilizer": {
        "name": "Calcium Zinc Stabilizer",
        "category": "stabilizer",
        "cas": "null",
        "molar_mass": "null",
        "density": 1.8,
        "solubility": {"water": 0},
        "cost_rel": 30,
        "min_pct": 0.5,
        "max_pct": 5,
        "function": ["stabilisation thermique", "anti degradation"],
        "compatible_with": ["polymer"],
        "properties": {
            "type": "thermique",
            "application": "PVC"
        }
    },
    "Titanium Dioxide": {
        "name": "Titanium Dioxide",
        "category": "pigment",
        "cas": "13463-67-7",
        "molar_mass": 79.87,
        "density": 4.23,
        "solubility": {"water": 0},
        "cost_rel": 35,
        "min_pct": 1,
        "max_pct": 10,
        "function": ["coloration", "opacite", "UV resistance"],
        "compatible_with": ["polymer"],
        "properties": {
            "type": "pigment blanc",
            "indice_refraction": "eleve"
        }
    },
    "Stearic Acid": {
        "name": "Stearic Acid",
        "category": "lubricant",
        "cas": "57-11-4",
        "molar_mass": 284.48,
        "density": 0.94,
        "solubility": {"water": 0},
        "cost_rel": 12,
        "min_pct": 0.2,
        "max_pct": 2,
        "function": ["lubrification", "facilite transformation"],
        "compatible_with": ["polymer"],
        "properties": {
        "type": "acide gras",
        "role": "reduction friction"
        }
    },
    "Aluminum Hydroxide" :{
        "name": "Aluminum Hydroxide",
        "category": "flame_retardant",
        "cas": "21645-51-2",
        "molar_mass": 78.0,
        "density": 2.42,
        "solubility": {"water": 0},
        "cost_rel": 18,
        "min_pct": 10,
        "max_pct": 60,
        "function": ["retardateur de flamme", "securite incendie"],
        "compatible_with": ["polymer"],
        "properties": {
        "type": "mineral",
        "mode_action": "degagement eau"
        }
    },
    "Dioctyl_Phtalate": {
        "name": "Dioctyl Phthalate (DOP)",
        "category": "plasticizer",
        "cas": "117-81-7",
        "molar_mass": 390.56,
        "density": 0.99,
        "solubility": {"water": 0},
        "cost_rel": 25,
        "min_pct": 5,
        "max_pct": 50,
        "function": ["plasticisation", "flexibilite"],
        "compatible_with": ["polymer"],
        "properties": {
            "type": "phtalate",
            "effect": "assouplit PVC"
        }
    }
}


# ─────────────────────────────────────────────────────────────────────────────
# Fonctions d'accès
# ─────────────────────────────────────────────────────────────────────────────

def get_material(material_id: str) -> Optional[Dict[str, Any]]:
    """Retourne un materiau par son identifiant."""
    return MATERIALS.get(material_id)

def get_all_materials() -> Dict[str, Dict[str, Any]]:
    """Retourne toute la base de donnees."""
    return MATERIALS

def get_by_category(category: str) -> Dict[str, Dict[str, Any]]:
    """Filtre par categorie."""
    return {k: v for k, v in MATERIALS.items() if v.get("category") == category}

def get_categories() -> List[str]:
    """Retourne la liste des categories disponibles."""
    return sorted(set(v["category"] for v in MATERIALS.values()))

def get_material_ids() -> List[str]:
    """Retourne la liste de tous les identifiants."""
    return list(MATERIALS.keys())

def search_by_function(function: str) -> Dict[str, Dict[str, Any]]:
    """Recherche les materiaux par fonction."""
    return {k: v for k, v in MATERIALS.items()
            if function in v.get("function", [])}

def get_compatible(material_id: str) -> List[str]:
    """Retourne les IDs compatibles avec un materiau donne."""
    mat = MATERIALS.get(material_id, {})
    compatible_cats = mat.get("compatible_with", [])
    return [k for k, v in MATERIALS.items()
            if v.get("category") in compatible_cats and k != material_id]

def estimate_blend_cost(formulation: Dict[str, float]) -> float:
    """
    Estime le cout relatif d'une formulation.
    formulation = {material_id: percentage, ...}
    """
    total_cost = 0.0
    for mat_id, pct in formulation.items():
        mat = MATERIALS.get(mat_id, {})
        cost_rel = mat.get("cost_rel", 10.0)
        total_cost += (pct / 100.0) * cost_rel
    return round(total_cost, 4)

def estimate_blend_density(formulation: Dict[str, float]) -> float:
    """Estime la densite de la formulation par regle de melange."""
    inv_density_sum = 0.0
    for mat_id, pct in formulation.items():
        mat = MATERIALS.get(mat_id, {})
        density = mat.get("density", 1.0)
        inv_density_sum += (pct / 100.0) / density
    return round(1.0 / inv_density_sum, 4) if inv_density_sum > 0 else 1.0


# ── Fusion automatique avec les matières premières CI ────────────────────────
# Importer ici pour que get_all_materials() retourne MATERIALS + CI
try:
    from data.ci_materials_db import CI_MATERIALS
    MATERIALS.update(CI_MATERIALS)
except ImportError:
    pass
