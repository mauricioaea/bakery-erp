# verificar_roles_permisos.py
import sqlite3
import os

def verificar_roles_permisos():
    """Verifica la estructura de roles y permisos en el sistema"""
    
    print("🔍 VERIFICANDO ROLES Y PERMISOS")
    print("=" * 70)
    
    # 1. Conectar a tenant_master para obtener tenants activos
    conn_master = sqlite3.connect('tenant_master.db')
    cursor_master = conn_master.cursor()
    cursor_master.execute("SELECT id, nombre, subdominio FROM tenants WHERE activo = 1 AND id != 1")
    tenants = cursor_master.fetchall()
    conn_master.close()
    
    if not tenants:
        print("❌ No hay tenants activos (excepto el principal)")
        return
    
    print(f"\n📋 Tenants activos: {len(tenants)}")
    print("-" * 70)
    
    # 2. Para cada tenant, verificar los roles y usuarios
    for tenant in tenants:
        tenant_id = tenant[0]
        nombre = tenant[1]
        subdominio = tenant[2]
        
        db_file = f"databases_tenants/{subdominio}.db"
        if not os.path.exists(db_file):
            db_file = f"databases_tenants/panaderia_cliente{tenant_id}.db"
        
        if not os.path.exists(db_file):
            print(f"⚠️ ID {tenant_id} - {nombre} → BD no encontrada")
            continue
        
        conn_tenant = sqlite3.connect(db_file)
        cursor_tenant = conn_tenant.cursor()
        
        print(f"\n🏪 {nombre} (ID: {tenant_id})")
        print("-" * 50)
        
        # 3. Verificar usuarios y sus roles
        cursor_tenant.execute("""
            SELECT id, username, rol, activo, nombre_completo 
            FROM usuarios 
            WHERE activo = 1
            ORDER BY rol, username
        """)
        usuarios = cursor_tenant.fetchall()
        
        if not usuarios:
            print("  ⚠️ No hay usuarios activos")
            conn_tenant.close()
            continue
        
        # Agrupar por rol
        roles = {}
        for usuario in usuarios:
            rol = usuario[2]
            if rol not in roles:
                roles[rol] = []
            roles[rol].append({
                'id': usuario[0],
                'username': usuario[1],
                'nombre': usuario[4]
            })
        
        # Mostrar resumen de roles
        print(f"\n  📊 USUARIOS POR ROL ({len(usuarios)} total):")
        for rol, usuarios_lista in roles.items():
            print(f"    👤 {rol.upper()}: {len(usuarios_lista)} usuarios")
            for u in usuarios_lista:
                print(f"       - {u['username']} ({u['nombre']})")
        
        # 4. Verificar permisos (si existe la tabla)
        cursor_tenant.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='permisos_usuario'")
        if cursor_tenant.fetchone():
            cursor_tenant.execute("SELECT DISTINCT modulo, accion FROM permisos_usuario")
            permisos = cursor_tenant.fetchall()
            print(f"\n  📋 PERMISOS CONFIGURADOS:")
            for p in permisos:
                print(f"    - {p[0]}: {p[1]}")
        else:
            print(f"\n  ℹ️ No hay tabla de permisos (los permisos están integrados en la lógica)")
        
        # 5. Verificar módulos disponibles (basado en templates)
        print(f"\n  📂 MÓDULOS DISPONIBLES PARA EL TENANT:")
        modulos = [
            "Dashboard",
            "Punto de Venta (POS)",
            "Inventario",
            "Producción",
            "Recetas",
            "Clientes",
            "Proveedores",
            "Reportes",
            "Cierre de Caja",
            "Gestión de Usuarios"
        ]
        for modulo in modulos:
            print(f"    - {modulo}")
        
        conn_tenant.close()
    
    print("\n" + "=" * 70)
    print("✅ VERIFICACIÓN COMPLETADA")

if __name__ == "__main__":
    verificar_roles_permisos()