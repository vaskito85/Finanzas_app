import streamlit as st
import json
import datetime

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


def formato_argentino_a_float(valor):
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    if isinstance(valor, str):
        valor = valor.strip()
        if valor == "":
            return None
        # Soporta formato argentino: "1.234,56"
        valor = valor.replace(".", "").replace(",", ".")
    try:
        return float(valor)
    except Exception:
        return None


def main():
    check_auth()
    topbar()

    if "user" not in st.session_state:
        st.error("No hay usuario autenticado.")
        st.stop()

    usuario_id = st.session_state["user"]["id"]

    st.markdown("## ➕ Cargar movimiento")
    st.markdown("Completá los datos y presioná Guardar para agregar un movimiento.")

    st.markdown("---")

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

    with st.form("form_cargar", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            fecha = st.date_input("📅 Fecha", value=datetime.date.today())
            tipo = st.selectbox("🔁 Tipo", ["ingreso", "gasto"])
        with col2:
            categoria = st.selectbox("📂 Categoría", options=["Sin categoría"] + categorias)
            cuenta = st.selectbox("🏦 Cuenta", options=["Sin cuenta"] + cuentas)
        with col3:
            monto_input = st.text_input("💵 Monto", value="")
            etiquetas_input = st.text_input(
                "🏷 Etiquetas (separadas por comas)", value=""
            )

        descripcion = st.text_area("📝 Descripción", value="", max_chars=500)

        submitted = st.form_submit_button("💾 Guardar movimiento", use_container_width=True)

    if submitted:
        # Validaciones simples
        monto = formato_argentino_a_float(monto_input)
        if monto is None:
            st.error("El monto no es válido. Usá números, p. ej. 1250.50 o 1.250,50")
            st.stop()

        etiquetas = []
        if isinstance(etiquetas_input, str) and etiquetas_input.strip():
            etiquetas = [e.strip() for e in etiquetas_input.split(",") if e.strip()]

        success = insertar_movimiento(
            usuario_id=usuario_id,
            fecha=str(fecha),
            categoria=categoria or "Sin categoría",
            tipo=tipo.lower(),
            descripcion=descripcion or "",
            monto=float(monto),
            cuenta=cuenta or "Sin cuenta",
            etiquetas_json=json.dumps(etiquetas, ensure_ascii=False),
        )

        if success:
            st.success("✅ Movimiento guardado correctamente.")
            # Forzar recarga y mostrar cambios
            st.experimental_rerun()
        else:
            st.error("❌ Error al guardar el movimiento. Revisá los logs del servidor.")

    st.markdown("---")
    st.info("También podés cargar movimientos en lote desde la opción 'Importar CSV' en el menú.")


if __name__ == "__main__":
    main()