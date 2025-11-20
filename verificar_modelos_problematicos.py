# verificar_modelos_problematicos.py
import sqlite3

def verificar_estructura_modelos():
    print("🔧 VERIFICANDO ESTRUCTURA DE MODELOS PROBLEMÁTICOS")
    print("=" * 50)
    
    # Verificar en tenant principal
    db_path = "panaderia.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Tablas críticas a verificar
        tablas_criticas = [
            "proveedor", "proveedores",
            "activo_fijo", "activos_fijos", 
            "gestion_financiera", "transaccion_financiera",
            "reporte", "reportes"
        ]
        
        for tabla in tablas_criticas:
            print(f"\n📋 Buscando tabla: {tabla}")
            
            # Verificar si existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?", (f'%{tabla}%',))
            resultados = cursor.fetchall()
            
            if resultados:
                for tabla_encontrada in resultados:
                    tabla_nombre = tabla_encontrada[0]
                    print(f"   ✅ Encontrada: {tabla_nombre}")
                    
                    # Verificar columnas
                    cursor.execute(f"PRAGMA table_info({tabla_nombre})")
                    columnas = cursor.fetchall()
                    
                    print(f"   🏗️  Columnas:")
                    tiene_panaderia_id = False
                    for col in columnas:
                        col_nombre = col[1]
                        col_tipo = col[2]
                        print(f"      - {col_nombre} ({col_tipo})")
                        if 'panaderia_id' in col_nombre.lower():
                            tiene_panaderia_id = True
                    
                    if tiene_panaderia_id:
                        print(f"   🛡️  ✅ TIENE panaderia_id - AISLADO")
                    else:
                        print(f"   🚨 ❌ NO TIENE panaderia_id - VULNERABLE")
                        
            else:
                print(f"   ⚠️  No encontrada: {tabla}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verificar_estructura_modelos()