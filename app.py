# app.py

import streamlit as st
from auth import check_auth
from ui import top_menu

# ?? set_page_config SIEMPRE debe ir antes de cualquier output
st.set_page_config(
    page_title="Finanzas Personales",
    page_icon="??",
    layout="wide"
)


def main():
    # Seguridad: si no hay usuario, muestra login/registro
    check_auth()

    # Men迆 superior (solo visible si hay usuario)
    top_menu()

    # Cargar estilos personalizados
    try:
        with open("styles.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

    st.title("?? Finanzas Personales")
    st.write("Us芍 el men迆 de la izquierda para navegar entre las secciones.")

    st.markdown(
        """
        ## ?? Secciones disponibles

        ### ?? An芍lisis y Reportes
        - **Resumen General**
        - **Movimientos**
        - **Balance por Cuenta**
        - **Dashboard Mensual**
        - **Dashboard Anual**
        - **Comparaci車n Mes a Mes**
        - **Proyecci車n Financiera (Forecast)**

        ### ?? Gesti車n y Control
        - **Cargar Movimiento**
        - **Importar CSV**
        - **Objetivos Financieros**
        - **Alertas Autom芍ticas**

        ### ?? Sistema
        - Multiusuario
        - Etiquetas manuales + sugeridas
        - Modo m車vil optimizado
        """
    )


if __name__ == "__main__":
    main()