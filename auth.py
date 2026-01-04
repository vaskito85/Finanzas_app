import streamlit as st
from supabase_client import get_supabase_client


def save_session(user):
    """Guarda la sesión persistente en session_state."""
    st.session_state["user"] = {
        "id": user.id,
        "email": user.email,
    }


def clear_session():
    """Elimina la sesión."""
    if "user" in st.session_state:
        del st.session_state["user"]


def check_auth():
    """
    Protege las páginas: si no hay usuario logueado,
    muestra el formulario de login/registro.
    """
    if "user" in st.session_state and st.session_state["user"] is not None:
        return

    supabase = get_supabase_client()

    st.title("🔐 Iniciar sesión")

    tab_login, tab_register = st.tabs(["Ingresar", "Registrarse"])

    # ---------- LOGIN ----------
    with tab_login:
        email = st.text_input("Email")
        password = st.text_input("Contraseña", type="password")

        if st.button("Entrar"):
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

    # ---------- REGISTRO ----------
    with tab_register:
        email_r = st.text_input("Email nuevo")
        pass_r = st.text_input("Contraseña nueva", type="password")
        pass_r2 = st.text_input("Repetir contraseña", type="password")

        if st.button("Crear cuenta"):
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
                        st.success("Cuenta creada. Revisá tu email si se requiere confirmación.")
                    else:
                        st.error("No se pudo crear la cuenta.")

                except Exception as e:
                    st.error(f"Error al registrar usuario: {e}")

    st.stop()


def logout_button():
    """Botón para cerrar sesión."""
    if st.button("Cerrar sesión"):
        clear_session()
        st.rerun()