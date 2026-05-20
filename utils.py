"""
Shared UI helpers and utility functions.
"""

import streamlit as st
from datetime import datetime


def apply_base_styles():
    """Inject global CSS for a clean healthcare aesthetic."""
    st.markdown(
        """
        <style>
        body {
            background-color: #0E1117;
            color: #F3F4F6;
        }

        .stApp {
            background-color: #0E1117;
        }

        section[data-testid="stSidebar"] {
            background-color: #161B22;
            border-right: 1px solid #2D3748;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #F3F4F6 !important;
            font-weight: 600;
        }

        p, span, label {
            color: #D1D5DB;
        }

        .stMetric {
            background-color: #1E2633;
            padding: 1rem;
            border-radius: 14px;
            border: 1px solid #2D3748;
        }

        button[kind="primary"] {
            background-color: #14B8A6 !important;
            color: white !important;
            border-radius: 10px !important;
            border: none !important;
            font-weight: 600 !important;
        }

        button[kind="primary"]:hover {
            background-color: #0F9C8D !important;
            color: white !important;
        }

        .stTextInput input,
        .stNumberInput input,
        .stSelectbox div[data-baseweb="select"] {
            background-color: #1E2633 !important;
            color: white !important;
            border: 1px solid #2D3748 !important;
            border-radius: 10px !important;
        }

        [data-testid="stPlotlyChart"] {
            background-color: #1E2633;
            border-radius: 14px;
            padding: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(title: str, value: str, sub: str = "", color: str = "#0F766E"):
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">{title}</div>
            <div class="card-value" style="color:{color}">{value}</div>
            <div class="card-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def meal_card(meal: dict):
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in meal.get("tags", []))
    st.markdown(
        f"""
        <div class="meal-card">
            <h4>{meal.get('name', 'Unnamed Meal')}</h4>
            <div class="meal-meta">
                🔥 {meal.get('calories', '—')} kcal &nbsp;|&nbsp;
                🥩 {meal.get('protein_g', '—')}g protein &nbsp;|&nbsp;
                🌾 {meal.get('carbs_g', '—')}g carbs &nbsp;|&nbsp;
                🧈 {meal.get('fats_g', '—')}g fat
            </div>
            <div style="margin-top:8px">{tags_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def section_header(text: str):
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


def get_today_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")
