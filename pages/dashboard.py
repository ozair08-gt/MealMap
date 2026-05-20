"""
Main dashboard: summary cards, today's snapshot, macro ring chart.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from database import get_profiles_collection, get_history_collection
from bmi_calculator import calculate_bmi, bmi_category, bmi_color
from calorie_calculator import (
    calculate_bmr, calculate_tdee, calculate_target_calories, calculate_macros, ACTIVITY_MULTIPLIERS
)
from utils import apply_base_styles, page_header, section_header, metric_card


def _load_profile(user_id: str) -> dict:
    col = get_profiles_collection()
    doc = col.find_one({"user_id": user_id})
    if doc:
        doc.pop("_id", None)
    return doc or {}


def _macro_donut(macros: dict) -> go.Figure:
    labels = ["Protein", "Carbohydrates", "Fats"]
    values = [macros["protein_g"] * 4, macros["carbs_g"] * 4, macros["fats_g"] * 9]
    colors = ["#22C55E", "#F59E0B", "#EF4444"]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.5,
            marker_colors=colors,
            textinfo="label+percent",
            textfont_size=12,
        )
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        height=240,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _weekly_calorie_bar(history: list) -> go.Figure:
    # Build last-7-days labels
    today = datetime.utcnow().date()
    days = [(today - timedelta(days=i)).strftime("%a %d") for i in range(6, -1, -1)]
    day_map = {d: 0 for d in days}

    for rec in history:
        ts = rec.get("created_at")
        if ts:
            label = ts.strftime("%a %d")
            if label in day_map:
                day_map[label] += rec.get("calories", 0)

    fig = go.Figure(
        go.Bar(
            x=list(day_map.keys()),
            y=list(day_map.values()),
            marker_color="#0D9488",
            marker_line_width=0,
        )
    )
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        height=220,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="kcal logged"),
        font=dict(family="Inter, sans-serif", size=11),
    )
    return fig


def render():
    apply_base_styles()
    user_id = st.session_state.get("user_id", "")
    username = st.session_state.get("username", "User")
    profile = _load_profile(user_id)

    # ── Greeting ────────────────────────────────────────────────────────────
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 18 else "Good evening")
    display_name = profile.get("name") or username
    page_header(f"{greeting}, {display_name}!", "Here is your health summary for today.")

    if not profile:
        st.info("Complete your profile to see personalised insights.")
        if st.button("Go to Profile"):
            st.session_state["page"] = "Profile"
            st.rerun()
        return

    # ── Computed values ──────────────────────────────────────────────────────
    bmi = calculate_bmi(profile.get("weight_kg", 0), profile.get("height_cm", 1))
    cat = bmi_category(bmi)
    color = bmi_color(bmi)
    bmr = calculate_bmr(
        profile.get("weight_kg", 65),
        profile.get("height_cm", 165),
        profile.get("age", 25),
        profile.get("gender", "Male"),
    )
    tdee = calculate_tdee(bmr, profile.get("activity_level", "Sedentary (little/no exercise)"))
    target = calculate_target_calories(tdee, profile.get("goal", "Maintenance"))
    macros = calculate_macros(target, profile.get("goal", "Maintenance"))

    # ── Top KPI cards ────────────────────────────────────────────────────────
    section_header("Your Key Metrics")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("BMI", str(bmi), cat, color)
    with c2:
        metric_card("Daily Calorie Target", f"{target} kcal", profile.get("goal", "Maintenance"), "#0F766E")
    with c3:
        metric_card("Condition", profile.get("disease", "None"), "Medical flag", "#0369A1")
    with c4:
        metric_card("Health Goal", profile.get("goal", "Maintenance"), profile.get("dietary_preference", ""), "#B45309")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts row ───────────────────────────────────────────────────────────
    ch1, ch2 = st.columns([1, 2])

    with ch1:
        section_header("Macro Split")
        st.plotly_chart(_macro_donut(macros), use_container_width=True, config={"displayModeBar": False})
        st.markdown(
            f"<p style='text-align:center;font-size:0.75rem;color:#64748B;margin-top:-16px;'>"
            f"P {macros['protein_g']}g &nbsp;|&nbsp; C {macros['carbs_g']}g &nbsp;|&nbsp; F {macros['fats_g']}g"
            f"</p>",
            unsafe_allow_html=True,
        )

    with ch2:
        section_header("Calorie Log — Last 7 Days")
        history_col = get_history_collection()
        since = datetime.utcnow() - timedelta(days=7)
        history = list(history_col.find({"user_id": user_id, "created_at": {"$gte": since}}, {"_id": 0}))
        st.plotly_chart(_weekly_calorie_bar(history), use_container_width=True, config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Quick info cards ─────────────────────────────────────────────────────
    section_header("Body Composition")
    b1, b2, b3 = st.columns(3)
    with b1:
        metric_card("Height", f"{profile.get('height_cm', '—')} cm", "", "#0F766E")
    with b2:
        metric_card("Weight", f"{profile.get('weight_kg', '—')} kg", "", "#0369A1")
    with b3:
        metric_card("Activity Level", profile.get("activity_level", "—").split("(")[0].strip(), "", "#B45309")
