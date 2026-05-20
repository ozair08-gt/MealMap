"""
User profile page: collect and update health information.
"""

import streamlit as st
from datetime import datetime
from database import get_profiles_collection
from bmi_calculator import calculate_bmi, bmi_category, bmi_color
from calorie_calculator import (
    calculate_bmr,
    calculate_tdee,
    calculate_target_calories,
    calculate_macros,
    ACTIVITY_MULTIPLIERS,
)
from utils import apply_base_styles, page_header, section_header, metric_card


def save_profile(user_id: str, data: dict):
    col = get_profiles_collection()
    data["user_id"] = user_id
    data["updated_at"] = datetime.utcnow()
    col.update_one({"user_id": user_id}, {"$set": data}, upsert=True)


def load_profile(user_id: str) -> dict:
    col = get_profiles_collection()
    doc = col.find_one({"user_id": user_id})
    if doc:
        doc.pop("_id", None)
    return doc or {}


def render():
    apply_base_styles()
    page_header("My Profile", "Enter your health details to personalise recommendations.")

    user_id = st.session_state.get("user_id", "")
    existing = load_profile(user_id)

    with st.form("profile_form"):
        section_header("Personal Information")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", value=existing.get("name", ""))
            age = st.number_input("Age", min_value=10, max_value=100, value=int(existing.get("age", 25)))
            gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other"],
                index=["Male", "Female", "Other"].index(existing.get("gender", "Male")),
            )
        with col2:
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=float(existing.get("height_cm", 165.0)), step=0.5)
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=float(existing.get("weight_kg", 65.0)), step=0.5)

        section_header("Lifestyle")
        col3, col4 = st.columns(2)
        with col3:
            activity_options = list(ACTIVITY_MULTIPLIERS.keys())
            activity = st.selectbox(
                "Activity Level",
                activity_options,
                index=activity_options.index(existing.get("activity_level", activity_options[1])) if existing.get("activity_level") in activity_options else 1,
            )
            dietary_pref = st.selectbox(
                "Dietary Preference",
                ["Non-Vegetarian", "Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free"],
                index=["Non-Vegetarian", "Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free"].index(existing.get("dietary_preference", "Non-Vegetarian")),
            )
        with col4:
            disease = st.selectbox(
                "Medical Condition",
                ["None", "Diabetes", "Hypertension", "Obesity", "PCOS", "Kidney Disease"],
                index=["None", "Diabetes", "Hypertension", "Obesity", "PCOS", "Kidney Disease"].index(existing.get("disease", "None")),
            )
            goal = st.selectbox(
                "Health Goal",
                ["Maintenance", "Weight Loss", "Weight Gain", "Muscle Gain"],
                index=["Maintenance", "Weight Loss", "Weight Gain", "Muscle Gain"].index(existing.get("goal", "Maintenance")),
            )

        submitted = st.form_submit_button("Save Profile", use_container_width=True)

    if submitted:
        profile_data = {
            "name": name,
            "age": age,
            "gender": gender,
            "height_cm": height,
            "weight_kg": weight,
            "activity_level": activity,
            "dietary_preference": dietary_pref,
            "disease": disease,
            "goal": goal,
        }
        save_profile(user_id, profile_data)
        st.success("Profile saved successfully!")
        st.session_state["profile"] = profile_data
        existing = profile_data

    # ── Live stats ──────────────────────────────────────────────────────────
    if existing.get("height_cm") and existing.get("weight_kg"):
        st.markdown("<br>", unsafe_allow_html=True)
        section_header("Your Stats")

        bmi = calculate_bmi(existing["weight_kg"], existing["height_cm"])
        cat = bmi_category(bmi)
        color = bmi_color(bmi)

        bmr = calculate_bmr(existing["weight_kg"], existing["height_cm"], existing.get("age", 25), existing.get("gender", "Male"))
        tdee = calculate_tdee(bmr, existing.get("activity_level", "Sedentary (little/no exercise)"))
        target = calculate_target_calories(tdee, existing.get("goal", "Maintenance"))
        macros = calculate_macros(target, existing.get("goal", "Maintenance"))

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            metric_card("BMI", str(bmi), cat, color)
        with c2:
            metric_card("BMR", f"{int(bmr)}", "kcal/day at rest", "#0369A1")
        with c3:
            metric_card("Daily Target", f"{target}", "kcal/day", "#0F766E")
        with c4:
            metric_card("TDEE", f"{int(tdee)}", "maintenance kcal", "#7C3AED" if False else "#B45309")

        st.markdown("<br>", unsafe_allow_html=True)
        section_header("Macro Targets")
        m1, m2, m3 = st.columns(3)
        with m1:
            metric_card("Protein", f"{macros['protein_g']}g", "per day", "#16A34A")
        with m2:
            metric_card("Carbohydrates", f"{macros['carbs_g']}g", "per day", "#D97706")
        with m3:
            metric_card("Fats", f"{macros['fats_g']}g", "per day", "#DC2626")
