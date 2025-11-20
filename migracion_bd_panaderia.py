#!/usr/bin/env python3
"""
MIGRACIÓN ESPECÍFICA PARA TU BASE DE DATOS - AGREGAR panaderia_id
"""

import sqlite3
import os
from datetime import datetime

def generar_migracion_sqlite():
    """Genera migración específica para SQLite"""
    
    print("🗄️ GENERANDO MIGRACIÓN SQLite PARA panaderia_id")
    print("=" * 60)
    
    # Sentencias SQL específicas para tu estructura
    migraciones = [
        "-- MIGRACIÓN PARA SISTEMA MULTI-TENANT PANADERÍAS",
        "-- FECHA: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    
    # Tablas y sus nuevas columnas
    tablas = [
        "sucursales",
        "configuracion_panaderia", 
        "panaderias",
        "compras_externas",
        "historial_compras",
        "clientes",
        "detalle_venta",
        "compras",
        "detalle_compras",
        "gastos",
        "receta_ingredientes",
        "historial_inventario",
        "stock_productos",
        "configuracion_produccion",
        "historial_rotacion_producto",
        "control_vida_util",
        "facturas",
        "jornadas_ventas",
        "cierres_diarios",
        "permisos_usuario",
        "consecutivos_pos"
    ]
    
    for tabla in tablas:
        migraciones.append(f"-- Migración para {tabla}")
        migraciones.append(f"ALTER TABLE {tabla} ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;")
        migraciones.append("")
    
    migraciones.append("COMMIT;")
    migraciones.append("")
    migraciones.append("-- ✅ MIGRACIÓN COMPLETADA")
    
    # Guardar archivo
    with open('migracion_panaderia_id.sql', 'w', encoding='utf-8') as f:
        f.write('\n'.join(migraciones))
    
    print("📁 Archivo de migración generado: migracion_panaderia_id.sql")
    print("📋 Ejecuta este archivo en tu base de datos SQLite")
    
    return migraciones

def ejecutar_migracion_automatica():
    """Ejecuta la migración automáticamente en SQLite"""
    
    db_path = "panaderia.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 EJECUTANDO MIGRACIÓN AUTOMÁTICA...")
        print("=" * 60)
        
        tablas = [
            "sucursales", "configuracion_panaderia", "panaderias", "compras_externas",
            "historial_compras", "clientes", "detalle_venta", "compras", "detalle_compras",
            "gastos", "receta_ingredientes", "historial_inventario", "stock_productos",
            "configuracion_produccion", "historial_rotacion_producto", "control_vida_util",
            "facturas", "jornadas_ventas", "cierres_diarios", "permisos_usuario", "consecutivos_pos"
        ]
        
        exitosas = 0
        for tabla in tablas:
            try:
                # Verificar si la columna ya existe
                cursor.execute(f"PRAGMA table_info({tabla})")
                columnas = [col[1] for col in cursor.fetchall()]
                
                if 'panaderia_id' not in columnas:
                    cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1")
                    print(f"  ✅ {tabla}: panaderia_id agregado")
                    exitosas += 1
                else:
                    print(f"  ✅ {tabla}: ya tiene panaderia_id")
                    
            except Exception as e:
                print(f"  ❌ {tabla}: Error - {e}")
        
        conn.commit()
        conn.close()
        
        print(f"\n🎯 Migración completada: {exitosas}/{len(tablas)} tablas actualizadas")
        return exitosas > 0
        
    except Exception as e:
        print(f"❌ Error en migración automática: {e}")
        return False

if __name__ == "__main__":
    print("🚀 MIGRACIÓN BASE DE DATOS MULTI-TENANT")
    print("=" * 60)
    
    # Generar archivo SQL
    generar_migracion_sqlite()
    
    # Preguntar si ejecutar automáticamente
    respuesta = input("\n¿Ejecutar migración automáticamente? (s/n): ").lower().strip()
    
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        if ejecutar_migracion_automatica():
            print("🎉 ¡Migración automática completada!")
        else:
            print("⚠️  Ejecuta manualmente el archivo migracion_panaderia_id.sql")
    else:
        print("📋 Ejecuta manualmente: sqlite3 panaderia.db < migracion_panaderia_id.sql")