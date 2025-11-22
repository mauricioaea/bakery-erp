# tenant_decorators.py - VERSIÓN CORREGIDA Y ESTABLE
"""
Sistema de decoradores para seguridad multi-tenant
Garantiza el aislamiento de datos entre clientes
"""

from functools import wraps
from flask import abort, session, g, request, flash, redirect, url_for
from flask_login import current_user
import logging

# Configurar logging
logger = logging.getLogger('tenant_security')

class TenantSecurityException(Exception):
    """Excepción específica para violaciones de seguridad tenant"""
    pass

def es_super_admin():
    """Verifica si el usuario actual es super administrador - VERSIÓN SEGURA"""
    try:
        # Verificación EXTRA segura
        if not current_user or not hasattr(current_user, 'is_authenticated') or not current_user.is_authenticated:
            return False
        
        # Obtener atributos de forma segura
        user_id = getattr(current_user, 'id', None)
        username = getattr(current_user, 'username', '')
        email = getattr(current_user, 'email', '')
        
        # Verificar si es super admin por múltiples criterios
        if user_id == 1:
            return True
        
        if username and username == 'dev_master':
            return True
        
        if email and hasattr(email, 'endswith') and email.endswith('dev_master'):
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"❌ Error en es_super_admin: {str(e)}")
        return False

def tenant_required(f):
    """
    Decorador principal que asegura el contexto tenant en todas las rutas
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 1. Verificar autenticación básica
            if not current_user or not current_user.is_authenticated:
                logger.warning("Intento de acceso sin autenticación")
                return redirect(url_for('login'))
            
            # 2. ✅ VERIFICACIÓN SEGURA PARA SUPER ADMIN
            if es_super_admin():
                # Super admin puede acceder sin restricciones de tenant
                g.panaderia_id = None
                g.current_tenant = "super_admin"
                g.es_super_admin = True
                logger.debug(f"✅ Super admin accediendo: {current_user.id}")
                return f(*args, **kwargs)
            
            # 3. ✅ VERIFICACIÓN PARA USUARIOS NORMALES
            if not hasattr(current_user, 'panaderia_id'):
                logger.error(f"❌ Usuario {current_user.id} no tiene atributo panaderia_id")
                flash('Error de configuración: Usuario no tiene tenant asignado', 'error')
                return redirect(url_for('dashboard'))  # ✅ CAMBIADO A 'dashboard'
            
            if not current_user.panaderia_id:
                logger.warning(f"⚠️ Usuario {current_user.id} tiene panaderia_id vacío")
                flash('Configuración incompleta: Contacte al administrador', 'warning')
                return redirect(url_for('dashboard'))  # ✅ CAMBIADO A 'dashboard'
            
            # 4. ✅ ESTABLECER CONTEXTO TENANT PARA USUARIOS NORMALES
            g.panaderia_id = current_user.panaderia_id
            g.current_tenant = f"panaderia_{current_user.panaderia_id}"
            g.es_super_admin = False
            
            logger.debug(f"✅ Tenant establecido: {g.panaderia_id} para usuario {current_user.id}")
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"❌ Error crítico en decorador tenant_required: {str(e)}", exc_info=True)
            flash('Error interno del sistema. Contacte al administrador.', 'error')
            return redirect(url_for('dashboard'))  # ✅ CAMBIADO A 'dashboard'
    
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
                
                # ✅ SI ES SUPER ADMIN, NO FILTRAR
                if getattr(g, 'es_super_admin', False):
                    query = model_class.query
                    logger.debug(f"✅ Super admin - consulta sin filtro para {model_class.__name__}")
                else:
                    if not tenant_id:
                        # Intentar obtener del usuario actual
                        if current_user and hasattr(current_user, 'panaderia_id'):
                            tenant_id = current_user.panaderia_id
                        else:
                            raise TenantSecurityException("No se pudo determinar el tenant")
                    
                    # Crear query filtrada automáticamente
                    query = model_class.query.filter_by(panaderia_id=tenant_id)
                    logger.debug(f"✅ Consulta filtrada por tenant: {tenant_id}")
                
                # Llamar a la función original con la query
                return f(query, *args, **kwargs)
                
            except TenantSecurityException as e:
                logger.error(f"Error de seguridad tenant: {str(e)}")
                flash(str(e), 'error')
                return redirect(url_for('dashboard'))
            except Exception as e:
                logger.error(f"Error en with_tenant_context: {str(e)}")
                flash('Error interno en consulta tenant', 'error')
                return redirect(url_for('dashboard'))
        
        return decorated_function
    return decorator

def tenant_query(model_class):
    """
    Decorador alternativo más simple - solo para consultas de lectura
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # ✅ SI ES SUPER ADMIN, NO FILTRAR
            if getattr(g, 'es_super_admin', False):
                return f(model_class.query, *args, **kwargs)
            
            tenant_id = getattr(g, 'panaderia_id', getattr(current_user, 'panaderia_id', None))
            if not tenant_id:
                flash('No se pudo determinar el tenant para la consulta', 'error')
                return redirect(url_for('dashboard'))
            
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
    if not tenant_id and not getattr(g, 'es_super_admin', False):
        raise TenantSecurityException("Contexto tenant no disponible")
    return tenant_id