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
#   TOPBAR FIJA (SOLO HTML)
# -------------------------------

def topbar():
    user = st.session_state.get("user")
    email = user["email"] if user else "Usuario"

    try:
        with open("version.txt", "r", encoding="utf-8") as f:
            version = f.read().strip()
    except:
        version = "v?"

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