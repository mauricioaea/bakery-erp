# corregir_tablas_faltantes.py
import sqlite3
import os
from datetime import datetime

def corregir_tablas_faltantes():
    print("🔧 CORRIGIENDO TABLAS FALTANTES")
    print("=" * 40)
    
    bases_datos = ["panaderia.db", "databases_tenants/panaderia_principal.db"]
    tablas_faltantes = ["registros_diarios", "pagos_individuales"]
    
    for db_path in bases_datos:
        if not os.path.exists(db_path):
            print(f"⚠️  Saltando {db_path} - no existe")
            continue
            
        print(f"\n📁 Procesando: {db_path}")
        print("-" * 30)
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            for tabla in tablas_faltantes:
                # Verificar si la tabla existe
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabla,))
                if not cursor.fetchone():
                    print(f"   ⚠️  {tabla} - no existe, saltando")
                    continue
                
                # Verificar si ya tiene panaderia_id
                cursor.execute(f"PRAGMA table_info({tabla})")
                columnas = [col[1] for col in cursor.fetchall()]
                
                if 'panaderia_id' in columnas:
                    print(f"   ✅ {tabla} - ya tiene panaderia_id")
                else:
                    # Agregar columna panaderia_id
                    cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN panaderia_id INTEGER DEFAULT 1")
                    print(f"   ✅ {tabla} - panaderia_id agregado")
                    
                    # Actualizar registros existentes
                    cursor.execute(f"UPDATE {tabla} SET panaderia_id = 1 WHERE panaderia_id IS NULL")
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                    total = cursor.fetchone()[0]
                    print(f"   ✅ {tabla} - {total} registros actualizados")
            
            conn.commit()
            print("   💾 Cambios guardados")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        finally:
            conn.close()

def verificar_todas_las_tablas_completo():
    print("\n🔍 VERIFICACIÓN COMPLETA DE TODAS LAS TABLAS")
    print("=" * 50)
    
    db_path = "panaderia.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = [tabla[0] for tabla in cursor.fetchall()]
        
        print("📊 ESTADO FINAL DE LAS TABLAS:")
        todas_correctas = True
        
        for tabla in tablas:
            if any(keyword in tabla.lower() for keyword in ['proveedor', 'activo', 'registro', 'pago', 'saldo', 'categoria', 'configuracion', 'consecutivo']):
                cursor.execute(f"PRAGMA table_info({tabla})")
                columnas = [col[1] for col in cursor.fetchall()]
                
                if 'panaderia_id' in columnas:
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla} WHERE panaderia_id IS NOT NULL")
                    con_id = cursor.fetchone()[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                    total = cursor.fetchone()[0]
                    
                    if con_id == total:
                        print(f"   ✅ {tabla}: COMPLETAMENTE CORREGIDA ({con_id}/{total})")
                    else:
                        print(f"   ⚠️  {tabla}: PARCIAL ({con_id}/{total})")
                        todas_correctas = False
                else:
                    print(f"   ❌ {tabla}: SIN panaderia_id")
                    todas_correctas = False
        
        if todas_correctas:
            print("\n🎯 ¡TODAS LAS TABLAS ESTÁN CORRECTAS!")
        else:
            print("\n⚠️  Algunas tablas necesitan atención")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("🛡️  CORRECCIÓN DE TABLAS FALTANTES")
    print("=" * 50)
    
    corregir_tablas_faltantes()
    verificar_todas_las_tablas_completo()
    
    print("\n🎯 PRÓXIMO PASO: Verificar filtros en app.py")