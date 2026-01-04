import streamlit as st
import json
import pandas as pd

from auth import check_auth
from ui import topbar, top_menu
from db import obtener_movimientos, obtener_movimiento_por_id, actualizar_movimiento


def main():
    check_auth()
    topbar()
    top_menu()

    # Validación segura del usuario
    if "user" not in st.session_state:
        st.error("No hay usuario autenticado.")
        st.stop()

    usuario_id = st.session_state["user"]["id"]

    st.title("✏️ Editar Movimiento")

    movimientos = obtener_movimientos(usuario_id)

    if not movimientos:
        st.info("No hay movimientos para editar.")
        return

    ids = [m["id"] for m in movimientos]
    id_sel = st.selectbox("Seleccionar ID de movimiento", ids)

    mov = obtener_movimiento_por_id(usuario_id, id_sel)
    if not mov:
        st.error("No se encontró el movimiento seleccionado.")
        return

    # Procesar etiquetas
    etiquetas_raw = mov.get("etiquetas") or []
    if isinstance(etiquetas_raw, list):
        etiquetas_str = ", ".join(etiquetas_raw)
    else:
        try:
            data = json.loads(etiquetas_raw)
            etiquetas_str = ", ".join(data) if isinstance(data, list) else ""
        except Exception:
            etiquetas_str = ""

    # Procesar fecha
    try:
        fecha_valor = pd.to_datetime(mov.get("fecha")).date()
    except Exception:
        fecha_valor = None

    with st.form("form_editar"):
        fecha = st.date_input("Fecha", value=fecha_valor)
        categoria = st.text_input("Categoría", value=mov.get("categoria") or "")
        tipo = st.selectbox("Tipo", ["ingreso", "gasto"], index=0 if mov.get("tipo") == "ingreso" else 1)
        descripcion = st.text_input("Descripción", value=mov.get("descripcion") or "")
        monto = st.number_input("Monto", min_value=0.0, step=0.01, value=float(mov.get("monto") or 0.0))
        cuenta = st.text_input("Cuenta", value=mov.get("cuenta") or "")
        etiquetas = st.text_input("Etiquetas (separadas por coma)", value=etiquetas_str)

        submitted = st.form_submit_button("Guardar cambios")

    if submitted:
        etiquetas_list = [e.strip() for e in etiquetas.split(",") if e.strip()]
        etiquetas_json = json.dumps(etiquetas_list, ensure_ascii=False)

        ok = actualizar_movimiento(
            usuario_id=usuario_id,
            movimiento_id=id_sel,
            fecha=str(fecha),
            categoria=categoria,
            tipo=tipo,
            descripcion=descripcion,
            monto=float(monto),
            cuenta=cuenta,
            etiquetas_json=etiquetas_json,
        )

        if ok:
            st.success("Movimiento actualizado correctamente.")
            st.rerun()
        else:
            st.error("Error al actualizar el movimiento.")


if __name__ == "__main__":
    main()