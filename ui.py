# ui.py

import streamlit as st
from auth import logout_button


# -------------------------------
#   TEMA CLARO / OSCURO
# -------------------------------

def init_theme():
    """Inicializa el modo de tema si no existe."""
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "light"


def toggle_theme():
    """Alterna entre modo claro y oscuro."""
    st.session_state["theme_mode"] = (
        "dark" if st.session_state["theme_mode"] == "light" else "light"
    )


# -------------------------------
#   TOP MENU
# -------------------------------

def top_menu():
    """Barra superior con logo, usuario, tema y logout."""
    init_theme()
    mode = st.session_state["theme_mode"]

    # Colores dinámicos según tema
    bg_color = "#ffffff" if mode == "light" else "#1E1E1E"
    border_color = "#e5e5e5" if mode == "light" else "#333333"
    text_color = "#333333" if mode == "light" else "#f5f5f5"
    subtext_color = "#555555" if mode == "light" else "#cccccc"

    # CSS del topbar
    st.markdown(
        f"""
        <style>
        .topbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.6rem 1rem;
            background-color: {bg_color};
            border-bottom: 1px solid {border_color};
            border-radius: 6px;
            margin-bottom: 1rem;
        }}

        .topbar-left {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .topbar-logo {{
            height: 36px;
        }}

        .topbar-title {{
            font-size: 1.2rem;
            font-weight: 600;
            color: {text_color};
        }}

        .topbar-right {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .topbar-user {{
            font-size: 0.95rem;
            color: {subtext_color};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # Usuario logueado
    user = st.session_state.get("user")

    # Evitar errores si no hay usuario
    user_email = user["email"] if user else "Usuario"

    # Render del topbar
    with st.container():
        st.markdown(
            f"""
            <div class="topbar">
                <div class="topbar-left">
                    <img src="assets/logo.svg" class="topbar-logo" onerror="this.style.display='none'">
                    <div class="topbar-title">Finanzas App</div>
                </div>

                <div class="topbar-right">
                    <div class="topbar-user">👤 {user_email}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Botones: tema + logout
        col1, col2 = st.columns([9, 1])

        with col1:
            pass

        with col2:
            # Botón de tema
            label = "🌙" if mode == "light" else "☀️"
            if st.button(label, help="Cambiar tema claro/oscuro"):
                toggle_theme()
                st.rerun()

            # Botón de logout
            logout_button()