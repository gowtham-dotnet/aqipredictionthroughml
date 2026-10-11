"""UI style helpers for Streamlit AQI app."""

import streamlit as st


def apply_page_config_and_styles() -> None:
    """Apply page configuration and custom CSS styles."""
    st.set_page_config(page_title="AQI Predictor & Live Data", layout="wide")

    st.markdown(
        """
        <style>
        :root {
            --bg-base: #0c1424;
            --bg-elev: #111d34;
            --surface-1: #15233d;
            --surface-2: #1a2b49;
            --text-primary: #eaf1ff;
            --text-secondary: #b4c3df;
            --text-muted: #8ea0c2;
            --accent-1: #0ea5a4;
            --accent-2: #1ec58f;
            --border-soft: rgba(150, 170, 210, 0.22);
            --shadow-soft: 0 16px 42px rgba(2, 8, 22, 0.45);
        }

        *, *::before, *::after {
            box-sizing: border-box;
        }

        html, body {
            overflow-x: hidden;
        }

        .stApp {
            min-width: 320px;
            background:
                radial-gradient(900px 520px at 6% 10%, rgba(31, 197, 143, 0.14), transparent 58%),
                radial-gradient(760px 420px at 92% 22%, rgba(14, 165, 164, 0.12), transparent 62%),
                linear-gradient(150deg, var(--bg-base) 0%, #0f1a2e 45%, #0b1324 100%);
            color: var(--text-primary);
        }

        /* Streamlit chrome: these selectors are intentionally unqualified
           because Streamlit's sidebar/header element type varies by version. */
        [data-testid="stHeader"],
        [data-testid="stToolbar"] {
            background: #0c1424 !important;
            border-bottom: 1px solid rgba(150, 170, 210, 0.18) !important;
        }

        [data-testid="stHeader"] *,
        [data-testid="stToolbar"] * {
            color: var(--text-primary) !important;
        }

        .block-container,
        [data-testid="stMainBlockContainer"] {
            max-width: 1440px;
            margin: 0 auto;
            padding: clamp(1.25rem, 2.5vw, 2.5rem) clamp(1rem, 3vw, 3rem) 3rem;
        }

        [data-testid="stHorizontalBlock"] {
            align-items: stretch;
            gap: clamp(0.85rem, 1.6vw, 1.5rem);
        }

        [data-testid="stColumn"] {
            min-width: 0;
        }

        [data-testid="stSidebar"],
        [data-testid="stSidebarContent"],
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #101d34 0%, #0b1527 100%);
            border-right: 1px solid var(--border-soft);
        }

        [data-testid="stSidebar"] > div,
        [data-testid="stSidebarContent"],
        section[data-testid="stSidebar"] > div:first-child {
            background: transparent !important;
            padding-top: 1rem;
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            color: var(--text-primary) !important;
        }

        h1, h2, h3 {
            letter-spacing: -0.02em;
            color: var(--text-primary) !important;
        }

        h1 {
            margin-bottom: 0.2rem !important;
        }

        h2, h3 {
            margin-top: 1.75rem !important;
            margin-bottom: 0.65rem !important;
        }

        .stButton > button,
        div[data-testid="stFormSubmitButton"] > button {
            border: 1px solid rgba(55, 236, 190, 0.42) !important;
            background: linear-gradient(130deg, var(--accent-1), var(--accent-2)) !important;
            color: #f7ffff !important;
            font-size: 0.95rem !important;
            font-weight: 650 !important;
            border-radius: 12px !important;
            min-height: 2.85rem !important;
            letter-spacing: 0.01em;
            box-shadow: 0 8px 22px rgba(26, 197, 155, 0.3);
            transition: transform 0.12s ease, box-shadow 0.2s ease, filter 0.2s ease;
            width: 100%;
        }

        .stButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 12px 28px rgba(26, 197, 155, 0.35);
            filter: saturate(1.06);
        }

        .stButton > button:focus-visible,
        div[data-testid="stFormSubmitButton"] > button:focus-visible {
            outline: 2px solid rgba(110, 255, 222, 0.6) !important;
            outline-offset: 1px !important;
        }

        .stTextInput label {
            color: var(--text-secondary) !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
        }

        /* Streamlit/BaseWeb uses several nested elements for text and password
           inputs. Style every layer so native light input defaults cannot leak
           through on the login page. */
        [data-testid="stTextInput"] [data-baseweb="input"],
        [data-testid="stTextInput"] [data-baseweb="input"] > div,
        [data-testid="stTextInput"] [data-baseweb="base-input"],
        [data-testid="stTextInput"] [data-baseweb="base-input"] > div,
        [data-testid="stTextInput"] input,
        .stTextInput input {
            background: #14223b !important;
            border-color: rgba(130, 156, 200, 0.48) !important;
            border-radius: 10px !important;
            color: #f2f7ff !important;
            min-height: 2.55rem;
        }

        [data-testid="stTextInput"] [data-baseweb="input"] input,
        [data-testid="stTextInput"] [data-baseweb="base-input"] input,
        [data-testid="stTextInput"] textarea,
        [data-baseweb="input"] input,
        [data-baseweb="base-input"] input,
        [data-baseweb="input"] textarea {
            color: #f2f7ff !important;
            -webkit-text-fill-color: #f2f7ff !important;
            caret-color: #f2f7ff !important;
        }

        [data-baseweb="input"] button,
        [data-baseweb="input"] svg {
            color: #dbe8ff !important;
            fill: currentColor;
        }

        .stTextInput input::placeholder {
            color: rgba(177, 196, 230, 0.64) !important;
        }

        .stTextInput input:focus {
            border-color: rgba(52, 225, 181, 0.62) !important;
            box-shadow: 0 0 0 0.14rem rgba(52, 225, 181, 0.18) !important;
        }

        .stMetric {
            background: linear-gradient(145deg, rgba(24, 39, 66, 0.88), rgba(18, 31, 52, 0.82));
            border: 1px solid rgba(126, 152, 196, 0.26);
            padding: 12px 14px;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(4, 10, 24, 0.3);
            min-height: 100%;
        }

        div[data-testid="stForm"] {
            border: 1px solid rgba(126, 152, 196, 0.26);
            border-radius: 14px;
            background: rgba(15, 26, 45, 0.42);
            padding: 0.85rem;
        }

        [data-testid="stSidebar"] div[data-testid="stForm"] {
            background: rgba(17, 29, 49, 0.82);
            border-color: rgba(130, 156, 200, 0.28);
        }

        [data-testid="stAlert"] {
            color: #eef5ff !important;
            background: rgba(26, 54, 88, 0.84) !important;
            border: 1px solid rgba(104, 173, 255, 0.35) !important;
            border-radius: 12px !important;
        }

        [data-testid="stAlert"] *,
        [data-testid="stAlert"] p,
        [data-testid="stAlert"] span {
            color: #eef5ff !important;
        }

        div[data-testid="stMetricLabel"] {
            color: #b8caea !important;
            font-weight: 600 !important;
            opacity: 1 !important;
        }

        div[data-testid="stMetricValue"] {
            color: #f2f7ff !important;
            font-weight: 760 !important;
            opacity: 1 !important;
        }

        div[data-testid="stMetricDelta"] {
            color: #35d39a !important;
            opacity: 1 !important;
            font-weight: 620 !important;
        }

        .stSelectbox label,
        .stNumberInput label,
        .stMarkdown,
        .stCaption,
        [data-testid="stCaptionContainer"] {
            color: var(--text-primary) !important;
            opacity: 1 !important;
        }

        [data-testid="stExpander"] {
            background: rgba(17, 29, 49, 0.72);
            border: 1px solid rgba(130, 156, 200, 0.28);
            border-radius: 12px;
        }

        [data-testid="stExpander"] summary,
        [data-testid="stExpander"] summary * {
            color: var(--text-primary) !important;
        }

        [data-testid="stVerticalBlock"] [data-testid="stPlotlyChart"] {
            background: rgba(18, 31, 52, 0.58);
            border: 1px solid rgba(121, 146, 188, 0.2);
            border-radius: 12px;
            padding: 0.35rem;
            overflow: hidden;
        }

        .login-shell {
            width: min(1180px, 100%);
            margin: clamp(1.25rem, 2.5vw, 2.8rem) auto 1rem;
            padding: 0;
        }

        .brand-panel {
            min-height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 0.88rem;
            padding: clamp(1rem, 1.8vw, 1.55rem);
            max-width: none;
            border: 1px solid rgba(118, 138, 176, 0.16);
            border-radius: 18px;
            background: linear-gradient(142deg, rgba(29, 47, 80, 0.44), rgba(14, 23, 40, 0.18));
        }

        .brand-badge {
            display: inline-flex;
            align-items: center;
            width: fit-content;
            font-size: 0.72rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            font-weight: 640;
            color: #d8fff4;
            background: linear-gradient(130deg, rgba(23, 168, 158, 0.3), rgba(30, 197, 143, 0.24));
            border: 1px solid rgba(74, 223, 185, 0.32);
            border-radius: 999px;
            padding: 0.36rem 0.68rem;
        }

        .brand-title {
            font-size: clamp(1.5rem, 2.2vw, 2.2rem);
            line-height: 1.24;
            font-weight: 740;
            letter-spacing: -0.018em;
            color: var(--text-primary);
            margin: 0.12rem 0 0.28rem 0;
            max-width: 21ch;
        }

        .brand-accent-line {
            width: 86px;
            height: 3px;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--accent-1), var(--accent-2));
            margin: 0.1rem 0 0.35rem 0;
            opacity: 0.95;
        }

        .brand-text {
            font-size: 0.95rem;
            line-height: 1.64;
            color: var(--text-secondary);
            max-width: 56ch;
            margin-bottom: 0.22rem;
        }

        .chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.08rem;
        }

        .chip {
            display: inline-flex;
            align-items: center;
            font-size: 0.77rem;
            line-height: 1;
            font-weight: 530;
            color: #dcf4ff;
            padding: 0.5rem 0.64rem;
            border-radius: 11px;
            border: 1px solid rgba(130, 156, 200, 0.3);
            background: linear-gradient(145deg, rgba(25, 38, 62, 0.78), rgba(22, 35, 57, 0.58));
        }

        .mini-stats {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 0.22rem;
        }

        .mini-stat {
            display: flex;
            flex-direction: column;
            gap: 0.14rem;
            min-width: 108px;
            padding: 0.58rem 0.7rem;
            border-radius: 11px;
            border: 1px solid rgba(120, 144, 186, 0.26);
            background: rgba(17, 29, 49, 0.68);
            box-shadow: 0 6px 18px rgba(3, 9, 20, 0.28);
        }

        .mini-stat strong {
            font-size: 1.07rem;
            color: #f2f8ff;
            line-height: 1.1;
        }

        .mini-stat span {
            font-size: 0.75rem;
            color: var(--text-muted);
            line-height: 1.22;
        }

        .st-key-login_card {
            width: 100%;
            max-width: 468px;
            margin: 0 auto;
            padding: clamp(1.2rem, 2vw, 1.95rem);
            border: 1px solid var(--border-soft);
            border-radius: 16px;
            background:
                linear-gradient(150deg, rgba(20, 34, 58, 0.94), rgba(16, 28, 47, 0.9));
            box-shadow: var(--shadow-soft);
        }

        .st-key-login_card {
            margin-top: 0.25rem;
        }

        /* The login card already provides the visual container. Do not add a
           second bordered box around its form fields. */
        .st-key-login_card div[data-testid="stForm"] {
            background: transparent !important;
            border: 0 !important;
            padding: 0 !important;
        }

        /* Scope the entered-value colour to the native keyed login container.
           This selector is independent of Streamlit's changing input test IDs. */
        .st-key-login_card input,
        .st-key-login_card input[type="text"],
        .st-key-login_card input[type="password"] {
            color: #f2f7ff !important;
            -webkit-text-fill-color: #f2f7ff !important;
            caret-color: #f2f7ff !important;
        }

        /* Browsers apply their own pale background to saved/autofilled login
           values after the user selects or enters credentials. This must be
           styled separately from the normal empty input state. */
        [data-testid="stTextInput"] input:-webkit-autofill,
        [data-testid="stTextInput"] input:-webkit-autofill:hover,
        [data-testid="stTextInput"] input:-webkit-autofill:focus,
        [data-testid="stTextInput"] input:-webkit-autofill:active {
            -webkit-text-fill-color: #f2f7ff !important;
            caret-color: #f2f7ff !important;
            -webkit-box-shadow: 0 0 0 1000px #14223b inset !important;
            box-shadow: 0 0 0 1000px #14223b inset !important;
            transition: background-color 9999s ease-out 0s;
        }

        .login-title {
            font-size: clamp(1.24rem, 1.85vw, 1.55rem);
            font-weight: 720;
            letter-spacing: -0.01em;
            color: #f2f8ff;
            margin-bottom: 0.3rem;
        }

        .login-subtitle {
            font-size: 0.9rem;
            line-height: 1.56;
            color: var(--text-secondary);
            margin-bottom: 0.85rem;
        }

        .role-strip {
            margin-top: 0.72rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.42rem;
        }

        .role-pill {
            font-size: 0.74rem;
            font-weight: 530;
            color: #d7e8ff;
            line-height: 1;
            padding: 0.38rem 0.52rem;
            border-radius: 999px;
            border: 1px solid rgba(130, 156, 200, 0.3);
            background: rgba(22, 37, 63, 0.66);
        }

        .small-note {
            margin-top: 0.7rem;
            font-size: 0.77rem;
            line-height: 1.5;
            color: var(--text-muted);
        }

        @media (max-width: 980px) {
            .block-container,
            [data-testid="stMainBlockContainer"] {
                padding-inline: 1.25rem;
            }

            .login-shell {
                width: min(780px, 100%);
                margin-top: 1rem;
            }

            .brand-panel {
                padding: 0.2rem 0;
                max-width: 100%;
                gap: 0.78rem;
            }

            .brand-title {
                max-width: 25ch;
            }

            .brand-text {
                max-width: 62ch;
            }

            .login-card {
                width: min(560px, 100%);
                margin-top: 0.25rem;
            }
        }

        @media (max-width: 640px) {
            .block-container,
            [data-testid="stMainBlockContainer"] {
                padding: 1rem 0.8rem 2rem;
            }

            [data-testid="stHorizontalBlock"] {
                gap: 0.8rem;
            }

            .login-shell {
                width: 100%;
                margin-top: 0.7rem;
                padding: 0;
            }

            .brand-title {
                font-size: clamp(1.28rem, 7vw, 1.55rem);
                line-height: 1.28;
            }

            .brand-text {
                font-size: 0.9rem;
                line-height: 1.58;
            }

            .chip {
                font-size: 0.74rem;
            }

            .mini-stat {
                min-width: 98px;
            }

            .login-card {
                padding: 1rem;
                border-radius: 14px;
            }

            div[data-testid="stForm"] {
                padding: 0.7rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
