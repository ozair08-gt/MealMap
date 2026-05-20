"""
Rule-based meal recommendation engine.

Scoring logic:
  1. Filter meals that violate hard restrictions for the condition.
  2. Score each remaining meal by how closely it matches calorie/macro targets.
  3. Add bonus points for matching dietary preference tags.
  4. Return ranked list.
"""

from database import get_meals_collection
from calorie_calculator import calculate_macros
from datetime import datetime
import pandas as pd


# --------------------------------------------------------------------------- #
# Hard restriction rules per disease                                           #
# --------------------------------------------------------------------------- #

DISEASE_RESTRICTIONS = {
    "Diabetes": {
        "max_sugar_g": 5,
        "avoid_tags": ["high-sugar", "refined-carbs", "sugary-drink"],
        "prefer_tags": ["low-gi", "high-fiber", "low-sugar"],
        "explanation": "Low sugar and high-fiber foods help manage blood glucose levels.",
    },
    "Hypertension": {
        "max_sodium_mg": 400,
        "avoid_tags": ["high-sodium", "processed", "canned"],
        "prefer_tags": ["low-sodium", "potassium-rich", "heart-healthy"],
        "explanation": "Limiting sodium reduces blood pressure and cardiovascular strain.",
    },
    "Obesity": {
        "calorie_cap_pct": 0.30,   # no single meal > 30% of daily target
        "avoid_tags": ["fried", "high-calorie", "fast-food"],
        "prefer_tags": ["low-calorie", "high-protein", "high-fiber"],
        "explanation": "Calorie-controlled, high-fiber meals support sustainable weight loss.",
    },
    "PCOS": {
        "max_sugar_g": 8,
        "avoid_tags": ["high-sugar", "refined-carbs", "processed"],
        "prefer_tags": ["anti-inflammatory", "low-gi", "high-fiber"],
        "explanation": "Low-GI and anti-inflammatory foods help regulate hormones in PCOS.",
    },
    "Kidney Disease": {
        "max_protein_g": 15,
        "max_sodium_mg": 350,
        "max_potassium_mg": 200,
        "max_phosphorus_mg": 150,
        "avoid_tags": ["high-protein", "high-potassium", "high-phosphorus"],
        "prefer_tags": ["kidney-friendly", "low-protein", "low-sodium"],
        "explanation": "Controlled protein and minerals reduce kidney workload.",
    },
    "None": {
        "avoid_tags": [],
        "prefer_tags": [],
        "explanation": "Balanced meals chosen to match your calorie and macro goals.",
    },
}

DIETARY_PREFERENCE_TAGS = {
    "Vegetarian": "vegetarian",
    "Vegan": "vegan",
    "Non-Vegetarian": None,
    "Gluten-Free": "gluten-free",
    "Dairy-Free": "dairy-free",
}

MEAL_TYPE_CALORIES = {
    "breakfast": 0.25,
    "lunch": 0.35,
    "dinner": 0.30,
    "snack": 0.10,
}


def _passes_restrictions(meal: dict, rules: dict, daily_calories: int) -> bool:
    tags = [t.lower() for t in meal.get("tags", [])]

    # Avoid tags check
    for avoid in rules.get("avoid_tags", []):
        if avoid in tags:
            return False

    # Numeric hard limits
    if "max_sugar_g" in rules and meal.get("sugar_g", 0) > rules["max_sugar_g"]:
        return False
    if "max_sodium_mg" in rules and meal.get("sodium_mg", 0) > rules["max_sodium_mg"]:
        return False
    if "max_protein_g" in rules and meal.get("protein_g", 0) > rules["max_protein_g"]:
        return False
    if "max_potassium_mg" in rules and meal.get("potassium_mg", 999) > rules["max_potassium_mg"]:
        return False
    if "max_phosphorus_mg" in rules and meal.get("phosphorus_mg", 999) > rules["max_phosphorus_mg"]:
        return False
    if "calorie_cap_pct" in rules:
        cap = daily_calories * rules["calorie_cap_pct"]
        if meal.get("calories", 0) > cap:
            return False

    return True


