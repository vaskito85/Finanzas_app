# models.py

from dataclasses import dataclass
from typing import List
from db import obtener_movimientos


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


def listar_movimientos(usuario_id: str) -> List[Movimiento]:
    """
    Convierte los registros crudos de Supabase en objetos Movimiento.
    """
    rows = obtener_movimientos(usuario_id)

    return [
        Movimiento(
            id=row["id"],
            fecha=row["fecha"],
            categoria=row["categoria"],
            tipo=row["tipo"],
            descripcion=row["descripcion"],
            monto=row["monto"],
            cuenta=row["cuenta"],
            etiquetas=row.get("etiquetas") or [],
        )
        for row in rows
    ]