# consultas_filtradas.py
import sys
import os
import logging

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import session
from models import Producto, ProductoExterno

logger = logging.getLogger('panaderia')

def productos_activos_con_stock():
    """
    Retorna query de productos de panadería activos con stock > 0
    Filtrados por la panadería del usuario actual
    """
    try:
        panaderia_id = obtener_panaderia_actual()
        logger.debug(f"🔍 consultas_filtradas - Panadería actual: {panaderia_id}")
        
        query = Producto.query.filter_by(
            activo=True,
            panaderia_id=panaderia_id
        ).filter(Producto.stock_actual > 0)
        
        # Debug: contar resultados
        count = query.count()
        logger.debug(f"🔍 consultas_filtradas - Productos panadería encontrados: {count}")
        
        return query
    except Exception as e:
        logger.error(f"❌ Error en productos_activos_con_stock: {e}")
        # Fallback seguro
        return Producto.query.filter_by(activo=True).filter(Producto.stock_actual > 0)

def productos_externos_activos_con_stock():
    """
    Retorna query de productos externos activos con stock > 0  
    Filtrados por la panadería del usuario actual
    """
    try:
        panaderia_id = obtener_panaderia_actual()
        logger.debug(f"🔍 consultas_filtradas - Panadería externos: {panaderia_id}")
        
        query = ProductoExterno.query.filter_by(
            activo=True,
            panaderia_id=panaderia_id
        ).filter(ProductoExterno.stock_actual > 0)
        
        # Debug: contar resultados
        count = query.count()
        logger.debug(f"🔍 consultas_filtradas - Productos externos encontrados: {count}")
        
        return query
    except Exception as e:
        logger.error(f"❌ Error en productos_externos_activos_con_stock: {e}")
        # Fallback seguro
        return ProductoExterno.query.filter_by(activo=True).filter(ProductoExterno.stock_actual > 0)

def obtener_panaderia_actual():
    """
    Obtiene la panadería actual del usuario
    """
    try:
        # 1. Primero de la sesión directa
        if 'panaderia_id' in session:
            panaderia_id = session['panaderia_id']
            logger.debug(f"🔍 obtener_panaderia_actual - Desde sesión: {panaderia_id}")
            return panaderia_id
        
        # 2. Del usuario en base de datos
        from models import Usuario
        user_id = session.get('user_id')
        if user_id:
            usuario = Usuario.query.get(user_id)
            if usuario and usuario.panaderia_id:
                logger.debug(f"🔍 obtener_panaderia_actual - Desde usuario: {usuario.panaderia_id}")
                return usuario.panaderia_id
        
        # 3. Fallback por defecto
        logger.debug("🔍 obtener_panaderia_actual - Usando fallback: 1")
        return 1
        
    except Exception as e:
        logger.error(f"❌ Error en obtener_panaderia_actual: {e}")
        return 1