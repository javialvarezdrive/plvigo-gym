import streamlit as st
from auth import check_auth_status, display_logout_button

def home_page():
    """Página de inicio que se muestra después del login."""
    if not check_auth_status():
        st.error("Acceso no autorizado. Por favor, inicia sesión.")
        return

    st.title("Dashboard Principal")
    st.write(f"Bienvenido, {st.session_state.user_data.get('nombre', 'Usuario')}!") # Saludo personalizado

    display_logout_button() # Botón de logout en la página principal

if __name__ == "__main__":
    home_page()
