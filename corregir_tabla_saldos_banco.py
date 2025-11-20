# corregir_tabla_saldos_banco.py
import sqlite3
import os
from datetime import datetime

def crear_backup_bd():
    """Crea backup de todas las bases de datos"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups_correccion_saldos"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    bases_datos = ["panaderia.db", "databases_tenants/panaderia_principal.db"]
    backups = []
    
    for db_path in bases_datos:
        if os.path.exists(db_path):
            backup_path = os.path.join(backup_dir, f"{os.path.basename(db_path)}_{timestamp}.backup")
            with open(db_path, 'rb') as original:
                with open(backup_path, 'wb') as backup:
                    backup.write(original.read())
            backups.append(backup_path)
            print(f"💾 Backup creado: {backup_path}")
    
    return backups

def corregir_tabla_saldos_banco():
    print("🔧 CORRIGIENDO TABLA saldos_banco")
    print("=" * 40)
    
    backups = crear_backup_bd()
    
    bases_datos = ["panaderia.db", "databases_tenants/panaderia_principal.db"]
    
    for db_path in bases_datos:
        if not os.path.exists(db_path):
            print(f"⚠️  Saltando {db_path} - no existe")
            continue
            
        print(f"\n📁 Procesando: {db_path}")
        print("-" * 30)
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar si la tabla saldos_banco existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='saldos_banco'")
            if not cursor.fetchone():
                print("   ⚠️  Tabla saldos_banco no existe, saltando")
                continue
            
            # Verificar si ya tiene panaderia_id
            cursor.execute("PRAGMA table_info(saldos_banco)")
            columnas = [col[1] for col in cursor.fetchall()]
            
            if 'panaderia_id' in columnas:
                print("   ✅ Ya tiene panaderia_id")
            else:
                # Agregar columna panaderia_id
                cursor.execute("ALTER TABLE saldos_banco ADD COLUMN panaderia_id INTEGER DEFAULT 1")
                print("   ✅ Columna panaderia_id agregada")
                
                # Actualizar registros existentes
                cursor.execute("UPDATE saldos_banco SET panaderia_id = 1 WHERE panaderia_id IS NULL")
                cursor.execute("SELECT COUNT(*) FROM saldos_banco")
                total = cursor.fetchone()[0]
                print(f"   ✅ {total} registros actualizados")
            
            conn.commit()
            print("   💾 Cambios guardados")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        finally:
            conn.close()
    
    print(f"\n📁 Backups disponibles en: backups_correccion_saldos/")

def verificar_todas_las_tablas():
    print("\n🔍 VERIFICANDO TODAS LAS TABLAS")
    print("=" * 40)
    
    db_path = "panaderia.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = [tabla[0] for tabla in cursor.fetchall()]
        
        print("📊 Tablas en la base de datos:")
        for tabla in tablas:
            if any(keyword in tabla.lower() for keyword in ['proveedor', 'activo', 'registro', 'pago', 'saldo']):
                cursor.execute(f"PRAGMA table_info({tabla})")
                columnas = [col[1] for col in cursor.fetchall()]
                
                if 'panaderia_id' in columnas:
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla} WHERE panaderia_id IS NOT NULL")
                    con_id = cursor.fetchone()[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                    total = cursor.fetchone()[0]
                    
                    print(f"   ✅ {tabla}: {con_id}/{total} registros con panaderia_id")
                else:
                    print(f"   ❌ {tabla}: SIN panaderia_id")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("🛡️  CORRECCIÓN COMPLETA - TABLA SALDOS_BANCO")
    print("=" * 50)
    
    corregir_tabla_saldos_banco()
    verificar_todas_las_tablas()
    
    print("\n🎯 PRÓXIMO PASO: Verificar filtros en app.py")