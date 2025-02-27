import streamlit as st
from supabase import create_client, Client

@st.cache_resource  # Cache el cliente para que no se reinicialice en cada rerun
def init_supabase_client():
    """Inicializa y devuelve el cliente de Supabase."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase_client = create_client(url, key)
    return supabase_client
