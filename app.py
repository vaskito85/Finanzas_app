import streamlit as st
from auth import check_auth
from ui import topbar, top_menu

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
    check_auth()

    topbar()
    top_menu()

    st.title("💸 Finanzas Personales")
    st.write("Usá el menú de la izquierda para navegar entre las secciones.")

    st.markdown(
        """
        ## 📌 Secciones disponibles

        ### 📊 Análisis y Reportes
        - **Resumen General**
        - **Movimientos**
        - **Balance por Cuenta**
        - **Dashboard Mensual**
        - **Dashboard Anual**
        - **Comparación Mes a Mes**
        - **Proyección Financiera (Forecast)**

        ### 🧭 Gestión y Control
        - **Cargar Movimiento**
        - **Importar CSV**
        - **Objetivos Financieros**
        - **Alertas Automáticas**

        ### 🛠 Sistema
        - Multiusuario
        - Etiquetas manuales + sugeridas
        - Modo móvil optimizado
        """
    )


if __name__ == "__main__":
    main()