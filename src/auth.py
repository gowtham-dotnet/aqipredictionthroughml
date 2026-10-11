import os
import json
import hashlib
import streamlit as st


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@st.cache_data
def load_users():
    users_file = "users.json"
    if not os.path.exists(users_file):
        return {}
    try:
        with open(users_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        users = data.get("users", [])
        return {u["username"]: u for u in users if u.get("active", False)}
    except Exception:
        return {}


def authenticate(username: str, password: str):
    users = load_users()
    user = users.get(username)
    if not user:
        return None
    if user.get("password_hash") == hash_password(password):
        return user
    return None


PERMISSIONS = {
    "basic": {"manual_predict"},
    "analyst": {"manual_predict", "charts", "difference_check"},
    "admin": {"manual_predict", "charts", "map", "difference_check"},
}


def require_login():
    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None

    if st.session_state.auth_user is None:
        st.markdown("## Air Quality Prediction & Monitoring Platform")
        st.caption("Secure access to forecasting, analytics, and geospatial AQI monitoring.")

        st.markdown('<div class="login-shell">', unsafe_allow_html=True)
        left_col, right_col = st.columns([1.1, 0.9], gap="large")

        with left_col:
            st.markdown("""
            <div class="brand-panel">
                <div class="brand-badge">Environmental Intelligence Platform</div>
                <div class="brand-title">Predict, monitor, and explore air quality with confidence.</div>
                <div class="brand-accent-line"></div>
                <div class="brand-text">
                    Build environmental decisions on trusted intelligence from one secure platform.
                    Monitor live AQI, forecast trends with ML, and compare regional patterns across
                    India, Ireland, and major global cities.
                </div>
                <div class="chip-row">
                    <span class="chip">🌍 Live AQI Monitoring</span>
                    <span class="chip">📈 ML-based Forecasting</span>
                    <span class="chip">🧭 Regional Analytics</span>
                    <span class="chip">🔐 Secure Role Access</span>
                </div>
                <div class="mini-stats">
                    <div class="mini-stat"><strong>125+</strong><span>Indian cities</span></div>
                    <div class="mini-stat"><strong>26</strong><span>Ireland counties</span></div>
                    <div class="mini-stat"><strong>12+</strong><span>Global cities</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with right_col:
            # Native Streamlit container: widgets cannot reliably be nested inside
            # HTML divs created by separate st.markdown calls.
            with st.container(border=True, key="login_card"):
                st.markdown('<div class="login-title">Sign in</div>', unsafe_allow_html=True)
                st.markdown('<div class="login-subtitle">Sign in to continue with secure access to prediction, analytics, and geospatial monitoring.</div>', unsafe_allow_html=True)

                with st.form("login_form", border=False, enter_to_submit=False):
                    login_username = st.text_input(
                        "Username",
                        placeholder="Enter your username",
                        autocomplete="username",
                    )
                    login_password = st.text_input(
                        "Password",
                        type="password",
                        placeholder="Enter your password",
                        autocomplete="current-password",
                    )
                    login_submit = st.form_submit_button("Continue securely", type="primary", width="stretch")

                st.markdown("""
                <div class="role-strip">
                    <span class="role-pill">Basic · Predict</span>
                    <span class="role-pill">Analyst · Charts</span>
                    <span class="role-pill">Admin · Full map access</span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<div class="small-note">Protected workspace · Enterprise-grade role controls enabled. Contact the administrator for elevated permissions.</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        if login_submit:
            user_obj = authenticate(login_username.strip(), login_password)
            if user_obj:
                st.session_state.auth_user = {
                    "username": user_obj["username"],
                    "role": user_obj["role"],
                }
                st.session_state.just_logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials. Please verify username/password and try again.")
        st.stop()

    current_user = st.session_state.auth_user
    current_role = current_user.get("role", "basic")
    allowed_features = PERMISSIONS.get(current_role, set())
    return current_user, current_role, allowed_features
