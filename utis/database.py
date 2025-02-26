# utils/database.py
import supabase
import pandas as pd

def init_supabase():
    # **¡¡¡CREDENTIALES DE SUPABASE HARDCODEADAS - NO RECOMENDADO PARA PRODUCCIÓN!!!**
    SUPABASE_URL = "https://anqvjvjpcokkwspaecfc.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFucXZqdmpwY29ra3dzcGFlY2ZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA1OTMyMDcsImV4cCI6MjA1NjE2OTIwN30.w4Y6sE8UyIA22pt5QAYQlcsWZceksF4AKF0zm7Jv7Lk"
    return supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

supabase_client = init_supabase()

def check_supabase_connection():
    """Verifica la conexión a Supabase."""
    try:
        response = supabase_client.table("actividades_tipos").select("id").limit(1).execute()
        if response.error:
            return False, response.error.message
        return True, None
    except Exception as e:
        return False, str(e)

def get_monitores():
    """Obtiene todos los monitores."""
    response = supabase_client.table("monitores").select("*").execute()
    if response.error:
        return None, response.error.message
    return response.data, None

def get_monitor_by_username(username):
    """Obtiene un monitor por su nombre de usuario."""
    response = supabase_client.table("monitores").select("*").eq("username", username).single().execute()
    if response.error:
        return None, response.error.message
    return response.data, None

def get_actividades_tipos():
    """Obtiene todos los tipos de actividad."""
    response = supabase_client.table("actividades_tipos").select("*").execute()
    if response.error:
        return None, response.error.message
    return response.data, None

def get_miembros():
    """Obtiene todos los miembros del gimnasio."""
    response = supabase_client.table("gym_members").select("*").execute()
    if response.error:
        return None, response.error.message
    return response.data, None

def crear_miembro(nip, nombre, apellidos, seccion, grupo):
    """Crea un nuevo miembro del gimnasio."""
    response = supabase_client.table("gym_members").insert({"nip": nip, "nombre": nombre, "apellidos": apellidos, "seccion": seccion, "grupo": grupo}).execute()
    return response

def get_actividades_programadas(fecha_inicio, fecha_fin):
    """Obtiene actividades programadas en un rango de fechas."""
    response = supabase_client.table("schedule").select("*, actividades_tipos(nombre), gym_members(nombre, apellidos)").gte("fecha", fecha_inicio).lte("fecha", fecha_fin).execute()
    if response.error:
        return None, response.error.message
    return response.data, None

def programar_actividad(member_id, actividad_tipo_id, fecha, turno, monitor_id):
    """Programa una actividad para un miembro."""
    response = supabase_client.table("schedule").insert({"member_id": member_id, "activity_id": actividad_tipo_id, "fecha": fecha, "turno": turno, "monitor_id": monitor_id}).execute()
    return response

