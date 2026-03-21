"""
data/ci_materials_db.py
========================
Base de donnees des matieres premieres locales de Cote d'Ivoire.
Prix en FCFA/kg (marche Abidjan 2024-2025).
Sources : CDCI, Socoprim, marche de Treichville, Chambre de Commerce CI.
"""

from __future__ import annotations
from typing import Dict, Any

# ── Structure etendue : champs supplementaires CI ────────────────────────────
# "price_fcfa_kg"    : prix moyen FCFA/kg (marche Abidjan)
# "price_min_fcfa"   : fourchette basse
# "price_max_fcfa"   : fourchette haute
# "suppliers_ci"     : [{name, city, contact, notes}]
# "local_availability": "facile" | "moderee" | "rare"
# "origin_ci"        : True si produit en CI, False si importe
# "season"           : mois de disponibilite optimale (si saisonnier)
# "certifications"   : certifications disponibles localement
# ─────────────────────────────────────────────────────────────────────────────

CI_MATERIALS: Dict[str, Dict[str, Any]] = {

    # ═══════════════════════════════════════════════════════════════════════
    # HUILES & GRAISSES LOCALES
    # ═══════════════════════════════════════════════════════════════════════

    "Huile_Palme_RBD": {
        "name":        "Huile de Palme RBD (Raffinee)",
        "name_local":  "Huile de palme blanche",
        "category":    "oil",
        "cas":         "8002-75-3",
        "density":     0.891,
        "melting_point": 35.0,
        "iodine_value":  52.0,
        "saponification_value": 199.0,
        "cost_rel":    5.0,
        "price_fcfa_kg":  650,
        "price_min_fcfa": 500,
        "price_max_fcfa": 800,
        "min_pct": 5.0, "max_pct": 80.0,
        "function": ["emollient","base","soap_making","emulsifier","occlusive"],
        "compatible_with": ["oil","wax","surfactant","polymer"],
        "suppliers_ci": [
            {"name":"PALMCI","city":"Abidjan-Port","contact":"27 21 24 77 00","notes":"Vente en gros, min 1 tonne"},
            {"name":"BLOHORN (Unilever CI)","city":"Abidjan-Yopougon","contact":"27 21 23 57 00","notes":"Qualite industrielle"},
            {"name":"Marche de Treichville","city":"Abidjan","contact":"Negoce local","notes":"Petites quantites, 5-50 kg"},
        ],
        "local_availability": "facile",
        "origin_ci":   True,
        "season":      None,
        "certifications": ["RSPO disponible via PALMCI"],
        "properties": {
            "fatty_acids": {"palmitic_C16": 44, "oleic_C18_1": 39, "linoleic_C18_2": 10},
            "color_lovibond": "Max 3R/30Y (RBD)",
            "FFA_pct": "<0.1",
        },
        "notes_technique": "Base ideale pour savons durs, cremes corporelles, bougies. Necessite un antioxydant (BHT/BHA) pour stabilite.",
    },

    "Huile_Palme_Brute": {
        "name":        "Huile de Palme Brute (CPO)",
        "name_local":  "Huile de palme rouge",
        "category":    "oil",
        "cas":         "8002-75-3",
        "density":     0.889,
        "melting_point": 35.0,
        "cost_rel":    3.0,
        "price_fcfa_kg":  450,
        "price_min_fcfa": 350,
        "price_max_fcfa": 550,
        "min_pct": 5.0, "max_pct": 60.0,
        "function": ["emollient","base","soap_making","antioxidant_source"],
        "compatible_with": ["oil","wax"],
        "suppliers_ci": [
            {"name":"PALMCI","city":"Abidjan-Port","contact":"27 21 24 77 00","notes":"Prix le plus bas, qualite brute"},
            {"name":"SANIA (filiale Wilmar)","city":"San-Pedro","contact":"27 34 71 12 00","notes":"Export et vente locale"},
        ],
        "local_availability": "facile",
        "origin_ci":   True,
        "season":      None,
        "properties": {
            "beta_carotene_ppm": "500-700",
            "tocopherols_ppm":   "600-1000",
            "FFA_pct":           "3-5",
            "color": "Rouge-orange intense (carotenes)",
        },
        "notes_technique": "Riche en beta-carotene et tocopherols. Usage cosmetique anti-age, savons artisanaux rouge-orange naturel.",
    },

    "Huile_Palmiste": {
        "name":        "Huile de Palmiste (PKO)",
        "name_local":  "Huile de noyau de palme",
        "category":    "oil",
        "cas":         "8023-79-8",
        "density":     0.912,
        "melting_point": 28.0,
        "saponification_value": 247.0,
        "cost_rel":    8.0,
        "price_fcfa_kg":  950,
        "price_min_fcfa": 750,
        "price_max_fcfa": 1200,
        "min_pct": 5.0, "max_pct": 50.0,
        "function": ["emollient","base","surfactant_precursor","soap_making","foam_booster"],
        "compatible_with": ["oil","wax","surfactant"],
        "suppliers_ci": [
            {"name":"PALMCI","city":"Abidjan","contact":"27 21 24 77 00","notes":"Disponible toute annee"},
            {"name":"SOPALMCI","city":"Abidjan-Treichville","contact":"Negociant local","notes":""},
        ],
        "local_availability": "facile",
        "origin_ci":   True,
        "properties": {
            "fatty_acids": {"lauric_C12": 48, "myristic_C14": 16, "palmitic_C16": 8},
            "notes": "Haute teneur en acide laurique — excellent pour la fabrication de tensioactifs (CAPB, SLS a partir de PKO)",
        },
        "notes_technique": "Precurseur du CAPB, SLS locaux. Mousse abondante dans les savons. Equivalent coco oil.",
    },

    "Beurre_Karite": {
        "name":        "Beurre de Karite Brut",
        "name_local":  "Beurre de karite / She butter",
        "category":    "oil",
        "cas":         "91080-23-8",
        "density":     0.863,
        "melting_point": 34.0,
        "iodine_value": 58.0,
        "saponification_value": 178.0,
        "HLB":         None,
        "cost_rel":    20.0,
        "price_fcfa_kg":  2500,
        "price_min_fcfa": 1800,
        "price_max_fcfa": 3500,
        "min_pct": 1.0, "max_pct": 30.0,
        "function": ["emollient","moisturizer","anti_aging","wound_healing","UV_protection"],
        "compatible_with": ["oil","wax","polymer","api"],
        "suppliers_ci": [
            {"name":"Coopec-Karite Nord","city":"Korhogo","contact":"Cooperative femmes","notes":"Production artisanale, certifiable bio"},
            {"name":"Marche de Bouake","city":"Bouake","contact":"Negoce","notes":"Prix variable selon saison"},
            {"name":"CDCI Abidjan","city":"Abidjan-Plateau","contact":"27 20 21 34 00","notes":"Import du Burkina si CI insuffisant"},
        ],
        "local_availability": "moderee",
        "origin_ci":   True,
        "season":      "Recolte juin-septembre (zone nord CI, Korhogo, Ferkessedougou)",
        "certifications": ["Bio certifiable", "Fair Trade possible"],
        "properties": {
            "fatty_acids": {"oleic_C18_1": 46, "stearic_C18": 38, "palmitic_C16": 5},
            "triterpenes_pct":   "6-12",
            "tocopherols_ppm":   "200-500",
            "unsaponifiable_pct":"7-12",
        },
        "notes_technique": "Fraction insaponifiable elevee = proprietes cicatrisantes. Beurre CI moins standardise que Burkina — controler la qualite a la reception.",
    },

    "Huile_Coco_CI": {
        "name":        "Huile de Coco Vierge (CI)",
        "name_local":  "Huile de noix de coco",
        "category":    "oil",
        "cas":         "8001-31-8",
        "density":     0.924,
        "melting_point": 24.0,
        "saponification_value": 258.0,
        "cost_rel":    15.0,
        "price_fcfa_kg":  1800,
        "price_min_fcfa": 1400,
        "price_max_fcfa": 2500,
        "min_pct": 1.0, "max_pct": 40.0,
        "function": ["emollient","soap_making","foam_booster","hair_conditioner","antibacterial"],
        "compatible_with": ["oil","wax","surfactant","polymer"],
        "suppliers_ci": [
            {"name":"Producteurs Cote Sud","city":"San-Pedro / Grand-Lahou","contact":"Cooperative locale","notes":"Production saisonniere"},
            {"name":"CDCI","city":"Abidjan-Plateau","contact":"27 20 21 34 00","notes":"Import Sri Lanka si stock local epuise"},
        ],
        "local_availability": "moderee",
        "origin_ci":   True,
        "season":      "Production ci : novembre-mars (cote atlantique)",
        "properties": {
            "fatty_acids": {"lauric_C12": 48, "caprylic_C8": 8, "capric_C10": 7},
            "peroxide_value": "<10 meq/kg (VCO)",
        },
        "notes_technique": "Qualite VCO (Virgin Coconut Oil) disponible en CI mais production limitee. Souvent coupe avec huile importee — verifier.",
    },

    "Beurre_Cacao_CI": {
        "name":        "Beurre de Cacao Deodorize (CI)",
        "name_local":  "Beurre de cacao",
        "category":    "oil",
        "cas":         "8002-31-1",
        "density":     0.974,
        "melting_point": 34.0,
        "saponification_value": 194.0,
        "cost_rel":    35.0,
        "price_fcfa_kg":  4500,
        "price_min_fcfa": 3500,
        "price_max_fcfa": 6000,
        "min_pct": 1.0, "max_pct": 25.0,
        "function": ["emollient","film_former","lip_care","skin_protector","texture_agent"],
        "compatible_with": ["oil","wax","polymer","api"],
        "suppliers_ci": [
            {"name":"CEMOI CI","city":"Abidjan-Yopougon","contact":"27 21 24 60 00","notes":"Beurre desodorise qualite cosmetique"},
            {"name":"SACO","city":"Abidjan","contact":"27 20 25 15 00","notes":"Filiale Barry Callebaut"},
            {"name":"Nestlé CI","city":"Abidjan-Yopougon","contact":"27 21 24 70 00","notes":"Usage alimentaire principalement"},
        ],
        "local_availability": "facile",
        "origin_ci":   True,
        "season":      None,
        "certifications": ["UTZ/Rainforest Alliance", "Fair Trade"],
        "properties": {
            "fatty_acids": {"stearic_C18": 34, "oleic_C18_1": 34, "palmitic_C16": 26},
            "melting_range": "32-35°C",
            "texture": "Solide a temp ambiante CI, fond sur la peau",
        },
        "notes_technique": "Point de fusion ideal pour le climat CI (fond a 34°C, ne transpire pas). Avantage concurrentiel majeur vs beurre de karite importe.",
    },

    "Huile_Coprah": {
        "name":        "Huile de Coprah (Hydrogenee)",
        "name_local":  "Huile de coco hydrogenee",
        "category":    "oil",
        "cas":         "68990-82-9",
        "density":     0.945,
        "melting_point": 32.0,
        "cost_rel":    12.0,
        "price_fcfa_kg":  1500,
        "price_min_fcfa": 1200,
        "price_max_fcfa": 1900,
        "min_pct": 2.0, "max_pct": 40.0,
        "function": ["base","soap_making","foam_booster","emollient"],
        "compatible_with": ["oil","wax","surfactant"],
        "suppliers_ci": [
            {"name":"CDCI","city":"Abidjan-Plateau","contact":"27 20 21 34 00","notes":"Import Philippines"},
        ],
        "local_availability": "moderee",
        "origin_ci":   False,
        "notes_technique": "Donne la moussite aux savons. Remplace avantageusement coconut oil importe en savonnerie industrielle.",
    },

    # ═══════════════════════════════════════════════════════════════════════
    # EXTRAITS VEGETAUX & ACTIFS LOCAUX
    # ═══════════════════════════════════════════════════════════════════════

    "Extrait_Moringa_CI": {
        "name":        "Extrait de Moringa Oleifera (CI)",
        "name_local":  "Extrait de Neverdye / Ben",
        "category":    "api",
        "cas":         "9000-40-6",
        "density":     1.10,
        "cost_rel":    45.0,
        "price_fcfa_kg":  5500,
        "price_min_fcfa": 4000,
        "price_max_fcfa": 7000,
        "min_pct": 0.5, "max_pct": 5.0,
        "function": ["api","antioxidant","antimicrobial","anti_inflammatory","skin_brightening"],
        "compatible_with": ["solvent","polymer","surfactant"],
        "suppliers_ci": [
            {"name":"Coopec Moringa Korhogo","city":"Korhogo","contact":"Cooperative","notes":"Poudre feuilles sechees"},
            {"name":"Ferm'Innov CI","city":"Abidjan","contact":"Startup agrotech","notes":"Extrait standardise 10:1"},
        ],
        "local_availability": "moderee",
        "origin_ci":   True,
        "season":      "Feuilles disponibles toute annee en CI (culture possible en zones nord et centre)",
        "properties": {
            "isothiocyanates_ppm": "80-150",
            "quercetin_ppm":       "120-200",
            "protein_pct_poudre":  "25-30",
            "antioxidant_DPPH":    "IC50 < 50 ug/mL",
        },
        "notes_technique": "Actif multifonction: antibacterien, antioxydant, eclaircissant naturel. Tendance forte sur marche cosmetique africain. Formuler entre pH 4-7.",
    },

    "Huile_Moringa": {
        "name":        "Huile de Moringa (Ben Oil)",
        "name_local":  "Huile de ben / Huile de moringa",
        "category":    "oil",
        "cas":         "8002-37-7",
        "density":     0.902,
        "iodine_value": 65.0,
        "cost_rel":    55.0,
        "price_fcfa_kg":  7500,
        "price_min_fcfa": 6000,
        "price_max_fcfa": 10000,
        "min_pct": 0.5, "max_pct": 10.0,
        "function": ["emollient","anti_aging","hair_care","antioxidant"],
        "compatible_with": ["oil","wax","polymer","api"],
        "suppliers_ci": [
            {"name":"Coopec Moringa Korhogo","city":"Korhogo","contact":"Cooperative locale","notes":"Pression a froid artisanale"},
        ],
        "local_availability": "rare",
        "origin_ci":   True,
        "properties": {
            "fatty_acids": {"oleic_C18_1": 73, "palmitic_C16": 6, "behenic_C22": 7},
            "tocopherols": "Elevé",
        },
        "notes_technique": "Huile tres stable (faible iodine value). Valorisation forte si positionnee premium CI-naturel.",
    },

    "Extrait_Papaye_CI": {
        "name":        "Extrait de Papaye (Carica papaya)",
        "name_local":  "Extrait de papaye / Pawpaw",
        "category":    "api",
        "density":     1.05,
        "cost_rel":    30.0,
        "price_fcfa_kg":  3500,
        "price_min_fcfa": 2500,
        "price_max_fcfa": 5000,
        "min_pct": 0.1, "max_pct": 5.0,
        "function": ["api","skin_brightening","exfoliant","anti_aging","enzyme_source"],
        "compatible_with": ["solvent","polymer"],
        "suppliers_ci": [
            {"name":"Laboratoire Phyto-CI","city":"Abidjan-Cocody","contact":"27 22 44 55 00","notes":"Extrait papaine standardise"},
            {"name":"Marche Adjame","city":"Abidjan","contact":"Negoce fruits","notes":"Papaye fraiche pour extraction locale"},
        ],
        "local_availability": "facile",
        "origin_ci":   True,
        "season":      "Papaye disponible toute annee en CI",
        "properties": {
            "papain_activity_TU_mg": "300-500 (extrait standardise)",
            "pH_optimal_papaine":    "6-7",
        },
        "notes_technique": "La papaine (enzyme) est tres demandee dans les cremes eclaircissantes africaines. Attention: peut irriter la peau a concentration >2%.",
    },

    "Aloe_Vera_CI": {
        "name":        "Gel d'Aloe Vera Stabilise (CI)",
        "name_local":  "Gel d'aloe vera",
        "category":    "api",
        "cas":         "85507-69-3",
        "density":     1.00,
        "cost_rel":    18.0,
        "price_fcfa_kg":  2200,
        "price_min_fcfa": 1500,
        "price_max_fcfa": 3000,
        "min_pct": 1.0, "max_pct": 80.0,
        "function": ["api","soothing","moisturizer","anti_inflammatory","wound_healing"],
        "compatible_with": ["solvent","polymer","surfactant","api"],
        "suppliers_ci": [
            {"name":"Aloe-CI SARL","city":"Abidjan-Bingerville","contact":"07 00 11 22 33","notes":"Culture locale, gel stabilise 200:1"},
            {"name":"Ferme Aloe Yamoussoukro","city":"Yamoussoukro","contact":"Agriculture locale","notes":"Feuilles fraiches et gel brut"},
        ],
        "local_availability": "moderee",
        "origin_ci":   True,
        "properties": {
            "polysaccharides_pct": "0.5-1.0 (acemannan)",
            "pH":                  "3.5-4.5",
            "solids_pct":          "0.5-1.5",
        },
        "notes_technique": "Base pour gels rafraichissants et apres-soleil adaptes au climat CI. Stabiliser avec citrate ou ascorbate.",
    },

    "Extrait_Hibiscus_CI": {
        "name":        "Extrait de Bissap (Hibiscus sabdariffa)",
        "name_local":  "Extrait de bissap / Foléré",
        "category":    "api",
        "density":     1.03,
        "cost_rel":    20.0,
        "price_fcfa_kg":  2500,
        "price_min_fcfa": 1800,
        "price_max_fcfa": 3500,
        "min_pct": 0.5, "max_pct": 10.0,
        "function": ["api","antioxidant","colorant_naturel","anti_aging","astringent"],
        "compatible_with": ["solvent","polymer"],
        "suppliers_ci": [
            {"name":"Producteurs Nord CI","city":"Korhogo / Ferkessedougou","contact":"Cooperative","notes":"Calices sechees, prix/kg fleurs"},
            {"name":"Marche Adjame","city":"Abidjan","contact":"Negoce","notes":"Fleurs sechees vrac"},
        ],
        "local_availability": "facile",
        "origin_ci":   True,
        "season":      "Recolte novembre-janvier (zone nord CI)",
        "properties": {
            "anthocyanins_ppm":  "1500-3000",
            "pH_extrait":        "2.5-3.5",
            "color":             "Rouge vif (naturel)",
        },
        "notes_technique": "Colorant naturel rouge-rose tres prisee sur le marche africain. Antioxydant puissant. Formuler a pH < 5 pour stabilite couleur.",
    },

    # ═══════════════════════════════════════════════════════════════════════
    # MATIERES PREMIERES MINERALES & ARGILES
    # ═══════════════════════════════════════════════════════════════════════

    "Argile_Kaolin_CI": {
        "name":        "Kaolin Blanc (Argile CI)",
        "name_local":  "Argile blanche / Kaolin de Man",
        "category":    "excipient",
        "cas":         "1332-58-7",
        "density":     2.60,
        "cost_rel":    3.0,
        "price_fcfa_kg":  350,
        "price_min_fcfa": 250,
        "price_max_fcfa": 500,
        "min_pct": 2.0, "max_pct": 40.0,
        "function": ["excipient","absorbent","opacifier","filler","skin_care","detoxifying"],
        "compatible_with": ["polymer","api","solvent","pigment"],
        "suppliers_ci": [
            {"name":"SODEMI","city":"Abidjan / Man","contact":"27 20 21 27 00","notes":"Exploitation miniere Man, livraison Abidjan"},
            {"name":"COGEB-CI","city":"Abidjan-Marcory","contact":"Importateur","notes":"Kaolin traitee qualite cosmetique"},
        ],
        "local_availability": "facile",
        "origin_ci":   True,
        "certifications": ["Gisement Man certifie SODEMI"],
        "properties": {
            "Al2O3_pct":       "35-38",
            "SiO2_pct":        "45-49",
            "whiteness_ISO":   "80-88",
            "oil_absorption":  "50-70 g/100g",
            "particle_size_um":"< 45",
        },
        "notes_technique": "Kaolin de Man de bonne qualite. Usage masques visage, poudres corporelles, savons surgras. Moins couteux que le titanium dioxide pour opacification.",
    },

    "Argile_Verte_CI": {
        "name":        "Argile Verte (Smectite CI)",
        "name_local":  "Argile verte / Terre verte",
        "category":    "excipient",
        "cas":         "1318-93-0",
        "density":     2.40,
        "cost_rel":    5.0,
        "price_fcfa_kg":  600,
        "price_min_fcfa": 400,
        "price_max_fcfa": 800,
        "min_pct": 2.0, "max_pct": 30.0,
        "function": ["excipient","absorbent","detoxifying","anti_inflammatory","thickener"],
        "compatible_with": ["polymer","api","solvent"],
        "suppliers_ci": [
            {"name":"Artisans Bouake","city":"Bouake","contact":"Marche artisanal","notes":"Argile brute, sechage solaire"},
            {"name":"COGEB-CI","city":"Abidjan","contact":"Importateur","notes":"Argile traitee import Maroc"},
        ],
        "local_availability": "moderee",
        "origin_ci":   True,
        "properties": {
            "swelling_index":  "10-18 mL/2g",
            "CEC_meq":         "80-120",
            "moisture_pct":    "< 12",
        },
        "notes_technique": "Masques purifiants et detoxifiants. Fort pouvoir absorbant. Populaire dans la cosmetique naturelle africaine.",
    },

    # ═══════════════════════════════════════════════════════════════════════
    # GOMMES & AGENTS TEXTURANTS LOCAUX
    # ═══════════════════════════════════════════════════════════════════════

    "Gomme_Arabique_CI": {
        "name":        "Gomme Arabique (Acacia senegal)",
        "name_local":  "Gomme arabique",
        "category":    "polymer",
        "cas":         "9000-01-5",
        "density":     1.35,
        "solubility":  {"water": 500.0},
        "cost_rel":    12.0,
        "price_fcfa_kg":  1500,
        "price_min_fcfa": 1100,
        "price_max_fcfa": 2000,
        "min_pct": 0.5, "max_pct": 20.0,
        "function": ["binder","emulsifier","film_former","stabilizer","thickener"],
        "compatible_with": ["solvent","api","excipient","surfactant"],
        "suppliers_ci": [
            {"name":"Importateurs Adjame","city":"Abidjan-Adjame","contact":"Marche de gros","notes":"Import Soudan/Niger, vrac 25 kg sacs"},
            {"name":"CDCI","city":"Abidjan-Plateau","contact":"27 20 21 34 00","notes":"Qualite alimentaire et pharmaceutique"},
        ],
        "local_availability": "facile",
        "origin_ci":   False,
        "properties": {
            "viscosity_mPas":    "5-50 (sol. 25%)",
            "pH_sol_10pct":      "4.5-5.5",
            "arabinogalactan_pct":"80-90",
        },
        "notes_technique": "Emulsifiant naturel tres utilise. Bon liant pour comprimes. Disponible en CI via import Sahel.",
    },

    "Cire_Abeilles_CI": {
        "name":        "Cire d'Abeilles Naturelle (CI)",
        "name_local":  "Cire d'abeilles jaune",
        "category":    "wax",
        "cas":         "8012-89-3",
        "density":     0.958,
        "melting_point": 62.0,
        "cost_rel":    30.0,
        "price_fcfa_kg":  4000,
        "price_min_fcfa": 3000,
        "price_max_fcfa": 5500,
        "min_pct": 1.0, "max_pct": 20.0,
        "function": ["wax","emulsifier","thickener","film_former","occlusive"],
        "compatible_with": ["oil","polymer","surfactant","api"],
        "suppliers_ci": [
            {"name":"Apiculteurs Korhogo","city":"Korhogo","contact":"Union apiculteurs Nord","notes":"Cire brute naturelle, filtration simple"},
            {"name":"Apiculteurs Man","city":"Man","contact":"Cooperative montagne","notes":"Cire qualite montagne, plus propre"},
            {"name":"Marche Bouake","city":"Bouake","contact":"Negoce","notes":"Prix variable, qualite a controler"},
        ],
        "local_availability": "moderee",
        "origin_ci":   True,
        "season":      "Disponibilite maximale : janvier-mars et juillet-septembre (apres miellees)",
        "certifications": ["Bio certifiable zone Nord CI"],
        "properties": {
            "acid_value":         "17-22",
            "ester_value":        "70-80",
            "color":              "Jaune a brun (brute)",
        },
        "notes_technique": "Cire CI de qualite correcte. Blanchir si usage cosmetique visage. Point de fusion 62°C ideal pour balsams/sticks en climat tropical.",
    },

    # ═══════════════════════════════════════════════════════════════════════
    # TENSIOACTIFS & BASES SAPONIFIEES LOCALES
    # ═══════════════════════════════════════════════════════════════════════

    "Savon_Base_CI": {
        "name":        "Savon de Base Saponifie (CI)",
        "name_local":  "Savon de base / Savon brut",
        "category":    "surfactant",
        "density":     1.04,
        "cost_rel":    4.0,
        "price_fcfa_kg":  500,
        "price_min_fcfa": 400,
        "price_max_fcfa": 650,
        "min_pct": 10.0, "max_pct": 70.0,
        "function": ["surfactant","base","soap_making","cleansing"],
        "compatible_with": ["oil","surfactant","excipient"],
        "suppliers_ci": [
            {"name":"BLOHORN Unilever CI","city":"Yopougon","contact":"27 21 23 57 00","notes":"Savon base palme/palmiste, 50kg blocs"},
            {"name":"Savonnerie CI-SOAD","city":"Abidjan-Koumassi","contact":"27 21 26 38 00","notes":"Savon base pour PME"},
        ],
        "local_availability": "facile",
        "origin_ci":   True,
        "properties": {
            "TFM_pct":       "72-80",
            "NaCl_pct":      "<1",
            "moisture_pct":  "10-18",
        },
        "notes_technique": "Base pour savon de toilette CI. TFM (Total Fatty Matter) > 72% requis pour la norme CI CODINORM.",
    },

    "Soude_Caustique": {
        "name":        "Soude Caustique (NaOH 98%)",
        "name_local":  "Soude / Lessive de soude",
        "category":    "other",
        "cas":         "1310-73-2",
        "density":     2.13,
        "cost_rel":    6.0,
        "price_fcfa_kg":  750,
        "price_min_fcfa": 600,
        "price_max_fcfa": 950,
        "min_pct": 0.1, "max_pct": 15.0,
        "function": ["saponification_agent","pH_adjuster","neutralizer"],
        "compatible_with": ["oil"],
        "suppliers_ci": [
            {"name":"SIVOP","city":"Abidjan-Vridi","contact":"27 21 27 34 00","notes":"Import Europe, sacs 25 kg granules"},
            {"name":"Chimie-Plus CI","city":"Abidjan-Marcory","contact":"27 21 26 12 00","notes":"Conditionnement 1 kg pour petits lots"},
        ],
        "local_availability": "facile",
        "origin_ci":   False,
        "properties": {
            "purity_pct": "98-99",
            "NaCl_pct":   "<1",
            "hazard":     "Corrosif - EPI obligatoire",
        },
        "notes_technique": "Saponification huile palme : index 0.141 g NaOH/g. Calculer avec soin via calculateur SAP. Stocker en endroit sec.",
    },

    # ═══════════════════════════════════════════════════════════════════════
    # CONSERVATEURS & ADDITIFS DISPONIBLES EN CI
    # ═══════════════════════════════════════════════════════════════════════

    "Vitamine_E_CI": {
        "name":        "Vitamin E (Tocopherol Naturel)",
        "name_local":  "Vitamine E / Tocophérol",
        "category":    "api",
        "cas":         "59-02-9",
        "density":     0.950,
        "cost_rel":    50.0,
        "price_fcfa_kg":  6500,
        "price_min_fcfa": 5000,
        "price_max_fcfa": 8000,
        "min_pct": 0.05, "max_pct": 0.5,
        "function": ["antioxidant","api","preservative_booster","skin_care"],
        "compatible_with": ["oil","polymer","api"],
        "suppliers_ci": [
            {"name":"PHARMALAND CI","city":"Abidjan-Plateau","contact":"27 20 31 24 00","notes":"Flacons 1L"},
            {"name":"CDCI","city":"Abidjan","contact":"27 20 21 34 00","notes":"Import Europeenne"},
        ],
        "local_availability": "moderee",
        "origin_ci":   False,
        "notes_technique": "Antioxydant indispensable pour huile de palme brute. Dose efficace 0.05-0.2%.",
    },

    "Acide_Citrique_CI": {
        "name":        "Acide Citrique Monohydrate",
        "name_local":  "Acide citrique",
        "category":    "other",
        "cas":         "5949-29-1",
        "molar_mass":  210.14,
        "density":     1.665,
        "solubility":  {"water": 1220.0},
        "cost_rel":    8.0,
        "price_fcfa_kg":  950,
        "price_min_fcfa": 750,
        "price_max_fcfa": 1200,
        "min_pct": 0.1, "max_pct": 5.0,
        "function": ["pH_adjuster","chelant","preservative_booster","antioxidant_synergist"],
        "compatible_with": ["solvent","polymer","surfactant","api"],
        "suppliers_ci": [
            {"name":"Chimie-Plus CI","city":"Abidjan-Marcory","contact":"27 21 26 12 00","notes":"Qualite alimentaire et cosmetique"},
            {"name":"Marche Adjame (negoce)","city":"Abidjan-Adjame","contact":"Negoce","notes":"Prix marche, qualite variable"},
        ],
        "local_availability": "facile",
        "origin_ci":   False,
        "notes_technique": "Ajuster le pH des formulations aqueuses CI (eau calcaire pH 7.5-8.5). Chelate les metaux lourds de l'eau du robinet.",
    },

    "Eau_Demineralisee_CI": {
        "name":        "Eau Demineralisee / Purifiee",
        "name_local":  "Eau purifiee / Eau DM",
        "category":    "solvent",
        "cas":         "7732-18-5",
        "density":     1.00,
        "cost_rel":    2.0,
        "price_fcfa_kg":  200,
        "price_min_fcfa": 150,
        "price_max_fcfa": 300,
        "min_pct": 0.0, "max_pct": 99.0,
        "function": ["solvent","vehicle","diluent"],
        "compatible_with": ["polymer","surfactant","api","excipient"],
        "suppliers_ci": [
            {"name":"SODECI","city":"Abidjan (reseau)","contact":"27 20 23 01 00","notes":"Eau robinet a traiter (dureté ~20 DH)"},
            {"name":"AQUA-CI","city":"Abidjan-Yopougon","contact":"27 21 75 00 00","notes":"Eau demineralisee en bidons 20L"},
            {"name":"Installation osmose inverse","city":"Sur site","contact":"Investissement","notes":"ROI 18 mois pour production >500L/j"},
        ],
        "local_availability": "facile",
        "origin_ci":   True,
        "properties": {
            "conductivity_uS":  "< 10 (demineralisee)",
            "pH":               "5.5-7.0",
            "TH":               "< 1 dH (demineralisee)",
            "remarque":         "Eau robinet Abidjan: dureté 18-22 dH — DOIT être traitée avant usage",
        },
        "notes_technique": "L'eau du robinet d'Abidjan est calcaire (TH ~20 dH). Obligatoire de demineraliser pour eviter le blanchiment des emulsions et l'incompatibilite avec les polymeres anioniques.",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Fournisseurs additionnels (non lies a un materiau specifique)
# ─────────────────────────────────────────────────────────────────────────────

CI_SUPPLIERS_GENERAL = [
    {
        "name":     "CDCI (Comptoir de Distribution CI)",
        "city":     "Abidjan-Plateau",
        "address":  "Rue du Commerce, Plateau, Abidjan",
        "phone":    "+225 27 20 21 34 00",
        "specialty":"Distribution generale matieres premieres cosmetique/pharma",
        "min_order": "5 kg",
        "payment":  "Virement, cheque, especes",
    },
    {
        "name":     "Socoprim CI",
        "city":     "Abidjan-Treichville",
        "address":  "Zone industrielle Treichville",
        "phone":    "+225 27 21 24 12 00",
        "specialty":"Produits chimiques industriels, huiles vegetales",
        "min_order": "25 kg",
    },
    {
        "name":     "Chimie-Plus CI",
        "city":     "Abidjan-Marcory",
        "address":  "Zone 4C, Marcory",
        "phone":    "+225 27 21 26 12 00",
        "specialty":"Additifs cosmetiques, conservateurs, acides",
        "min_order": "1 kg",
    },
    {
        "name":     "PHARMALAND CI",
        "city":     "Abidjan-Plateau",
        "phone":    "+225 27 20 31 24 00",
        "specialty":"Matieres premieres pharmaceutiques et cosmetiques",
        "min_order": "500 g",
        "notes":    "Prix plus eleves mais qualite certifiee",
    },
    {
        "name":     "Marche de gros Adjame",
        "city":     "Abidjan-Adjame",
        "specialty":"Gommes, resines, extraits vegetaux, prix marche",
        "min_order": "1 kg",
        "notes":    "Prix competitifs, qualite a verifier systematiquement",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Fonctions d'accès
# ─────────────────────────────────────────────────────────────────────────────

def get_ci_materials() -> Dict[str, Dict]:
    return CI_MATERIALS

def get_ci_material(mat_id: str):
    return CI_MATERIALS.get(mat_id)

def get_ci_suppliers_general():
    return CI_SUPPLIERS_GENERAL

def get_ci_material_ids():
    return list(CI_MATERIALS.keys())

def get_ci_by_origin(local_only: bool = True):
    return {k: v for k, v in CI_MATERIALS.items() if v.get("origin_ci") == local_only}

def estimate_cost_fcfa(formulation: dict, batch_kg: float = 1.0) -> dict:
    """
    Calcule le cout reel en FCFA pour un batch donne.
    Utilise les prix CI si disponibles, sinon estime depuis cost_rel.
    """
    from data.materials_db import MATERIALS
    from data.ci_materials_db import CI_MATERIALS

    all_mats = {**MATERIALS, **CI_MATERIALS}
    total_fcfa = 0.0
    detail = {}
    missing = []

    for mat_id, pct in formulation.items():
        mat = all_mats.get(mat_id, {})
        kg  = batch_kg * pct / 100.0

        if "price_fcfa_kg" in mat:
            price = mat["price_fcfa_kg"]
            cost  = round(kg * price, 0)
            detail[mat_id] = {
                "pct": pct, "kg": round(kg, 4),
                "price_fcfa_kg": price, "cost_fcfa": cost,
                "source": "prix_ci",
            }
        else:
            # Estimation depuis cost_rel (1 unit ≈ 100 FCFA/kg)
            cost_rel = mat.get("cost_rel", 10)
            price    = int(cost_rel * 100)
            cost     = round(kg * price, 0)
            detail[mat_id] = {
                "pct": pct, "kg": round(kg, 4),
                "price_fcfa_kg": price, "cost_fcfa": cost,
                "source": "estimation_cost_rel",
            }
            missing.append(mat_id)
        total_fcfa += cost

    return {
        "batch_kg":      batch_kg,
        "total_fcfa":    round(total_fcfa, 0),
        "total_fcfa_fmt":f"{int(total_fcfa):,} FCFA".replace(",", " "),
        "cost_per_kg":   round(total_fcfa / batch_kg, 0),
        "cost_per_kg_fmt":f"{int(total_fcfa/batch_kg):,} FCFA/kg".replace(",", " "),
        "detail":        detail,
        "estimated_ids": missing,
        "currency":      "XOF (FCFA)",
    }
