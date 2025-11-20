# tenant_context.py - VERSIÓN CORREGIDA
"""
Manejo del contexto global del tenant integrado con sistema SaaS existente
"""

from flask import g, session
from flask_login import current_user  # ✅ CORRECCIÓN: Importar desde flask_login
import logging

logger = logging.getLogger('tenant_context')

class TenantContext:
    """Gestor centralizado del contexto multi-tenant - INTEGRADO CON SAAS EXISTENTE"""
    
    @staticmethod
    def initialize_app(app):
        """Inicializar la aplicación con soporte multi-tenant - COMPATIBLE CON TU MIDDLEWARE"""
        @app.before_request
        def set_tenant_context():
            """Establece el contexto tenant antes de cada petición - COEXISTE CON TU SAAS"""
            try:
                # Respetar tu sistema SaaS existente - trabajar en conjunto
                tenant_id = None
                
                # 1. Intentar obtener del usuario autenticado (PRIMARIO)
                if current_user and current_user.is_authenticated:
                    if hasattr(current_user, 'panaderia_id') and current_user.panaderia_id:
                        tenant_id = current_user.panaderia_id
                        logger.debug(f"✅ TenantContext: Obtenido de current_user: {tenant_id}")
                
                # 2. Si no hay usuario, intentar de session (compatibilidad con tu SaaS)
                if not tenant_id and session.get('panaderia_id'):
                    tenant_id = session.get('panaderia_id')
                    logger.debug(f"✅ TenantContext: Obtenido de session: {tenant_id}")
                
                # 3. Si no hay tenant_id, establecer como None (rutas públicas)
                g.panaderia_id = tenant_id
                g.current_tenant = f"panaderia_{tenant_id}" if tenant_id else "public"
                
                logger.debug(f"🏪 TenantContext final: {g.panaderia_id}")
                    
            except Exception as e:
                logger.error(f"❌ Error en TenantContext: {str(e)}")
                g.panaderia_id = None
                g.current_tenant = "error"
    
    @staticmethod
    def get_current_tenant_id():
        """Obtiene el tenant ID actual - COMPATIBLE CON TU SISTEMA"""
        # 1. Intentar del contexto g (nuestro sistema)
        tenant_id = getattr(g, 'panaderia_id', None)
        
        # 2. Intentar del usuario actual
        if not tenant_id and current_user and hasattr(current_user, 'panaderia_id'):
            tenant_id = current_user.panaderia_id
        
        # 3. Intentar de session (tu sistema existente)
        if not tenant_id:
            tenant_id = session.get('panaderia_id')
        
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
        if not tenant_id:
            from tenant_decorators import TenantSecurityException
            raise TenantSecurityException("Contexto tenant no disponible para la operación")
        return tenant_id
    
    @staticmethod
    def is_super_admin():
        """Verifica si el usuario actual es super administrador"""
        if current_user and hasattr(current_user, 'es_super_admin'):
            return current_user.es_super_admin
        return False
    
    @staticmethod
    def get_tenant_filter(model_class):
        """Retorna el filtro tenant para un modelo específico"""
        tenant_id = TenantContext.get_current_tenant_id()
        if hasattr(model_class, 'panaderia_id') and tenant_id:
            return model_class.panaderia_id == tenant_id
        return True  # Sin filtro si no hay tenant_id