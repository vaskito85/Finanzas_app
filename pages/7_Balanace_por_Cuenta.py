import streamlit as st
import pandas as pd

from models import listar_movimientos
from auth import check_auth
from ui import topbar


def formato_argentino(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    check_auth()
    topbar()

    usuario_id = st.session_state["user"]["id"]

    st.markdown("## 🏦 Balance por Cuenta")
    st.markdown("Visualizá el saldo actual de cada una de tus cuentas.")

    st.markdown("---")

    movimientos = listar_movimientos(usuario_id)

    if not movimientos:
        st.info("Todavía no hay movimientos cargados.")
        return

    df = pd.DataFrame(
        [
            {
                "Cuenta": m.cuenta,
                "Tipo": m.tipo.lower(),
                "Monto": m.monto,
            }
            for m in movimientos
        ]
    )

    df["Monto_signed"] = df.apply(
        lambda row: row["Monto"] if row["Tipo"] == "ingreso" else -row["Monto"],
        axis=1,
    )

    saldo_por_cuenta = df.groupby("Cuenta")["Monto_signed"].sum().reset_index()

    st.subheader("📋 Saldos actuales por cuenta")
    saldo_por_cuenta["Saldo"] = saldo_por_cuenta["Monto_signed"].apply(formato_argentino)

    st.dataframe(saldo_por_cuenta[["Cuenta", "Saldo"]], use_container_width=True)

    st.markdown("---")

    st.subheader("📈 Gráfico de saldos")
    st.bar_chart(saldo_por_cuenta, x="Cuenta", y="Monto_signed")


if __name__ == "__main__":
    main()