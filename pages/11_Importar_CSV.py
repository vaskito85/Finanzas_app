import streamlit as st
import pandas as pd
import json

from db import insertar_movimiento
from auth import check_auth
from ui import topbar


def formato_argentino_a_float(valor):
    """
    Convierte valores tipo '10.500,75' → 10500.75
    """
    if isinstance(valor, str):
        valor = valor.replace(".", "").replace(",", ".")
    try:
        return float(valor)
    except:
        return None


def main():
    # Seguridad
    check_auth()

    # Barra fija + menú superior
    topbar()

    usuario_id = st.session_state["user"]["id"]

    st.title("📥 Importar Movimientos desde CSV")

    st.write("""
    Subí un archivo CSV con las siguientes columnas:

    - **fecha** (YYYY-MM-DD)
    - **categoria**
    - **tipo** (ingreso / gasto)
    - **descripcion**
    - **monto**
    - **cuenta**
    - **etiquetas** (opcional, separadas por comas)
    """)

    archivo = st.file_uploader("Seleccionar archivo CSV", type=["csv"])

    if archivo is None:
        return

    # Leer CSV
    try:
        df = pd.read_csv(archivo)
    except Exception as e:
        st.error(f"Error al leer el CSV: {e}")
        return

    columnas_obligatorias = ["fecha", "categoria", "tipo", "descripcion", "monto", "cuenta"]

    if not all(col in df.columns for col in columnas_obligatorias):
        st.error("El CSV no contiene todas las columnas obligatorias.")
        st.write("Columnas requeridas:", columnas_obligatorias)
        st.write("Columnas encontradas:", df.columns.tolist())
        return

    # Convertir montos al formato correcto
    df["monto"] = df["monto"].apply(formato_argentino_a_float)

    # Procesar etiquetas si existen
    if "etiquetas" not in df.columns:
        df["etiquetas"] = ""

    st.subheader("Previsualización del archivo")
    st.dataframe(df)

    # Importar movimientos
    if st.button("Importar movimientos"):
        errores = 0
        cargados = 0

        for _, row in df.iterrows():
            try:
                etiquetas = []
                if isinstance(row["etiquetas"], str) and row["etiquetas"].strip():
                    etiquetas = [e.strip() for e in row["etiquetas"].split(",") if e.strip()]

                insertar_movimiento(
                    usuario_id=usuario_id,
                    fecha=str(row["fecha"]),
                    categoria=row["categoria"],
                    tipo=row["tipo"].lower(),  # 🔥 Normalizamos
                    descripcion=row["descripcion"],
                    monto=float(row["monto"]),
                    cuenta=row["cuenta"],
                    etiquetas_json=json.dumps(etiquetas, ensure_ascii=False),
                )
                cargados += 1
            except Exception as e:
                errores += 1

        st.success(f"Movimientos cargados: {cargados}")
        if errores > 0:
            st.warning(f"Movimientos con error: {errores}")


if __name__ == "__main__":
    main()