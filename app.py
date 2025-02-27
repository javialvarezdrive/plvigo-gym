import streamlit as st
from auth import display_login_form, check_auth_status
from database import init_supabase_client
from pages import home

st.set_page_config(
    page_title="Dashboard Gym",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializar el cliente de Supabase (fuera de la condicional para que esté disponible siempre)
supabase_client = init_supabase_client()

def main():
    st.title("Dashboard de Gestión de Gimnasio")

    if not check_auth_status():
        display_login_form(supabase_client)  # Mostrar formulario de login si no está logueado
    else:
        home.home_page()  # Mostrar la página principal si está logueado


if __name__ == "__main__":
    main()
