import streamlit as st
from database import init_supabase_client
import bcrypt  # Importamos la biblioteca bcrypt

def hash_password(password):
    """Hashea la contraseña utilizando bcrypt."""
    salt = bcrypt.gensalt()  # Genera una 'sal' aleatoria
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt) # Hashea la contraseña (codificándola a bytes)
    return hashed_password.decode('utf-8') # Devuelve el hash como string

def verify_password(plain_password, hashed_password_from_db):
    """Verifica si la contraseña en texto plano coincide con el hash almacenado."""
    hashed_bytes = hashed_password_from_db.encode('utf-8') # Codifica el hash de la DB a bytes
    plain_bytes = plain_password.encode('utf-8') # Codifica la contraseña plana a bytes
    return bcrypt.checkpw(plain_bytes, hashed_bytes) # Compara usando bcrypt.checkpw

def login(username, password, supabase_client):
    """
    Autentica al usuario contra la tabla 'monitores' en Supabase, usando hashing bcrypt.
    Devuelve True si la autenticación es exitosa, False en caso contrario.
    """
    try:
        response = supabase_client.table("monitors").select("*").eq("username", username).execute() # ¡OJO! Usamos "monitors" en minúsculas
        data = response.data

        if data:
            user_data = data[0]
            stored_password_hash = user_data.get("password_hash")

            if stored_password_hash and verify_password(password, stored_password_hash): # ¡Usamos verify_password para comparar hashes!
                st.session_state.logged_in = True
                st.session_state.user_data = user_data
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
    st.session_state.user_data = None

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
            st.rerun()

    if st.button("Recuperar Contraseña"):
        forgot_password()

def display_logout_button():
    """Muestra el botón de cierre de sesión."""
    if st.button("Cerrar Sesión"):
        logout()
        st.rerun()


# --- Funciones de EJEMPLO para REGISTRO (solo para demostración, NO para UI todavía) ---
# --- ¡IMPORTANTE! En un sistema real, el registro debe ser más robusto y seguro ---

def register_monitor(supabase_client, username, plain_password, nombre, apellidos, email=None, rol='monitor'):
    """
    Registra un nuevo monitor en la base de datos.
    ¡Solo para DEMOSTRACIÓN y pruebas iniciales!
    En un sistema real, el registro sería más complejo y seguro.
    """
    hashed_password = hash_password(plain_password) # Hashea la contraseña ANTES de guardar
    try:
        response = supabase_client.table("monitors").insert({
            'username': username,
            'password_hash': hashed_password, # Guarda el HASH, no la contraseña plana
            'nombre': nombre,
            'apellidos': apellidos,
            'email': email,
            'rol': rol
        }).execute()
        if response.error:
            st.error(f"Error al registrar monitor: {response.error}")
            return False
        else:
            st.success(f"Monitor '{username}' registrado exitosamente.")
            return True
    except Exception as e:
        st.error(f"Error inesperado durante el registro: {e}")
        return False


if __name__ == "__main__":
    # --- Código de EJEMPLO para REGISTRAR un usuario de prueba (¡SOLO PARA DEMOSTRACIÓN!) ---
    # --- ¡BORRAR o COMENTAR este bloque después de crear un usuario de prueba! ---
    supabase_client_example = init_supabase_client() # Inicializa el cliente para el ejemplo

    if register_monitor(supabase_client_example,
                        username="monitor_prueba", # Nombre de usuario de prueba
                        plain_password="password123", # Contraseña de prueba (¡NO SEGURA para producción!)
                        nombre="Monitor",
                        apellidos="De Prueba",
                        email="monitor.prueba@example.com"):
        st.success("Usuario de prueba 'monitor_prueba' registrado. ¡Ahora puedes intentar iniciar sesión con él!")
    else:
        st.error("No se pudo registrar el usuario de prueba.")

    # --- FIN del bloque de EJEMPLO de REGISTRO ---
