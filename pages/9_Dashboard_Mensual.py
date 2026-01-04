import streamlit as st
import pandas as pd

from models import listar_movimientos
from auth import check_auth
from ui import topbar, top_menu


def formato_argentino(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    # Seguridad
    check_auth()

    # Barra fija + menú superior
    topbar()
    top_menu()

    usuario_id = st.session_state["user"]["id"]

    st.title("📅 Dashboard Mensual")

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

    # Selección de mes
    meses = sorted(df["Mes"].unique())
    mes_sel = st.selectbox("Seleccionar mes", meses)

    df_mes = df[df["Mes"] == mes_sel]

    # Cálculos del mes
    ingresos = df_mes[df_mes["Tipo"] == "ingreso"]["Monto"].sum()
    gastos = df_mes[df_mes["Tipo"] == "gasto"]["Monto"].sum()
    balance = ingresos - gastos

    # Métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("Ingresos", f"${formato_argentino(ingresos)}")
    col2.metric("Gastos", f"${formato_argentino(gastos)}")
    col3.metric("Balance", f"${formato_argentino(balance)}")

    st.markdown("---")

    # Evolución del mes
    st.subheader("📈 Evolución del mes")
    st.line_chart(df_mes, x="Fecha", y="Monto_signed")

    st.markdown("---")

    # Categorías del mes
    st.subheader("🏆 Categorías del mes")
    categorias = (
        df_mes.groupby("Categoría")["Monto"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    st.dataframe(categorias)


if __name__ == "__main__":
    main()