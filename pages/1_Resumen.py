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

    st.markdown("## 📊 Resumen General")
    st.markdown("Visualizá tus ingresos, gastos y evolución financiera.")

    st.markdown("---")

    movimientos = listar_movimientos(usuario_id)

    if not movimientos:
        st.info("Todavía no hay movimientos cargados.")
        return

    df = pd.DataFrame(
        [
            {
                "Fecha": m.fecha,
                "Tipo": m.tipo,
                "Categoría": m.categoria,
                "Monto": m.monto,
                "Cuenta": m.cuenta,
            }
            for m in movimientos
        ]
    )

    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Monto_signed"] = df.apply(
        lambda row: row["Monto"] if row["Tipo"] == "ingreso" else -row["Monto"],
        axis=1,
    )

    total_ingresos = df[df["Tipo"] == "ingreso"]["Monto"].sum()
    total_gastos = df[df["Tipo"] == "gasto"]["Monto"].sum()
    balance = total_ingresos - total_gastos

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Ingresos", f"${formato_argentino(total_ingresos)}")
    col2.metric("💸 Gastos", f"${formato_argentino(total_gastos)}")
    col3.metric("📈 Balance", f"${formato_argentino(balance)}")

    st.markdown("---")

    st.subheader("📅 Evolución mensual")

    df["Mes"] = df["Fecha"].dt.to_period("M").astype(str)
    resumen_mensual = df.groupby("Mes")["Monto_signed"].sum().reset_index()

    st.line_chart(resumen_mensual, x="Mes", y="Monto_signed")

    st.markdown("---")

    st.subheader("🏆 Categorías más relevantes")

    categorias = (
        df.groupby("Categoría")["Monto"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    st.dataframe(categorias, use_container_width=True)


if __name__ == "__main__":
    main()