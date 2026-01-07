import streamlit as st
import pandas as pd
import altair as alt

from models import listar_movimientos
from auth import check_auth
from ui import topbar


def formato_argentino(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    # Seguridad
    check_auth()

    # Barra fija + menú superior
    topbar()

    usuario_id = st.session_state["user"]["id"]

    st.title("📊 Dashboard Anual")

    # Obtener movimientos desde Supabase
    movimientos = listar_movimientos(usuario_id)

    if not movimientos:
        st.info("Todavía no hay movimientos cargados.")
        return

    # Convertir a DataFrame
    df = pd.DataFrame(
        [
            {
                "Fecha": m.fecha,
                "Tipo": m.tipo.lower(),   # 🔥 Normalizamos a minúsculas
                "Categoría": m.categoria,
                "Monto": m.monto,
                "Cuenta": m.cuenta,
            }
            for m in movimientos
        ]
    )

    # Procesamiento de fechas
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Año"] = df["Fecha"].dt.year

    # Monto firmado según tipo
    df["Monto_signed"] = df.apply(
        lambda row: row["Monto"] if row["Tipo"] == "ingreso" else -row["Monto"],
        axis=1,
    )

    # ----------------------------------------------------------------------
    # 📅 RESUMEN POR AÑO
    # ----------------------------------------------------------------------
    st.header("📅 Resumen por Año")

    resumen = (
        df.groupby("Año", as_index=False)["Monto_signed"]
        .sum()
        .rename(columns={"Monto_signed": "Balance"})
    )

    resumen["Ingresos"] = df[df["Tipo"] == "ingreso"].groupby("Año")["Monto"].sum()
    resumen["Gastos"] = df[df["Tipo"] == "gasto"].groupby("Año")["Monto"].sum()

    resumen = resumen.fillna(0)

    st.dataframe(resumen)

    # ----------------------------------------------------------------------
    # 📈 EVOLUCIÓN DEL BALANCE ANUAL
    # ----------------------------------------------------------------------
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

    # ----------------------------------------------------------------------
    # 🏆 CATEGORÍAS MÁS RELEVANTES DEL AÑO
    # ----------------------------------------------------------------------
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

    st.dataframe(top_cat)

    # ----------------------------------------------------------------------
    # 💰 DISTRIBUCIÓN DE GASTOS POR CATEGORÍA
    # ----------------------------------------------------------------------
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