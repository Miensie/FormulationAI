"""
data/ci_materials_db.py
========================
Base de donnees des matieres premieres locales d'Afrique de l'Ouest
et particulierement de Cote d'Ivoire.

Sources : filiere palmier (Palmci/PHCI), filiere cacao (CCC/Saco),
filiere anacarde (CONSEIL COTON), marche local (CDCI Abidjan),
travaux CNRA et CSRS Abidjan, litterature scientifique africaine.

Cout en FCFA/kg (prix marche Abidjan 2024, indicatifs).
"""

from __future__ import annotations
from typing import Dict, Any

CI_MATERIALS: Dict[str, Dict[str, Any]] = {

    # ═══════════════════════════════════════════════════════════════════════
    # HUILES VEGETALES LOCALES
    # ═══════════════════════════════════════════════════════════════════════

    "Huile_Palme_Brute": {
        "name":         "Huile de Palme Brute (CPO)",
        "name_local":   "Huile de palme",
        "category":     "oil",
        "origin":       "Cote d'Ivoire (Sassandra, San Pedro, Aboisso)",
        "cas":          "8002-75-3",
        "density":      0.891,
        "melting_point": 35.0,
        "iodine_value": 53.0,
        "saponification_value": 199.0,
        "fatty_acids": {
            "palmitic_C16:0":  44.0,
            "oleic_C18:1":     39.0,
            "linoleic_C18:2":   10.0,
            "stearic_C18:0":    5.0,
        },
        "cost_FCFA_kg":   500.0,
        "cost_rel":       4.0,
        "min_pct":        1.0,
        "max_pct":        80.0,
        "function":       ["emollient", "base", "soap_base", "lubricant", "vehicle"],
        "compatible_with":["oil", "wax", "surfactant", "polymer"],
        "properties":     {
            "color":          "rouge-orange",
            "carotene_ppm":   500,
            "tocopherol_ppm": 800,
            "free_fatty_acid_max": 5.0,
            "peroxide_value_max":  10,
        },
        "applications":   ["savonnerie", "cosmetique", "alimentaire", "biodiesel"],
        "_source":        "Palmci CI / CNRA Abidjan",
    },

    "Huile_Palme_RBD": {
        "name":         "Huile de Palme Raffinee Blanchie Deodorisee (RBD)",
        "name_local":   "Huile de palme raffinee",
        "category":     "oil",
        "origin":       "Cote d'Ivoire",
        "cas":          "8002-75-3",
        "density":      0.889,
        "melting_point": 36.0,
        "iodine_value": 52.0,
        "saponification_value": 200.0,
        "cost_FCFA_kg":   750.0,
        "cost_rel":       6.0,
        "min_pct":        1.0,
        "max_pct":        80.0,
        "function":       ["emollient", "base", "lubricant", "emulsifier"],
        "compatible_with":["oil", "wax", "surfactant", "polymer"],
        "properties":     {
            "color":     "blanc-jaune pale",
            "odor":      "neutre",
            "FFA_max":   0.1,
        },
        "applications":   ["cosmetique", "savonnerie", "pharmaceutique", "alimentaire"],
        "_source":        "PHCI / Blohorn CI",
    },

    "Huile_Palmiste": {
        "name":         "Huile de Palmiste (PKO - Palm Kernel Oil)",
        "name_local":   "Huile de palmiste",
        "category":     "oil",
        "origin":       "Cote d'Ivoire",
        "cas":          "8023-79-8",
        "density":      0.914,
        "melting_point": 28.0,
        "iodine_value": 19.0,
        "saponification_value": 247.0,
        "fatty_acids": {
            "lauric_C12:0":   48.0,
            "myristic_C14:0": 16.0,
            "palmitic_C16:0": 8.0,
            "oleic_C18:1":    15.0,
        },
        "cost_FCFA_kg":   600.0,
        "cost_rel":       5.0,
        "min_pct":        1.0,
        "max_pct":        80.0,
        "function":       ["emollient", "soap_base", "foaming_agent", "base"],
        "compatible_with":["oil", "wax", "surfactant"],
        "properties":     {
            "color":   "blanc-jaune",
            "odor":    "caracteristique",
            "note":    "Riche en acide laurique — excellent pouvoir moussant en savonnerie",
        },
        "applications":   ["savonnerie (mousse riche)", "cosmetique", "alimentaire"],
        "_source":        "Palmci / marche CDCI Abidjan",
    },

    "Beurre_Karite": {
        "name":         "Beurre de Karite Non Raffine",
        "name_local":   "Beurre de karite (sihi en dioula)",
        "category":     "oil",
        "origin":       "Zone nord CI (Korhogo, Ferkessedougou), Burkina, Mali",
        "cas":          "91080-23-8",
        "density":      0.863,
        "melting_point": 36.0,
        "iodine_value": 58.0,
        "saponification_value": 183.0,
        "unsaponifiable_pct": 7.5,
        "fatty_acids": {
            "stearic_C18:0":  40.0,
            "oleic_C18:1":    45.0,
            "palmitic_C16:0": 5.0,
            "linoleic_C18:2": 7.0,
        },
        "cost_FCFA_kg":   3500.0,
        "cost_rel":       28.0,
        "min_pct":        1.0,
        "max_pct":        30.0,
        "function":       ["emollient", "moisturizer", "skin_protector",
                           "anti_inflammatory", "base", "wax_substitute"],
        "compatible_with":["oil", "wax", "polymer", "surfactant", "api"],
        "properties":     {
            "color":            "creme-ivoire",
            "odor":             "noix doux",
            "triterpene_pct":   5.0,
            "lupeol":           True,
            "anti_UV":          True,
            "cicatrisant":      True,
            "note":             "Fraction insaponifiable elevee — proprietes cosmetiques premium",
        },
        "applications":   ["creme corps", "baume levres", "cosmetique capillaire",
                           "beurre corporel", "savon surgras"],
        "_source":        "Marche Korhogo / cooperatives femmes nord CI",
    },

    "Beurre_Karite_Raffine": {
        "name":         "Beurre de Karite Raffine (Grade A)",
        "name_local":   "Karite raffine",
        "category":     "oil",
        "origin":       "Zone nord CI / Burkina Faso",
        "density":      0.860,
        "melting_point": 38.0,
        "cost_FCFA_kg":   5000.0,
        "cost_rel":       40.0,
        "min_pct":        0.5,
        "max_pct":        25.0,
        "function":       ["emollient", "moisturizer", "skin_protector", "base"],
        "compatible_with":["oil", "wax", "polymer"],
        "properties":     {"color": "blanc", "odor": "neutre", "FFA_max": 0.5},
        "applications":   ["cosmetique haut de gamme", "pharmaceutique"],
        "_source":        "Exportateurs CI / APEX-CI",
    },

    "Huile_Coco_Vierge": {
        "name":         "Huile de Noix de Coco Vierge (VCO)",
        "name_local":   "Huile de coco",
        "category":     "oil",
        "origin":       "Zone cotiere CI (Grand-Bassam, Jacqueville, San-Pedro)",
        "cas":          "8001-31-8",
        "density":      0.925,
        "melting_point": 24.0,
        "iodine_value": 10.0,
        "saponification_value": 256.0,
        "fatty_acids": {
            "lauric_C12:0":   47.0,
            "myristic_C14:0": 18.0,
            "caprylic_C8:0":   8.0,
            "capric_C10:0":    7.0,
            "palmitic_C16:0":  9.0,
        },
        "cost_FCFA_kg":   3000.0,
        "cost_rel":       24.0,
        "min_pct":        1.0,
        "max_pct":        80.0,
        "function":       ["emollient", "moisturizer", "antimicrobial",
                           "soap_base", "hair_conditioner"],
        "compatible_with":["oil", "wax", "surfactant", "polymer"],
        "properties":     {
            "color":        "blanc cristallin (< 25°C) / liquide clair",
            "odor":         "coco doux",
            "MCT_pct":      62,
            "antimicrobial":True,
            "note":         "Riche en acide laurique — proprietes antimicrobiennes naturelles",
        },
        "applications":   ["capillaire", "soin corps", "savonnerie",
                           "cosmetique naturel", "huile de massage"],
        "_source":        "Producteurs locaux Grand-Bassam / CNRA",
    },

    "Huile_Anacarde": {
        "name":         "Huile de Noix de Cajou (Cashew Nut Shell Liquid - CNSL)",
        "name_local":   "Huile de cajou",
        "category":     "oil",
        "origin":       "Zone nord CI (Bouake, Korhogo) — 1er producteur mondial",
        "density":      0.950,
        "iodine_value": 200.0,
        "cost_FCFA_kg":   1500.0,
        "cost_rel":       12.0,
        "min_pct":        1.0,
        "max_pct":        30.0,
        "function":       ["lubricant", "resin_former", "anti_rust", "antimicrobial"],
        "compatible_with":["oil", "polymer"],
        "properties":     {
            "color":       "brun-rouge",
            "cardanol_pct": 90,
            "irritant":    True,
            "note":        "Usage industriel principalement — irritant cutane a eviter en cosmetique direct",
        },
        "applications":   ["lubrifiants industriels", "peintures", "resines", "traitement bois"],
        "_source":        "Conseil Coton-Anacarde CI / FIRCA",
    },

    "Beurre_Cacao": {
        "name":         "Beurre de Cacao (grade cosmetique)",
        "name_local":   "Beurre de cacao",
        "category":     "oil",
        "origin":       "CI (1er producteur mondial) — Daloa, Soubre, Aboisso",
        "cas":          "8002-31-1",
        "density":      0.964,
        "melting_point": 34.0,
        "iodine_value": 34.0,
        "saponification_value": 192.0,
        "fatty_acids": {
            "stearic_C18:0":  35.0,
            "oleic_C18:1":    35.0,
            "palmitic_C16:0": 25.0,
            "linoleic_C18:2":  3.0,
        },
        "cost_FCFA_kg":   5000.0,
        "cost_rel":       40.0,
        "min_pct":        1.0,
        "max_pct":        40.0,
        "function":       ["emollient", "moisturizer", "film_former",
                           "base", "skin_softener", "antioxidant"],
        "compatible_with":["oil", "wax", "polymer", "api"],
        "properties":     {
            "color":       "jaune pale a blanc",
            "odor":        "cacao caracteristique",
            "polyphenols": True,
            "anti_UV":     True,
            "note":        "Point de fusion proche temperature cutanee — sensation fondante premium",
        },
        "applications":   ["baume a levres", "creme corps", "chocolat",
                           "savon surgras", "cosmetique premium"],
        "_source":        "SACO CI / CSRS Abidjan / CCC",
    },

    "Huile_Avocat_CI": {
        "name":         "Huile d'Avocat Pressee a Froid (grade cosmetique)",
        "name_local":   "Huile d'avocat",
        "category":     "oil",
        "origin":       "Zone ouest CI (Man, Daloa) / Plateau de Korhogo",
        "cas":          "8024-32-6",
        "density":      0.912,
        "iodine_value": 85.0,
        "saponification_value": 188.0,
        "fatty_acids": {
            "oleic_C18:1":    66.0,
            "palmitic_C16:0": 16.0,
            "linoleic_C18:2": 12.0,
            "palmitoleic_C16:1": 3.0,
        },
        "cost_FCFA_kg":   8000.0,
        "cost_rel":       65.0,
        "min_pct":        1.0,
        "max_pct":        20.0,
        "function":       ["emollient", "moisturizer", "penetrating_oil",
                           "anti_aging", "hair_conditioner"],
        "compatible_with":["oil", "polymer", "api"],
        "properties":     {
            "color":          "vert-jaune",
            "vitamin_A":      True,
            "vitamin_D":      True,
            "vitamin_E":      True,
            "lecithin":       True,
            "penetration":    "profonde",
            "note":           "Excellent agent penetrant — vitamine A regenerante",
        },
        "applications":   ["anti-age", "soin capillaire", "creme hydratante", "cosmetique premium"],
        "_source":        "Producteurs ouest CI / ANADER",
    },

    "Huile_Sesame_CI": {
        "name":         "Huile de Sesame Pressee a Froid",
        "name_local":   "Huile de sesame (wanan en dioula)",
        "category":     "oil",
        "origin":       "Zone nord CI (Korhogo, Odienne)",
        "cas":          "8008-74-0",
        "density":      0.917,
        "iodine_value": 108.0,
        "saponification_value": 190.0,
        "cost_FCFA_kg":   6000.0,
        "cost_rel":       48.0,
        "min_pct":        1.0,
        "max_pct":        25.0,
        "function":       ["emollient", "moisturizer", "antioxidant",
                           "UV_filter", "anti_inflammatory"],
        "compatible_with":["oil", "polymer", "api"],
        "properties":     {
            "sesamol":  True,
            "sesamolin":True,
            "UV_filter_index": 6,
            "note":     "Sesaminol — antioxydant naturel puissant, leger filtre UV",
        },
        "applications":   ["soin solaire", "massage", "cosmetique ayurvedique adaptee CI"],
        "_source":        "Marche Korhogo / cooperatives nord CI",
    },

    "Huile_Baobab": {
        "name":         "Huile de Baobab (Adansonia digitata)",
        "name_local":   "Huile de pain de singe",
        "category":     "oil",
        "origin":       "Zone soudanienne CI (nord) / Sahel",
        "cas":          "223749-11-9",
        "density":      0.910,
        "iodine_value": 72.0,
        "cost_FCFA_kg":   12000.0,
        "cost_rel":       96.0,
        "min_pct":        0.5,
        "max_pct":        10.0,
        "function":       ["emollient", "moisturizer", "anti_aging",
                           "skin_regenerator", "anti_inflammatory"],
        "compatible_with":["oil", "polymer", "api"],
        "properties":     {
            "omega369":    True,
            "vitamin_A_C_E":True,
            "absorption":  "rapide",
            "note":        "Profil en acides gras equilibre omega 3-6-9 rare",
        },
        "applications":   ["serum anti-age", "cosmetique premium", "soin peau seche"],
        "_source":        "Collecteurs zone nord CI / Afrique subsaharienne",
    },

    # ═══════════════════════════════════════════════════════════════════════
    # CIRES & EXTRAITS LOCAUX
    # ═══════════════════════════════════════════════════════════════════════

    "Cire_Abeille_CI": {
        "name":         "Cire d'Abeille Naturelle de Cote d'Ivoire",
        "name_local":   "Cire d'abeille",
        "category":     "wax",
        "origin":       "CI (apiculture traditionnelle : Bondoukou, Man, Seguela)",
        "cas":          "8012-89-3",
        "density":      0.960,
        "melting_point": 63.0,
        "iodine_value": 10.0,
        "saponification_value": 93.0,
        "cost_FCFA_kg":   5000.0,
        "cost_rel":       40.0,
        "min_pct":        1.0,
        "max_pct":        20.0,
        "function":       ["wax", "thickener", "emulsifier",
                           "film_former", "stabilizer", "occlusive"],
        "compatible_with":["oil", "polymer", "surfactant"],
        "properties":     {
            "color":     "jaune doree",
            "odor":      "miel characteristique",
            "note":      "Cire naturelle CI — structure de baume et stick",
        },
        "applications":   ["baume levres", "creme", "stick deodorant", "cosmetique solide"],
        "_source":        "Apiculteurs CI / FIRCA",
    },

    "Gomme_Arabique_CI": {
        "name":         "Gomme Arabique (Acacia senegal)",
        "name_local":   "Gomme arabique",
        "category":     "polymer",
        "origin":       "Zone sahelienne CI / Mali / Burkina / Senegal",
        "cas":          "9000-01-5",
        "density":      1.35,
        "solubility":   {"water": 500.0},
        "cost_FCFA_kg":   2500.0,
        "cost_rel":       20.0,
        "min_pct":        0.5,
        "max_pct":        40.0,
        "function":       ["binder", "emulsifier", "stabilizer",
                           "thickener", "film_former", "suspending_agent"],
        "compatible_with":["solvent", "api", "excipient", "surfactant"],
        "properties":     {
            "pH_stability": [3, 9],
            "E_number":     "E414",
            "biodegradable":True,
            "note":         "100% naturel, Halal/Kosher, biodegradable — atout marche africain",
        },
        "applications":   ["alimentaire (liant)", "pharmaceutique", "cosmetique naturel",
                           "encres", "confiserie"],
        "_source":        "Marche Abidjan Adjame / importation zone sahel",
    },

    "Poudre_Moringa": {
        "name":         "Poudre de Feuilles de Moringa (Moringa oleifera)",
        "name_local":   "Moringa / nebeday",
        "category":     "api",
        "origin":       "Nord CI / zone sahelienne",
        "density":      0.55,
        "solubility":   {"water": 5.0},
        "cost_FCFA_kg":   3000.0,
        "cost_rel":       24.0,
        "min_pct":        0.1,
        "max_pct":        5.0,
        "function":       ["api", "antioxidant", "anti_inflammatory",
                           "antimicrobial", "superfood", "pigment"],
        "compatible_with":["solvent", "polymer", "excipient"],
        "properties":     {
            "vitamin_C":    True,
            "vitamin_A":    True,
            "iron_mg_100g": 28.0,
            "protein_pct":  27.0,
            "chlorophyll":  True,
            "color":        "vert vif",
            "note":         "Actif cosmeto-alimentaire en plein essor CI/Afrique",
        },
        "applications":   ["cosmetique naturel", "complement alimentaire",
                           "savon scrub", "masque visage"],
        "_source":        "Producteurs nord CI / ANADER Korhogo",
    },

    "Argile_Kaolin_CI": {
        "name":         "Argile Kaolin Blanc de Cote d'Ivoire",
        "name_local":   "Argile blanche / terre d'abidjan",
        "category":     "excipient",
        "origin":       "Gisements CI (region de Man, Divo)",
        "cas":          "1332-58-7",
        "density":      2.60,
        "solubility":   {"water": 0.0},
        "cost_FCFA_kg":   500.0,
        "cost_rel":       4.0,
        "min_pct":        1.0,
        "max_pct":        50.0,
        "function":       ["absorbent", "opacifier", "filler",
                           "anti_caking", "scrub", "detoxifying"],
        "compatible_with":["polymer", "solvent", "api", "excipient"],
        "properties":     {
            "pH":          7.0,
            "whiteness":   85,
            "particle_um": 2.0,
            "Al2O3_pct":  39.0,
            "SiO2_pct":   47.0,
            "note":        "Matiere premiere locale tres accessible — usage cosmetique et pharmaceutique",
        },
        "applications":   ["masque argile", "poudre talc substitute",
                           "savon", "produit pharmaceutique"],
        "_source":        "SODEMI / mines CI",
    },

    "Aloe_Vera_Gel_CI": {
        "name":         "Gel d'Aloe Vera (Aloe barbadensis Miller)",
        "name_local":   "Aloe vera / Pita",
        "category":     "api",
        "origin":       "Culture CI (zone cotiere et centre)",
        "density":      1.01,
        "solubility":   {"water": 1000.0},
        "pH":           4.5,
        "cost_FCFA_kg":   2000.0,
        "cost_rel":       16.0,
        "min_pct":        1.0,
        "max_pct":        80.0,
        "function":       ["moisturizer", "anti_inflammatory", "healing",
                           "soothing", "antimicrobial", "vehicle"],
        "compatible_with":["solvent", "polymer", "api", "surfactant"],
        "properties":     {
            "acemannan":      True,
            "anthraquinones": True,
            "vitamin_C_E":    True,
            "pH_stability":   [3, 7],
            "note":           "Cicatrisant et anti-inflammatoire naturel — usage traditionnel CI",
        },
        "applications":   ["apres-soleil", "soin peau irritee", "gel coiffant naturel",
                           "cosmetique naturel", "soin brulures"],
        "_source":        "Producteurs CI / medecine traditionnelle",
    },

    "Neem_Huile": {
        "name":         "Huile de Neem (Azadirachta indica)",
        "name_local":   "Huile de neem / margousier",
        "category":     "oil",
        "origin":       "Zone nord CI (Korhogo) / Sahel",
        "cas":          "8002-65-1",
        "density":      0.921,
        "iodine_value": 68.0,
        "cost_FCFA_kg":   4000.0,
        "cost_rel":       32.0,
        "min_pct":        0.5,
        "max_pct":        10.0,
        "function":       ["antimicrobial", "antifungal", "anti_inflammatory",
                           "pesticide", "repellent", "api"],
        "compatible_with":["oil", "polymer"],
        "properties":     {
            "azadirachtin":   True,
            "odor":           "forte caracteristique (diluer!)",
            "anti_parasite":  True,
            "note":           "Usage limite en cosmetique en raison de l'odeur — diluer a max 2%",
        },
        "applications":   ["shampoing anti-pelliculaire", "savon medicinal",
                           "produit veterinaire", "pesticide naturel"],
        "_source":        "Marche Adjame Abidjan / nord CI",
    },

    "Hibiscus_Extrait": {
        "name":         "Extrait de Bissap / Hibiscus (Hibiscus sabdariffa)",
        "name_local":   "Bissap / oseille de Guinee",
        "category":     "api",
        "origin":       "Zone nord CI / zone sahelienne",
        "density":      1.05,
        "cost_FCFA_kg":   8000.0,
        "cost_rel":       65.0,
        "min_pct":        0.1,
        "max_pct":        5.0,
        "function":       ["antioxidant", "pigment", "anti_aging",
                           "astringent", "brightening"],
        "compatible_with":["solvent", "polymer", "api"],
        "properties":     {
            "anthocyanins": True,
            "vitamin_C":    True,
            "AHA":          True,
            "color":        "rouge-bordeaux",
            "pH_sensitive": True,
            "note":         "Riche en anthocyanines — antioxydant puissant, pigment naturel rouge",
        },
        "applications":   ["serum eclat", "masque visage", "colorant naturel",
                           "cosmetique anti-age", "boisson fonctionnelle"],
        "_source":        "Producteurs nord CI / marche local",
    },

    "Savon_Potasse_CI": {
        "name":         "Savon de Potasse Traditionnel (Savon Nzema/Sanga)",
        "name_local":   "Savon de potasse / savon natif",
        "category":     "surfactant",
        "origin":       "CI (production artisanale : Nzema, region cotiere)",
        "density":      1.05,
        "pH":           10.5,
        "cost_FCFA_kg":   800.0,
        "cost_rel":       6.5,
        "min_pct":        1.0,
        "max_pct":        20.0,
        "function":       ["surfactant", "soap_base", "cleansing",
                           "antimicrobial", "traditional"],
        "compatible_with":["oil", "water", "excipient"],
        "properties":     {
            "pH_range":    [9, 12],
            "saponins":    True,
            "alkali":      "cendres vegetales (KOH naturel)",
            "note":        "Savoir-faire traditionnel CI — marketing cosmeto culturel fort",
        },
        "applications":   ["savon noir africain", "nettoyant corporel",
                           "cosmetique ethnique", "savon solide"],
        "_source":        "Artisanat traditionnel CI / cooperatives femmes",
    },

    "Poudre_Cacao_CI": {
        "name":         "Poudre de Cacao Alcalinisee (grade cosmetique)",
        "name_local":   "Poudre de cacao",
        "category":     "excipient",
        "origin":       "CI (Daloa, Soubre, Aboisso) — 1er producteur mondial",
        "cas":          "8002-31-1",
        "density":      0.50,
        "cost_FCFA_kg":   3000.0,
        "cost_rel":       24.0,
        "min_pct":        0.1,
        "max_pct":        10.0,
        "function":       ["antioxidant", "pigment", "filler",
                           "fragrance", "anti_aging"],
        "compatible_with":["oil", "polymer", "wax", "excipient"],
        "properties":     {
            "polyphenols_mg_100g": 3500,
            "flavonoids":          True,
            "theobromine":         True,
            "color":               "marron",
            "pH":                  7.8,
            "note":                "Riche en polyphenols — antioxydant et pigment naturel",
        },
        "applications":   ["gommage corps", "masque visage", "cosmetique chocolate",
                           "fond de teint naturel", "savon exfoliant"],
        "_source":        "CCC / SACO / marche Abidjan",
    },

    "Cire_Carnauba_AFrique": {
        "name":         "Cire de Carnauba (importee, usage courant en CI)",
        "name_local":   "Cire carnauba",
        "category":     "wax",
        "cas":          "8015-86-9",
        "origin":       "Importee Bresil — disponible Abidjan (CDCI)",
        "density":      0.990,
        "melting_point": 85.0,
        "cost_FCFA_kg":   9000.0,
        "cost_rel":       72.0,
        "min_pct":        0.5,
        "max_pct":        10.0,
        "function":       ["wax", "coating", "film_former", "lubricant", "gloss"],
        "compatible_with":["wax", "oil", "polymer"],
        "properties":     {"hardness": "elevee", "gloss": "haut"},
        "applications":   ["rouge a levres", "brillant levres", "stick", "vernis"],
        "_source":        "Importateurs CDCI Abidjan",
    },

    # ═══════════════════════════════════════════════════════════════════════
    # CONSERVATEURS & TENSIOACTIFS LOCAUX / DISPONIBLES
    # ═══════════════════════════════════════════════════════════════════════

    "Saponines_Gousses_CI": {
        "name":         "Extrait de Saponines (Sapindus saponaria / Gousses CI)",
        "name_local":   "Noix de lavage / gousses saponaires",
        "category":     "surfactant",
        "origin":       "Zone forestiere CI",
        "cost_FCFA_kg":   2000.0,
        "cost_rel":       16.0,
        "min_pct":        0.5,
        "max_pct":        10.0,
        "function":       ["surfactant", "foaming_agent", "natural_soap",
                           "emulsifier", "antimicrobial"],
        "compatible_with":["solvent", "polymer", "oil"],
        "properties":     {
            "pH_stability": [4, 8],
            "biodegradable":True,
            "HLB":          11.0,
            "note":         "Tensioactif 100% naturel — labellisation bio / naturel facilitee",
        },
        "applications":   ["shampoing naturel", "savon liquide", "detergent eco"],
        "_source":        "Marche traditionnel CI / foret CI",
    },

    "Glycerine_Locale": {
        "name":         "Glycerine Vegetale (coproduit savonnerie locale)",
        "name_local":   "Glycerine",
        "category":     "solvent",
        "origin":       "Coproduit des savonneries CI (Blohorn, etc.)",
        "cas":          "56-81-5",
        "molar_mass":   92.09,
        "density":      1.261,
        "solubility":   {"water": 1000.0},
        "cost_FCFA_kg":   800.0,
        "cost_rel":       6.5,
        "min_pct":        1.0,
        "max_pct":        50.0,
        "function":       ["humectant", "solvent", "plasticizer", "moisturizer"],
        "compatible_with":["polymer", "surfactant", "api", "water"],
        "properties":     {"purity_min": 95, "vegetal": True},
        "applications":   ["cosmetique", "pharmaceutique", "alimentaire"],
        "_source":        "Savonneries CI (coproduit palm oil refinery)",
    },

    "Eau_Florale_Hibiscus": {
        "name":         "Eau Florale de Bissap (Hydrolat Hibiscus)",
        "name_local":   "Eau de bissap",
        "category":     "solvent",
        "origin":       "Production artisanale CI / Afrique de l'Ouest",
        "density":      1.00,
        "pH":           4.2,
        "cost_FCFA_kg":   5000.0,
        "cost_rel":       20.0,
        "min_pct":        5.0,
        "max_pct":        80.0,
        "function":       ["solvent", "toner", "antioxidant",
                           "astringent", "brightening"],
        "compatible_with":["polymer", "surfactant", "api"],
        "properties":     {
            "anthocyanins": True,
            "pH_natural":   4.2,
            "color":        "rose-rouge",
            "note":         "Remplace partiellement l'eau — apporte actifs et differentiation",
        },
        "applications":   ["tonique visage", "serum", "brume hydratante",
                           "cosmetique naturel africain"],
        "_source":        "Artisans distillateurs CI / cooperatives",
    },
}

