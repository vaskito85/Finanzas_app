import streamlit as st
import json
import pandas as pd

from auth import check_auth
from ui import topbar
from db import obtener_movimientos, obtener_movimiento_por_id, actualizar_movimiento
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

    st.markdown("## ✏️ Editar Movimiento")

    movimientos = obtener_movimientos(usuario_id)

    if not movimientos:
        st.info("No hay movimientos para editar.")
        return

    ids = [m["id"] for m in movimientos]
    id_sel = st.selectbox("📄 Seleccionar movimiento por ID", ids)

    mov = obtener_movimiento_por_id(usuario_id, id_sel)
    if not mov:
        st.error("No se encontró el movimiento seleccionado.")
        return

    categorias = obtener_categorias(usuario_id)
    etiquetas_base = obtener_etiquetas(usuario_id)
    cuentas = obtener_cuentas(usuario_id)

    # ENTRENAR MODELO
    mov_prev = listar_movimientos(usuario_id)
    modelo = entrenar_modelo([
        {"descripcion": m.descripcion, "etiquetas": m.etiquetas}
        for m in mov_prev
    ])

    # Etiquetas existentes
    etiquetas_existentes = mov.get("etiquetas") or []
    if isinstance(etiquetas_existentes, str):
        try:
            etiquetas_existentes = json.loads(etiquetas_existentes)
        except:
            etiquetas_existentes = []

    # Fecha
    try:
        fecha_valor = pd.to_datetime(mov.get("fecha")).date()
    except:
        fecha_valor = None

    with st.form("form_editar"):
        col1, col2 = st.columns(2)

        with col1:
            fecha = st.date_input("📅 Fecha", value=fecha_valor)
            tipo = st.selectbox("📌 Tipo", ["ingreso", "gasto"], index=0 if mov.get("tipo") == "ingreso" else 1)
            descripcion = st.text_input("📝 Descripción", value=mov.get("descripcion") or "")

            # IA: sugerencias automáticas
            etiquetas_ai = []
            if descripcion.strip():
                etiquetas_ai = predecir_etiquetas(modelo, descripcion)

        with col2:
            categoria_actual = mov.get("categoria") or ""
            categoria_sel = st.selectbox("📂 Categoría", categorias + ["Otra..."],
                                         index=(categorias.index(categoria_actual) if categoria_actual in categorias else len(categorias)))
            categoria_nueva = ""
            if categoria_sel == "Otra...":
                categoria_nueva = st.text_input("➕ Nueva categoría")
            categoria_final = categoria_nueva.strip() if categoria_nueva else categoria_sel

            cuenta_actual = mov.get("cuenta") or ""
            cuenta_sel = st.selectbox("🏦 Cuenta", cuentas + ["Otra..."],
                                      index=(cuentas.index(cuenta_actual) if cuenta_actual in cuentas else len(cuentas)))
            cuenta_nueva = ""
            if cuenta_sel == "Otra...":
                cuenta_nueva = st.text_input("➕ Nueva cuenta")
            cuenta_final = cuenta_nueva.strip() if cuenta_nueva else cuenta_sel

        st.markdown("### 🏷 Etiquetas")

        etiquetas_multi = st.multiselect(
            "Etiquetas sugeridas por IA",
            options=list(set(etiquetas_ai + etiquetas_base)),
            default=list(set(etiquetas_existentes + etiquetas_ai))
        )

        etiquetas_extra = st.text_input(
            "Etiquetas adicionales (separadas por ;)",
            value="; ".join([e for e in etiquetas_existentes if e not in etiquetas_base]),
        )

        submitted = st.form_submit_button("💾 Guardar cambios", use_container_width=True)

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

        ok = actualizar_movimiento(
            usuario_id=usuario_id,
            movimiento_id=id_sel,
            fecha=str(fecha),
            categoria=categoria_final,
            tipo=tipo,
            descripcion=descripcion,
            monto=float(mov.get("monto") or 0),
            cuenta=cuenta_final,
            etiquetas_json=etiquetas_json,
        )

        if ok:
            st.success("Movimiento actualizado correctamente.")
            st.rerun()
        else:
            st.error("Error al actualizar el movimiento.")