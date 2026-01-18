import os
import streamlit as st
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

# ---------------------------------------------------------
#  OBTENER CLIENTE SUPABASE (CACHEADO POR STREAMLIT)
# ---------------------------------------------------------
# Usamos st.cache_resource para reutilizar el cliente entre reruns
# y evitar recrearlo en cada interacción.
@st.cache_resource(ttl=None)
def get_supabase_client() -> Client:
    """
    Devuelve una instancia cacheada del cliente de Supabase.
    Si falla la creación, lanza un error claro.
    """
    try:
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    except Exception as e:
        raise RuntimeError(f"Error al inicializar Supabase: {e}")
    return client