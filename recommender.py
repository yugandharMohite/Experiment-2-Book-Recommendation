"""
recommender.py — Core recommendation engine loaded by FastAPI
"""

import pickle, os, copy
import numpy as np
import pandas as pd
from typing import Dict, Any

from nutrition_plans import (
    NUTRITION_PLANS, DIET_OVERRIDES,
    ALLERGY_RESTRICTIONS, classify_bmi
)
from schemas import UserProfileRequest, NutritionPlanResponse, SimilarUser


MODEL_PATH = os.path.join("models", "nutrition_model.pkl")
_artifacts = None


def load_artifacts():
    global _artifacts
    if _artifacts is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. "
                "Please run: python train_and_save_model.py"
            )
        with open(MODEL_PATH, "rb") as f:
            _artifacts = pickle.load(f)
    return _artifacts


def _preprocess(user: UserProfileRequest, artifacts: dict) -> np.ndarray:
    """Convert UserProfileRequest → scaled feature vector."""
    label_encoders = artifacts["label_encoders"]
    scaler         = artifacts["scaler"]
    feature_cols   = artifacts["feature_cols"]

    # Map request fields → raw dict matching training column names
    raw = {
        "Gender"        : user.gender,
        "Age"           : user.age,
        "Height"        : user.height_cm / 100,
        "Weight"        : user.weight_kg,
        "FamilyHistory" : user.family_history_obesity,
        "FAVC"          : user.high_caloric_food,
        "FCVC"          : user.vegetable_frequency,
        "NCP"           : user.main_meals_per_day,
        "CAEC"          : user.snacking,
        "SMOKE"         : user.smoker,
        "CH2O"          : user.water_intake_litres,
        "SCC"           : user.calorie_monitoring,
        "FAF"           : user.physical_activity_days / 7 * 3,  # normalise to 0-3
        "TUE"           : min(user.tech_device_hours / 8, 2),   # normalise to 0-2
        "CALC"          : user.alcohol_frequency,
        "MTRANS"        : user.transport_mode,
    }

    row = pd.DataFrame([raw])
    for col, le in label_encoders.items():
        if col in row.columns:
            val = str(row[col].values[0])
            try:
                row[col] = le.transform([val])[0]
            except ValueError:
                row[col] = 0

    height_m        = raw["Height"]
    row["BMI"]           = row["Weight"] / (height_m ** 2)
    row["ActivityScore"] = row["FAF"] * row["CH2O"]
    row["DietScore"]     = row["FCVC"] * row["NCP"] - row["FAVC"]
    row["HealthIndex"]   = row["FAF"] + row["FCVC"] + row["CH2O"] - row["TUE"]

    for c in feature_cols:
        if c not in row.columns:
            row[c] = 0

    vec = row[feature_cols].values
    return scaler.transform(vec)


def _personal_alerts(user: UserProfileRequest) -> list:
    flags = []
    if user.high_caloric_food == "yes":
        flags.append("⚠️ Frequent high-caloric food consumption detected")
    if user.water_intake_litres < 2:
        flags.append("💧 Low water intake — aim for at least 2.5 litres/day")
    if user.physical_activity_days < 2:
        flags.append("🏃 Very low physical activity — start with 20-min daily walks")
    if user.smoker == "yes":
        flags.append("🚭 Smoking detected — cessation strongly recommended for weight loss")
    if user.alcohol_frequency in ["Frequently", "Always"]:
        flags.append("🍺 Frequent alcohol consumption — high empty calories detected")
    if user.tech_device_hours > 4:
        flags.append("📱 High screen/device usage — sedentary risk, take movement breaks")
    if user.snacking == "Always":
        flags.append("🍪 Constant snacking detected — switch to healthy snack alternatives")
    if user.vegetable_frequency < 2:
        flags.append("🥦 Low vegetable intake — increase to at least 2–3 portions/day")
    if user.family_history_obesity == "yes":
        flags.append("🧬 Family history of obesity — higher genetic risk, stay consistent")
    return flags


def _apply_diet_and_allergy(plan: dict, user: UserProfileRequest) -> tuple:
    """Apply diet preference overrides and allergy exclusions."""
    plan  = copy.deepcopy(plan)
    notes = []

    diet_key = user.diet_preference if isinstance(user.diet_preference, str) else user.diet_preference.value
    override = DIET_OVERRIDES.get(diet_key, DIET_OVERRIDES["none"])

    # Meal plan text replacements
    new_meals = []
    for meal in plan["meal_plan"]:
        for old, new in override.get("replace", {}).items():
            meal = meal.replace(old, new)
        new_meals.append(meal)
    plan["meal_plan"] = new_meals

    # Extra foods & avoids
    plan["foods_to_increase"] += override.get("add_foods", [])
    plan["foods_to_avoid"]    += override.get("avoid_additional", [])
    plan["supplements"]       += override.get("supplements_extra", [])

    if diet_key != "none":
        notes.append(f"✅ Meal plan adjusted for {diet_key.replace('_',' ').title()} diet")

    # Allergy exclusions
    for allergy in user.allergies:
        allergy_key = allergy if isinstance(allergy, str) else allergy.value
        restricted  = ALLERGY_RESTRICTIONS.get(allergy_key, [])
        if restricted:
            plan["foods_to_avoid"] += restricted
            new_meals = []
            for meal in plan["meal_plan"]:
                skip = any(r.lower() in meal.lower() for r in restricted)
                if skip:
                    meal = meal + "  ⚠️ (check allergy-safe alternatives)"
                new_meals.append(meal)
            plan["meal_plan"] = new_meals
            notes.append(f"🚫 {allergy_key.capitalize()} allergy noted — restricted items flagged")

    # Goal-based calorie tweak note
    goal = user.health_goal if isinstance(user.health_goal, str) else user.health_goal.value
    if goal == "gain_muscle":
        notes.append("💪 Goal: Muscle gain — increase protein to 40–45% and add post-workout meal")
    elif goal == "heart_health":
        notes.append("❤️ Goal: Heart health — avoid saturated fats, increase Omega-3 & fibre")
    elif goal == "manage_diabetes":
        notes.append("🩺 Goal: Diabetes management — prioritise low-GI foods, avoid all sugar")
    elif goal == "maintain":
        notes.append("⚖️ Goal: Maintenance — keep calorie intake at the middle of your range")

    # Deduplicate
    plan["foods_to_increase"] = list(dict.fromkeys(plan["foods_to_increase"]))
    plan["foods_to_avoid"]    = list(dict.fromkeys(plan["foods_to_avoid"]))
    plan["supplements"]       = list(dict.fromkeys(plan["supplements"]))

    return plan, notes


