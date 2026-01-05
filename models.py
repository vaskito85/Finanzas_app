from dataclasses import dataclass
from typing import List, Any
from db import obtener_movimientos, obtener_movimientos_borrados
import json


@dataclass
class Movimiento:
    id: int
    fecha: str
    categoria: str
    tipo: str
    descripcion: str
    monto: float
    cuenta: str
    etiquetas: list
    created_at: str | None
    deleted: bool


def _parse_etiquetas(raw: Any) -> list:
    """Convierte etiquetas en lista segura."""
    if raw is None:
        return []

    if isinstance(raw, list):
        return raw

    if isinstance(raw, str):
        try:
            data = json.loads(raw)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    return []


def _parse_deleted(value: Any) -> bool:
    """Convierte deleted en booleano seguro."""
    if isinstance(value, bool):
        return value
    if value in ("true", "True", "1", 1):
        return True
    return False


def listar_movimientos(usuario_id: str) -> List[Movimiento]:
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


def listar_movimientos_borrados(usuario_id: str) -> List[Movimiento]:
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