"""
Analytics page: nutrition trends, macro breakdown over time, insights.
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import get_profiles_collection, get_history_collection
from utils import apply_base_styles, page_header, section_header, metric_card


def _load_profile(user_id: str) -> dict:
    col = get_profiles_collection()
    doc = col.find_one({"user_id": user_id})
    if doc:
        doc.pop("_id", None)
    return doc or {}


def _macro_trend(history: list) -> go.Figure:
    """Line chart: protein, carbs, fats over time."""
    daily = {}
    for rec in history:
        ts = rec.get("created_at")
        if ts:
            key = ts.strftime("%Y-%m-%d")
            if key not in daily:
                daily[key] = {"protein": 0, "carbs": 0, "fats": 0}
            daily[key]["protein"] += rec.get("protein_g", 0)
            daily[key]["carbs"] += rec.get("carbs_g", 0)
            daily[key]["fats"] += rec.get("fats_g", 0)

    sorted_days = sorted(daily.keys())
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=sorted_days,
            y=[daily[d]["protein"] for d in sorted_days],
            name="Protein (g)",
            line=dict(color="#22C55E", width=2),
            mode="lines+markers",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=sorted_days,
            y=[daily[d]["carbs"] for d in sorted_days],
            name="Carbs (g)",
            line=dict(color="#F59E0B", width=2),
            mode="lines+markers",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=sorted_days,
            y=[daily[d]["fats"] for d in sorted_days],
            name="Fats (g)",
            line=dict(color="#EF4444", width=2),
            mode="lines+markers",
        )
    )
    fig.update_layout(
        title="Macro Intake Over Time",
        xaxis_title="Date",
        yaxis_title="Grams",
        hovermode="x unified",
        margin=dict(t=40, b=20, l=20, r=20),
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=10),
    )
    return fig


def _meal_type_dist(history: list) -> go.Figure:
    """Pie chart: meals logged by type."""
    types = {}
    for rec in history:
        mt = rec.get("meal_type", "other")
        types[mt] = types.get(mt, 0) + 1

    fig = go.Figure(
        go.Pie(
            labels=list(types.keys()),
            values=list(types.values()),
            marker_colors=["#0D9488", "#0369A1", "#7C3AED", "#EC4899"],
            textinfo="label+percent",
            textfont_size=11,
        )
    )
    fig.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        height=240,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=10),
    )
    return fig


def render():
    apply_base_styles()
    page_header("Analytics & Insights", "Track your nutrition trends and progress.")

    user_id = st.session_state.get("user_id", "")
    profile = _load_profile(user_id)

    if not profile:
        st.warning("Complete your profile first.")
        return

    col = get_history_collection()
    since = datetime.utcnow() - timedelta(days=30)
    history = list(
        col.find({"user_id": user_id, "created_at": {"$gte": since}}, {"_id": 0})
           .sort("created_at", 1)
    )

    if not history:
        st.info("No meal history yet. Log meals to see analytics.")
        return

    # ── Summary stats ────────────────────────────────────────────────────────
    section_header("Last 30 Days Summary")
    total_cal = sum(r.get("calories", 0) for r in history)
    total_protein = sum(r.get("protein_g", 0) for r in history)
    meals_logged = len(history)
    avg_cal = total_cal // meals_logged if meals_logged > 0 else 0

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        metric_card("Meals Logged", str(meals_logged), "over 30 days", "#0D9488")
    with s2:
        metric_card("Total Calories", f"{int(total_cal)}", "kcal consumed", "#0F766E")
    with s3:
        metric_card("Avg per Meal", f"{avg_cal}", "kcal", "#0369A1")
    with s4:
        metric_card("Total Protein", f"{int(total_protein)}g", "logged", "#22C55E")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ───────────────────────────────────────────────────────────────
    ch1, ch2 = st.columns([2, 1])
    with ch1:
        section_header("Macro Trends")
        st.plotly_chart(_macro_trend(history), use_container_width=True, config={"displayModeBar": False})

    with ch2:
        section_header("Meal Types")
        st.plotly_chart(_meal_type_dist(history), use_container_width=True, config={"displayModeBar": False})

    # ── Insights ─────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Insights")
    col1, col2 = st.columns(2)
    with col1:
        avg_daily_cal = total_cal // max(len(set(r["created_at"].strftime("%Y-%m-%d") for r in history if r.get("created_at"))), 1)
        st.metric("Avg Daily Intake", f"{avg_daily_cal} kcal", delta=None)
    with col2:
        most_common = max(set(r.get("meal_type", "—") for r in history), key=lambda x: sum(1 for r in history if r.get("meal_type") == x), default="—")
        st.metric("Most Logged Meal Type", most_common.title())
