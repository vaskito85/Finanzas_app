import streamlit as st
import pandas as pd
import altair as alt

from models import listar_movimientos
from auth import check_auth
from ui import top_menu


def formato_argentino(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    # Seguridad
    check_auth()
    top_menu()

    usuario_id = st.session_state["user"]["id"]

    st.title("📊 Comparación Mes a Mes")

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
    df["Mes"] = df["Fecha"].dt.to_period("M").astype(str)

    # Monto firmado según tipo
    df["Monto_signed"] = df.apply(
        lambda row: row["Monto"] if row["Tipo"] == "ingreso" else -row["Monto"],
        axis=1,
    )

    meses = sorted(df["Mes"].unique())

    if len(meses) < 2:
        st.info("Se necesitan al menos dos meses para comparar.")
        return

    mes_actual = meses[-1]
    mes_anterior = meses[-2]

    st.header(f"📅 Comparación: {mes_anterior} → {mes_actual}")

    df_act = df[df["Mes"] == mes_actual]
    df_ant = df[df["Mes"] == mes_anterior]

    balance_act = df_act["Monto_signed"].sum()
    balance_ant = df_ant["Monto_signed"].sum()

    variacion = balance_act - balance_ant
    variacion_pct = (variacion / abs(balance_ant)) * 100 if balance_ant != 0 else 0

    # Métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("Balance mes anterior", f"${formato_argentino(balance_ant)}")
    col2.metric("Balance mes actual", f"${formato_argentino(balance_act)}")
    col3.metric("Variación", f"${formato_argentino(variacion)}", f"{variacion_pct:.1f}%")

    st.markdown("---")

    # Gráfico mensual
    st.subheader("📈 Gráfico de comparación mensual")

    resumen = (
        df.groupby("Mes", as_index=False)["Monto_signed"]
        .sum()
        .rename(columns={"Monto_signed": "Balance"})
    )

    chart = (
        alt.Chart(resumen)
        .mark_bar()
        .encode(
            x="Mes:N",
            y="Balance:Q",
            color="Mes:N",
            tooltip=["Mes:N", "Balance:Q"],
        )
        .properties(height=350)
    )

    st.altair_chart(chart, use_container_width=True)

    st.markdown("---")

    # Categorías que más crecieron
    st.subheader("🏆 Categorías que más crecieron")

    gastos_act = (
        df_act[df_act["Tipo"] == "gasto"]
        .groupby("Categoría")["Monto"]
        .sum()
    )

    gastos_ant = (
        df_ant[df_ant["Tipo"] == "gasto"]
        .groupby("Categoría")["Monto"]
        .sum()
    )

    comparacion = pd.DataFrame({
        "Gasto_actual": gastos_act,
        "Gasto_anterior": gastos_ant
    }).fillna(0)

    comparacion["Variación"] = comparacion["Gasto_actual"] - comparacion["Gasto_anterior"]
    comparacion["Variación_pct"] = (
        comparacion["Variación"] / comparacion["Gasto_anterior"].replace(0, 1)
    ) * 100

    comparacion = comparacion.sort_values("Variación", ascending=False).head(5)

    st.dataframe(comparacion)


if __name__ == "__main__":
    main()