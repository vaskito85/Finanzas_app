import streamlit as st
import pandas as pd
from typing import Optional

from auth import check_auth
from ui import topbar
from db import obtener_movimientos_paginados, eliminar_movimiento_logico
from catalogos import obtener_cuentas, obtener_categorias


PAGE_SIZE_OPTIONS = [10, 25, 50, 100]


def _reset_pagination_if_filters_changed(key: str, current_filters: tuple):
    """
    Guarda filtros en session_state bajo key+'_filters' y resetea page si cambiaron.
    """
    prev = st.session_state.get(f"{key}_filters")
    if prev != current_filters:
        st.session_state[f"{key}_filters"] = current_filters
        st.session_state[f"{key}_page"] = 0


def main():
    check_auth()
    topbar()

    if "user" not in st.session_state:
        st.error("No hay usuario autenticado.")
        st.stop()

    usuario_id = st.session_state["user"]["id"]

    st.markdown("## 📄 Movimientos (Paginado)")
    st.markdown("Filtrá, buscá y administrá tus movimientos financieros. Usamos paginación server-side para escalabilidad.")

    st.markdown("---")

    # Inicializar valores de paginación en session_state
    if "movimientos_page" not in st.session_state:
        st.session_state["movimientos_page"] = 0
    if "movimientos_page_size" not in st.session_state:
        st.session_state["movimientos_page_size"] = PAGE_SIZE_OPTIONS[1]  # default 25

    # Cargar catálogos
    try:
        cuentas = obtener_cuentas(usuario_id)
    except Exception:
        cuentas = []
    try:
        categorias = obtener_categorias(usuario_id)
    except Exception:
        categorias = []

    # Filtros UI
    colf1, colf2, colf3, colf4 = st.columns([3, 3, 2, 2])
    with colf1:
        fecha_desde = st.date_input("📅 Fecha desde", value=None)
    with colf2:
        fecha_hasta = st.date_input("📅 Fecha hasta", value=None)
    with colf3:
        cuenta_filtro = st.selectbox("🏦 Cuenta", ["Todas"] + cuentas)
    with colf4:
        categoria_filtro = st.selectbox("📂 Categoría", ["Todas"] + categorias)

    # Page size selector
    colp1, colp2 = st.columns([3, 1])
    with colp1:
        page_size = st.selectbox("Filas por página", PAGE_SIZE_OPTIONS, index=PAGE_SIZE_OPTIONS.index(st.session_state["movimientos_page_size"]))
    with colp2:
        # Search-like action to reset page
        if st.button("Aplicar filtros", use_container_width=True):
            # will cause fetching with new filters + reset page
            st.session_state["movimientos_page_size"] = page_size
            st.session_state["movimientos_page"] = 0

    # Guardar/actualizar page_size en session_state
    st.session_state["movimientos_page_size"] = page_size

    # Preparar filtros para comparar cambios
    filtros_tuple = (
        str(fecha_desde) if fecha_desde else "",
        str(fecha_hasta) if fecha_hasta else "",
        cuenta_filtro or "Todas",
        categoria_filtro or "Todas",
        page_size,
    )
    _reset_pagination_if_filters_changed("movimientos", filtros_tuple)

    # Obtener página actual desde session_state
    page = st.session_state.get("movimientos_page", 0)
    limit = int(st.session_state.get("movimientos_page_size", page_size))
    offset = page * limit

    # Llamada al servidor (con spinner)
    with st.spinner("Obteniendo movimientos..."):
        fecha_desde_str: Optional[str] = str(fecha_desde) if fecha_desde else None
        fecha_hasta_str: Optional[str] = str(fecha_hasta) if fecha_hasta else None

        result = obtener_movimientos_paginados(
            usuario_id=usuario_id,
            limit=limit,
            offset=offset,
            fecha_desde=fecha_desde_str,
            fecha_hasta=fecha_hasta_str,
            cuenta=(None if (cuenta_filtro == "Todas") else cuenta_filtro),
            categoria=(None if (categoria_filtro == "Todas") else categoria_filtro),
        )

    rows = result.get("data", []) or []
    total = int(result.get("count", 0) or 0)

    if total == 0:
        st.info("No hay movimientos que coincidan con los filtros seleccionados.")
        return

    df = pd.DataFrame(rows)

    # Asegurar columnas esperadas
    display_cols = ["id", "fecha", "categoria", "tipo", "descripcion", "monto", "cuenta"]
    available_cols = [c for c in display_cols if c in df.columns]
    st.markdown("### 📋 Listado de movimientos (página actual)")
    st.dataframe(df[available_cols], use_container_width=True)

    # Paginación UI
    coln1, coln2, coln3 = st.columns([1, 1, 4])
    with coln1:
        if st.button("⬅️ Anterior", disabled=(page == 0)):
            if page > 0:
                st.session_state["movimientos_page"] = page - 1
                st.experimental_rerun()
    with coln2:
        # Calcular si hay siguiente página
        has_next = (offset + len(rows)) < total
        if st.button("Siguiente ➡️", disabled=(not has_next)):
            if has_next:
                st.session_state["movimientos_page"] = page + 1
                st.experimental_rerun()
    with coln3:
        start_display = offset + 1
        end_display = offset + len(rows)
        st.markdown(f"Mostrando {start_display}–{end_display} de {total} movimientos — Página {page + 1}")

    st.markdown("---")
    st.markdown("### 🗑 Borrar movimiento (lógico) — solo IDs de la página actual")

    ids = df["id"].tolist() if "id" in df.columns else []
    if not ids:
        st.info("No hay movimientos en la página actual para borrar.")
        return

    id_sel = st.selectbox("Seleccionar ID a borrar", ids)

    if st.button("🗑 Borrar seleccionado", use_container_width=True):
        if eliminar_movimiento_logico(usuario_id, id_sel):
            st.success("Movimiento marcado como borrado.")
            # después de borrar, mantener en la misma página o recargar si página quedó vacía
            # si la página actual quedó vacía y no es la primera página, retrocedemos una página
            # forzamos recarga completa
            st.experimental_rerun()
        else:
            st.error("Error al borrar movimiento.")


if __name__ == "__main__":
    main()