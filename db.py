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

        payload = {
            "usuario_id": usuario_id,
            "fecha": fecha,
            "categoria": categoria,
            "tipo": tipo,
            "descripcion": descripcion,
            "monto": monto,
            "cuenta": cuenta,
            "etiquetas": etiquetas_json or "[]",
            "deleted": False,
        }

        result = supabase.table("movimientos").insert(payload).execute()

        # Si la inserción fue exitosa, invalidamos cache de movimientos
        st.cache_data.clear()
        return result.data is not None

    except Exception as e:
        print(f"[DB] Error al insertar movimiento: {e}")
        return False


# ---------------------------------------------------------
#  OBTENER MOVIMIENTOS (ACTIVOS)
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

        payload = {
            "fecha": fecha,
            "categoria": categoria,
            "tipo": tipo,
            "descripcion": descripcion,
            "monto": monto,
            "cuenta": cuenta,
            "etiquetas": etiquetas_json or "[]",
        }

        result = (
            supabase.table("movimientos")
            .update(payload)
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