import streamlit as st
from auth import logout_button

# -------------------------------
#   TEMA CLARO / OSCURO
# -------------------------------

def init_theme():
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "light"

def toggle_theme():
    st.session_state["theme_mode"] = (
        "dark" if st.session_state["theme_mode"] == "light" else "light"
    )

# -------------------------------
#   TOPBAR FIJA (HTML + CSS)
# -------------------------------

def topbar():
    user = st.session_state.get("user")
    email = user.get("email", "Usuario") if user else "Usuario"

    try:
        with open("version.txt", "r", encoding="utf-8") as f:
            version = f.read().strip()
    except:
        version = "v?"

    # CSS robusto para barra fija + soporte claro/oscuro
    st.markdown("""
        <style>
        /* Variables de color según tema */
        [data-theme="light"] {
            --topbar-bg: #ffffff;
            --topbar-text: #000000;
            --topbar-border: #cccccc;
        }

        [data-theme="dark"] {
            --topbar-bg: #0E1117;
            --topbar-text: #ffffff;
            --topbar-border: #333333;
        }

        /* Barra fija */
        .topbar-container {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background-color: var(--topbar-bg);
            color: var(--topbar-text);
            border-bottom: 1px solid var(--topbar-border);
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 20px;
            font-family: sans-serif;
        }

        .topbar-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .topbar-logo {
            height: 40px;
        }

        .topbar-title {
            font-size: 20px;
            font-weight: bold;
        }

        .topbar-version {
            font-size: 12px;
            opacity: 0.6;
            margin-left: 6px;
        }

        .topbar-user {
            font-size: 14px;
            opacity: 0.9;
        }

        /* Compensación para que el contenido no quede tapado */
        .topbar-spacer {
            margin-top: 70px;
        }
        </style>
    """, unsafe_allow_html=True)

    # HTML de la barra
    st.markdown(f"""
        <div class="topbar-container">
            <div class="topbar-left">
                <img src="assets/logo.svg" class="topbar-logo">
                <div class="topbar-title">
                    Finanzas App <span class="topbar-version">{version}</span>
                </div>
            </div>
            <div class="topbar-user">👤 {email}</div>
        </div>
        <div class="topbar-spacer"></div>
    """, unsafe_allow_html=True)

# -------------------------------
#   BOTONES DE TEMA + LOGOUT
# -------------------------------

def top_menu():
    init_theme()
    mode = st.session_state["theme_mode"]

    col1, col2 = st.columns([9, 1])

    with col1:
        pass

    with col2:
        label = "🌙" if mode == "light" else "☀️"
        if st.button(label, help="Cambiar tema claro/oscuro"):
            toggle_theme()
            st.rerun()

        logout_button()