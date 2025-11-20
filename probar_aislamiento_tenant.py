# probar_aislamiento_tenant.py
import sqlite3

def verificar_aislamiento_bd():
    print("🧪 VERIFICANDO AISLAMIENTO EN BASE DE DATOS")
    print("=" * 50)
    
    # Verificar que todas las tablas tienen panaderia_id
    db_path = "panaderia.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        tablas_verificar = ["proveedor", "activos_fijos"]
        
        for tabla in tablas_verificar:
            print(f"\n📋 Verificando {tabla}:")
            
            # Verificar estructura
            cursor.execute(f"PRAGMA table_info({tabla})")
            columnas = [col[1] for col in cursor.fetchall()]
            
            if 'panaderia_id' in columnas:
                print(f"   ✅ Estructura OK - tiene panaderia_id")
                
                # Verificar que todos los registros tienen panaderia_id
                cursor.execute(f"SELECT COUNT(*) FROM {tabla} WHERE panaderia_id IS NOT NULL")
                con_id = cursor.fetchone()[0]
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                total = cursor.fetchone()[0]
                
                if con_id == total:
                    print(f"   ✅ Datos OK - {con_id}/{total} registros con panaderia_id")
                else:
                    print(f"   ❌ Datos ERROR - {con_id}/{total} registros con panaderia_id")
            else:
                print(f"   ❌ Estructura ERROR - sin panaderia_id")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def instrucciones_prueba_manual():
    print("\n" + "=" * 50)
    print("🎯 INSTRUCCIONES PARA PRUEBA MANUAL")
    print("=" * 50)
    print("1. 🔄 REINICIA el servidor Flask")
    print("2. 🔐 LOGIN como admin_2 (Panadería Norte)")
    print("3. ➕ CREA datos en:")
    print("   • Proveedores: 'Proveedor Norte TEST'")
    print("   • Activos Fijos: 'Activo Norte TEST'") 
    print("   • Financiero: Registra un gasto")
    print("4. 🔐 LOGOUT y LOGIN como admin_3 (Panadería Sur)")
    print("5. 👀 VERIFICA que NO ves los datos de Panadería Norte")
    print("6. ✅ Si no los ves: ¡AISLAMIENTO EXITOSO!")

if __name__ == "__main__":
    verificar_aislamiento_bd()
    instrucciones_prueba_manual()