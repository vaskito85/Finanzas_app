import streamlit as st
import json

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


def formato_monto_a_str(m):
    try:
        return f"{float(m):.2f}"
    except Exception:
        return ""


def main():
    check_auth()
    topbar()

    if "user" not in st.session_state:
        st.error("No hay usuario autenticado.")
        st.stop()

    usuario_id = st.session_state["user"]["id"]

    st.markdown("## ✏️ Editar Movimiento")
    st.markdown("Seleccioná un movimiento y editá sus campos. Guardá para aplicar los cambios.")

    st.markdown("---")

    # Obtener movimientos directos desde la DB (no cacheado aquí para permitir edición inmediata)
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

    # Cargar catálogos
    try:
        categorias = obtener_categorias(usuario_id)
    except Exception:
        categorias = []

    try:
        cuentas = obtener_cuentas(usuario_id)
    except Exception:
        cuentas = []

    try:
        etiquetas_base = obtener_etiquetas(usuario_id)
    except Exception:
        etiquetas_base = []

    # Preparar valores iniciales
    fecha_init = mov.get("fecha") or ""
    categoria_init = mov.get("categoria") or "Sin categoría"
    tipo_init = (mov.get("tipo") or "").lower()
    descripcion_init = mov.get("descripcion") or ""
    monto_init = formato_monto_a_str(mov.get("monto") or 0)
    cuenta_init = mov.get("cuenta") or "Sin cuenta"
    etiquetas_raw = mov.get("etiquetas") or []
    if isinstance(etiquetas_raw, list):
        etiquetas_init = ", ".join([str(e) for e in etiquetas_raw])
    else:
        etiquetas_init = str(etiquetas_raw)

    with st.form("form_editar", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            fecha = st.text_input("📅 Fecha (YYYY-MM-DD)", value=str(fecha_init))
            tipo = st.selectbox("🔁 Tipo", ["ingreso", "gasto"], index=0 if tipo_init == "ingreso" else 1)
        with col2:
            categoria = st.selectbox("📂 Categoría", options=["Sin categoría"] + categorias, index=(0 if categoria_init == "Sin categoría" else (categorias.index(categoria_init)+1) if categoria_init in categorias else 0))
            cuenta = st.selectbox("🏦 Cuenta", options=["Sin cuenta"] + cuentas, index=(0 if cuenta_init == "Sin cuenta" else (cuentas.index(cuenta_init)+1) if cuenta_init in cuentas else 0))
        with col3:
            monto_input = st.text_input("💵 Monto", value=monto_init)
            etiquetas_input = st.text_input("🏷 Etiquetas (separadas por comas)", value=etiquetas_init)

        descripcion = st.text_area("📝 Descripción", value=descripcion_init, max_chars=500)

        submitted = st.form_submit_button("💾 Guardar cambios", use_container_width=True)

    if submitted:
        # Validaciones y preparación
        try:
            monto = float(monto_input.replace(".", "").replace(",", ".")) if isinstance(monto_input, str) else float(monto_input)
        except Exception:
            st.error("Monto inválido. Usá formato numérico, p. ej. 1250.50 o 1.250,50")
            st.stop()

        etiquetas = []
        if isinstance(etiquetas_input, str) and etiquetas_input.strip():
            etiquetas = [e.strip() for e in etiquetas_input.split(",") if e.strip()]

        ok = actualizar_movimiento(
            usuario_id=usuario_id,
            movimiento_id=id_sel,
            fecha=str(fecha),
            categoria=categoria or "Sin categoría",
            tipo=tipo.lower(),
            descripcion=descripcion or "",
            monto=float(monto),
            cuenta=cuenta or "Sin cuenta",
            etiquetas_json=json.dumps(etiquetas, ensure_ascii=False),
        )

        if ok:
            st.success("✅ Movimiento actualizado correctamente.")
            st.experimental_rerun()
        else:
            st.error("❌ Error al actualizar el movimiento. Revisá los logs del servidor.")

    st.markdown("---")
    st.info("Si necesitás cambiar muchas filas, usá la importación por CSV y luego edita puntos puntuales aquí.")


if __name__ == "__main__":
    main()