def get_recommendation(user: UserProfileRequest) -> NutritionPlanResponse:
    arts       = load_artifacts()
    clf        = arts["classifier"]
    knn        = arts["knn"]
    target_le  = arts["target_le"]
    df_enc     = arts["df_enc"]
    X_scaled   = arts["X_scaled"]

    user_vec   = _preprocess(user, arts)
    bmi        = user.weight_kg / ((user.height_cm / 100) ** 2)
    
    # ── Classifier prediction ──
    pred_idx   = clf.predict(user_vec)[0]
    proba      = clf.predict_proba(user_vec)[0]
    pred_label = target_le.classes_[pred_idx]
    confidence = float(proba[pred_idx])
    all_proba  = {cls: round(float(p), 4) for cls, p in zip(target_le.classes_, proba)}

    # OPTIMIZATION: Use predicted label for plan (Model-Driven)
    plan_key   = pred_label
    base_plan  = copy.deepcopy(NUTRITION_PLANS.get(plan_key, NUTRITION_PLANS["Normal_Weight"]))

    # ── Model Insights ──
    insights = [f"Model analysis identifies your profile as '{pred_label.replace('_', ' ')}' with {confidence*100:.1f}% confidence."]
    if confidence < 0.6:
        insights.append("Note: Your habits fall between categories; plan includes balanced preventive measures.")
    
    # Activity & Goal Adjustments
    activity_map = {"sedentary": -100, "light": 0, "moderate": 150, "active": 300, "very_active": 500}
    kcal_adj = activity_map.get(user.activity_level.value if hasattr(user.activity_level, 'value') else user.activity_level, 0)
    
    if user.health_goal in ["gain_muscle"]:
        kcal_adj += 200
        insights.append("Increased caloric target to support muscle synthesis.")
    elif user.health_goal in ["lose_weight"]:
        kcal_adj -= 200
        insights.append("Caloric deficit applied for sustainable weight loss.")

    # Apply adjustments to plan text
    if kcal_adj != 0:
        insights.append(f"Calorie target adjusted by {kcal_adj:+} kcal based on activity & goals.")

    # ── Apply personalisation ──
    plan, diet_notes = _apply_diet_and_allergy(base_plan, user)
    alerts = _personal_alerts(user)

    # ── Similar users via KNN ──
    dists, idxs = knn.kneighbors(user_vec)
    sim_rows = df_enc.iloc[idxs[0]]
    similar_users = []
    for i, (_, row) in enumerate(sim_rows.iterrows()):
        similar_users.append(SimilarUser(
            age          = round(float(row["Age"]), 1),
            bmi          = round(float(row["BMI"]), 2),
            activity     = round(float(row["FAF"]), 2),
            vegetables   = round(float(row["FCVC"]), 2),
            water        = round(float(row["CH2O"]), 2),
            obesity_level= str(row["ObesityLevel"]),
            similarity   = round(float(1 - dists[0][i]), 4),
        ))

    # ── Weight goal calculations ──
    h = user.height_cm / 100
    healthy_min = round(18.5 * h ** 2, 1)
    healthy_max = round(24.9 * h ** 2, 1)
    diff        = round(user.weight_kg - healthy_max, 1)
    to_lose     = diff  if diff > 0 else None
    to_gain     = abs(diff) if diff < 0 else None

    return NutritionPlanResponse(
        name                 = user.name,
        bmi                  = round(bmi, 2),
        bmi_category         = pred_label,
        bmi_range            = base_plan.get("bmi_range", ""),
        confidence           = round(confidence, 4),
        current_weight_kg    = user.weight_kg,
        healthy_weight_min_kg= healthy_min,
        healthy_weight_max_kg= healthy_max,
        weight_to_lose_kg    = to_lose,
        weight_to_gain_kg    = to_gain,
        calorie_target       = plan["calorie_target"],
        macros               = plan["macros"],
        meal_plan            = plan["meal_plan"],
        foods_to_increase    = plan["foods_to_increase"],
        foods_to_avoid       = plan["foods_to_avoid"],
        hydration            = plan["hydration"],
        exercise             = plan["exercise"],
        priority             = plan["priority"],
        supplements          = plan["supplements"],
        diet_preference      = user.diet_preference if isinstance(user.diet_preference, str) else user.diet_preference.value,
        health_goal          = user.health_goal if isinstance(user.health_goal, str) else user.health_goal.value,
        personal_alerts      = alerts,
        diet_adjustments     = diet_notes,
        similar_users        = similar_users,
        obesity_probabilities= all_proba,
        insights             = insights
    )
