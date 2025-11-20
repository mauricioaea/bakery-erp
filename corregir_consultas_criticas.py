# corregir_consultas_criticas.py
"""
Corrige las consultas más problemáticas identificadas
"""

consultas_criticas = [
    # Línea 1675: Proveedor.query.filter_by(panaderia_id=1, activo=True)
    # ❌ PROBLEMA: Usa ID fijo 1 en lugar del tenant actual
    # ✅ SOLUCIÓN: Proveedor.query.filter_by(panaderia_id=current_user.panaderia_id, activo=True)
    
    # Línea 1874: Mismo problema
    # Línea 1894: Mismo problema  
    # Línea 1990: Mismo problema
]