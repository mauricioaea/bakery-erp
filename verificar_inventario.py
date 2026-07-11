# verificar_inventario.py
import os
import re
import sqlite3

def verificar_inventario():
    """Verifica el aislamiento multi-tenant de los módulos de inventario"""
    
    print("🔍 VERIFICANDO AISLAMIENTO DE INVENTARIO")
    print("=" * 70)
    
    app_path = 'app.py'
    if not os.path.exists(app_path):
        print("❌ No se encuentra app.py")
        return
    
    with open(app_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Módulos de inventario a verificar
    modulos_inventario = [
        ('Materias Primas', '/materias_primas'),
        ('Productos Externos', '/productos_externos'),
        ('Stock Vitrina', '/stock_vitrina'),
        ('Configurar Stock', '/configurar_stock'),
        ('Configurar Stock Producto', '/configurar_stock_producto'),
        ('Reporte Inventario Externo', '/reporte_inventario_externo')
    ]
    
    print("\n📋 VERIFICANDO MÓDULOS DE INVENTARIO:")
    print("-" * 70)
    
    for nombre, ruta in modulos_inventario:
        print(f"\n🔍 {nombre} ({ruta}):")
        
        if ruta in contenido:
            print(f"  ✅ Ruta encontrada")
            
            # Buscar si tiene filtro panaderia_id
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
    
    # Verificar templates de inventario
    print("\n\n📂 TEMPLATES DE INVENTARIO:")
    print("-" * 70)
    
    templates_dir = 'templates'
    if os.path.exists(templates_dir):
        templates_inventario = [
            'configurar_stock.html',
            'configurar_stock_producto.html',
            'productos_externos.html',
            'productos_populares.html',
            'reporte_inventario_externo.html',
            'stock_vitrina.html'
        ]
        
        for template in templates_inventario:
            ruta_template = os.path.join(templates_dir, template)
            if os.path.exists(ruta_template):
                print(f"  ✅ {template} existe")
            else:
                print(f"  ❌ {template} no existe")
    
    print("\n" + "=" * 70)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("\n💡 RECOMENDACIONES:")
    print("  1. Verificar que todos los módulos tengan filtro panaderia_id")
    print("  2. Verificar que todos tengan @login_required")
    print("  3. Probar con diferentes tenants para asegurar aislamiento")

if __name__ == "__main__":
    verificar_inventario()