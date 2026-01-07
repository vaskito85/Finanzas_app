import streamlit as st
from auth import logout_button

# -------------------------------
#   TOPBAR NATIVA (SIN HTML)
# -------------------------------

def topbar():
    user = st.session_state.get("user")
    email = user.get("email", "Usuario") if user else "Usuario"

    try:
        with open("version.txt", "r", encoding="utf-8") as f:
            version = f.read().strip()
    except:
        version = "v?"

    logo_url = "https://raw.githubusercontent.com/vaskito85/Finanzas_app/main/assets/logo.svg"

    # Barra superior nativa
    col_logo, col_title, col_user = st.columns([1, 6, 3])

    with col_logo:
        st.image(logo_url, width=40)

    with col_title:
        st.markdown(
            f"### Finanzas App "
            f"<span style='font-size:0.8em; opacity:0.6;'>({version})</span>",
            unsafe_allow_html=True
        )

    with col_user:
        st.markdown(f"**👤 {email}**")


# -------------------------------
#   BOTÓN LOGOUT ARRIBA A LA DERECHA
# -------------------------------

def top_menu():
    col1, col2 = st.columns([9, 1])

    with col1:
        pass

    with col2:
        logout_button()