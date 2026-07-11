# verificar_tenants_activos.py
import sqlite3
import os

def verificar_tenants_activos():
    """Verifica qué tenants están activos en el sistema"""
    
    print("🔍 VERIFICANDO TENANTS ACTIVOS")
    print("=" * 60)
    
    # 1. Conectar a tenant_master.db
    if not os.path.exists('tenant_master.db'):
        print("❌ No se encuentra tenant_master.db")
        return
    
    conn_master = sqlite3.connect('tenant_master.db')
    cursor_master = conn_master.cursor()
    
    # Obtener todos los tenants con su estado
    cursor_master.execute("""
        SELECT id, nombre, subdominio, activo, fecha_creacion 
        FROM tenants 
        ORDER BY id
    """)
    tenants = cursor_master.fetchall()
    conn_master.close()
    
    if not tenants:
        print("❌ No hay tenants registrados")
        return
    
    print("\n📋 LISTA DE TENANTS:")
    print("-" * 60)
    print(f"{'ID':<6} {'Nombre':<30} {'Estado':<12} {'Creado'}")
    print("-" * 60)
    
    activos = 0
    inactivos = 0
    
    for tenant in tenants:
        tenant_id = tenant[0]
        nombre = tenant[1] or "Sin nombre"
        subdominio = tenant[2] or "Sin subdominio"
        activo = tenant[3] if tenant[3] is not None else 1
        fecha = tenant[4] if tenant[4] else "Desconocida"
        
        estado = "🟢 ACTIVO" if activo == 1 else "🔴 INACTIVO"
        
        if activo == 1:
            activos += 1
        else:
            inactivos += 1
        
        # Verificar si el archivo de BD existe
        db_file = f"databases_tenants/{subdominio}.db"
        if not os.path.exists(db_file):
            db_file = f"databases_tenants/panaderia_cliente{tenant_id}.db"
        archivo_existe = "✅" if os.path.exists(db_file) else "❌"
        
        print(f"{tenant_id:<6} {nombre[:28]:<30} {estado:<12} {fecha[:10] if fecha else 'N/A'} {archivo_existe}")
    
    print("-" * 60)
    print(f"\n📊 RESUMEN:")
    print(f"  🟢 Tenants activos: {activos}")
    print(f"  🔴 Tenants inactivos: {inactivos}")
    print(f"  📦 Total tenants: {len(tenants)}")
    
    # Verificar tenants que tienen archivo pero no están en master
    print("\n🔍 VERIFICANDO ARCHIVOS HUÉRFANOS:")
    if os.path.exists('databases_tenants'):
        archivos_db = [f for f in os.listdir('databases_tenants') if f.endswith('.db')]
        archivos_master = [t[2] for t in tenants if t[2]]
        huerfanos = []
        
        for archivo in archivos_db:
            if archivo == 'tenant_plantilla.db':
                continue
            if archivo == 'panaderia_principal.db':
                continue
            # Buscar si el archivo está en master
            encontrado = False
            for t in tenants:
                if archivo == t[2] or archivo == f"panaderia_cliente{t[0]}.db":
                    encontrado = True
                    break
            if not encontrado:
                huerfanos.append(archivo)
        
        if huerfanos:
            print(f"  ⚠️ Archivos huérfanos encontrados ({len(huerfanos)}):")
            for h in huerfanos:
                print(f"    - {h}")
        else:
            print("  ✅ No hay archivos huérfanos")

if __name__ == "__main__":
    verificar_tenants_activos()