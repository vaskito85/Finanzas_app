import streamlit as st
import pandas as pd
import json
import os

from models import listar_movimientos
from auth import check_auth
from ui import topbar


OBJ_FILE = "objetivos.json"


def formato_argentino(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def cargar_objetivos():
    if not os.path.exists(OBJ_FILE):
        return {"cuentas": {}, "cuentas_min": {}, "categorias": {}}

    with open(OBJ_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Compatibilidad con versiones anteriores
    if "cuentas_min" not in data:
        data["cuentas_min"] = {}

    return data


def main():
    # Seguridad
    check_auth()

    # Barra fija + menú superior
    topbar()

    usuario_id = st.session_state["user"]["id"]

    st.title("🚨 Alertas Automáticas")

    objetivos = cargar_objetivos()
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

    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Mes"] = df["Fecha"].dt.to_period("M").astype(str)
    df["Monto_signed"] = df.apply(
        lambda row: row["Monto"] if row["Tipo"] == "ingreso" else -row["Monto"],
        axis=1,
    )

    # ----------------------------------------------------------------------
    # 🏦 ALERTAS POR CUENTA
    # ----------------------------------------------------------------------
    st.header("🏦 Alertas por Cuenta")

    saldo_por_cuenta = df.groupby("Cuenta")["Monto_signed"].sum()

    for cuenta, saldo in saldo_por_cuenta.items():
        minimo = objetivos["cuentas_min"].get(cuenta)
        objetivo = objetivos["cuentas"].get(cuenta)

        # Alerta por mínimo
        if minimo is not None:
            if saldo < minimo:
                st.error(
                    f"🔻 La cuenta **{cuenta}** está por debajo del mínimo.\n"
                    f"Saldo: ${formato_argentino(saldo)} — Mínimo: ${formato_argentino(minimo)}"
                )
            else:
                st.success(
                    f"✔ La cuenta **{cuenta}** está por encima del mínimo.\n"
                    f"Saldo: ${formato_argentino(saldo)} — Mínimo: ${formato_argentino(minimo)}"
                )

        # Alerta por objetivo
        if objetivo is not None:
            if saldo < objetivo:
                st.warning(
                    f"⚠ La cuenta **{cuenta}** aún no alcanzó el objetivo total.\n"
                    f"Saldo: ${formato_argentino(saldo)} — Objetivo: ${formato_argentino(objetivo)}"
                )
            else:
                st.success(
                    f"✔ La cuenta **{cuenta}** alcanzó el objetivo total.\n"
                    f"Saldo: ${formato_argentino(saldo)} — Objetivo: ${formato_argentino(objetivo)}"
                )

    st.markdown("---")

    # ----------------------------------------------------------------------
    # 📂 ALERTAS POR CATEGORÍA
    # ----------------------------------------------------------------------
    st.header("📂 Alertas por Categoría")

    gastos_por_cat = (
        df[df["Tipo"] == "gasto"]
        .groupby("Categoría")["Monto"]
        .sum()
    )

    for categoria, gasto in gastos_por_cat.items():
        objetivo = objetivos["categorias"].get(categoria)

        if objetivo is not None:
            if gasto > objetivo:
                st.error(
                    f"🔥 La categoría **{categoria}** superó el límite.\n"
                    f"Gasto: ${formato_argentino(gasto)} — Límite: ${formato_argentino(objetivo)}"
                )
            else:
                st.success(
                    f"✔ La categoría **{categoria}** está dentro del límite.\n"
                    f"Gasto: ${formato_argentino(gasto)} — Límite: ${formato_argentino(objetivo)}"
                )

    st.markdown("---")

    # ----------------------------------------------------------------------
    # 📅 ALERTA DE BALANCE MENSUAL
    # ----------------------------------------------------------------------
    st.header("📅 Alerta de Balance Mensual")

    resumen_mensual = df.groupby("Mes")["Monto_signed"].sum().sort_index()

    mes_actual = resumen_mensual.index.max()
    balance_actual = resumen_mensual.loc[mes_actual]

    if balance_actual < 0:
        st.error(
            f"⚠ El balance del mes **{mes_actual}** es negativo: "
            f"${formato_argentino(balance_actual)}"
        )
    else:
        st.success(
            f"✔ El balance del mes **{mes_actual}** es positivo: "
            f"${formato_argentino(balance_actual)}"
        )

    st.markdown("---")

    # ----------------------------------------------------------------------
    # 📈 ALERTA DE GASTO INUSUAL
    # ----------------------------------------------------------------------
    st.header("📈 Alerta de Gasto Inusual")

    gastos_mensuales = (
        df[df["Tipo"] == "gasto"]
        .groupby(["Mes", "Categoría"])["Monto"]
        .sum()
        .reset_index()
    )

    meses = sorted(gastos_mensuales["Mes"].unique())

    if len(meses) >= 2:
        mes_actual = meses[-1]
        mes_anterior = meses[-2]

        df_act = gastos_mensuales[gastos_mensuales["Mes"] == mes_actual]
        df_ant = gastos_mensuales[gastos_mensuales["Mes"] == mes_anterior]

        merged = pd.merge(df_act, df_ant, on="Categoría", how="left", suffixes=("_act", "_ant"))
        merged["Monto_ant"] = merged["Monto_ant"].fillna(0)

        for _, row in merged.iterrows():
            if row["Monto_ant"] > 0:
                variacion = (row["Monto_act"] - row["Monto_ant"]) / row["Monto_ant"]
                if variacion > 0.5:
                    st.warning(
                        f"🔶 Gasto inusual en **{row['Categoría']}**.\n"
                        f"Mes actual: ${formato_argentino(row['Monto_act'])} — "
                        f"Mes anterior: ${formato_argentino(row['Monto_ant'])}\n"
                        f"Aumento del {variacion*100:.1f}%"
                    )
    else:
        st.info("No hay suficientes meses para comparar gastos.")


if __name__ == "__main__":
    main()