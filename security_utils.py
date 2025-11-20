# security_utils.py - VERSIÓN CORREGIDA
"""
Utilidades de seguridad y validación para multi-tenant
"""

from flask import current_app
from flask_login import current_user  # ✅ CORRECCIÓN: Importar desde flask_login
from tenant_decorators import TenantSecurityException
import logging

logger = logging.getLogger('security_utils')

def validate_tenant_access(panaderia_id):
    """
    Valida que el usuario tenga acceso al tenant especificado
    """
    from tenant_context import TenantContext
    
    current_tenant = TenantContext.get_current_tenant_id()
    
    # Super admin puede acceder a cualquier tenant
    if TenantContext.is_super_admin():
        return True
    
    # Usuario normal solo puede acceder a su tenant
    if current_tenant != panaderia_id:
        logger.warning(f"Intento de acceso cross-tenant: usuario {current_tenant} intentó acceder a {panaderia_id}")
        raise TenantSecurityException("Acceso denegado - Violación de aislamiento tenant")
    
    return True

def safe_tenant_query(model_class, **filters):
    """
    Realiza una consulta segura filtrada automáticamente por tenant
    """
    from tenant_context import TenantContext
    
    tenant_id = TenantContext.ensure_tenant_context()
    
    # Asegurar que el modelo tiene panaderia_id
    if not hasattr(model_class, 'panaderia_id'):
        logger.warning(f"Modelo {model_class.__name__} no tiene panaderia_id")
        # Permitir consulta pero registrar advertencia
        return model_class.query.filter_by(**filters)
    
    # Consulta filtrada por tenant
    filters['panaderia_id'] = tenant_id
    return model_class.query.filter_by(**filters)

def check_tenant_ownership(instance):
    """
    Verifica que una instancia pertenezca al tenant actual
    """
    from tenant_context import TenantContext
    
    if not instance:
        return True  # Instancia nula, no hay problema
    
    if not hasattr(instance, 'panaderia_id'):
        logger.warning(f"Instancia de {type(instance).__name__} no tiene panaderia_id")
        return True
    
    current_tenant = TenantContext.get_current_tenant_id()
    
    # Super admin puede acceder a cualquier instancia
    if TenantContext.is_super_admin():
        return True
    
    # Verificar que la instancia pertenece al tenant actual
    if instance.panaderia_id != current_tenant:
        logger.error(f"Violación de seguridad: usuario tenant {current_tenant} intentó acceder a instancia de tenant {instance.panaderia_id}")
        raise TenantSecurityException("Acceso denegado - La instancia no pertenece a su tenant")
    
    return True