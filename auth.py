import streamlit as st
from database import init_supabase_client

def login(username, password, supabase_client):
    """
    Autentica al usuario contra la tabla 'monitores' en Supabase.
    Devuelve True si la autenticación es exitosa, False en caso contrario.
    """
    try:
        response = supabase_client.table("monitores").select("*").eq("username", username).execute()
        data = response.data

        if data:
            user_data = data[0]
            stored_password_hash = user_data.get("password_hash")

            # **¡IMPORTANTE DE SEGURIDAD!**
            # En un sistema real, NUNCA almacenes contraseñas en texto plano.
            # Aquí, para simplicidad del ejemplo, asumimos que 'password_hash'
            # contiene la contraseña en texto plano.
            # **DEBES USAR UN HASHING ROBUSTO DE CONTRASEÑAS EN PRODUCCIÓN.**
            # Ejemplos de hashing seguro: bcrypt, argon2, scrypt.

            if password == stored_password_hash: # **¡REEMPLAZAR CON COMPARACIÓN DE HASHES EN PRODUCCIÓN!**
                st.session_state.logged_in = True
                st.session_state.user_data = user_data # Guarda información del usuario en sesión
                return True
            else:
                st.error("Contraseña incorrecta.")
                return False
        else:
            st.error("Usuario no encontrado.")
            return False
    except Exception as e:
        st.error(f"Error inesperado durante el login: {e}")
        return False

def logout():
    """Cierra la sesión del usuario."""
    st.session_state.logged_in = False
    st.session_state.user_data = None # Limpia la información del usuario

def forgot_password():
    """Función placeholder para la recuperación de contraseña."""
    st.info("Funcionalidad de recuperación de contraseña no implementada en este ejemplo básico.")
    st.info("En un sistema real, esto implicaría enviar un email de restablecimiento de contraseña.")

def check_auth_status():
    """Verifica si el usuario ha iniciado sesión."""
    return st.session_state.get("logged_in", False)

def display_login_form(supabase_client):
    """Muestra el formulario de inicio de sesión."""
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar Sesión"):
        if login(username, password, supabase_client):
            st.success("Inicio de sesión exitoso!")
            st.rerun() # Recargar la app para mostrar el contenido logueado

    if st.button("Recuperar Contraseña"):
        forgot_password()


def display_logout_button():
    """Muestra el botón de cierre de sesión."""
    if st.button("Cerrar Sesión"):
        logout()
        st.rerun() # Recargar la app para volver a la pantalla de login
