# tenant_decorators.py
from functools import wraps
from flask import abort, current_user, session, g
from src.infrastructure.database.db import db

def tenant_required(f):
    """Decorador principal que asegura el contexto tenant"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user or not hasattr(current_user, 'panaderia_id'):
            abort(403, "Acceso denegado - Usuario sin tenant asignado")
        
        # Establecer tenant en contexto global
        g.panaderia_id = current_user.panaderia_id
        return f(*args, **kwargs)
    return decorated_function

def with_tenant_query(model_class):
    """Decorador para consultas automáticamente filtradas"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Forzar filtrado por tenant
            tenant_id = getattr(g, 'panaderia_id', None) or getattr(current_user, 'panaderia_id', None)
            if not tenant_id:
                abort(403, "No se pudo determinar el tenant")
            
            # Modificar la función para recibir query ya filtrada
            query = model_class.query.filter_by(panaderia_id=tenant_id)
            return f(query, *args, **kwargs)
        return decorated_function
    return decorator