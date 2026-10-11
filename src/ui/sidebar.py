"""Sidebar rendering helpers."""

import streamlit as st


def render_sidebar(current_user: dict, current_role: str) -> None:
    """Render sidebar with user info, logout, AQI categories, and WAQI token input."""
    with st.sidebar:
        st.markdown(f"### Welcome, {current_user['username']}")
        st.caption(f"Role: {current_role}")

        if st.button("Logout"):
            st.session_state.auth_user = None
            st.rerun()

        with st.expander("AQI Categories (CPCB)"):
            st.markdown(
                """
- Good (0–50): Minimal impact  
- Satisfactory (51–100): Minor breathing discomfort  
- Moderate (101–200): Breathing discomfort to sensitive people  
- Poor (201–300): Breathing discomfort to most people  
- Very Poor (301–400): Respiratory illness on prolonged exposure  
- Severe (401–500): Affects healthy people
                """
            )

        waqi_token = st.text_input(
            "WAQI Token",
            type="password",
            help="Get free token: aqicn.org/data-platform/token/",
        )
        if waqi_token:
            st.session_state.waqi_token = waqi_token
