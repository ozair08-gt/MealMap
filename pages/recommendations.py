"""
Meal recommendations page: per-meal-type tabs + weekly planner + history.
"""

import streamlit as st
from datetime import datetime
from database import get_profiles_collection, get_history_collection
from calorie_calculator import calculate_bmr, calculate_tdee, calculate_target_calories
from recommendation_engine import (
    get_recommendations,
    generate_weekly_plan,
    get_recommendation_explanation,
)
from utils import apply_base_styles, page_header, section_header, meal_card


def _load_profile(user_id: str) -> dict:
    col = get_profiles_collection()
    doc = col.find_one({"user_id": user_id})
    if doc:
        doc.pop("_id", None)
    return doc or {}


def _save_to_history(user_id: str, meals: list, meal_type: str):
    col = get_history_collection()
    records = []
    for m in meals:
        records.append({
            "user_id": user_id,
            "meal_name": m.get("name"),
            "meal_type": meal_type,
            "calories": m.get("calories", 0),
            "protein_g": m.get("protein_g", 0),
            "carbs_g": m.get("carbs_g", 0),
            "fats_g": m.get("fats_g", 0),
            "tags": m.get("tags", []),
            "created_at": datetime.utcnow(),
        })
    if records:
        col.insert_many(records)


def render():
    apply_base_styles()
    page_header("Meal Recommendations", "Personalised suggestions based on your health profile.")

    user_id = st.session_state.get("user_id", "")
    profile = _load_profile(user_id)

    if not profile:
        st.warning("Please complete your profile first.")
        return

    bmr = calculate_bmr(
        profile.get("weight_kg", 65),
        profile.get("height_cm", 165),
        profile.get("age", 25),
        profile.get("gender", "Male"),
    )
    tdee = calculate_tdee(bmr, profile.get("activity_level", "Sedentary (little/no exercise)"))
    daily_cal = calculate_target_calories(tdee, profile.get("goal", "Maintenance"))

    disease = profile.get("disease", "None")
    st.markdown(
        f"<p style='color:#64748B;font-size:0.875rem;margin-bottom:20px;'>"
        f"Daily target: <b>{daily_cal} kcal</b> &nbsp;|&nbsp; Condition: <b>{disease}</b> "
        f"&nbsp;|&nbsp; Goal: <b>{profile.get('goal','Maintenance')}</b> "
        f"&nbsp;|&nbsp; Diet: <b>{profile.get('dietary_preference','—')}</b>"
        f"</p>",
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["Today's Meals", "Weekly Planner", "History"])

    # ── Tab 1: Today's Meals ─────────────────────────────────────────────────
    with tab1:
        meal_tabs = st.tabs(["Breakfast", "Lunch", "Dinner", "Snacks"])
        type_map = {0: "breakfast", 1: "lunch", 2: "dinner", 3: "snack"}
        for i, mt in enumerate(meal_tabs):
            mt_key = type_map[i]
            recs = get_recommendations(profile, daily_cal, mt_key, top_n=4)
            if not recs:
                mt.info(f"No {mt_key} options match your current filters. Try adjusting your profile.")
                continue
            for meal in recs:
                with mt:
                    meal_card(meal)
                    with st.expander("Why this meal?"):
                        st.write(get_recommendation_explanation(meal, disease))
            if mt.button(f"Log {mt_key.title()} Meals", key=f"log_{mt_key}"):
                _save_to_history(user_id, recs, mt_key)
                mt.success(f"{mt_key.title()} meals logged!")

    # ── Tab 2: Weekly Planner ────────────────────────────────────────────────
    with tab2:
        section_header("7-Day Meal Plan")
        if st.button("Generate Weekly Plan", use_container_width=False):
            with st.spinner("Building your personalised week..."):
                plan = generate_weekly_plan(profile, daily_cal)
            st.session_state["weekly_plan"] = plan

        plan = st.session_state.get("weekly_plan")
        if plan:
            for day, meals_by_type in plan.items():
                with st.expander(day, expanded=(day == "Monday")):
                    for mt_key, meals in meals_by_type.items():
                        st.markdown(f"**{mt_key.title()}**")
                        if meals:
                            meal_card(meals[0])
                        else:
                            st.caption("No suitable meal found.")

    # ── Tab 3: History ────────────────────────────────────────────────────────
    with tab3:
        section_header("Recommendation History")
        col = get_history_collection()
        records = list(
            col.find({"user_id": user_id}, {"_id": 0})
               .sort("created_at", -1)
               .limit(30)
        )
        if not records:
            st.info("No history yet. Log some meals from the Today's Meals tab.")
        else:
            for rec in records:
                ts = rec.get("created_at")
                date_str = ts.strftime("%d %b %Y, %H:%M") if ts else "—"
                st.markdown(
                    f"<div class='meal-card'>"
                    f"<h4>{rec.get('meal_name','—')}</h4>"
                    f"<div class='meal-meta'>"
                    f"{rec.get('meal_type','').title()} &nbsp;|&nbsp; "
                    f"{rec.get('calories','—')} kcal &nbsp;|&nbsp; {date_str}"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )
