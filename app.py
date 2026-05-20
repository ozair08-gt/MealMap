"""
Main Streamlit app entry point.
Multi-page navigation with auth system.
"""

import streamlit as st
from datetime import datetime
from database import check_connection, seed_meals_if_empty
from auth import is_logged_in, logout, create_user, login_user
from utils import apply_base_styles
from pages import dashboard, profile, recommendations, analytics

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MealMap",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_base_styles()

# ── Session state init ───────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "page" not in st.session_state:
    st.session_state["page"] = "Dashboard"

st.markdown("""
<style>
[data-testid="stSidebarNav"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)


def render_auth_page():
    """Login/signup page."""
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(
            """
            <div style="padding: 40px 30px; text-align: center;">
                <h1 style="font-size: 2.5rem; color: #0F766E; margin-bottom: 10px;">🥗 MealMap</h1>
                <p style="color: #64748B; font-size: 1.05rem; margin-bottom: 30px;">
                    Personalised meal recommendations for your health.
                </p>
                <div style="background: #F0FDF4; padding: 20px 16px; border-radius: 10px; border-left: 4px solid #22C55E;">
                    <p style="color: #15803D; font-size: 0.9rem; margin: 0;">
                        ✓ Personalised recommendations<br>
                        ✓ Supports 5 medical conditions<br>
                        ✓ Personalized nutrition tracking<br>
                        ✓ Weekly meal planning
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        with tab1:
            st.markdown("### Welcome Back")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pwd")
            if st.button("Login", use_container_width=True):
                result = login_user(email, password)
                if result["success"]:
                    st.session_state["authenticated"] = True
                    st.session_state["user_id"] = result["user_id"]
                    st.session_state["username"] = result["username"]
                    st.session_state["email"] = result["email"]
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error(result["error"])

        with tab2:
            st.markdown("### Create Account")
            new_username = st.text_input("Username", key="signup_user")
            new_email = st.text_input("Email", key="signup_email")
            new_pwd = st.text_input("Password", type="password", key="signup_pwd")
            new_pwd_confirm = st.text_input("Confirm Password", type="password", key="signup_pwd_confirm")

            if st.button("Sign Up", use_container_width=True):
                if new_pwd != new_pwd_confirm:
                    st.error("Passwords do not match.")
                elif len(new_pwd) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    result = create_user(new_username, new_email, new_pwd)
                    if result["success"]:
                        st.success("Account created! Please log in.")
                    else:
                        st.error(result["error"])


def render_main_app():
    """Authenticated app with sidebar navigation."""
    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding: 20px 16px; border-bottom: 1px solid #E2E8F0; margin-bottom: 20px;">
                <h2 style="color: #0F766E; font-size: 1.1rem; margin: 0 0 4px 0;">MealMap</h2>
                <p style="color: #64748B; font-size: 0.8rem; margin: 0;">
                    Logged in as <b>{st.session_state.get('username', 'User')}</b>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        pages = ["Dashboard", "Profile", "Recommendations", "Analytics"]
        icons = ["📊", "👤", "🍽️", "📈"]

        for i, page in enumerate(pages):
            if st.button(f"{icons[i]} {page}", use_container_width=True, key=f"nav_{page}"):
                st.session_state["page"] = page

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.session_state["page"] = "Dashboard"
            st.rerun()

    # ── Page router ──────────────────────────────────────────────────────────
    page = st.session_state.get("page", "Dashboard")

    if page == "Dashboard":
        dashboard.render()
    elif page == "Profile":
        profile.render()
    elif page == "Recommendations":
        recommendations.render()
    elif page == "Analytics":
        analytics.render()


# ── Main entry ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Check DB connection
    if not check_connection():
        st.error(
            "⚠️ Cannot connect to MongoDB. "
            "Please ensure MongoDB Atlas is configured and MONGODB_URI is set in .env"
        )
        st.stop()

    # Seed meals on first load
    seed_meals_if_empty()

    # Route based on auth state
    if is_logged_in():
        render_main_app()
    else:
        render_auth_page()
