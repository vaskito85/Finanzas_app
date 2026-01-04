import streamlit as st
import json
import os
import pandas as pd

from models import listar_movimientos
from auth import check_auth
from ui import topbar, top_menu


def formato_argentino(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# -------------------------------
#   ARCHIVO POR USUARIO
# -------------------------------

def get_user_obj_file(user_id: str) -> str:
    os.makedirs("objetivos", exist_ok=True)
    return os.path.join("objetivos", f"{user_id}.json")


def cargar_objetivos(user_id: str):
    path = get_user_obj_file(user_id)

    if not os.path.exists(path):
        return {"cuentas": {}, "cuentas_min": {}, "categorias": {}}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Migración suave
    if "cuentas_min" not in data:
        data["cuentas_min"] = {}

    return data


def guardar_objetivos(user_id: str, data):
    path = get_user_obj_file(user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# -------------------------------
#   PÁGINA PRINCIPAL
# -------------------------------

def main():
    check_auth()

    # Barra fija + menú superior
    topbar()
    top_menu()

    user_id = st.session_state["user"]["id"]

    st.title("🎯 Objetivos Financieros")

    objetivos = cargar_objetivos(user_id)

    movimientos = listar_movimientos(user_id)
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

    df["Monto_signed"] = df.apply(
        lambda row: row["Monto"] if row["Tipo"] == "ingreso" else -row["Monto"],
        axis=1,
    )

    # -------------------------------
    #   OBJETIVOS POR CUENTA
    # -------------------------------

    st.header("🏦 Objetivos por Cuenta")

    cuentas = sorted(df["Cuenta"].unique().tolist())
    cuenta_sel = st.selectbox("Seleccionar cuenta", cuentas)

    objetivo_total = st.number_input(
        "Objetivo de saldo total",
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        value=float(objetivos["cuentas"].get(cuenta_sel, 0)),
    )

    objetivo_minimo = st.number_input(
        "Saldo mínimo permitido",
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        value=float(objetivos["cuentas_min"].get(cuenta_sel, 0)),
    )

    if st.button("Guardar objetivos de cuenta"):
        objetivos["cuentas"][cuenta_sel] = objetivo_total
        objetivos["cuentas_min"][cuenta_sel] = objetivo_minimo
        guardar_objetivos(user_id, objetivos)
        st.success("Objetivos guardados.")

    st.subheader("Progreso por cuenta")

    saldo_por_cuenta = df.groupby("Cuenta")["Monto_signed"].sum()

    for cuenta, saldo in saldo_por_cuenta.items():
        st.write(f"### {cuenta}")
        st.write(f"Saldo actual: **${formato_argentino(saldo)}**")

        minimo = objetivos["cuentas_min"].get(cuenta)
        objetivo = objetivos["cuentas"].get(cuenta)

        if minimo:
            if saldo < minimo:
                st.error(f"🔻 Por debajo del mínimo (${formato_argentino(minimo)})")
            else:
                st.success(f"✔ Por encima del mínimo (${formato_argentino(minimo)})")

        if objetivo:
            progreso = min(saldo / objetivo, 1.0)
            st.progress(progreso)
            st.write(f"Objetivo total: ${formato_argentino(objetivo)}")
        else:
            st.info("No hay objetivo total definido para esta cuenta.")

    st.markdown("---")

    # -------------------------------
    #   OBJETIVOS POR CATEGORÍA
    # -------------------------------

    st.header("📂 Objetivos por Categoría")

    categorias = sorted(df["Categoría"].unique().tolist())
    categoria_sel = st.selectbox("Seleccionar categoría", categorias)

    objetivo_cat = st.number_input(
        "Límite de gasto para esta categoría",
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        value=float(objetivos["categorias"].get(categoria_sel, 0)),
    )

    if st.button("Guardar objetivo de categoría"):
        objetivos["categorias"][categoria_sel] = objetivo_cat
        guardar_objetivos(user_id, objetivos)
        st.success("Objetivo guardado.")

    st.subheader("Progreso por categoría")

    gastos_por_cat = (
        df[df["Tipo"] == "gasto"]
        .groupby("Categoría")["Monto"]
        .sum()
    )

    for categoria, gasto in gastos_por_cat.items():
        st.write(f"### {categoria}")
        st.write(f"Gasto actual: **${formato_argentino(gasto)}**")

        objetivo = objetivos["categorias"].get(categoria)
        if objetivo:
            progreso = min(gasto / objetivo, 1.0)
            st.progress(progreso)
            st.write(f"Límite: ${formato_argentino(objetivo)}")
        else:
            st.info("No hay límite definido para esta categoría.")


if __name__ == "__main__":
    main()