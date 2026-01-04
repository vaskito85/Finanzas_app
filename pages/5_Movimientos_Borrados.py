import streamlit as st
import pandas as pd

from auth import check_auth
from ui import topbar, top_menu
from models import listar_movimientos_borrados


def main():
    check_auth()
    topbar()
    top_menu()

    usuario = st.session_state.get("user")
    usuario_id = usuario["id"]

    st.title("🗑 Movimientos borrados")

    movimientos = listar_movimientos_borrados(usuario_id)

    if not movimientos:
        st.info("No hay movimientos borrados.")
        return

    df = pd.DataFrame([m.__dict__ for m in movimientos])

    st.dataframe(df[["id", "fecha", "categoria", "tipo", "descripcion", "monto", "cuenta"]])


if __name__ == "__main__":
    main()