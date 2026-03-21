"""
utils/currency.py
==================
Gestion des devises : FCFA, EUR, USD.
Taux de change indicatifs (a mettre a jour periodiquement).
1 EUR = 655.957 FCFA (taux fixe XOF/EUR - zone UEMOA)
1 USD = ~600 FCFA (indicatif 2024)
"""

from typing import Dict

# Taux de change (base FCFA)
EXCHANGE_RATES: Dict[str, float] = {
    "FCFA": 1.0,
    "XOF":  1.0,          # alias FCFA
    "EUR":  655.957,      # taux fixe officiel XOF/EUR
    "USD":  600.0,        # indicatif — mettre a jour
}

CURRENCY_SYMBOLS: Dict[str, str] = {
    "FCFA": "FCFA",
    "XOF":  "FCFA",
    "EUR":  "€",
    "USD":  "$",
}

CURRENCY_FORMATS: Dict[str, dict] = {
    "FCFA": {"decimals": 0, "thousands": " ", "decimal_sep": ","},
    "EUR":  {"decimals": 2, "thousands": ".", "decimal_sep": ","},
    "USD":  {"decimals": 2, "thousands": ",", "decimal_sep": "."},
}


def convert(amount_fcfa: float, target_currency: str = "FCFA") -> float:
    """Convertit un montant en FCFA vers la devise cible."""
    rate = EXCHANGE_RATES.get(target_currency.upper(), 1.0)
    return round(amount_fcfa / rate, 4)


def convert_to_fcfa(amount: float, source_currency: str) -> float:
    """Convertit un montant depuis une devise vers FCFA."""
    rate = EXCHANGE_RATES.get(source_currency.upper(), 1.0)
    return round(amount * rate, 4)


def format_price(amount_fcfa: float, currency: str = "FCFA", per_kg: bool = True) -> str:
    """Formate un prix pour affichage."""
    converted = convert(amount_fcfa, currency)
    sym = CURRENCY_SYMBOLS.get(currency.upper(), currency)
    fmt = CURRENCY_FORMATS.get(currency.upper(), {"decimals": 2})
    dec = fmt["decimals"]
    unit = "/kg" if per_kg else ""
    if dec == 0:
        return f"{int(converted):,} {sym}{unit}".replace(",", " ")
    return f"{converted:,.{dec}f} {sym}{unit}"


def cost_rel_to_fcfa(cost_rel: float) -> float:
    """
    Convertit le cout relatif (echelle interne 1-100) en FCFA/kg approximatif.
    Echelle : 1 (eau ~50 FCFA/kg) → 100 (actif premium ~15000 FCFA/kg)
    """
    return round(50 + (cost_rel - 1) * 151.5, 0)


def price_formulation(formulation: Dict[str, float],
                      currency: str = "FCFA") -> Dict[str, any]:
    """
    Calcule le prix reel d'une formulation en FCFA et devise cible.
    Utilise cost_FCFA_kg si disponible, sinon cost_rel_to_fcfa().
    """
    from data.materials_db import MATERIALS

    total_fcfa = 0.0
    detail = []

    for mat_id, pct in formulation.items():
        mat = MATERIALS.get(mat_id, {})
        fcfa_kg = mat.get("cost_FCFA_kg") or cost_rel_to_fcfa(mat.get("cost_rel", 10))
        cost_pct = fcfa_kg * (pct / 100)
        total_fcfa += cost_pct
        detail.append({
            "id":        mat_id,
            "name":      mat.get("name", mat_id),
            "pct":       pct,
            "price_kg":  fcfa_kg,
            "cost_contribution_FCFA": round(cost_pct, 2),
        })

    return {
        "total_FCFA_per_kg": round(total_fcfa, 2),
        "total_converted":   convert(total_fcfa, currency),
        "currency":          currency,
        "symbol":            CURRENCY_SYMBOLS.get(currency.upper(), currency),
        "detail":            detail,
        "exchange_rate":     EXCHANGE_RATES.get(currency.upper(), 1.0),
    }


def get_exchange_rates() -> Dict:
    return {
        "rates":     EXCHANGE_RATES,
        "symbols":   CURRENCY_SYMBOLS,
        "base":      "FCFA",
        "note":      "EUR/FCFA taux fixe UEMOA. USD/FCFA indicatif — mettre a jour.",
    }


def update_usd_rate(new_rate: float):
    """Met a jour le taux USD/FCFA (indicatif)."""
    EXCHANGE_RATES["USD"] = new_rate
