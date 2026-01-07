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
    # Seguridad
    check_auth()

    # Barra fija + menú superior
    topbar()

    if "user" not in st.session_state or "user" not in st.session_state:
        st.error("No hay usuario autenticado.")
        st.stop()

    usuario_id = st.session_state["user"]["id"]

    st.title("🧮 Proyección Financiera (Forecast)")

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
                "Tipo": m.tipo.lower(),   # Normalizamos a minúsculas
                "Monto": m.monto,
            }
            for m in movimientos
        ]
    )

    # Procesamiento de fechas
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"])

    if df.empty:
        st.info("No hay datos válidos de fecha para generar el forecast.")
        return

    df["Mes"] = df["Fecha"].dt.to_period("M").astype(str)

    # Monto firmado según tipo
    df["Monto_signed"] = df.apply(
        lambda row: row["Monto"] if row["Tipo"] == "ingreso" else -row["Monto"],
        axis=1,
    )

    # Balance mensual
    mensual = (
        df.groupby("Mes", as_index=False)["Monto_signed"]
        .sum()
        .rename(columns={"Monto_signed": "Balance"})
    )

    # Ordenamos por Mes para que Mes_num tenga sentido temporal
    mensual = mensual.sort_values("Mes").reset_index(drop=True)
    mensual["Mes_num"] = np.arange(len(mensual))

    # ----------------------------------------------------------------------
    # 🔍 VALIDACIONES ANTES DEL MODELO
    # ----------------------------------------------------------------------
    if mensual.empty or len(mensual) < 2:
        st.warning("No hay suficientes datos mensuales para generar un forecast.")
        return

    if mensual["Balance"].isna().any() or mensual["Mes_num"].isna().any():
        st.warning("Hay datos inválidos en el cálculo mensual.")
        return

    if mensual["Balance"].nunique() == 1:
        st.warning("No se puede generar un forecast porque todos los valores mensuales son iguales.")
        return

    # ----------------------------------------------------------------------
    # 🔮 MODELO LINEAL SIMPLE (FORECAST)
    # ----------------------------------------------------------------------
    try:
        coef = np.polyfit(mensual["Mes_num"], mensual["Balance"], 1)
        tendencia = np.poly1d(coef)
    except Exception as e:
        st.error(f"No se pudo calcular el forecast (error numérico en el ajuste): {e}")
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
        .mark_line(point=True, color="blue")
        .encode(x="Mes_num:Q", y="Balance:Q")
        +
        alt.Chart(df_futuro)
        .mark_line(point=True, color="orange", strokeDash=[5, 5])
        .encode(x="Mes_num:Q", y="Balance:Q")
    ).properties(height=350)

    st.altair_chart(chart, use_container_width=True)

    st.markdown("---")

    # ----------------------------------------------------------------------
    # 🔮 ESTIMACIONES CLAVE
    # ----------------------------------------------------------------------
    st.subheader("🔮 Estimaciones clave")

    if len(futuro_y) >= 12:
        st.write(f"Balance estimado en 3 meses: **${formato_argentino(futuro_y[2])}**")
        st.write(f"Balance estimado en 6 meses: **${formato_argentino(futuro_y[5])}**")
        st.write(f"Balance estimado en 12 meses: **${formato_argentino(futuro_y[11])}**")
    else:
        st.info("No se pudieron calcular todas las estimaciones de 3, 6 y 12 meses.")


if __name__ == "__main__":
    main()