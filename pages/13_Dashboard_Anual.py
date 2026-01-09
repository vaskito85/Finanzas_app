import streamlit as st
import pandas as pd
import altair as alt

from models import listar_movimientos
from auth import check_auth
from ui import topbar


def formato_argentino(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    check_auth()
    topbar()

    usuario_id = st.session_state["user"]["id"]

    st.markdown("## 📊 Dashboard Anual")
    st.markdown("Visualizá tu evolución financiera año por año.")

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
    df["Año"] = df["Fecha"].dt.year

    df["Monto_signed"] = df.apply(
        lambda row: row["Monto"] if row["Tipo"] == "ingreso" else -row["Monto"],
        axis=1,
    )

    st.header("📅 Resumen por Año")

    resumen = (
        df.groupby("Año", as_index=False)["Monto_signed"]
        .sum()
        .rename(columns={"Monto_signed": "Balance"})
    )

    resumen["Ingresos"] = df[df["Tipo"] == "ingreso"].groupby("Año")["Monto"].sum()
    resumen["Gastos"] = df[df["Tipo"] == "gasto"].groupby("Año")["Monto"].sum()

    resumen = resumen.fillna(0)

    st.dataframe(resumen, use_container_width=True)

    st.markdown("---")

    st.subheader("📈 Evolución del Balance Anual")

    chart = (
        alt.Chart(resumen)
        .mark_line(point=True)
        .encode(
            x="Año:O",
            y="Balance:Q",
            tooltip=["Año:O", "Balance:Q"],
        )
        .properties(height=350)
    )

    st.altair_chart(chart, use_container_width=True)

    st.markdown("---")

    st.subheader("🏆 Categorías más relevantes del año")

    año_sel = st.selectbox("Seleccionar año", resumen["Año"].tolist())

    df_año = df[df["Año"] == año_sel]

    top_cat = (
        df_año[df_año["Tipo"] == "gasto"]
        .groupby("Categoría")["Monto"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .head(5)
    )

    st.dataframe(top_cat, use_container_width=True)

    st.markdown("---")

    st.subheader("💰 Distribución de gastos por categoría")

    chart_torta = (
        alt.Chart(top_cat)
        .mark_arc()
        .encode(
            theta="Monto:Q",
            color="Categoría:N",
            tooltip=["Categoría:N", "Monto:Q"],
        )
        .properties(height=350)
    )

    st.altair_chart(chart_torta, use_container_width=True)


if __name__ == "__main__":
    main()