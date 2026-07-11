# validar_modulos_detallado.py
import os
import re
import sqlite3

def validar_modulos_detallado():
    """Valida cada módulo individualmente para asegurar aislamiento multi-tenant"""
    
    print("🔍 VALIDANDO MÓDULOS DETALLADAMENTE")
    print("=" * 70)
    
    app_path = 'app.py'
    if not os.path.exists(app_path):
        print("❌ No se encuentra app.py")
        return
    
    with open(app_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Lista de módulos a validar (prioritarios)
    modulos_prioritarios = [
        ('Reportes', '/reportes'),
        ('Ventas', '/ventas'),
        ('Clientes', '/clientes'),
        ('Productos', '/productos'),
        ('Produccion', '/produccion'),
        ('Gestion Clientes', '/gestion_clientes'),
        ('Punto Venta', '/punto_venta'),
        ('Inventario', '/inventario'),
        ('Cierre Caja', '/cierre_caja'),
        ('Analisis Predictivo', '/analisis_predictivo')
    ]
    
    print("\n📋 VALIDANDO MÓDULOS PRIORITARIOS:")
    print("-" * 70)
    
    for nombre, ruta in modulos_prioritarios:
        print(f"\n🔍 {nombre} ({ruta}):")
        
        # Buscar la ruta en app.py
        if ruta in contenido:
            print(f"  ✅ Ruta encontrada")
            
            # Buscar si tiene filtro panaderia_id
            # Buscar en el contexto de la ruta
            patron_contexto = rf'{re.escape(ruta)}.*?panaderia_id'
            if re.search(patron_contexto, contenido, re.DOTALL):
                print(f"  ✅ Tiene filtro panaderia_id")
            else:
                print(f"  ⚠️ Puede no tener filtro panaderia_id (revisar manualmente)")
            
            # Buscar si tiene @login_required
            patron_login = rf'@login_required.*?{re.escape(ruta)}'
            if re.search(patron_login, contenido, re.DOTALL):
                print(f"  ✅ Tiene @login_required")
            else:
                print(f"  ⚠️ Puede no tener @login_required (revisar manualmente)")
        else:
            print(f"  ❌ Ruta no encontrada")
    
    # Verificar módulos con IA
    print("\n\n🤖 VERIFICANDO MÓDULOS CON IA:")
    print("-" * 70)
    
    modulos_ia = [
        ('analisis_predictivo', 'Análisis Predictivo'),
        ('productos_populares', 'Productos Populares'),
        ('ventas_periodo', 'Ventas por Período')
    ]
    
    for ruta, nombre in modulos_ia:
        if ruta in contenido:
            print(f"  ✅ {nombre}: Implementado")
        else:
            print(f"  ⚠️ {nombre}: No encontrado")
    
    print("\n" + "=" * 70)
    print("✅ VALIDACIÓN COMPLETADA")
    print("\n💡 RECOMENDACIONES:")
    print("  1. Revisar manualmente los módulos marcados con ⚠️")
    print("  2. Verificar que todas las consultas tengan filtro panaderia_id")
    print("  3. Probar cada módulo con diferentes roles de usuario")

if __name__ == "__main__":
    validar_modulos_detallado()