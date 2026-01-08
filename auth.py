import streamlit as st
from supabase_client import get_supabase_client

def save_session(user):
    st.session_state["user"] = {
        "id": user.id,
        "email": user.email,
    }

def clear_session():
    if "user" in st.session_state:
        del st.session_state["user"]

def check_auth():
    if "user" in st.session_state and st.session_state["user"] is not None:
        return

    supabase = get_supabase_client()

    st.markdown("## 🔐 Iniciar sesión")

    tab_login, tab_register = st.tabs(["Ingresar", "Registrarse"])

    with tab_login:
        st.markdown("### Accedé a tu cuenta")
        email = st.text_input("📧 Email")
        password = st.text_input("🔒 Contraseña", type="password")

        if st.button("➡️ Entrar", use_container_width=True):
            if not email or not password:
                st.error("Completá email y contraseña.")
            else:
                try:
                    result = supabase.auth.sign_in_with_password(
                        {"email": email, "password": password}
                    )
                    if result.user:
                        save_session(result.user)
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas.")
                except Exception as e:
                    st.error(f"Error al iniciar sesión: {e}")

    with tab_register:
        st.markdown("### Creá una cuenta nueva")
        email_r = st.text_input("📧 Email nuevo")
        pass_r = st.text_input("🔒 Contraseña nueva", type="password")
        pass_r2 = st.text_input("🔁 Repetir contraseña", type="password")

        if st.button("🆕 Crear cuenta", use_container_width=True):
            if not email_r or not pass_r or not pass_r2:
                st.error("Completá todos los campos.")
            elif pass_r != pass_r2:
                st.error("Las contraseñas no coinciden.")
            else:
                try:
                    result = supabase.auth.sign_up(
                        {"email": email_r, "password": pass_r}
                    )
                    if result.user:
                        st.success("✅ Cuenta creada. Revisá tu email si se requiere confirmación.")
                    else:
                        st.error("No se pudo crear la cuenta.")
                except Exception as e:
                    st.error(f"Error al registrar usuario: {e}")

    st.stop()

def logout_button():
    st.markdown(
        """
        <style>
        .logout-btn button {
            background-color: #d9534f;
            color: white;
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
            border-radius: 6px;
            border: none;
        }
        .logout-btn button:hover {
            background-color: #c9302c;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    with st.container():
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("Cerrar sesión"):
            clear_session()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)