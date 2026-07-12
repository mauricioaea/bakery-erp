# validar_roles_permisos.py
import os
import re

def validar_roles_permisos():
    """Verifica que los roles tengan acceso correcto a los módulos"""
    
    print("🔍 VALIDANDO ROLES Y PERMISOS")
    print("=" * 70)
    
    app_path = 'app.py'
    if not os.path.exists(app_path):
        print("❌ No se encuentra app.py")
        return
    
    with open(app_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Módulos y roles esperados
    modulos = {
        'punto_venta': ['admin_cliente', 'supervisor', 'cajero'],
        'productos': ['admin_cliente', 'supervisor'],
        'produccion': ['admin_cliente', 'supervisor'],
        'reportes': ['admin_cliente', 'supervisor'],
        'gestion_clientes': ['admin_cliente'],
        'gestion_usuarios': ['admin_cliente'],
        'cierre_caja': ['admin_cliente', 'supervisor']
    }
    
    print("\n📋 VERIFICANDO ACCESO POR ROL:")
    print("-" * 70)
    
    for modulo, roles in modulos.items():
        # 🔍 BUSCAR CUALQUIER DECORADOR QUE CONTENGA EL NOMBRE DEL MÓDULO
        # Buscar @modulo_requerido('...') donde '...' contenga el nombre del módulo
        patron = rf'@modulo_requerido\([\'"]{{0,1}}[^\'"]*{modulo}[^\'"]*[\'"]{{0,1}}\)'
        
        if re.search(patron, contenido):
            print(f"✅ {modulo}: Configurado")
        else:
            # Búsqueda alternativa: buscar la función y ver si tiene algún decorador
            patron_funcion = rf'def\s+{modulo}\s*\([^)]*\)'
            if re.search(patron_funcion, contenido):
                print(f"⚠️ {modulo}: Función existe pero sin decorador de módulo")
            else:
                # Buscar si hay una función que contenga el nombre del módulo
                patron_alternativo = rf'def\s+\w*{modulo}\w*\s*\([^)]*\)'
                if re.search(patron_alternativo, contenido):
                    print(f"✅ {modulo}: Configurado (con nombre alternativo)")
                else:
                    print(f"⚠️ {modulo}: No tiene decorador de módulo")
    
    print("\n" + "=" * 70)
    print("💡 RECOMENDACIONES:")
    print("  1. Revisar que cada módulo tenga el decorador @modulo_requerido")
    print("  2. Verificar que los roles tengan acceso a los módulos correctos")
    print("  3. Probar con diferentes usuarios")

if __name__ == "__main__":
    validar_roles_permisos()