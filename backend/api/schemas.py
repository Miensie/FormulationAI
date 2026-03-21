from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ComponentConstraint(BaseModel):
    id:    str
    min:   float = Field(0.0, ge=0, le=100)
    max:   float = Field(100.0, ge=0, le=100)
    fixed: bool  = False

class GenerateRequest(BaseModel):
    components:     List[ComponentConstraint]
    n_formulations: int    = Field(5, ge=1, le=50)
    method:         str    = Field("lhs", description="lhs|random")
    seed:           int    = 42

class OptimizeCostRequest(BaseModel):
    components: List[ComponentConstraint]
    method:     str = Field("differential_evolution", description="differential_evolution|slsqp")
    seed:       int = 42

class OptimizePropertyRequest(BaseModel):
    components:       List[ComponentConstraint]
    target_property:  str
    target_value:     Optional[float] = None
    maximize:         bool  = True
    weights:          Optional[Dict[str, float]] = None
    method:           str   = "differential_evolution"
    seed:             int   = 42

class ParetoRequest(BaseModel):
    components:  List[ComponentConstraint]
    n_solutions: int = Field(20, ge=5, le=50)
    seed:        int = 42

class TrainRequest(BaseModel):
    formulations:     List[Dict[str, float]]
    target_values:    List[float]
    component_ids:    List[str]
    target_property:  str
    model_type:       str  = Field("random_forest", description="random_forest|gradient_boosting|svr|ridge|linear")
    n_estimators:     int  = 100

class PredictRequest(BaseModel):
    formulations:    List[Dict[str, float]]
    component_ids:   List[str]
    model_cache_key: str

class QuickPredictRequest(BaseModel):
    train_formulations: List[Dict[str, float]]
    target_values:      List[float]
    new_formulations:   List[Dict[str, float]]
    component_ids:      List[str]
    target_property:    str  = "property"
    model_type:         str  = "random_forest"

class RecommendRequest(BaseModel):
    target_properties:  List[str]
    application:        str  = Field("cosmetic", description="cosmetic|pharmaceutical|food|industrial")
    current_components: Optional[List[str]] = None
    constraints:        Optional[Dict[str, Any]] = None
    budget_level:       str  = Field("medium", description="low|medium|high")

class AnalyzeFormulationRequest(BaseModel):
    formulation:       Dict[str, float]
    target_properties: Optional[List[str]] = None
    application:       Optional[str]       = None

class SimulateViscosityRequest(BaseModel):
    formulation:   Dict[str, float]
    T_range:       List[float]
    ref_viscosity: float = 1000.0

class SimulateReleaseRequest(BaseModel):
    formulation:       Dict[str, float]
    time_hours:        List[float]
    api_id:            str = "Ibuprofen"
    dissolution_medium:str = "PBS_pH6.8"

class SimulateStabilityRequest(BaseModel):
    formulation:   Dict[str, float]
    time_months:   List[float]
    temperature_C: float = 25.0
    humidity_pct:  float = 60.0

class CompareFormulationsRequest(BaseModel):
    formulations:           List[Dict[str, float]]
    labels:                 List[str]
    properties_to_compare:  List[str]

class ValidateFormulationRequest(BaseModel):
    formulation: Dict[str, float]
