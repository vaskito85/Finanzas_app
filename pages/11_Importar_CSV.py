import streamlit as st
import pandas as pd
import json

from db import insertar_movimiento
from auth import check_auth
from ui import topbar


def formato_argentino_a_float(valor):
    if isinstance(valor, str):
        valor = valor.replace(".", "").replace(",", ".")
    try:
        return float(valor)
    except:
        return None


def main():
    check_auth()
    topbar()

    usuario_id = st.session_state["user"]["id"]

    st.markdown("## 📥 Importar Movimientos desde CSV")
    st.markdown("Subí un archivo CSV para cargar múltiples movimientos de forma automática.")

    st.info(
        """
        El archivo debe contener las siguientes columnas:

        - **fecha** (YYYY-MM-DD)  
        - **categoria**  
        - **tipo** (ingreso / gasto)  
        - **descripcion**  
        - **monto**  
        - **cuenta**  
        - **etiquetas** (opcional, separadas por comas)
        """
    )

    archivo = st.file_uploader("Seleccionar archivo CSV", type=["csv"])

    if archivo is None:
        return

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

    df["monto"] = df["monto"].apply(formato_argentino_a_float)

    if "etiquetas" not in df.columns:
        df["etiquetas"] = ""

    st.subheader("📄 Previsualización del archivo")
    st.dataframe(df, use_container_width=True)

    if st.button("📥 Importar movimientos", use_container_width=True):
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
                    tipo=row["tipo"].lower(),
                    descripcion=row["descripcion"],
                    monto=float(row["monto"]),
                    cuenta=row["cuenta"],
                    etiquetas_json=json.dumps(etiquetas, ensure_ascii=False),
                )
                cargados += 1
            except:
                errores += 1

        st.success(f"Movimientos cargados: {cargados}")
        if errores > 0:
            st.warning(f"Movimientos con error: {errores}")


if __name__ == "__main__":
    main()