#!/usr/bin/env python3
"""
APLICACIÓN DE DECORADORES AL MÓDULO PROVEEDORES
Corrige automáticamente las rutas de proveedores en app.py
"""

import re

def aplicar_decoradores_proveedores():
    """Aplica decoradores tenant a las rutas de proveedores en app.py"""
    
    archivo = "app.py"
    
    print("🔧 APLICANDO DECORADORES AL MÓDULO PROVEEDORES")
    print("=" * 60)
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Backup
    backup_file = archivo + '.backup_antes_decoradores_proveedores'
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(contenido)
    print(f"📁 Backup creado: {backup_file}")
    
    cambios_realizados = 0
    nuevo_contenido = contenido
    
    # Patrones para encontrar rutas de proveedores y aplicar decoradores
    patrones_rutas = [
        # Rutas principales de proveedores
        (r"(@app\.route\(['\"]/proveedores['\"]\)\s*\n)(def proveedores)", r"\1@tenant_required\n\2"),
        (r"(@app\.route\(['\"]/proveedores/crear['\"]\)\s*\n)(def crear_proveedor)", r"\1@tenant_required\n\2"),
        (r"(@app\.route\(['\"]/proveedores/editar/<int:id>['\"]\)\s*\n)(def editar_proveedor)", r"\1@tenant_required\n\2"),
        (r"(@app\.route\(['\"]/proveedores/eliminar/<int:id>['\"]\)\s*\n)(def eliminar_proveedor)", r"\1@tenant_required\n\2"),
        
        # Rutas API/JSON de proveedores
        (r"(@app\.route\(['\"]/api/proveedores['\"]\)\s*\n)(def api_proveedores)", r"\1@tenant_required\n\2"),
        (r"(@app\.route\(['\"]/api/proveedores/crear['\"]\)\s*\n)(def api_crear_proveedor)", r"\1@tenant_required\n\2"),
    ]
    
    for patron, reemplazo in patrones_rutas:
        if re.search(patron, nuevo_contenido):
            nuevo_contenido = re.sub(patron, reemplazo, nuevo_contenido)
            cambios_realizados += 1
            print(f"✅ Decorador aplicado a ruta proveedores")
    
    # Guardar cambios
    if cambios_realizados > 0:
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(nuevo_contenido)
        
        print(f"\n🎯 {cambios_realizados} decoradores aplicados a rutas de proveedores")
    else:
        print("ℹ️  No se encontraron rutas de proveedores para corregir")
    
    return cambios_realizados

def corregir_consultas_proveedores():
    """Corrige las consultas de proveedores para que usen el tenant actual"""
    
    archivo = "app.py"
    
    print("\n🔧 CORRIGIENDO CONSULTAS DE PROVEEDORES")
    print("=" * 60)
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Patrones de consultas problemáticas y sus correcciones
    correcciones = [
        # Consultas con ID fijo 1
        (r"Proveedor\.query\.filter_by\(panaderia_id=1", 
         r"Proveedor.query.filter_by(panaderia_id=current_user.panaderia_id"),
        
        # Consultas con session.get('panaderia_id', 1)
        (r"Proveedor\.query\.filter_by\(panaderia_id=session\.get\('panaderia_id', 1\)", 
         r"Proveedor.query.filter_by(panaderia_id=current_user.panaderia_id"),
        
        # Consultas sin filtro (muy peligrosas)
        (r"Proveedor\.query\.all\(\)", 
         r"Proveedor.query.filter_by(panaderia_id=current_user.panaderia_id).all()"),
        
        # Consultas con get sin filtro
        (r"Proveedor\.query\.get\(", 
         r"Proveedor.query.filter_by(panaderia_id=current_user.panaderia_id, "),
    ]
    
    cambios_realizados = 0
    nuevo_contenido = contenido
    
    for patron, reemplazo in correcciones:
        if re.search(patron, nuevo_contenido):
            nuevo_contenido = re.sub(patron, reemplazo, nuevo_contenido)
            cambios_realizados += 1
            print(f"✅ Consulta corregida: {patron}")
    
    # Guardar cambios
    if cambios_realizados > 0:
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(nuevo_contenido)
        
        print(f"\n🎯 {cambios_realizados} consultas de proveedores corregidas")
    else:
        print("ℹ️  No se encontraron consultas problemáticas de proveedores")
    
    return cambios_realizados

if __name__ == "__main__":
    print("🚀 APLICACIÓN DE SEGURIDAD TENANT A PROVEEDORES")
    print("=" * 60)
    
    # Aplicar decoradores
    decoradores = aplicar_decoradores_proveedores()
    
    # Corregir consultas
    consultas = corregir_consultas_proveedores()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL:")
    print(f"   • Decoradores aplicados: {decoradores}")
    print(f"   • Consultas corregidas: {consultas}")
    
    if decoradores > 0 or consultas > 0:
        print("🎉 ¡Módulo de proveedores asegurado para multi-tenant!")
        print("\n📋 Próximos pasos:")
        print("   1. Reiniciar la aplicación Flask")
        print("   2. Probar el aislamiento entre panaderías")
        print("   3. Verificar que cada tenant ve solo sus proveedores")
    else:
        print("ℹ️  No se realizaron cambios - El módulo puede estar ya seguro")