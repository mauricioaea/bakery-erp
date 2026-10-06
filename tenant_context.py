# tenant_context.py - VERSIÓN CORREGIDA Y ESTABLE
"""
Manejo del contexto global del tenant integrado con sistema SaaS existente
"""

from flask import g, session
from flask_login import current_user
import logging

# ✅ DT-43: es_super_admin() se importa de tenant_decorators (definición canónica).
# Se eliminó la definición local duplicada para evitar inconsistencias futuras.
from tenant_decorators import es_super_admin

logger = logging.getLogger('tenant_context')

class TenantContext:
    """Gestor centralizado del contexto multi-tenant - COMPATIBLE CON SUPER ADMIN"""
    
    @staticmethod
    def initialize_app(app):
        """Inicializar la aplicación con soporte multi-tenant"""
        @app.before_request
        def set_tenant_context():
            """Establece el contexto tenant antes de cada petición"""
            try:
                # Respetar el contexto ya establecido por el decorador
                if hasattr(g, 'panaderia_id'):
                    # El decorador ya estableció el contexto
                    logger.debug(f"✅ TenantContext: Usando contexto existente: {g.panaderia_id}")
                    return
                
                # Si no hay contexto, establecer uno por defecto
                tenant_id = None
                
                # 1. Intentar obtener del usuario autenticado
                if current_user and current_user.is_authenticated:
                    # ✅ VERIFICACIÓN SUPER ADMIN SEGURA
                    if es_super_admin():
                        tenant_id = None  # Super admin no tiene tenant específico
                        logger.debug(f"✅ TenantContext: Super admin detectado")
                    elif hasattr(current_user, 'panaderia_id') and current_user.panaderia_id:
                        tenant_id = current_user.panaderia_id
                        logger.debug(f"✅ TenantContext: Obtenido de current_user: {tenant_id}")
                
                # 2. Si no hay usuario, intentar de session
                if not tenant_id and session.get('panaderia_id'):
                    tenant_id = session.get('panaderia_id')
                    logger.debug(f"✅ TenantContext: Obtenido de session: {tenant_id}")
                
                # Establecer contexto
                g.panaderia_id = tenant_id
                g.current_tenant = f"panaderia_{tenant_id}" if tenant_id else "public"
                
                # ✅ Marcar si es super admin
                if current_user and current_user.is_authenticated and es_super_admin():
                    g.es_super_admin = True
                else:
                    g.es_super_admin = False
                
                logger.debug(f"🏪 TenantContext establecido: {g.panaderia_id}, es_super_admin: {g.es_super_admin}")
                    
            except Exception as e:
                logger.error(f"❌ Error en TenantContext: {str(e)}")
                g.panaderia_id = None
                g.current_tenant = "error"
                g.es_super_admin = False
    
    @staticmethod
    def get_current_tenant_id():
        """Obtiene el tenant ID actual - COMPATIBLE CON SUPER ADMIN"""
        # 1. Intentar del contexto g (establecido por decorador)
        tenant_id = getattr(g, 'panaderia_id', None)
        
        # 2. Si es super admin, retornar None
        if getattr(g, 'es_super_admin', False):
            return None
        
        # 3. Para usuarios normales, verificar consistencia
        if tenant_id and current_user and hasattr(current_user, 'panaderia_id'):
            if tenant_id != current_user.panaderia_id:
                logger.warning(f"⚠️ Discrepancia en tenant: contexto={tenant_id}, usuario={current_user.panaderia_id}")
        
        logger.debug(f"🔍 TenantContext.get_current_tenant_id() = {tenant_id}")
        return tenant_id
    
    @staticmethod
    def set_current_tenant(tenant_id):
        """Establece el tenant actual en todos los sistemas"""
        g.panaderia_id = tenant_id
        g.current_tenant = f"panaderia_{tenant_id}"
        
        # También actualizar session para compatibilidad con tu sistema existente
        session['panaderia_id'] = tenant_id
        
        logger.debug(f"✅ TenantContext establecido en todos los sistemas: {tenant_id}")
    
    @staticmethod
    def ensure_tenant_context():
        """Garantiza que hay un contexto tenant válido"""
        tenant_id = TenantContext.get_current_tenant_id()
        if not tenant_id and not getattr(g, 'es_super_admin', False):
            from tenant_decorators import TenantSecurityException
            raise TenantSecurityException("Contexto tenant no disponible para la operación")
        return tenant_id
    
    @staticmethod
    def is_super_admin():
        """Verifica si el usuario actual es super administrador"""
        # Usar la función auxiliar que ya tenemos
        return es_super_admin()
    
    @staticmethod
    def get_tenant_filter(model_class):
        """Retorna el filtro tenant para un modelo específico"""
        tenant_id = TenantContext.get_current_tenant_id()
        if hasattr(model_class, 'panaderia_id') and tenant_id:
            return model_class.panaderia_id == tenant_id
        return True  # Sin filtro si no hay tenant_id o es super admin
    
    @staticmethod
    def get_super_admin_behavior():
        """Define el comportamiento para super administrador"""
        if TenantContext.is_super_admin():
            return "super_admin"
        return "normal"