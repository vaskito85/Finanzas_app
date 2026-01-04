import os
from supabase import create_client, Client

# ---------------------------------------------------------
#  CARGA DE VARIABLES DE ENTORNO
# ---------------------------------------------------------

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").strip()
SUPABASE_ANON_KEY = (os.getenv("SUPABASE_ANON_KEY") or "").strip()

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise RuntimeError(
        "Faltan SUPABASE_URL o SUPABASE_ANON_KEY en las variables de entorno."
    )

# Cliente global reutilizable
_supabase_client: Client | None = None


# ---------------------------------------------------------
#  OBTENER CLIENTE SUPABASE (SINGLETON)
# ---------------------------------------------------------

def get_supabase_client() -> Client:
    """
    Devuelve una instancia única del cliente de Supabase.
    Si falla la creación, lanza un error claro.
    """
    global _supabase_client

    if _supabase_client is None:
        try:
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        except Exception as e:
            raise RuntimeError(f"Error al inicializar Supabase: {e}")

    return _supabase_client