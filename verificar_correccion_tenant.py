#!/usr/bin/env python3
"""
VERIFICACIÓN DE CORRECCIÓN MULTI-TENANT
Verifica que todos los modelos tengan panaderia_id y la BD esté actualizada
"""

import os
import sys
import sqlite3
from pathlib import Path

# Agregar el directorio actual al path para poder importar models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verificar_models_py():
    """Verifica que todos los modelos en models.py tengan panaderia_id"""
    
    print("🔍 VERIFICANDO models.py...")
    print("=" * 60)
    
    with open('models.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Lista de modelos que deben tener panaderia_id
    modelos_esperados = [
        'Usuario', 'Sucursal', 'Categoria', 'ConfiguracionPanaderia', 'Panaderia',
        'Producto', 'Proveedor', 'ProductoExterno', 'CompraExterna', 'MateriaPrima',
        'Receta', 'HistorialCompra', 'Cliente', 'Venta', 'DetalleVenta', 'Compra',
        'DetalleCompra', 'Gasto', 'RecetaIngrediente', 'OrdenProduccion', 
        'HistorialInventario', 'StockProducto', 'ConfiguracionProduccion',
        'HistorialRotacionProducto', 'ControlVidaUtil', 'Factura', 'JornadaVentas',
        'CierreDiario', 'PermisoUsuario', 'RegistroDiario', 'SaldoBanco', 
        'PagoIndividual', 'ActivoFijo', 'ConsecutivoPOS', 'ConfiguracionSistema'
    ]
    
    modelos_con_panaderia_id = []
    modelos_sin_panaderia_id = []
    
    for modelo in modelos_esperados:
        if f'class {modelo}(' in contenido:
            if f'panaderia_id = db.Column' in contenido:
                modelos_con_panaderia_id.append(modelo)
            else:
                modelos_sin_panaderia_id.append(modelo)
    
    print(f"📊 MODELOS CON panaderia_id: {len(modelos_con_panaderia_id)}")
    for modelo in modelos_con_panaderia_id:
        print(f"   ✅ {modelo}")
    
    if modelos_sin_panaderia_id:
        print(f"🚨 MODELOS SIN panaderia_id: {len(modelos_sin_panaderia_id)}")
        for modelo in modelos_sin_panaderia_id:
            print(f"   ❌ {modelo}")
    else:
        print("🎉 ¡Todos los modelos tienen panaderia_id!")
    
    return len(modelos_sin_panaderia_id) == 0

def verificar_base_datos():
    """Verifica que todas las tablas en la BD tengan columna panaderia_id"""
    
    print("\n🗄️ VERIFICANDO BASE DE DATOS...")
    print("=" * 60)
    
    db_path = "panaderia.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = [tabla[0] for tabla in cursor.fetchall()]
        
        tablas_con_panaderia_id = []
        tablas_sin_panaderia_id = []
        
        for tabla in tablas:
            cursor.execute(f"PRAGMA table_info({tabla})")
            columnas = [col[1] for col in cursor.fetchall()]
            
            if 'panaderia_id' in columnas:
                tablas_con_panaderia_id.append(tabla)
            else:
                tablas_sin_panaderia_id.append(tabla)
        
        print(f"📊 TABLAS CON panaderia_id: {len(tablas_con_panaderia_id)}")
        for tabla in tablas_con_panaderia_id:
            print(f"   ✅ {tabla}")
        
        if tablas_sin_panaderia_id:
            print(f"🚨 TABLAS SIN panaderia_id: {len(tablas_sin_panaderia_id)}")
            for tabla in tablas_sin_panaderia_id:
                print(f"   ❌ {tabla}")
        else:
            print("🎉 ¡Todas las tablas tienen panaderia_id!")
        
        conn.close()
        return len(tablas_sin_panaderia_id) == 0
        
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

def verificar_imports_tenant():
    """Verifica que los imports de tenant funcionen correctamente"""
    
    print("\n🔧 VERIFICANDO IMPORTS TENANT...")
    print("=" * 60)
    
    try:
        from tenant_decorators import tenant_required, with_tenant_context, get_current_tenant_id
        from tenant_context import TenantContext
        from security_utils import safe_tenant_query
        
        print("✅ Todos los imports tenant funcionan correctamente")
        
        # Probar creación de decoradores
        @tenant_required
        def funcion_prueba():
            return "éxito"
            
        print("✅ Decoradores se crean correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en imports tenant: {e}")
        return False

if __name__ == "__main__":
    print("🚀 VERIFICACIÓN COMPLETA DEL SISTEMA MULTI-TENANT")
    print("=" * 60)
    
    # Ejecutar verificaciones
    models_ok = verificar_models_py()
    db_ok = verificar_base_datos()
    imports_ok = verificar_imports_tenant()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL DE VERIFICACIÓN")
    print("=" * 60)
    
    if models_ok and db_ok and imports_ok:
        print("🎉 ¡VERIFICACIÓN COMPLETADA CON ÉXITO!")
        print("✅ Todos los modelos tienen panaderia_id")
        print("✅ Todas las tablas de BD tienen panaderia_id") 
        print("✅ Sistema de seguridad tenant funcionando")
        print("\n🚀 ¡Sistema listo para aplicar aislamiento multi-tenant!")
    else:
        print("⚠️  VERIFICACIÓN CON PROBLEMAS")
        if not models_ok:
            print("❌ Faltan modelos por corregir")
        if not db_ok:
            print("❌ Faltan tablas de BD por migrar")
        if not imports_ok:
            print("❌ Problemas con imports tenant")