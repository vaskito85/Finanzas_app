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

    # Barra superior nativa alineada
    col1, col2, col3, col4 = st.columns([1, 5, 3, 1])

    with col1:
        st.image(logo_url, width=40)

    with col2:
        st.markdown(
            f"### Finanzas App <span style='font-size:0.8em; opacity:0.6;'>({version})</span>",
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(f"**👤 {email}**")

    with col4:
        logout_button()