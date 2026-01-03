# db.py

import json
from typing import Any, Dict, List
from supabase_client import get_supabase_client


def insertar_movimiento(
    usuario_id: str,
    fecha: str,
    categoria: str,
    tipo: str,
    descripcion: str,
    monto: float,
    cuenta: str,
    etiquetas_json: str | None
) -> None:
    try:
        supabase = get_supabase_client()

        data = {
            "usuario_id": usuario_id,
            "fecha": fecha,
            "categoria": categoria,
            "tipo": tipo,
            "descripcion": descripcion,
            "monto": monto,
            "cuenta": cuenta,
            "etiquetas": json.loads(etiquetas_json) if etiquetas_json else [],
        }

        supabase.table("movimientos").insert(data).execute()

    except Exception as e:
        print(f"Error al insertar movimiento: {e}")


def obtener_movimientos(usuario_id: str) -> List[Dict[str, Any]]:
    try:
        supabase = get_supabase_client()

        result = (
            supabase.table("movimientos")
            .select("*")
            .eq("usuario_id", usuario_id)
            .order("fecha", desc=True)
            .execute()
        )

        return result.data or []

    except Exception as e:
        print(f"Error al obtener movimientos: {e}")
        return []


def eliminar_movimiento(usuario_id: str, movimiento_id: int) -> None:
    try:
        supabase = get_supabase_client()

        supabase.table("movimientos") \
            .delete() \
            .eq("id", movimiento_id) \
            .eq("usuario_id", usuario_id) \
            .execute()

    except Exception as e:
        print(f"Error al eliminar movimiento: {e}")