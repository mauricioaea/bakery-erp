# tenant_context.py
from flask import g, current_user

class TenantContext:
    """Maneja el contexto del tenant globalmente"""
    
    @staticmethod
    def get_current_tenant_id():
        """Obtiene el ID del tenant actual desde cualquier lugar"""
        return getattr(g, 'panaderia_id', None) or getattr(current_user, 'panaderia_id', None)
    
    @staticmethod
    def set_current_tenant(tenant_id):
        """Establece el tenant actual en contexto global"""
        g.panaderia_id = tenant_id
    
    @staticmethod
    def ensure_tenant_context():
        """Garantiza que hay un contexto tenant válido"""
        tenant_id = TenantContext.get_current_tenant_id()
        if not tenant_id:
            raise SecurityException("Contexto tenant no disponible")
        return tenant_id