def _score_meal(meal: dict, target_cal: int, macros: dict, rules: dict, pref_tag: str | None) -> float:
    score = 100.0

    # Calorie proximity (penalise deviation)
    cal_diff = abs(meal.get("calories", 0) - target_cal)
    score -= cal_diff * 0.05

    # Macro proximity
    score -= abs(meal.get("protein_g", 0) - macros["protein_g"]) * 0.1
    score -= abs(meal.get("carbs_g", 0) - macros["carbs_g"]) * 0.05
    score -= abs(meal.get("fats_g", 0) - macros["fats_g"]) * 0.07

    # Bonus for preferred tags
    tags = [t.lower() for t in meal.get("tags", [])]
    for prefer in rules.get("prefer_tags", []):
        if prefer in tags:
            score += 10

    # Dietary preference match
    if pref_tag and pref_tag in tags:
        score += 15

    return round(score, 2)


def get_recommendations(profile: dict, daily_calories: int, meal_type: str = "all", top_n: int = 5) -> list[dict]:
    """
    Returns a ranked list of recommended meal dicts.

    profile keys: disease, goal, dietary_preference
    """
    disease = profile.get("disease", "None") or "None"
    goal = profile.get("goal", "Maintenance")
    diet_pref = profile.get("dietary_preference", "Non-Vegetarian")

    rules = DISEASE_RESTRICTIONS.get(disease, DISEASE_RESTRICTIONS["None"])
    pref_tag = DIETARY_PREFERENCE_TAGS.get(diet_pref)
    macros = calculate_macros(daily_calories, goal)

    # Pull meals from MongoDB
    col = get_meals_collection()
    query = {}
    if meal_type != "all":
        query["meal_type"] = meal_type

    meals = list(col.find(query, {"_id": 0}))

    # Dietary preference hard filter for vegan/vegetarian
    if diet_pref in ("Vegetarian", "Vegan"):
        meals = [m for m in meals if pref_tag in [t.lower() for t in m.get("tags", [])]]

    # Disease restriction filter
    filtered = [m for m in meals if _passes_restrictions(m, rules, daily_calories)]

    # Determine per-meal calorie target based on meal type
    type_pct = MEAL_TYPE_CALORIES.get(meal_type, 1.0 / 3)
    target_cal = int(daily_calories * type_pct)
    meal_macros = {
        "protein_g": round(macros["protein_g"] * type_pct),
        "carbs_g": round(macros["carbs_g"] * type_pct),
        "fats_g": round(macros["fats_g"] * type_pct),
    }

    # Score and rank
    for m in filtered:
        m["_score"] = _score_meal(m, target_cal, meal_macros, rules, pref_tag)

    ranked = sorted(filtered, key=lambda x: x["_score"], reverse=True)
    return ranked[:top_n]


def generate_weekly_plan(profile: dict, daily_calories: int) -> dict:
    """
    Generates a 7-day meal plan dict:
    { "Monday": {"breakfast": [...], "lunch": [...], "dinner": [...], "snack": [...]}, ... }
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    plan = {}
    for day in days:
        plan[day] = {
            "breakfast": get_recommendations(profile, daily_calories, "breakfast", top_n=1),
            "lunch": get_recommendations(profile, daily_calories, "lunch", top_n=1),
            "dinner": get_recommendations(profile, daily_calories, "dinner", top_n=1),
            "snack": get_recommendations(profile, daily_calories, "snack", top_n=1),
        }
    return plan


def get_recommendation_explanation(meal: dict, disease: str) -> str:
    rules = DISEASE_RESTRICTIONS.get(disease, DISEASE_RESTRICTIONS["None"])
    base = rules.get("explanation", "This meal fits your nutritional targets.")
    tags = meal.get("tags", [])
    tag_str = ", ".join(tags) if tags else "balanced"
    return (
        f"{base} "
        f"'{meal.get('name', 'This meal')}' provides {meal.get('calories', '—')} kcal "
        f"with {meal.get('protein_g', '—')}g protein, {meal.get('carbs_g', '—')}g carbs, "
        f"and {meal.get('fats_g', '—')}g fat. Tags: {tag_str}."
    )
