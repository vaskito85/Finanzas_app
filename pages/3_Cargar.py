import streamlit as st
import json
from datetime import date

from db import insertar_movimiento
from auth import check_auth
from ui import top_menu


ETIQUETAS_SUGERIDAS = [
    "comida",
    "supermercado",
    "transporte",
    "combustible",
    "salud",
    "farmacia",
    "servicios",
    "alquiler",
    "ocio",
    "educación",
    "inversión",
    "impuestos",
    "compras",
    "hogar",
    "viajes",
]


def main():
    # Seguridad
    check_auth()
    top_menu()

    usuario_id = st.session_state["user"]["id"]

    st.title("➕ Cargar Movimiento")

    cuentas = [
        "Banco Santander",
        "Mercado Pago",
        "BullMarket",
        "Balanz",
        "Buenbit",
        "Efectivo",
    ]

    with st.form("form_movimiento"):
        fecha = st.date_input("Fecha", value=date.today())
        tipo = st.selectbox("Tipo", ["ingreso", "gasto"])
        categoria = st.text_input("Categoría", value="General")
        cuenta = st.selectbox("Cuenta", cuentas)
        descripcion = st.text_area("Descripción")
        monto = st.number_input("Monto", min_value=0.0, step=100.0, format="%.2f")

        st.markdown("### 🏷 Etiquetas")

        etiquetas_sel = st.multiselect(
            "Etiquetas sugeridas",
            options=ETIQUETAS_SUGERIDAS,
        )

        etiquetas_extra = st.text_input(
            "Etiquetas adicionales (separadas por comas)",
            value=""
        )

        submitted = st.form_submit_button("Guardar")

    if submitted:
        # Combinar etiquetas sugeridas + adicionales
        etiquetas_finales = etiquetas_sel.copy()

        if etiquetas_extra.strip():
            extras = [e.strip() for e in etiquetas_extra.split(",") if e.strip()]
            etiquetas_finales.extend(extras)

        etiquetas_json = json.dumps(etiquetas_finales, ensure_ascii=False)

        # Guardar en Supabase
        insertar_movimiento(
            usuario_id=usuario_id,
            fecha=str(fecha),
            categoria=categoria,
            tipo=tipo,
            descripcion=descripcion,
            monto=float(monto),
            cuenta=cuenta,
            etiquetas_json=etiquetas_json,
        )

        st.success("Movimiento guardado correctamente.")
        st.rerun()


if __name__ == "__main__":
    main()