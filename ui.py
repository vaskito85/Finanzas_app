import streamlit as st
from auth import logout_button

def topbar():
    user = st.session_state.get("user")
    email = user.get("email", "Usuario") if user else "Usuario"

    try:
        with open("version.txt", "r", encoding="utf-8") as f:
            version = f.read().strip()
    except:
        version = "v?"

    logo_url = "https://raw.githubusercontent.com/vaskito85/Finanzas_app/main/assets/logo.svg"

    # Barra superior con mejor alineación
    st.markdown(
        """
        <style>
        .topbar-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 20px;
            background-color: #0E1117;
            border-bottom: 1px solid #333;
            height: 65px;
        }
        .topbar-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .topbar-title {
            font-size: 20px;
            font-weight: 600;
            color: white;
        }
        .topbar-version {
            font-size: 13px;
            opacity: 0.6;
            margin-left: 4px;
        }
        .topbar-user {
            font-size: 15px;
            color: white;
            margin-right: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Layout nativo + HTML para alineación perfecta
    col1, col2 = st.columns([8, 2])

    with col1:
        st.markdown(
            f"""
            <div class="topbar-container">
                <div class="topbar-left">
                    <img src="{logo_url}" width="40">
                    <div class="topbar-title">
                        Finanzas App <span class="topbar-version">({version})</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="topbar-container" style="justify-content: flex-end;">
                <div class="topbar-user">👤 {email}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        logout_button()