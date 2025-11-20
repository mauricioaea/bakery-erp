#!/usr/bin/env python3
"""
DIAGNÓSTICO DE MODELOS Y RELACIONES - ACTUALIZADO
Verifica que todos los modelos tengan panaderia_id después de las correcciones
"""

import re
import os

def analizar_modelos(archivo_models):
    """Analiza models.py para verificar estructura multi-tenant"""
    
    print("🔍 ANALIZANDO ESTRUCTURA DE MODELOS - POST CORRECCIÓN")
    print("=" * 60)
    
    with open(archivo_models, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar todos los modelos (clases que heredan de db.Model)
    patron_modelos = r'class\s+(\w+)\(.*db\.Model.*\):'
    modelos = re.findall(patron_modelos, contenido)
    
    print(f"📋 MODELOS ENCONTRADOS: {len(modelos)}")
    
    resultados_modelos = {}
    modelos_con_tenant = []
    modelos_sin_tenant = []
    
    for modelo in modelos:
        # Buscar la definición de cada modelo
        patron_definicion = rf'class {modelo}\(.*?db\.Model.*?\):(.*?)(?=class\s+\w+|$)'
        match = re.search(patron_definicion, contenido, re.DOTALL)
        
        if match:
            definicion = match.group(1)
            tiene_panaderia_id = 'panaderia_id = db.Column' in definicion
            
            if tiene_panaderia_id:
                modelos_con_tenant.append(modelo)
                print(f"  ✅ {modelo}: TIENE panaderia_id")
            else:
                modelos_sin_tenant.append(modelo)
                print(f"  ❌ {modelo}: NO TIENE panaderia_id")
    
    return modelos, modelos_con_tenant, modelos_sin_tenant

def verificar_base_datos():
    """Verifica que la base de datos tenga las columnas panaderia_id"""
    
    print("\n🗄️ VERIFICANDO BASE DE DATOS...")
    print("=" * 60)
    
    import sqlite3
    
    db_path = "panaderia.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        return [], []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = [tabla[0] for tabla in cursor.fetchall()]
        
        tablas_con_tenant = []
        tablas_sin_tenant = []
        
        for tabla in tablas:
            # Verificar si la tabla tiene columna panaderia_id
            cursor.execute(f"PRAGMA table_info({tabla})")
            columnas = [col[1] for col in cursor.fetchall()]
            
            if 'panaderia_id' in columnas:
                tablas_con_tenant.append(tabla)
                print(f"  ✅ {tabla}: TIENE panaderia_id")
            else:
                tablas_sin_tenant.append(tabla)
                print(f"  ❌ {tabla}: NO TIENE panaderia_id")
        
        conn.close()
        return tablas_con_tenant, tablas_sin_tenant
        
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return [], []

def generar_reporte_final(modelos, modelos_con_tenant, modelos_sin_tenant, tablas_con_tenant, tablas_sin_tenant):
    """Genera reporte final del diagnóstico"""
    
    print("\n📊 REPORTE FINAL - POST CORRECCIÓN")
    print("=" * 60)
    
    print(f"🎯 MODELOS ENCONTRADOS: {len(modelos)}")
    print(f"✅ Modelos CON panaderia_id: {len(modelos_con_tenant)}")
    print(f"❌ Modelos SIN panaderia_id: {len(modelos_sin_tenant)}")
    
    print(f"\n🗄️ TABLAS EN BD: {len(tablas_con_tenant) + len(tablas_sin_tenant)}")
    print(f"✅ Tablas CON panaderia_id: {len(tablas_con_tenant)}")
    print(f"❌ Tablas SIN panaderia_id: {len(tablas_sin_tenant)}")
    
    # Verificar si estamos 100% completos
    modelos_completos = len(modelos_sin_tenant) == 0
    bd_completa = len(tablas_sin_tenant) == 0
    
    if modelos_completos and bd_completa:
        print("\n🎉 ¡SISTEMA 100% PREPARADO PARA MULTI-TENANT!")
        print("✅ Todos los modelos tienen panaderia_id")
        print("✅ Todas las tablas de BD tienen panaderia_id")
        print("🚀 ¡Listo para aplicar decoradores de seguridad!")
    else:
        print("\n⚠️  SISTEMA PARCIALMENTE PREPARADO")
        if not modelos_completos:
            print(f"❌ Faltan {len(modelos_sin_tenant)} modelos por corregir:")
            for modelo in modelos_sin_tenant:
                print(f"   • {modelo}")
        if not bd_completa:
            print(f"❌ Faltan {len(tablas_sin_tenant)} tablas por migrar:")
            for tabla in tablas_sin_tenant:
                print(f"   • {tabla}")

if __name__ == "__main__":
    archivo_models = "models.py"
    
    if not os.path.exists(archivo_models):
        print("❌ Error: models.py no encontrado")
        exit(1)
    
    print("🚀 DIAGNÓSTICO POST-CORRECCIÓN MULTI-TENANT")
    print("=" * 60)
    
    # Analizar modelos
    modelos, modelos_con_tenant, modelos_sin_tenant = analizar_modelos(archivo_models)
    
    # Verificar base de datos
    tablas_con_tenant, tablas_sin_tenant = verificar_base_datos()
    
    # Generar reporte final
    generar_reporte_final(modelos, modelos_con_tenant, modelos_sin_tenant, tablas_con_tenant, tablas_sin_tenant)
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNÓSTICO COMPLETADO")
    print("=" * 60)