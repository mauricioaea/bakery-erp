# diagnosticar_tenant_seguridad.py
import sqlite3
import os
from flask import Flask, g, session
import sys

def diagnosticar_seguridad_tenants():
    print("🔍 INICIANDO DIAGNÓSTICO DE SEGURIDAD MULTI-TENANT")
    print("=" * 60)
    
    # Configuración básica de Flask para el diagnóstico
    app = Flask(__name__)
    app.secret_key = 'diagnostico_temp'
    
    # Lista de bases de datos de tenants
    tenants_dir = "databases_tenants"
    tenants_db = []
    
    if os.path.exists(tenants_dir):
        for file in os.listdir(tenants_dir):
            if file.endswith(".db"):
                tenants_db.append(os.path.join(tenants_dir, file))
    
    print(f"📁 Tenants encontrados: {len(tenants_db)}")
    for db in tenants_db:
        print(f"   - {db}")
    
    # Verificar estructura de tablas en cada tenant
    for db_path in tenants_db:
        print(f"\n🔎 ANALIZANDO: {os.path.basename(db_path)}")
        print("-" * 40)
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Obtener todas las tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            print(f"📊 Tablas encontradas: {len(tables)}")
            
            # Analizar cada tabla
            for table in tables:
                table_name = table[0]
                print(f"\n   📋 Tabla: {table_name}")
                
                # Verificar si tiene columna panaderia_id
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                has_panaderia_id = any('panaderia_id' in col[1].lower() for col in columns)
                
                if has_panaderia_id:
                    print(f"      ✅ TIENE panaderia_id - AISLAMIENTO OK")
                else:
                    print(f"      ❌ NO TIENE panaderia_id - VULNERABLE")
                    
                # Contar registros
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"      📊 Registros: {count}")
                    
                    # Mostrar algunos registros si es pequeña
                    if count > 0 and count <= 10:
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                        sample = cursor.fetchall()
                        print(f"      🧪 Muestra: {sample}")
                        
                except Exception as e:
                    print(f"      ⚠️ Error contando registros: {e}")
                    
        except Exception as e:
            print(f"❌ Error analizando {db_path}: {e}")
        
        finally:
            conn.close()
    
    print("\n" + "=" * 60)
    print("🎯 MÓDULOS A VERIFICAR MANUALMENTE:")
    modulos_criticos = [
        "proveedores",
        "activos_fijos", 
        "gestion_financiera",
        "reportes"
    ]
    
    for modulo in modulos_criticos:
        print(f"   🔍 {modulo}")

if __name__ == "__main__":
    diagnosticar_seguridad_tenants()