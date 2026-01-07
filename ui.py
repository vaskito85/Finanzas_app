import streamlit as st
from auth import logout_button

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

    # ⚠️ Cambiá esta URL por la de tu repo real
    logo_url = "https://github.com/vaskito85/Finanzas_app/blob/main/assets/logo.svg"

    st.markdown(
        f"""
        <style>
        .custom-topbar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background-color: #0E1117;
            color: white;
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 20px;
            font-family: sans-serif;
            border-bottom: 1px solid #333;
        }}

        .custom-topbar-left {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .custom-topbar-logo {{
            height: 40px;
        }}

        .custom-topbar-title {{
            font-size: 20px;
            font-weight: bold;
        }}

        .custom-topbar-version {{
            font-size: 12px;
            opacity: 0.6;
            margin-left: 6px;
        }}

        .custom-topbar-user {{
            font-size: 14px;
            opacity: 0.9;
        }}

        /* Compensar el espacio de la barra para que no tape el contenido */
        .custom-topbar-spacer {{
            margin-top: 70px;
        }}
        </style>

        <div class="custom-topbar">
            <div class="custom-topbar-left">
                <img src="{logo_url}" class="custom-topbar-logo">
                <div class="custom-topbar-title">
                    Finanzas App <span class="custom-topbar-version">{version}</span>
                </div>
            </div>
            <div class="custom-topbar-user">👤 {email}</div>
        </div>
        <div class="custom-topbar-spacer"></div>
        """,
        unsafe_allow_html=True,
    )

# -------------------------------
#   BOTÓN LOGOUT ARRIBA A LA DERECHA
# -------------------------------

def top_menu():
    col1, col2 = st.columns([9, 1])

    with col1:
        pass

    with col2:
        logout_button()