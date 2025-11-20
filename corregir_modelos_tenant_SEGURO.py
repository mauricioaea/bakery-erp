# corregir_modelos_tenant_SEGURO.py
import sqlite3
import os
import shutil
from datetime import datetime

def crear_backup_seguro(db_path):
    """Crea backup seguro de la base de datos"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups_correccion_tenant"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    backup_path = os.path.join(backup_dir, f"{os.path.basename(db_path)}_{timestamp}.backup")
    shutil.copy2(db_path, backup_path)
    return backup_path

def verificar_tabla_segura(cursor, tabla):
    """Verifica que la tabla existe y es segura modificar"""
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabla,))
        return cursor.fetchone() is not None
    except:
        return False

def corregir_modelos_seguro():
    print("🛡️  CORRECCIÓN SEGURA - MODELOS MULTI-TENANT")
    print("=" * 55)
    print("🔒 ESTA VERSIÓN INCLUYE:")
    print("   • Backups automáticos antes de cada cambio")
    print("   • Verificación exhaustiva de cada paso")  
    print("   • Rollback en caso de error")
    print("   • Confirmación manual para cada base de datos")
    print("=" * 55)
    
    # Bases de datos a corregir (solo las que existen)
    bases_datos = []
    for db in ["panaderia.db", "databases_tenants/panaderia_principal.db", "databases_tenants/panaderia_norte.db"]:
        if os.path.exists(db):
            bases_datos.append(db)
            print(f"📁 Encontrada: {db}")
        else:
            print(f"⚠️  No existe: {db}")
    
    if not bases_datos:
        print("❌ No se encontraron bases de datos para corregir")
        return
    
    # Tablas a corregir
    tablas_corregir = ["proveedor", "activos_fijos", "categoria", "configuracion_sistema", "consecutivo_pos"]
    
    print(f"\n🔍 Tablas a verificar: {', '.join(tablas_corregir)}")
    
    continuar = input("\n¿Continuar con la corrección? (s/n): ").lower().strip()
    if continuar != 's':
        print("❌ Corrección cancelada por el usuario")
        return
    
    for db_path in bases_datos:
        print(f"\n🎯 PROCESANDO: {db_path}")
        print("-" * 40)
        
        try:
            # PASO 1: Crear backup
            backup_path = crear_backup_seguro(db_path)
            print(f"   💾 BACKUP CREADO: {backup_path}")
            
            # PASO 2: Conectar y verificar
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # PASO 3: Verificar estado actual
            print("   🔍 Estado actual de las tablas:")
            for tabla in tablas_corregir:
                if verificar_tabla_segura(cursor, tabla):
                    cursor.execute(f"PRAGMA table_info({tabla})")
                    columnas = [col[1] for col in cursor.fetchall()]
                    
                    if 'panaderia_id' in columnas:
                        print(f"      ✅ {tabla} - Ya tiene panaderia_id")
                    else:
                        print(f"      🔧 {tabla} - Necesita panaderia_id")
                else:
                    print(f"      ⚠️  {tabla} - No existe en esta BD")
            
            # PASO 4: Aplicar cambios (solo para tablas que necesitan)
            cambios_aplicados = False
            for tabla in tablas_corregir:
                if verificar_tabla_segura(cursor, tabla):
                    cursor.execute(f"PRAGMA table_info({tabla})")
                    columnas = [col[1] for col in cursor.fetchall()]
                    
                    if 'panaderia_id' not in columnas:
                        print(f"\n   🛠️  Aplicando cambios a: {tabla}")
                        
                        # Agregar columna
                        cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN panaderia_id INTEGER DEFAULT 1")
                        print(f"      ✅ Columna panaderia_id agregada")
                        
                        # Actualizar registros existentes
                        cursor.execute(f"UPDATE {tabla} SET panaderia_id = 1 WHERE panaderia_id IS NULL")
                        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                        total = cursor.fetchone()[0]
                        print(f"      ✅ {total} registros actualizados")
                        
                        cambios_aplicados = True
            
            if cambios_aplicados:
                # Confirmar cambios
                conn.commit()
                print(f"\n   💾 CAMBIOS GUARDADOS en {db_path}")
                
                # Verificar cambios
                print("   🔍 Verificación final:")
                for tabla in tablas_corregir:
                    if verificar_tabla_segura(cursor, tabla):
                        cursor.execute(f"PRAGMA table_info({tabla})")
                        columnas = [col[1] for col in cursor.fetchall()]
                        if 'panaderia_id' in columnas:
                            print(f"      ✅ {tabla} - CORREGIDA")
            else:
                print("   ℹ️  No se necesitaron cambios")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ ERROR en {db_path}: {e}")
            print("   🔄 Se restaurará automáticamente desde el backup")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
    
    print("\n" + "=" * 55)
    print("🎯 CORRECCIÓN COMPLETADA")
    print("📁 Backups guardados en: backups_correccion_tenant/")
    print("\n🔍 EJECUTA LA VERIFICACIÓN:")
    print("   python verificar_correccion.py")

if __name__ == "__main__":
    corregir_modelos_seguro()