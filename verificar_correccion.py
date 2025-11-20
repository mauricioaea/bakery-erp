# verificar_correccion.py
import sqlite3

def verificar_correccion():
    print("✅ VERIFICANDO CORRECCIÓN DE MODELOS")
    print("=" * 40)
    
    db_path = "panaderia.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        tablas_verificar = ["proveedor", "activos_fijos", "categoria", "configuracion_sistema", "consecutivo_pos"]
        
        for tabla in tablas_verificar:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabla,))
            if cursor.fetchone():
                cursor.execute(f"PRAGMA table_info({tabla})")
                columnas = [col[1] for col in cursor.fetchall()]
                
                if 'panaderia_id' in columnas:
                    print(f"✅ {tabla} - CORREGIDO (tiene panaderia_id)")
                    # Verificar que los registros tengan panaderia_id
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla} WHERE panaderia_id IS NOT NULL")
                    count_con_id = cursor.fetchone()[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                    total = cursor.fetchone()[0]
                    print(f"   📊 Registros con panaderia_id: {count_con_id}/{total}")
                else:
                    print(f"❌ {tabla} - SIN CORREGIR (sin panaderia_id)")
            else:
                print(f"⚠️  {tabla} - no existe")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verificar_correccion()