# Métadonnées de la base
CI_MATERIALS_META = {
    "region":        "Afrique de l'Ouest / Cote d'Ivoire",
    "n_materials":   len(CI_MATERIALS),
    "categories":    list(set(v["category"] for v in CI_MATERIALS.values())),
    "last_update":   "2024",
    "currency":      "FCFA",
    "price_basis":   "Prix indicatifs marche Abidjan 2024 — valider avec fournisseurs",
    "sources":       [
        "Palmci / PHCI", "CCC / SACO", "Conseil Coton-Anacarde",
        "CNRA Abidjan", "CSRS Abidjan", "FIRCA", "ANADER",
        "Marche CDCI Abidjan", "Marche Adjame Abidjan",
        "Cooperatives nord CI"
    ],
}


def get_ci_materials():
    return CI_MATERIALS

def get_ci_material(mid: str):
    return CI_MATERIALS.get(mid)

def get_all_materials_with_ci():
    """Retourne la BD principale + CI fusionnees."""
    from data.materials_db import MATERIALS
    return {**MATERIALS, **CI_MATERIALS}


# ─────────────────────────────────────────────────────────────────────────────
# Fonctions utilitaires manquantes (importées par routes et engine)
# ─────────────────────────────────────────────────────────────────────────────

def estimate_cost_fcfa(material_id: str, pct: float) -> float:
    """
    Estime le cout en FCFA pour une quantite donnee d'un materiau.
    pct : pourcentage dans la formulation (0-100)
    Retourne le cout en FCFA pour 1 kg de formulation.
    """
    mat  = CI_MATERIALS.get(material_id)
    if mat is None:
        # Chercher dans la BD principale
        try:
            from data.materials_db import MATERIALS
            mat = MATERIALS.get(material_id, {})
        except Exception:
            mat = {}

    fcfa_kg = mat.get("cost_FCFA_kg") or (mat.get("cost_rel", 10) * 125)
    return round(fcfa_kg * (pct / 100.0), 3)


# Alias pour compatibilite
estimate_cost_cfa = estimate_cost_fcfa


def get_ci_by_origin(region: str = "") -> dict:
    """Filtre les materiaux CI par region d'origine."""
    if not region:
        return CI_MATERIALS
    region_lower = region.lower()
    return {k: v for k, v in CI_MATERIALS.items()
            if region_lower in v.get("origin", "").lower()}


# Fournisseurs generaux Abidjan (reference simple)
CI_SUPPLIERS_GENERAL = {
    "CDCI":    "Compagnie de Distribution de Cote d'Ivoire — Treichville",
    "PALMCI":  "Palmci / PHCI — Zone industrielle Yopougon",
    "SACO":    "SACO (cacao) — Zone portuaire",
    "CCC":     "Conseil Cafe-Cacao — Abidjan Plateau",
    "FIRCA":   "FIRCA — Zone agricole CI",
    "ANADER":  "ANADER — reseau national",
    "ADJAME":  "Marche Adjame — grossistes matieres premieres",
}