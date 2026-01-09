import streamlit as st
import json

from auth import check_auth
from ui import topbar
from db import insertar_movimiento
from catalogos import (
    obtener_categorias,
    obtener_etiquetas,
    obtener_cuentas,
    agregar_categoria,
    agregar_etiqueta,
    agregar_cuenta,
)
from models import listar_movimientos
from etiquetas_inteligentes import entrenar_modelo, predecir_etiquetas


def main():
    check_auth()
    topbar()

    if "user" not in st.session_state:
        st.error("No hay usuario autenticado.")
        st.stop()

    usuario_id = st.session_state["user"]["id"]

    st.markdown("## ➕ Cargar Movimiento")

    # ENTRENAR MODELO DE ETIQUETAS
    movimientos_previos = listar_movimientos(usuario_id)
    modelo = entrenar_modelo([
        {"descripcion": m.descripcion, "etiquetas": m.etiquetas}
        for m in movimientos_previos
    ])

    categorias = obtener_categorias(usuario_id)
    etiquetas_base = obtener_etiquetas(usuario_id)
    cuentas = obtener_cuentas(usuario_id)

    with st.form("form_movimiento"):
        fecha = st.date_input("📅 Fecha")

        col1, col2 = st.columns(2)

        with col1:
            tipo = st.selectbox("📌 Tipo", ["ingreso", "gasto"])
            descripcion = st.text_input("📝 Descripción")

            # IA: sugerencias automáticas
            etiquetas_ai = []
            if descripcion.strip():
                etiquetas_ai = predecir_etiquetas(modelo, descripcion)

        with col2:
            categoria_sel = st.selectbox("📂 Categoría", categorias + ["Otra..."])
            categoria_nueva = ""
            if categoria_sel == "Otra...":
                categoria_nueva = st.text_input("➕ Nueva categoría")
            categoria_final = categoria_nueva.strip() if categoria_nueva else categoria_sel

            cuenta_sel = st.selectbox("🏦 Cuenta", cuentas + ["Otra..."])
            cuenta_nueva = ""
            if cuenta_sel == "Otra...":
                cuenta_nueva = st.text_input("➕ Nueva cuenta")
            cuenta_final = cuenta_nueva.strip() if cuenta_nueva else cuenta_sel

        st.markdown("### 🏷 Etiquetas")

        etiquetas_multi = st.multiselect(
            "Etiquetas sugeridas por IA",
            options=list(set(etiquetas_ai + etiquetas_base)),
            default=etiquetas_ai
        )

        etiquetas_extra = st.text_input(
            "Etiquetas adicionales (separadas por ;)",
            help="Ejemplo: urgente; tarjeta; online",
        )

        submitted = st.form_submit_button("💾 Guardar movimiento", use_container_width=True)

    if submitted:
        if categoria_nueva.strip():
            agregar_categoria(usuario_id, categoria_nueva)

        if cuenta_nueva.strip():
            agregar_cuenta(usuario_id, cuenta_nueva)

        etiquetas_list = list(etiquetas_multi)

        if etiquetas_extra.strip():
            extras = [e.strip() for e in etiquetas_extra.split(";") if e.strip()]
            for e in extras:
                etiquetas_list.append(e)
                agregar_etiqueta(usuario_id, e)

        etiquetas_json = json.dumps(etiquetas_list, ensure_ascii=False)

        ok = insertar_movimiento(
            usuario_id=usuario_id,
            fecha=str(fecha),
            categoria=categoria_final,
            tipo=tipo,
            descripcion=descripcion,
            monto=float(st.session_state.get("monto", 0)),
            cuenta=cuenta_final,
            etiquetas_json=etiquetas_json,
        )

        if ok:
            st.success("Movimiento guardado correctamente.")
            st.rerun()
        else:
            st.error("Error al guardar el movimiento.")