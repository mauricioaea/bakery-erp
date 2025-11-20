# tenant_decorators.py - VERSIÓN CORREGIDA
"""
Sistema de decoradores para seguridad multi-tenant
Garantiza el aislamiento de datos entre clientes
"""

from functools import wraps
from flask import abort, session, g, request
from flask_login import current_user  # ✅ CORRECCIÓN: Importar desde flask_login
import logging

# Configurar logging
logger = logging.getLogger('tenant_security')

class TenantSecurityException(Exception):
    """Excepción específica para violaciones de seguridad tenant"""
    pass

def tenant_required(f):
    """
    Decorador principal que asegura el contexto tenant en todas las rutas
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Verificar que el usuario está autenticado
            if not current_user or not current_user.is_authenticated:
                logger.warning("Intento de acceso sin autenticación")
                abort(403, "Acceso denegado - Autenticación requerida")
            
            # Verificar que tiene panaderia_id
            if not hasattr(current_user, 'panaderia_id') or not current_user.panaderia_id:
                logger.error(f"Usuario {current_user.id} sin panaderia_id asignado")
                abort(403, "Acceso denegado - Tenant no configurado")
            
            # Establecer tenant en contexto global de Flask
            g.panaderia_id = current_user.panaderia_id
            g.current_tenant = f"panaderia_{current_user.panaderia_id}"
            
            logger.debug(f"Tenant establecido: {g.panaderia_id} para usuario {current_user.id}")
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error en decorador tenant_required: {str(e)}")
            abort(500, "Error interno de seguridad tenant")
    
    return decorated_function

def with_tenant_context(model_class):
    """
    Decorador para funciones que realizan consultas a modelos específicos
    Automáticamente filtra por tenant_id
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Obtener tenant del contexto global
                tenant_id = getattr(g, 'panaderia_id', None)
                if not tenant_id:
                    # Intentar obtener del usuario actual
                    if current_user and hasattr(current_user, 'panaderia_id'):
                        tenant_id = current_user.panaderia_id
                    else:
                        raise TenantSecurityException("No se pudo determinar el tenant")
                
                # Crear query filtrada automáticamente
                query = model_class.query.filter_by(panaderia_id=tenant_id)
                
                # Llamar a la función original con la query filtrada
                return f(query, *args, **kwargs)
                
            except TenantSecurityException as e:
                logger.error(f"Error de seguridad tenant: {str(e)}")
                abort(403, str(e))
            except Exception as e:
                logger.error(f"Error en with_tenant_context: {str(e)}")
                abort(500, "Error interno en consulta tenant")
        
        return decorated_function
    return decorator

def tenant_query(model_class):
    """
    Decorador alternativo más simple - solo para consultas de lectura
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            tenant_id = getattr(g, 'panaderia_id', getattr(current_user, 'panaderia_id', None))
            if not tenant_id:
                abort(403, "No se pudo determinar el tenant para la consulta")
            
            # Forzar filtrado por tenant
            if hasattr(model_class, 'panaderia_id'):
                query = model_class.query.filter_by(panaderia_id=tenant_id)
                return f(query, *args, **kwargs)
            else:
                # Si el modelo no tiene panaderia_id, usar query normal (con advertencia)
                logger.warning(f"Modelo {model_class.__name__} no tiene panaderia_id")
                return f(model_class.query, *args, **kwargs)
        
        return decorated_function
    return decorator

# Función de utilidad para obtener el tenant actual
def get_current_tenant_id():
    """Obtiene el ID del tenant actual desde cualquier parte del código"""
    return getattr(g, 'panaderia_id', 
                  getattr(current_user, 'panaderia_id', None) if current_user and hasattr(current_user, 'panaderia_id') else None)

def ensure_tenant_context():
    """Garantiza que existe un contexto tenant válido"""
    tenant_id = get_current_tenant_id()
    if not tenant_id:
        raise TenantSecurityException("Contexto tenant no disponible")
    return tenant_id