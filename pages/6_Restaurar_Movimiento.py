import streamlit as st
import pandas as pd

from auth import check_auth
from ui import topbar
from models import listar_movimientos_borrados
from db import restaurar_movimiento


def main():
    check_auth()
    topbar()

    usuario = st.session_state.get("user")
    usuario_id = usuario["id"]

    st.markdown("## ♻️ Restaurar Movimiento")
    st.markdown("Seleccioná un movimiento borrado para restaurarlo.")

    st.markdown("---")

    movimientos = listar_movimientos_borrados(usuario_id)

    if not movimientos:
        st.info("No hay movimientos borrados para restaurar.")
        return

    df = pd.DataFrame([m.__dict__ for m in movimientos])

    st.subheader("🗂 Movimientos borrados")
    st.dataframe(
        df[["id", "fecha", "categoria", "tipo", "descripcion", "monto", "cuenta"]],
        use_container_width=True
    )

    st.markdown("---")

    ids = df["id"].tolist()
    id_sel = st.selectbox("Seleccionar ID a restaurar", ids)

    if st.button("♻️ Restaurar seleccionado", use_container_width=True):
        if restaurar_movimiento(usuario_id, id_sel):
            st.success("Movimiento restaurado correctamente.")
            st.rerun()
        else:
            st.error("Error al restaurar movimiento.")


if __name__ == "__main__":
    main()