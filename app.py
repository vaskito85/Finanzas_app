import streamlit as st
from auth import check_auth
from ui import topbar

st.set_page_config(
    page_title="Finanzas Personales",
    page_icon="💸",
    layout="wide"
)

# Cargar estilos ANTES de dibujar UI
try:
    with open("styles.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass


def main():
    # Autenticación
    check_auth()

    # Barra superior
    topbar()

    # Título principal
    st.markdown("## 💸 Finanzas Personales")
    st.markdown("Bienvenido a tu panel de control financiero.")

    st.markdown("---")

    # Secciones organizadas en columnas
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📊 Análisis")
        st.markdown("""
        - **Resumen General**  
        - **Movimientos**  
        - **Balance por Cuenta**  
        - **Dashboard Mensual**  
        - **Dashboard Anual**  
        - **Comparación Mes a Mes**  
        - **Proyección Financiera (Forecast)**  
        """)

    with col2:
        st.markdown("### 🧭 Gestión")
        st.markdown("""
        - **Cargar Movimiento**  
        - **Importar CSV**  
        - **Objetivos Financieros**  
        - **Alertas Automáticas**  
        """)

    with col3:
        st.markdown("### 🛠 Sistema")
        st.markdown("""
        - Multiusuario  
        - Etiquetas inteligentes  
        - Modo móvil optimizado  
        - Seguridad con RLS  
        """)

    st.markdown("---")
    st.info("Usá el menú de la izquierda para navegar entre las secciones.")


if __name__ == "__main__":
    main()