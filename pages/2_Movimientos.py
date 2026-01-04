import streamlit as st
import pandas as pd

from auth import check_auth
from ui import topbar, top_menu
from models import listar_movimientos
from db import eliminar_movimiento_logico


def main():
    check_auth()
    topbar()
    top_menu()

    usuario = st.session_state.get("user")
    usuario_id = usuario["id"]

    st.title("📄 Movimientos")

    movimientos = listar_movimientos(usuario_id)

    if not movimientos:
        st.info("Todavía no hay movimientos cargados.")
        return

    df = pd.DataFrame([m.__dict__ for m in movimientos])

    st.subheader("Filtros")

    col1, col2, col3 = st.columns(3)

    with col1:
        fecha_desde = st.date_input("Fecha desde", value=None)
    with col2:
        fecha_hasta = st.date_input("Fecha hasta", value=None)
    with col3:
        categoria = st.text_input("Categoría contiene")

    if fecha_desde:
        df = df[df["fecha"] >= str(fecha_desde)]
    if fecha_hasta:
        df = df[df["fecha"] <= str(fecha_hasta)]
    if categoria:
        df = df[df["categoria"].str.contains(categoria, case=False, na=False)]

    st.subheader("Listado de movimientos")
    st.dataframe(df[["id", "fecha", "categoria", "tipo", "descripcion", "monto", "cuenta"]])

    st.subheader("🗑 Borrar movimiento (lógico)")

    ids = df["id"].tolist()
    id_sel = st.selectbox("Seleccionar ID a borrar", ids)

    if st.button("Borrar seleccionado"):
        if eliminar_movimiento_logico(usuario_id, id_sel):
            st.success("Movimiento marcado como borrado.")
            st.rerun()
        else:
            st.error("Error al borrar movimiento.")


if __name__ == "__main__":
    main()