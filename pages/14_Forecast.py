import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

from models import listar_movimientos
from auth import check_auth
from ui import topbar


def formato_argentino(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    check_auth()
    topbar()

    if "user" not in st.session_state:
        st.error("No hay usuario autenticado.")
        st.stop()

    usuario_id = st.session_state["user"]["id"]

    st.markdown("## 🧮 Proyección Financiera (Forecast)")
    st.markdown("Estimación de tu balance futuro basada en tu historial mensual.")

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
                "Monto": m.monto,
            }
            for m in movimientos
        ]
    )

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"])

    if df.empty:
        st.info("No hay datos válidos de fecha para generar el forecast.")
        return

    df["Mes"] = df["Fecha"].dt.to_period("M").astype(str)

    df["Monto_signed"] = df.apply(
        lambda row: row["Monto"] if row["Tipo"] == "ingreso" else -row["Monto"],
        axis=1,
    )

    mensual = (
        df.groupby("Mes", as_index=False)["Monto_signed"]
        .sum()
        .rename(columns={"Monto_signed": "Balance"})
    )

    mensual = mensual.sort_values("Mes").reset_index(drop=True)
    mensual["Mes_num"] = np.arange(len(mensual))

    # Validaciones
    if len(mensual) < 2:
        st.warning("Se necesitan al menos dos meses para generar un forecast.")
        return

    if mensual["Balance"].nunique() == 1:
        st.warning("No se puede generar un forecast porque todos los valores mensuales son iguales.")
        return

    # Modelo lineal
    try:
        coef = np.polyfit(mensual["Mes_num"], mensual["Balance"], 1)
        tendencia = np.poly1d(coef)
    except Exception as e:
        st.error(f"No se pudo calcular el forecast: {e}")
        return

    meses_futuros = 12
    futuro_x = np.arange(len(mensual), len(mensual) + meses_futuros)
    futuro_y = tendencia(futuro_x)

    df_futuro = pd.DataFrame({
        "Mes_num": futuro_x,
        "Balance": futuro_y,
        "Mes": [f"Futuro {i+1}" for i in range(meses_futuros)]
    })

    # ----------------------------------------------------------------------
    # 📈 GRÁFICO DE PROYECCIÓN
    # ----------------------------------------------------------------------
    st.subheader("📈 Proyección de los próximos 12 meses")

    chart = (
        alt.Chart(mensual)
        .mark_line(point=True, color="#4A90E2")
        .encode(x="Mes_num:Q", y="Balance:Q", tooltip=["Mes", "Balance"])
        +
        alt.Chart(df_futuro)
        .mark_line(point=True, color="#F5A623", strokeDash=[5, 5])
        .encode(x="Mes_num:Q", y="Balance:Q", tooltip=["Mes", "Balance"])
    ).properties(height=350)

    st.altair_chart(chart, use_container_width=True)

    st.markdown("---")

    # ----------------------------------------------------------------------
    # 🔮 ESTIMACIONES CLAVE
    # ----------------------------------------------------------------------
    st.subheader("🔮 Estimaciones clave")

    if len(futuro_y) >= 12:
        col1, col2, col3 = st.columns(3)
        col1.metric("En 3 meses", f"${formato_argentino(futuro_y[2])}")
        col2.metric("En 6 meses", f"${formato_argentino(futuro_y[5])}")
        col3.metric("En 12 meses", f"${formato_argentino(futuro_y[11])}")
    else:
        st.info("No se pudieron calcular todas las estimaciones de 3, 6 y 12 meses.")


if __name__ == "__main__":
    main()