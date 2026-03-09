"""
schemas.py — Pydantic request/response models for the Nutrition API
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from enum import Enum


class GenderEnum(str, Enum):
    male   = "Male"
    female = "Female"


class YesNoEnum(str, Enum):
    yes = "yes"
    no  = "no"


class FrequencyEnum(str, Enum):
    no         = "no"
    sometimes  = "Sometimes"
    frequently = "Frequently"
    always     = "Always"


class CalcEnum(str, Enum):
    no         = "no"
    sometimes  = "Sometimes"
    frequently = "Frequently"
    always     = "Always"


class TransportEnum(str, Enum):
    automobile           = "Automobile"
    motorbike            = "Motorbike"
    bike                 = "Bike"
    public_transportation= "Public_Transportation"
    walking              = "Walking"


class DietPreferenceEnum(str, Enum):
    none        = "none"
    vegan       = "vegan"
    vegetarian  = "vegetarian"
    keto        = "keto"
    diabetic    = "diabetic"
    gluten_free = "gluten_free"
    halal       = "halal"


class AllergyEnum(str, Enum):
    none     = "none"
    nuts     = "nuts"
    dairy    = "dairy"
    gluten   = "gluten"
    eggs     = "eggs"
    soy      = "soy"
    fish     = "fish"
    shellfish= "shellfish"


class GoalEnum(str, Enum):
    lose_weight    = "lose_weight"
    maintain       = "maintain"
    gain_muscle    = "gain_muscle"
    manage_diabetes= "manage_diabetes"
    heart_health   = "heart_health"


class ActivityLevelEnum(str, Enum):
    sedentary  = "sedentary"
    light      = "light"
    moderate   = "moderate"
    active     = "active"
    very_active= "very_active"


# ── Request Schema ────────────────────────────────────────────
class UserProfileRequest(BaseModel):
    # Basic Info
    name            : str               = Field(...,  example="Rahul Sharma")
    gender          : GenderEnum        = Field(...,  example="Male")
    age             : int               = Field(...,  ge=10, le=100, example=35)
    height_cm       : float             = Field(...,  ge=100, le=250, example=170)
    weight_kg       : float             = Field(...,  ge=20,  le=300, example=110)

    # Eating Habits (from UCI dataset features)
    family_history_obesity : YesNoEnum  = Field(...,  example="yes")
    high_caloric_food      : YesNoEnum  = Field(...,  example="yes",
                                                description="Do you frequently eat high-caloric food?")
    vegetable_frequency    : float      = Field(...,  ge=1, le=3, example=1,
                                                description="1=rarely, 2=sometimes, 3=always")
    main_meals_per_day     : int        = Field(...,  ge=1, le=5, example=3)
    snacking               : FrequencyEnum = Field(..., example="Always",
                                                description="Eating between meals")
    smoker                 : YesNoEnum  = Field(...,  example="no")
    water_intake_litres    : float      = Field(...,  ge=0, le=5, example=1.5,
                                                description="Daily water intake in litres")
    calorie_monitoring     : YesNoEnum  = Field(...,  example="no")
    physical_activity_days : float      = Field(...,  ge=0, le=7, example=1,
                                                description="Days/week of physical activity")
    tech_device_hours      : float      = Field(...,  ge=0, le=24, example=4,
                                                description="Daily hours on screens/devices")
    alcohol_frequency      : CalcEnum   = Field(...,  example="Frequently")
    transport_mode         : TransportEnum = Field(..., example="Automobile")

    # Personalisation extras
    diet_preference : DietPreferenceEnum = Field(DietPreferenceEnum.none, example="vegetarian")
    allergies       : List[AllergyEnum]  = Field(default=[], example=["dairy"])
    health_goal     : GoalEnum           = Field(GoalEnum.lose_weight, example="lose_weight")
    activity_level  : ActivityLevelEnum  = Field(ActivityLevelEnum.sedentary, example="sedentary")

    @field_validator("gender", mode="before")
    def validate_gender(cls, v):
        if isinstance(v, str):
            mapping = {"male": GenderEnum.male, "female": GenderEnum.female}
            return mapping.get(v.lower(), v)
        return v

    @field_validator("family_history_obesity", "high_caloric_food", "smoker", "calorie_monitoring", mode="before")
    def validate_yes_no(cls, v):
        if isinstance(v, str):
            val = v.lower().strip()
            if val in ["yes", "y", "true", "1"]: return YesNoEnum.yes
            if val in ["no", "n", "false", "0"]: return YesNoEnum.no
        return v

    @field_validator("snacking", "alcohol_frequency", mode="before")
    def validate_frequency(cls, v):
        if isinstance(v, str):
            val = v.lower().strip()
            mapping = {
                "no": FrequencyEnum.no,
                "none": FrequencyEnum.no,
                "sometimes": FrequencyEnum.sometimes,
                "often": FrequencyEnum.frequently,
                "frequently": FrequencyEnum.frequently,
                "always": FrequencyEnum.always
            }
            return mapping.get(val, v)
        return v

    @field_validator("diet_preference", mode="before")
    def validate_diet(cls, v):
        if isinstance(v, str):
            val = v.lower().strip()
            mapping = {
                "veg": DietPreferenceEnum.vegetarian,
                "vegetarian": DietPreferenceEnum.vegetarian,
                "vegan": DietPreferenceEnum.vegan,
                "keto": DietPreferenceEnum.keto,
                "diabetic": DietPreferenceEnum.diabetic,
                "halal": DietPreferenceEnum.halal,
                "gluten free": DietPreferenceEnum.gluten_free,
                "gluten_free": DietPreferenceEnum.gluten_free,
                "none": DietPreferenceEnum.none,
                "non-veg": DietPreferenceEnum.none
            }
            return mapping.get(val, v)
        return v

    @field_validator("health_goal", mode="before")
    def validate_goal(cls, v):
        if isinstance(v, str):
            val = v.lower().replace(" ", "_")
            for goal in GoalEnum:
                if val == goal.value.lower():
                    return goal
        return v

    @field_validator("transport_mode", mode="before")
    def validate_transport(cls, v):
        if isinstance(v, str):
            val = v.lower().replace(" ", "_")
            for mode in TransportEnum:
                if val == mode.value.lower():
                    return mode
        return v

    class Config:
        use_enum_values = True


# ── Response Schema ───────────────────────────────────────────
class SimilarUser(BaseModel):
    age         : float
    bmi         : float
    activity    : float
    vegetables  : float
    water       : float
    obesity_level: str
    similarity  : float


class NutritionPlanResponse(BaseModel):
    # Identity
    name            : str
    bmi             : float
    bmi_category    : str
    bmi_range       : str
    confidence      : float

    # Weight goals
    current_weight_kg   : float
    healthy_weight_min_kg: float
    healthy_weight_max_kg: float
    weight_to_lose_kg   : Optional[float]
    weight_to_gain_kg   : Optional[float]

    # Plan
    calorie_target      : str
    macros              : str
    meal_plan           : List[str]
    foods_to_increase   : List[str]
    foods_to_avoid      : List[str]
    hydration           : str
    exercise            : str
    priority            : str
    supplements         : List[str]

    # Personalisation
    diet_preference     : str
    health_goal         : str
    personal_alerts     : List[str]
    diet_adjustments    : List[str]

    # Collaborative
    similar_users       : List[SimilarUser]

    # Probability breakdown
    obesity_probabilities: Dict[str, float]
    
    # Model insights / Explanations
    insights            : List[str] = []
