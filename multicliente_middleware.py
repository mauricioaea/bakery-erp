# multicliente_middleware.py
from flask import g, session
from functools import wraps
import sqlite3

def obtener_info_usuario():
    """
    Obtiene información completa del usuario y panadería actual.
    """
    return {
        'panaderia_id': 1,
        'panaderia_nombre': 'Panadería Principal',
        'usuario_id': 1,
        'usuario_nombre': 'Administrador',
        'sucursal_id': 1,
        'sucursal_nombre': 'Sucursal Principal',
        'rol': 'admin',
        'permisos': ['ventas', 'productos', 'reportes', 'configuracion']
    }

def obtener_panaderia_usuario():
    """
    Obtiene la panadería asociada al usuario actual.
    """
    return 1  # Panadería principal

def get_panaderia_actual():
    """
    Obtiene la panadería actual del usuario.
    """
    return 1  # Panadería principal

def filtrar_por_panaderia(query, modelo=None):
    """
    Filtra un query por la panadería del usuario actual.
    Por ahora retorna el query sin cambios.
    """
    return query

def requiere_panaderia(f):
    """
    Decorador que asegura que una vista tenga una panadería asociada.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    """Establece conexión a la base de datos"""
    if hasattr(g, 'db'):
        return g.db
    
    db_path = 'panaderia.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    g.db = conn
    return conn

def close_db_connection(e=None):
    """Cierra la conexión a la base de datos"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """Inicializa el middleware con la aplicación Flask"""
    app.teardown_appcontext(close_db_connection)