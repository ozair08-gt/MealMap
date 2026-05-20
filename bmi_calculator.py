"""
BMI calculation and categorization.
"""


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    if height_cm <= 0:
        return 0.0
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25.0:
        return "Normal weight"
    elif bmi < 30.0:
        return "Overweight"
    else:
        return "Obese"


def bmi_color(bmi: float) -> str:
    """Returns a hex color for the BMI category badge."""
    cat = bmi_category(bmi)
    colors = {
        "Underweight": "#3B82F6",   # blue
        "Normal weight": "#22C55E", # green
        "Overweight": "#F59E0B",    # amber
        "Obese": "#EF4444",         # red
    }
    return colors.get(cat, "#6B7280")
