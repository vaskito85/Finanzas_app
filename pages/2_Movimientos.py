import streamlit as st
import pandas as pd

from models import listar_movimientos
from db import eliminar_movimiento
from auth import check_auth
from ui import top_menu


def formato_argentino(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def aplicar_filtros(df: pd.DataFrame):
    if df.empty:
        return df

    st.sidebar.subheader("Filtros")

    # Convertir fecha
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    min_date = df["Fecha"].min().date()
    max_date = df["Fecha"].max().date()

    # Filtro de fechas
    fecha_desde, fecha_hasta = st.sidebar.date_input(
        "Rango de fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # Streamlit a veces devuelve tupla dentro de tupla
    if isinstance(fecha_desde, tuple):
        fecha_desde, fecha_hasta = fecha_desde

    mask_fecha = (df["Fecha"].dt.date >= fecha_desde) & (df["Fecha"].dt.date <= fecha_hasta)

    # Filtro de categorías
    categorias = sorted(df["Categoría"].dropna().unique().tolist())
    categorias_sel = st.sidebar.multiselect(
        "Categorías",
        options=categorias,
        default=categorias,
    )
    mask_cat = df["Categoría"].isin(categorias_sel) if categorias_sel else True

    # Filtro de cuentas
    cuentas = sorted(df["Cuenta"].dropna().unique().tolist())
    cuentas_sel = st.sidebar.multiselect(
        "Cuenta",
        options=cuentas,
        default=cuentas,
    )
    mask_cuenta = df["Cuenta"].isin(cuentas_sel) if cuentas_sel else True

    return df[mask_fecha & mask_cat & mask_cuenta].copy()


def main():
    # Seguridad
    check_auth()
    top_menu()

    usuario_id = st.session_state["user"]["id"]

    st.title("📄 Movimientos")

    # Obtener movimientos desde Supabase
    movimientos = listar_movimientos(usuario_id)

    if not movimientos:
        st.info("Todavía no hay movimientos cargados.")
        return

    # Convertir a DataFrame
    df = pd.DataFrame(
        [
            {
                "ID": m.id,
                "Fecha": m.fecha,
                "Tipo": m.tipo.lower(),  # 🔥 Normalizamos
                "Categoría": m.categoria,
                "Descripción": m.descripcion,
                "Monto": m.monto,
                "Cuenta": m.cuenta,
                "Etiquetas": ", ".join(m.etiquetas),
            }
            for m in movimientos
        ]
    )

    # Aplicar filtros
    df_filtrado = aplicar_filtros(df)

    if df_filtrado.empty:
        st.warning("No hay movimientos que coincidan con los filtros seleccionados.")
        return

    # Formato argentino
    df_filtrado["Monto"] = df_filtrado["Monto"].apply(formato_argentino)

    # Mostrar tabla
    st.subheader("Listado de movimientos")
    st.dataframe(df_filtrado, use_container_width=True)

    # Exportar CSV
    st.subheader("Exportar")
    csv_data = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar CSV",
        data=csv_data,
        file_name="movimientos_filtrados.csv",
        mime="text/csv",
    )

    st.markdown("---")

    # Eliminar movimiento
    st.subheader("Eliminar movimiento")
    id_a_eliminar = st.number_input("ID del movimiento a eliminar", min_value=0, step=1)

    if st.button("Eliminar"):
        if id_a_eliminar > 0:
            eliminar_movimiento(usuario_id, int(id_a_eliminar))
            st.success("Movimiento eliminado. Recargá la página.")
        else:
            st.warning("Ingresá un ID válido.")


if __name__ == "__main__":
    main()