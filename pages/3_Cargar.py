import streamlit as st
import json

from auth import check_auth
from ui import topbar, top_menu
from db import insertar_movimiento


def main():
    check_auth()
    topbar()
    top_menu()

    usuario = st.session_state.get("user")
    usuario_id = usuario["id"]

    st.title("➕ Cargar Movimiento")

    with st.form("form_movimiento"):
        fecha = st.date_input("Fecha")
        categoria = st.text_input("Categoría")
        tipo = st.selectbox("Tipo", ["ingreso", "gasto"])
        descripcion = st.text_input("Descripción")
        monto = st.number_input("Monto", min_value=0.0, step=0.01)
        cuenta = st.text_input("Cuenta")
        etiquetas = st.text_input("Etiquetas (separadas por coma)")

        submitted = st.form_submit_button("Guardar")

    if submitted:
        etiquetas_list = [e.strip() for e in etiquetas.split(",") if e.strip()]
        etiquetas_json = json.dumps(etiquetas_list, ensure_ascii=False)

        ok = insertar_movimiento(
            usuario_id=usuario_id,
            fecha=str(fecha),
            categoria=categoria,
            tipo=tipo,
            descripcion=descripcion,
            monto=float(monto),
            cuenta=cuenta,
            etiquetas_json=etiquetas_json,
        )

        if ok:
            st.success("Movimiento guardado correctamente.")
            st.rerun()
        else:
            st.error("Error al guardar el movimiento.")