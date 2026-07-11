# validar_tenants.py
import sqlite3
import os

def validar_tenants():
    """Valida que todos los tenants activos tengan las tablas necesarias"""
    
    print("🔍 VALIDANDO TENANTS ACTIVOS")
    print("=" * 60)
    
    # Tablas necesarias
    tablas_requeridas = [
        'usuarios',
        'ventas',
        'facturas',
        'consecutivos_pos',
        'productos',
        'clientes',
        'configuracion_panaderia'
    ]
    
    # 1. Obtener tenants activos
    conn_master = sqlite3.connect('tenant_master.db')
    cursor_master = conn_master.cursor()
    cursor_master.execute("SELECT id, nombre, subdominio FROM tenants WHERE activo = 1")
    tenants = cursor_master.fetchall()
    conn_master.close()
    
    if not tenants:
        print("❌ No hay tenants activos")
        return
    
    print(f"\n📋 Tenants activos: {len(tenants)}")
    print("-" * 60)
    
    tenants_con_problemas = []
    
    for tenant in tenants:
        tenant_id = tenant[0]
        nombre = tenant[1]
        subdominio = tenant[2]
        
        # Buscar el archivo de BD
        db_file = f"databases_tenants/{subdominio}.db"
        if not os.path.exists(db_file):
            db_file = f"databases_tenants/panaderia_cliente{tenant_id}.db"
        
        if not os.path.exists(db_file):
            print(f"❌ ID {tenant_id} - {nombre} → BD no encontrada")
            tenants_con_problemas.append(tenant_id)
            continue
        
        # Verificar tablas
        conn_tenant = sqlite3.connect(db_file)
        cursor_tenant = conn_tenant.cursor()
        
        tablas_faltantes = []
        for tabla in tablas_requeridas:
            cursor_tenant.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabla,))
            if not cursor_tenant.fetchone():
                tablas_faltantes.append(tabla)
        
        conn_tenant.close()
        
        if tablas_faltantes:
            print(f"⚠️ ID {tenant_id} - {nombre} → Tablas faltantes: {', '.join(tablas_faltantes)}")
            tenants_con_problemas.append(tenant_id)
        else:
            print(f"✅ ID {tenant_id} - {nombre} → Todas las tablas OK")
    
    print("-" * 60)
    print(f"\n📊 RESUMEN:")
    print(f"  ✅ Tenants correctos: {len(tenants) - len(tenants_con_problemas)}")
    print(f"  ⚠️ Tenants con problemas: {len(tenants_con_problemas)}")
    
    if tenants_con_problemas:
        print(f"\n💡 Tenants con problemas (IDs): {tenants_con_problemas}")
        print("   → Ejecuta 'python migrar_tenants.py' para corregirlos")

if __name__ == "__main__":
    validar_tenants()