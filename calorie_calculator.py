"""
Calorie and macro target calculations using Mifflin-St Jeor equation.
"""

ACTIVITY_MULTIPLIERS = {
    "Sedentary (little/no exercise)": 1.2,
    "Lightly active (1-3 days/week)": 1.375,
    "Moderately active (3-5 days/week)": 1.55,
    "Very active (6-7 days/week)": 1.725,
    "Extra active (physical job)": 1.9,
}

GOAL_ADJUSTMENTS = {
    "Weight Loss": -500,
    "Weight Gain": +500,
    "Muscle Gain": +250,
    "Maintenance": 0,
}


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Mifflin-St Jeor BMR."""
    if gender == "Male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def calculate_tdee(bmr: float, activity_level: str) -> float:
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    return round(bmr * multiplier)


def calculate_target_calories(tdee: float, goal: str) -> int:
    adjustment = GOAL_ADJUSTMENTS.get(goal, 0)
    return max(1200, int(tdee + adjustment))


def calculate_macros(target_calories: int, goal: str) -> dict:
    """
    Returns grams of protein, carbs, fats based on goal.
    """
    if goal == "Muscle Gain":
        protein_pct, carb_pct, fat_pct = 0.30, 0.45, 0.25
    elif goal == "Weight Loss":
        protein_pct, carb_pct, fat_pct = 0.35, 0.35, 0.30
    elif goal == "Weight Gain":
        protein_pct, carb_pct, fat_pct = 0.25, 0.50, 0.25
    else:
        protein_pct, carb_pct, fat_pct = 0.25, 0.50, 0.25

    return {
        "protein_g": round((target_calories * protein_pct) / 4),
        "carbs_g": round((target_calories * carb_pct) / 4),
        "fats_g": round((target_calories * fat_pct) / 9),
    }
