from dataclasses import dataclass
from typing import List, Any, Dict
import json
import streamlit as st

from db import obtener_movimientos, obtener_movimientos_borrados

@dataclass
class Movimiento:
    id: Any
    fecha: str
    categoria: str
    tipo: str
    descripcion: str
    monto: float
    cuenta: str
    etiquetas: List[str]
    created_at: Any = None
    deleted: bool = False


def _parse_etiquetas(raw: Any) -> list:
    """Convierte etiquetas en lista segura."""
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x) for x in raw]
    try:
        # Si viene como JSON string
        return json.loads(raw)
    except Exception:
        # Fallback: intentar separar por comas
        try:
            return [x.strip() for x in str(raw).split(",") if x.strip()]
        except Exception:
            return []


def _parse_deleted(value: Any) -> bool:
    """Convierte deleted en booleano seguro."""
    if isinstance(value, bool):
        return value
    if value in (1, "1", "true", "True", "TRUE"):
        return True
    return False


@st.cache_data(ttl=300)
def listar_movimientos(usuario_id: str) -> List[Movimiento]:
    """
    Devuelve la lista de movimientos como objetos Movimiento.
    Cacheada por Streamlit por defecto 300s (5 minutos).
    """
    rows = obtener_movimientos(usuario_id)
    movimientos: List[Movimiento] = []

    for row in rows:
        movimientos.append(
            Movimiento(
                id=row.get("id"),
                fecha=row.get("fecha") or "",
                categoria=row.get("categoria") or "Sin categoría",
                tipo=row.get("tipo") or "",
                descripcion=row.get("descripcion") or "",
                monto=float(row.get("monto") or 0),
                cuenta=row.get("cuenta") or "Sin cuenta",
                etiquetas=_parse_etiquetas(row.get("etiquetas")),
                created_at=row.get("created_at"),
                deleted=_parse_deleted(row.get("deleted")),
            )
        )

    return movimientos


@st.cache_data(ttl=300)
def listar_movimientos_borrados(usuario_id: str) -> List[Movimiento]:
    """
    Lista movimientos marcados como borrados (deleted = True).
    Cacheada por 300s.
    """
    rows = obtener_movimientos_borrados(usuario_id)
    movimientos: List[Movimiento] = []

    for row in rows:
        movimientos.append(
            Movimiento(
                id=row.get("id"),
                fecha=row.get("fecha") or "",
                categoria=row.get("categoria") or "Sin categoría",
                tipo=row.get("tipo") or "",
                descripcion=row.get("descripcion") or "",
                monto=float(row.get("monto") or 0),
                cuenta=row.get("cuenta") or "Sin cuenta",
                etiquetas=_parse_etiquetas(row.get("etiquetas")),
                created_at=row.get("created_at"),
                deleted=_parse_deleted(row.get("deleted")),
            )
        )

    return movimientos