from typing import List
from supabase_client import get_supabase_client

CATEGORIAS_SUGERIDAS = [
    "Ingresos",        # nueva categoría para entradas de dinero
    "General",
    "Comida",
    "Transporte",
    "Servicios",
    "Salud",
    "Educación",
    "Inversión",
    "Hogar",
    "Ocio",
    "Viajes",
    "Impuestos",
    "Compras",
]

ETIQUETAS_SUGERIDAS = [
    "comida",
    "supermercado",
    "transporte",
    "combustible",
    "salud",
    "farmacia",
    "servicios",
    "alquiler",
    "ocio",
    "educación",
    "inversión",
    "impuestos",
    "compras",
    "hogar",
    "viajes",
]

CUENTAS_SUGERIDAS = [
    "Banco Santander",
    "Mercado Pago",
    "BullMarket",
    "Balanz",
    "Buenbit",
    "Efectivo",
]


def _ensure_defaults(usuario_id: str):
    supabase = get_supabase_client()

    # Categorías
    for nombre in CATEGORIAS_SUGERIDAS:
        supabase.table("categorias").upsert(
            {"usuario_id": usuario_id, "nombre": nombre},
            on_conflict="usuario_id,nombre"
        ).execute()

    # Etiquetas
    for nombre in ETIQUETAS_SUGERIDAS:
        supabase.table("etiquetas").upsert(
            {"usuario_id": usuario_id, "nombre": nombre},
            on_conflict="usuario_id,nombre"
        ).execute()

    # Cuentas
    for nombre in CUENTAS_SUGERIDAS:
        supabase.table("cuentas").upsert(
            {"usuario_id": usuario_id, "nombre": nombre},
            on_conflict="usuario_id,nombre"
        ).execute()


def obtener_categorias(usuario_id: str) -> List[str]:
    supabase = get_supabase_client()
    _ensure_defaults(usuario_id)

    result = (
        supabase.table("categorias")
        .select("nombre")
        .eq("usuario_id", usuario_id)
        .order("nombre", desc=False)
        .execute()
    )
    return [r["nombre"] for r in (result.data or [])]


def obtener_etiquetas(usuario_id: str) -> List[str]:
    supabase = get_supabase_client()
    _ensure_defaults(usuario_id)

    result = (
        supabase.table("etiquetas")
        .select("nombre")
        .eq("usuario_id", usuario_id)
        .order("nombre", desc=False)
        .execute()
    )
    return [r["nombre"] for r in (result.data or [])]


def obtener_cuentas(usuario_id: str) -> List[str]:
    supabase = get_supabase_client()
    _ensure_defaults(usuario_id)

    result = (
        supabase.table("cuentas")
        .select("nombre")
        .eq("usuario_id", usuario_id)
        .order("nombre", desc=False)
        .execute()
    )
    return [r["nombre"] for r in (result.data or [])]


def agregar_categoria(usuario_id: str, nombre: str):
    if not nombre.strip():
        return
    supabase = get_supabase_client()
    supabase.table("categorias").upsert(
        {"usuario_id": usuario_id, "nombre": nombre.strip()},
        on_conflict="usuario_id,nombre"
    ).execute()


def agregar_etiqueta(usuario_id: str, nombre: str):
    if not nombre.strip():
        return
    supabase = get_supabase_client()
    supabase.table("etiquetas").upsert(
        {"usuario_id": usuario_id, "nombre": nombre.strip()},
        on_conflict="usuario_id,nombre"
    ).execute()


def agregar_cuenta(usuario_id: str, nombre: str):
    if not nombre.strip():
        return
    supabase = get_supabase_client()
    supabase.table("cuentas").upsert(
        {"usuario_id": usuario_id, "nombre": nombre.strip()},
        on_conflict="usuario_id,nombre"
    ).execute()