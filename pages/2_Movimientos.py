import streamlit as st
import pandas as pd

from auth import check_auth
from ui import topbar, top_menu
from models import listar_movimientos
from db import eliminar_movimiento_logico
from catalogos import obtener_cuentas, obtener_categorias


def main():
    check_auth()
    topbar()
    top_menu()

    if "user" not in st.session_state:
        st.error("No hay usuario autenticado.")
        st.stop()

    usuario_id = st.session_state["user"]["id"]

    st.title("📄 Movimientos")

    # Obtener movimientos del usuario
    movimientos = listar_movimientos(usuario_id)

    if not movimientos:
        st.info("Todavía no hay movimientos cargados.")
        return

    # Convertir a DataFrame
    df = pd.DataFrame([m.__dict__ for m in movimientos])

    # Obtener catálogos desde Supabase
    cuentas = obtener_cuentas(usuario_id)
    categorias = obtener_categorias(usuario_id)

    st.subheader("Filtros")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        fecha_desde = st.date_input("Fecha desde", value=None)
    with col2:
        fecha_hasta = st.date_input("Fecha hasta", value=None)
    with col3:
        cuenta_filtro = st.selectbox("Cuenta", ["Todas"] + cuentas)
    with col4:
        categoria_filtro = st.selectbox("Categoría", ["Todas"] + categorias)

    # Aplicar filtros
    if fecha_desde:
        df = df[df["fecha"] >= str(fecha_desde)]
    if fecha_hasta:
        df = df[df["fecha"] <= str(fecha_hasta)]
    if cuenta_filtro != "Todas":
        df = df[df["cuenta"] == cuenta_filtro]
    if categoria_filtro != "Todas":
        df = df[df["categoria"] == categoria_filtro]

    st.subheader("Listado de movimientos")

    if df.empty:
        st.info("No hay movimientos que coincidan con los filtros seleccionados.")
        return

    st.dataframe(df[["id", "fecha", "categoria", "tipo", "descripcion", "monto", "cuenta"]])

    st.subheader("🗑 Borrar movimiento (lógico)")

    ids = df["id"].tolist()
    if not ids:
        st.info("No hay movimientos para borrar con los filtros actuales.")
        return

    id_sel = st.selectbox("Seleccionar ID a borrar", ids)

    if st.button("Borrar seleccionado"):
        if eliminar_movimiento_logico(usuario_id, id_sel):
            st.success("Movimiento marcado como borrado.")
            st.rerun()
        else:
            st.error("Error al borrar movimiento.")


if __name__ == "__main__":
    main()