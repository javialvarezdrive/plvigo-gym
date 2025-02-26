# app.py
import streamlit as st
import datetime
import pandas as pd
import plotly_express as px
from utils import database

st.set_page_config(page_title="Gestión Gimnasio Nuevo", page_icon="💪")

def main():
    st.title("Gestión del Gimnasio")

    # Inicialización de Supabase y verificación de conexión
    if 'supabase_client' not in st.session_state:
        st.session_state['supabase_client'] = database.supabase_client
    supabase_client = st.session_state['supabase_client']

    connected, error_message = database.check_supabase_connection()
    if not connected:
        st.error(f"Error de conexión a Supabase: {error_message}")
        return

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'monitor' not in st.session_state:
        st.session_state['monitor'] = None

    if not st.session_state['logged_in']:
        login_section()
    else:
        app_content()

def login_section():
    st.header("Inicio de Sesión de Monitor")
    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        login_button = st.form_submit_button("Iniciar Sesión")

        if login_button:
            monitor_data, error_message = database.get_monitor_by_username(username)
            if error_message:
                st.error(f"Error al verificar usuario: {error_message}")
            elif monitor_data and bcrypt_check_password(password, monitor_data['password']): # Usando función bcrypt_check_password
                st.session_state['logged_in'] = True
                st.session_state['monitor'] = monitor_data
                st.success(f"Bienvenido, {monitor_data['nombre']}!")
                st.experimental_rerun()
            else:
                st.error("Credenciales incorrectas.")

def bcrypt_check_password(plain_password, hashed_password): # Función auxiliar para verificar bcrypt hash
    import bcrypt
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def app_content():
    st.sidebar.header(f"Monitor: {st.session_state['monitor']['nombre']}")
    menu_option = st.sidebar.radio("Menú", ["Registrar Miembro", "Programar Actividad", "Ver Reportes", "Cerrar Sesión"])

    if menu_option == "Registrar Miembro":
        registrar_miembro_ui()
    elif menu_option == "Programar Actividad":
        programar_actividad_ui()
    elif menu_option == "Ver Reportes":
        ver_reportes_ui()
    elif menu_option == "Cerrar Sesión":
        st.session_state['logged_in'] = False
        st.session_state['monitor'] = None
        st.experimental_rerun()

def registrar_miembro_ui():
    st.header("Registrar Nuevo Miembro")
    with st.form("registrar_miembro_form"):
        nip = st.text_input("NIP (Numérico)")
        nombre = st.text_input("Nombre")
        apellidos = st.text_input("Apellidos")
        seccion = st.selectbox("Sección", options=["SETRA", "Motorista", "GOA", "Patrullas"])
        grupo = st.selectbox("Grupo", options=["G-1", "G-2", "G-3"])
        submit_button = st.form_submit_button("Registrar Miembro")

        if submit_button:
            if not nip.isdigit():
                st.error("El NIP debe ser numérico.")
            else:
                response = database.crear_miembro(nip, nombre, apellidos, seccion, grupo)
                if response and response.status_code in range(200, 300):
                    st.success("Miembro registrado con éxito.")
                else:
                    st.error("Error al registrar el miembro.")

def programar_actividad_ui():
    st.header("Programar Actividad")
    actividades_tipos, error_tipos = database.get_actividades_tipos()
    miembros, error_miembros = database.get_miembros()

    if error_tipos:
        st.error(f"Error al cargar tipos de actividad: {error_tipos}")
        return
    if error_miembros:
        st.error(f"Error al cargar miembros: {error_miembros}")
        return

    if not actividades_tipos:
        st.warning("No hay tipos de actividad definidos.")
        return
    if not miembros:
        st.warning("No hay miembros registrados.")
        return

    tipo_actividad_options = {tipo['nombre']: tipo['id'] for tipo in actividades_tipos}
    miembro_options = {f"{miembro['nombre']} {miembro['apellidos']} - NIP: {miembro['nip']}": miembro['id'] for miembro in miembros}

    with st.form("programar_actividad_form"):
        fecha = st.date_input("Fecha", value=datetime.date.today())
        turno = st.selectbox("Turno", options=["Mañana", "Tarde", "Noche"])
        tipo_actividad_nombre = st.selectbox("Tipo de Actividad", options=list(tipo_actividad_options.keys()))
        miembro_nombre_nip = st.selectbox("Miembro", options=list(miembro_options.keys()))

        submit_button = st.form_submit_button("Programar Actividad")

        if submit_button:
            actividad_tipo_id = tipo_actividad_options[tipo_actividad_nombre]
            miembro_id = miembro_options[miembro_nombre_nip]
            monitor_id = st.session_state['monitor']['id'] # Asume que el monitor logueado es quien programa la actividad

            response = database.programar_actividad(miembro_id, actividad_tipo_id, fecha.isoformat(), turno, monitor_id)
            if response and response.status_code in range(200, 300):
                st.success("Actividad programada con éxito.")
            else:
                st.error("Error al programar la actividad.")

def ver_reportes_ui():
    st.header("Reportes de Actividades Programadas")
    fecha_inicio = st.date_input("Fecha de inicio", value=datetime.date.today() - datetime.timedelta(days=30))
    fecha_fin = st.date_input("Fecha de fin", value=datetime.date.today())

    if st.button("Generar Reporte"):
        actividades_programadas, error_actividades = database.get_actividades_programadas(fecha_inicio.isoformat(), fecha_fin.isoformat())
        if error_actividades:
            st.error(f"Error al obtener actividades: {error_actividades}")
            return

        if not actividades_programadas:
            st.info("No hay actividades programadas en el rango de fechas seleccionado.")
            return

        df_actividades = pd.DataFrame(actividades_programadas)
        if not df_actividades.empty:
            # Extracción de nombres de actividad y miembro para mejor visualización
            df_actividades['tipo_actividad_nombre'] = df_actividades['actividades_tipos'].apply(lambda x: x['nombre'] if x else 'Desconocido')
            df_actividades['miembro_nombre'] = df_actividades['gym_members'].apply(lambda x: f"{x['nombre']} {x['apellidos']}" if x else 'Desconocido')

            # Gráfico de barras por tipo de actividad
            conteo_actividades = df_actividades['tipo_actividad_nombre'].value_counts().reset_index()
            conteo_actividades.columns = ['Tipo de Actividad', 'Cantidad']
            fig = px.bar(conteo_actividades, x='Tipo de Actividad', y='Cantidad', title=f'Cantidad de Actividades por Tipo ({fecha_inicio.strftime("%d-%m-%Y")} a {fecha_fin.strftime("%d-%m-%Y")})')
            st.plotly_chart(fig)

            st.dataframe(df_actividades[['fecha', 'turno', 'tipo_actividad_nombre', 'miembro_nombre']], use_container_width=True)
        else:
            st.info("No hay actividades para mostrar en el rango de fechas.")


if __name__ == "__main__":
    main()
