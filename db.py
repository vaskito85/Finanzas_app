import json
from typing import Any, Dict, List, Optional
import streamlit as st

from supabase_client import get_supabase_client

# ---------------------------------------------------------
#  INSERTAR MOVIMIENTO
# ---------------------------------------------------------
def insertar_movimiento(
    usuario_id: str,
    fecha: str,
    categoria: str,
    tipo: str,
    descripcion: str,
    monto: float,
    cuenta: str,
    etiquetas_json: Optional[str],
) -> bool:
    """
    Inserta un movimiento en la tabla 'movimientos'.
    Devuelve True si fue insertado correctamente.
    """
    try:
        supabase = get_supabase_client()

        try:
            etiquetas = json.loads(etiquetas_json) if etiquetas_json else []
            if not isinstance(etiquetas, list):
                etiquetas = []
        except Exception:
            etiquetas = []

        data = {
            "usuario_id": usuario_id,
            "fecha": fecha,
            "categoria": categoria or "Sin categoría",
            "tipo": tipo,
            "descripcion": descripcion or "",
            "monto": float(monto) if monto is not None else 0.0,
            "cuenta": cuenta or "Sin cuenta",
            "etiquetas": etiquetas,
            "deleted": False,
        }

        result = supabase.table("movimientos").insert(data).execute()

        # Invalidar cache tras inserción
        st.cache_data.clear()
        return result.data is not None

    except Exception as e:
        print(f"[DB] Error al insertar movimiento: {e}")
        return False


# ---------------------------------------------------------
#  OBTENER MOVIMIENTOS (ACTIVOS) - legacy (trae todo)
# ---------------------------------------------------------
def obtener_movimientos(usuario_id: str) -> List[Dict[str, Any]]:
    try:
        supabase = get_supabase_client()

        result = (
            supabase.table("movimientos")
            .select("*")
            .eq("usuario_id", usuario_id)
            .eq("deleted", False)
            .order("fecha", desc=True)
            .order("id", desc=True)
            .execute()
        )

        return result.data or []

    except Exception as e:
        print(f"[DB] Error al obtener movimientos: {e}")
        return []


# ---------------------------------------------------------
#  OBTENER MOVIMIENTOS PAGINADOS (server-side)
# ---------------------------------------------------------
def obtener_movimientos_paginados(
    usuario_id: str,
    limit: int = 50,
    offset: int = 0,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    cuenta: Optional[str] = None,
    categoria: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Devuelve un dict con:
      - data: lista de filas (dicts)
      - count: número total de filas que coinciden con los filtros (int)

    Usa select(..., count="exact") para obtener el total (si el proveedor lo soporta).
    La paginación se aplica con .range(start, end) (supabase python client).
    """
    try:
        supabase = get_supabase_client()

        query = supabase.table("movimientos").select("*", count="exact").eq("usuario_id", usuario_id).eq("deleted", False)

        if fecha_desde:
            # Supabase/Postgres:>= fecha_desde
            query = query.gte("fecha", fecha_desde)
        if fecha_hasta:
            query = query.lte("fecha", fecha_hasta)
        if cuenta and cuenta != "Todas":
            query = query.eq("cuenta", cuenta)
        if categoria and categoria != "Todas":
            query = query.eq("categoria", categoria)

        # Order consistent: fecha desc, id desc
        query = query.order("fecha", desc=True).order("id", desc=True)

        start = int(offset)
        end = int(offset + limit - 1)
        result = query.range(start, end).execute()

        rows = result.data or []
        total = getattr(result, "count", None)
        # Si count no está disponible, intentar inferir (menos preciso)
        if total is None:
            # Si estamos en la primera página y rows < limit, asumimos total = len(rows)
            # No es perfecto pero evita None
            total = len(rows) if offset == 0 else None

        return {"data": rows, "count": total or 0}

    except Exception as e:
        print(f"[DB] Error al obtener movimientos paginados: {e}")
        return {"data": [], "count": 0}


# ---------------------------------------------------------
#  OBTENER MOVIMIENTOS BORRADOS
# ---------------------------------------------------------
def obtener_movimientos_borrados(usuario_id: str) -> List[Dict[str, Any]]:
    try:
        supabase = get_supabase_client()

        result = (
            supabase.table("movimientos")
            .select("*")
            .eq("usuario_id", usuario_id)
            .eq("deleted", True)
            .order("fecha", desc=True)
            .order("id", desc=True)
            .execute()
        )

        return result.data or []

    except Exception as e:
        print(f"[DB] Error al obtener movimientos borrados: {e}")
        return []


# ---------------------------------------------------------
#  OBTENER UN MOVIMIENTO POR ID
# ---------------------------------------------------------
def obtener_movimiento_por_id(usuario_id: str, movimiento_id: int) -> Optional[Dict[str, Any]]:
    try:
        supabase = get_supabase_client()

        result = (
            supabase.table("movimientos")
            .select("*")
            .eq("usuario_id", usuario_id)
            .eq("id", movimiento_id)
            .single()
            .execute()
        )

        return result.data

    except Exception as e:
        print(f"[DB] Error al obtener movimiento por id: {e}")
        return None


# ---------------------------------------------------------
#  ACTUALIZAR MOVIMIENTO
# ---------------------------------------------------------
def actualizar_movimiento(
    usuario_id: str,
    movimiento_id: int,
    fecha: str,
    categoria: str,
    tipo: str,
    descripcion: str,
    monto: float,
    cuenta: str,
    etiquetas_json: Optional[str],
) -> bool:
    try:
        supabase = get_supabase_client()

        try:
            etiquetas = json.loads(etiquetas_json) if etiquetas_json else []
            if not isinstance(etiquetas, list):
                etiquetas = []
        except Exception:
            etiquetas = []

        data = {
            "fecha": fecha,
            "categoria": categoria or "Sin categoría",
            "tipo": tipo,
            "descripcion": descripcion or "",
            "monto": float(monto) if monto is not None else 0.0,
            "cuenta": cuenta or "Sin cuenta",
            "etiquetas": etiquetas,
        }

        result = (
            supabase.table("movimientos")
            .update(data)
            .eq("id", movimiento_id)
            .eq("usuario_id", usuario_id)
            .execute()
        )

        # Invalidar cache tras actualización
        st.cache_data.clear()
        return result.data is not None

    except Exception as e:
        print(f"[DB] Error al actualizar movimiento: {e}")
        return False


# ---------------------------------------------------------
#  ELIMINAR (LÓGICO) MOVIMIENTO
# ---------------------------------------------------------
def eliminar_movimiento_logico(usuario_id: str, movimiento_id: int) -> bool:
    try:
        supabase = get_supabase_client()

        result = (
            supabase.table("movimientos")
            .update({"deleted": True})
            .eq("id", movimiento_id)
            .eq("usuario_id", usuario_id)
            .execute()
        )

        # Invalidar cache tras eliminación lógica
        st.cache_data.clear()
        return result.data is not None

    except Exception as e:
        print(f"[DB] Error al eliminar (lógico) movimiento: {e}")
        return False


# ---------------------------------------------------------
#  RESTAURAR MOVIMIENTO
# ---------------------------------------------------------
def restaurar_movimiento(usuario_id: str, movimiento_id: int) -> bool:
    try:
        supabase = get_supabase_client()

        result = (
            supabase.table("movimientos")
            .update({"deleted": False})
            .eq("id", movimiento_id)
            .eq("usuario_id", usuario_id)
            .execute()
        )

        # Invalidar cache tras restaurar
        st.cache_data.clear()
        return result.data is not None

    except Exception as e:
        print(f"[DB] Error al restaurar movimiento: {e}")
        return False