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

    st.markdown("## 📅 Dashboard Mensual")
    st.markdown("Analizá ingresos, gastos y categorías de un mes específico.")

    st.markdown("---")

    movimientos = listar_movimientos(usuario_id)

    if not movimientos:
        st.info("Todavía no hay movimientos cargados.")
        return

    df = pd.DataFrame(
        [
            {
                "Fecha": m.fecha,
                "Tipo": m.tipo.lower(),
                "Categoría": m.categoria,
                "Monto": m.monto,
                "Cuenta": m.cuenta,
            }
            for m in movimientos
        ]
    )

    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Mes"] = df["Fecha"].dt.to_period("M").astype(str)

    df["Monto_signed"] = df.apply(
        lambda row: row["Monto"] if row["Tipo"] == "ingreso" else -row["Monto"],
        axis=1,
    )

    meses = sorted(df["Mes"].unique())
    mes_sel = st.selectbox("Seleccionar mes", meses)

    df_mes = df[df["Mes"] == mes_sel]

    ingresos = df_mes[df_mes["Tipo"] == "ingreso"]["Monto"].sum()
    gastos = df_mes[df_mes["Tipo"] == "gasto"]["Monto"].sum()
    balance = ingresos - gastos

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Ingresos", f"${formato_argentino(ingresos)}")
    col2.metric("💸 Gastos", f"${formato_argentino(gastos)}")
    col3.metric("📈 Balance", f"${formato_argentino(balance)}")

    st.markdown("---")

    st.subheader("📈 Evolución del mes")
    st.line_chart(df_mes, x="Fecha", y="Monto_signed")

    st.markdown("---")

    st.subheader("🏆 Categorías del mes")
    categorias = (
        df_mes.groupby("Categoría")["Monto"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    st.dataframe(categorias, use_container_width=True)


if __name__ == "__main__":
    main()