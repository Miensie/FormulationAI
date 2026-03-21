"""
engine/prediction_engine.py
=============================
Prediction de proprietes par ML (sklearn + PyTorch).
Toutes les fonctions sont standalone — pas de classes globales.
"""

from __future__ import annotations
import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from sklearn.metrics import r2_score, mean_squared_error
from loguru import logger

# Cache simple en memoire (modeles entraines)
_MODEL_CACHE: Dict[str, Any] = {}


# ─────────────────────────────────────────────────────────────────────────────
# Construction des features depuis une formulation
# ─────────────────────────────────────────────────────────────────────────────

def formulation_to_features(
    formulations: List[Dict[str, float]],
    component_ids: List[str],
) -> np.ndarray:
    """
    Convertit une liste de formulations en matrice de features.
    Chaque colonne = pourcentage d'un composant.
    """
    X = np.zeros((len(formulations), len(component_ids)))
    for i, form in enumerate(formulations):
        for j, cid in enumerate(component_ids):
            X[i, j] = form.get(cid, 0.0)
    return X


# ─────────────────────────────────────────────────────────────────────────────
# Builders de modeles
# ─────────────────────────────────────────────────────────────────────────────

def _build_model(model_type: str, n_estimators: int = 100) -> Any:
    """Construit un Pipeline sklearn selon le type."""
    estimators = {
        "random_forest":    RandomForestRegressor(n_estimators=n_estimators, random_state=42, n_jobs=-1),
        "gradient_boosting":GradientBoostingRegressor(n_estimators=n_estimators, random_state=42),
        "svr":              SVR(kernel="rbf", C=10.0, epsilon=0.1),
        "ridge":            Ridge(alpha=1.0),
        "linear":           LinearRegression(),
    }
    if model_type not in estimators:
        raise ValueError(f"Modele inconnu : {model_type}. Valides : {list(estimators.keys())}")
    return Pipeline([("scaler", StandardScaler()), ("model", estimators[model_type])])


# ─────────────────────────────────────────────────────────────────────────────
# FONCTIONS PUBLIQUES
# ─────────────────────────────────────────────────────────────────────────────

def train_predictor(
    formulations: List[Dict[str, float]],
    target_values: List[float],
    component_ids: List[str],
    target_property: str,
    model_type: str = "random_forest",
    n_estimators: int = 100,
) -> Dict[str, Any]:
    """
    Entraine un modele ML pour predire une propriete.

    Parameters
    ----------
    formulations      : liste de formulations {mat_id: pct}
    target_values     : valeurs de la propriete cible
    component_ids     : ordre fixe des composants pour les features
    target_property   : nom de la propriete predite
    model_type        : type de modele ML
    n_estimators      : nb estimateurs (RF/GBM)

    Returns
    -------
    dict avec metriques d'entrainement et infos modele
    """
    logger.info(f"train_predictor — {target_property}, {model_type}, n={len(formulations)}")

    X  = formulation_to_features(formulations, component_ids)
    y  = np.array(target_values, dtype=float)

    model = _build_model(model_type, n_estimators)
    model.fit(X, y)
    y_pred = model.predict(X)

    r2   = float(r2_score(y, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y, y_pred)))

    # Cross-validation si assez de donnees
    cv_r2 = None
    if len(X) >= 5:
        cv_scores = cross_val_score(model, X, y, cv=min(5, len(X)//2), scoring="r2")
        cv_r2 = round(float(cv_scores.mean()), 4)

    # Feature importances (RF/GBM)
    feat_imp = None
    m = model["model"]
    if hasattr(m, "feature_importances_"):
        feat_imp = dict(zip(component_ids, m.feature_importances_.tolist()))

    # Stocker le modele + metadata en cache
    cache_key = f"{target_property}_{model_type}"
    _MODEL_CACHE[cache_key] = {
        "model":         model,
        "component_ids": component_ids,
        "target":        target_property,
        "model_type":    model_type,
    }

    logger.info(f"  → R2={r2:.4f}, RMSE={rmse:.4f}")
    return {
        "status":             "ok",
        "target_property":    target_property,
        "model_type":         model_type,
        "n_samples":          len(X),
        "r2_train":           round(r2, 6),
        "rmse_train":         round(rmse, 6),
        "cv_r2":              cv_r2,
        "feature_importances":feat_imp,
        "model_cache_key":    cache_key,
    }


def predict_property(
    formulations: List[Dict[str, float]],
    component_ids: List[str],
    model_cache_key: str,
) -> Dict[str, Any]:
    """
    Predit une propriete sur de nouvelles formulations.
    Le modele doit avoir ete entraine avec train_predictor.
    """
    logger.info(f"predict_property — key={model_cache_key}, n={len(formulations)}")

    if model_cache_key not in _MODEL_CACHE:
        return {"status": "error",
                "error": f"Modele '{model_cache_key}' non entraine. Lancez train_predictor d'abord."}

    cache     = _MODEL_CACHE[model_cache_key]
    model     = cache["model"]
    comp_ids  = cache["component_ids"]

    X = formulation_to_features(formulations, comp_ids)
    y_pred = model.predict(X)

    return {
        "status":          "ok",
        "target_property": cache["target"],
        "model_type":      cache["model_type"],
        "predictions":     y_pred.tolist(),
        "pred_stats": {
            "mean": round(float(np.mean(y_pred)), 6),
            "std":  round(float(np.std(y_pred)),  6),
            "min":  round(float(np.min(y_pred)),  6),
            "max":  round(float(np.max(y_pred)),  6),
        },
    }


def predict_from_composition(
    formulation: Dict[str, float],
    component_ids: List[str],
    model_cache_key: str,
) -> Dict[str, Any]:
    """Predit la propriete pour une seule formulation."""
    result = predict_property([formulation], component_ids, model_cache_key)
    if result["status"] == "ok":
        result["prediction"] = result["predictions"][0]
    return result


def quick_estimate(
    formulations: List[Dict[str, float]],
    component_ids: List[str],
    target_values: List[float],
    new_formulations: List[Dict[str, float]],
    target_property: str = "property",
    model_type: str = "random_forest",
) -> Dict[str, Any]:
    """
    Entraine et predit en une seule etape.
    Pratique pour les appels API sans gestion de cache.
    """
    train_result = train_predictor(
        formulations, target_values, component_ids, target_property, model_type
    )
    if train_result.get("status") != "ok":
        return train_result

    pred_result = predict_property(
        new_formulations, component_ids, train_result["model_cache_key"]
    )
    return {**train_result, **pred_result, "status": "ok"}


def list_trained_models() -> List[str]:
    """Retourne la liste des modeles en cache."""
    return list(_MODEL_CACHE.keys())
