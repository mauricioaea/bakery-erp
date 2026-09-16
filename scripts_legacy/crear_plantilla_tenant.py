# crear_plantilla_tenant.py
import sqlite3
import shutil
from pathlib import Path

def crear_plantilla_tenant():
    """Crea una plantilla de base de datos tenant limpia"""
    print("🔄 CREANDO PLANTILLA DE TENANT PROFESIONAL")
    print("="*60)
    
    # 1. Usar panaderia_principal.db como base (tiene estructura completa)
    origen = "databases_tenants/panaderia_principal.db"
    plantilla = "databases_tenants/tenant_plantilla.db"
    
    if not Path(origen).exists():
        print(f"❌ No existe: {origen}")
        return False
    
    # 2. Crear copia
    shutil.copy2(origen, plantilla)
    print(f"✅ Plantilla creada: {plantilla}")
    
    # 3. Conectar y limpiar datos de tenant (pero mantener estructura)
    conn = sqlite3.connect(plantilla)
    cursor = conn.cursor()
    
    # Lista de tablas a limpiar (datos específicos de tenant)
    # PERO mantener tablas de configuración del sistema
    tablas_a_limpiar = [
        'facturas', 'ventas', 'detalle_venta', 'cierre_diario',
        'depositos_bancarios', 'productos', 'productos_externos',
        'materias_primas', 'recetas', 'ordenes_produccion',
        'proveedores', 'activos_fijos', 'usuarios_panaderia',
        'detalle_cierre', 'detalle_venta_externo'
    ]
    
    print("\n🧹 Limpiando datos de tenant...")
    for tabla in tablas_a_limpiar:
        try:
            cursor.execute(f"DELETE FROM {tabla}")
            print(f"   ✅ {tabla}")
        except sqlite3.OperationalError:
            print(f"   ⚠️  {tabla} (no existe)")
        except Exception as e:
            print(f"   ❌ {tabla}: {e}")
    
    # 4. Mantener/crear configuración base
    print("\n⚙️ Configurando estructura base...")
    
    # Asegurar que existe tabla configuracion_sistema
    try:
        cursor.execute("SELECT COUNT(*) FROM configuracion_sistema")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO configuracion_sistema (modo_pruebas, version_sistema) 
                VALUES (1, '1.0.0')
            """)
            print("   ✅ configuracion_sistema creada")
    except:
        print("   ⚠️  configuracion_sistema (configuración global)")
    
    # 5. Crear consecutivo POS inicial (panaderia_id será reemplazado luego)
    try:
        cursor.execute("DELETE FROM consecutivo_pos")
        cursor.execute("INSERT INTO consecutivo_pos (panaderia_id, numero_actual) VALUES (0, 0)")
        print("   ✅ consecutivo_pos inicializado")
    except:
        print("   ⚠️  consecutivo_pos (se creará dinámicamente)")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎯 PLANTILLA CREADA EXITOSAMENTE: {plantilla}")
    print("   Estructura completa, datos de tenant limpios")
    
    return True

if __name__ == "__main__":
    print("⚠️  Este script creará una plantilla profesional para nuevos tenants.")
    print("   No afectará los tenants existentes.")
    
    respuesta = input("\n¿Crear plantilla tenant? (si/no): ")
    if respuesta.lower() == 'si':
        crear_plantilla_tenant()
        print("\n✅ PASO 1 COMPLETADO. Continúa con el PASO 2.")
    else:
        print("Cancelado.")