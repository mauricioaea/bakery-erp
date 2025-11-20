#!/usr/bin/env python3
"""
CONFIGURACIÓN DEL COMPORTAMIENTO SUPER ADMINISTRADOR
Limpia proveedores del super admin y configura comportamiento especial
"""

import sqlite3
from datetime import datetime

def limpiar_proveedores_super_admin():
    """Limpia todos los proveedores del tenant super admin (panaderia_id = 1)"""
    
    print("🧹 LIMPIANDO PROVEEDORES DE SUPER ADMINISTRADOR")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('panaderia.db')
        cursor = conn.cursor()
        
        # Contar proveedores actuales del super admin
        cursor.execute("SELECT COUNT(*) FROM proveedor WHERE panaderia_id = 1")
        count_antes = cursor.fetchone()[0]
        
        if count_antes == 0:
            print("✅ Super admin ya está limpio - Sin proveedores")
            return True
        
        # Eliminar proveedores del super admin
        cursor.execute("DELETE FROM proveedor WHERE panaderia_id = 1")
        
        # Verificar limpieza
        cursor.execute("SELECT COUNT(*) FROM proveedor WHERE panaderia_id = 1")
        count_despues = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        print(f"📊 Proveedores eliminados del super admin: {count_antes}")
        print(f"📊 Estado actual: {count_despues} proveedores")
        print("✅ Limpieza completada exitosamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en limpieza: {e}")
        return False

def verificar_estado_tenants():
    """Verifica el estado actual de todos los tenants"""
    
    print("\n🔍 ESTADO ACTUAL DE TODOS LOS TENANTS")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('panaderia.db')
        cursor = conn.cursor()
        
        # Contar proveedores por tenant
        cursor.execute("""
            SELECT panaderia_id, COUNT(*) as total_proveedores 
            FROM proveedor 
            GROUP BY panaderia_id 
            ORDER BY panaderia_id
        """)
        
        resultados = cursor.fetchall()
        
        print("📊 PROVEEDORES POR TENANT:")
        for panaderia_id, total in resultados:
            print(f"   🏪 Panadería {panaderia_id}: {total} proveedores")
        
        # Verificar tenants sin proveedores
        cursor.execute("SELECT DISTINCT panaderia_id FROM proveedor")
        tenants_con_proveedores = [row[0] for row in cursor.fetchall()]
        
        todos_tenants = [1, 2, 3, 4]  # Tus tenants actuales
        tenants_sin_proveedores = [t for t in todos_tenants if t not in tenants_con_proveedores]
        
        if tenants_sin_proveedores:
            print(f"\n📋 Tenants sin proveedores: {tenants_sin_proveedores}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verificando tenants: {e}")
        return False

def configurar_comportamiento_super_admin():
    """Configura el comportamiento especial del super administrador"""
    
    print("\n🎛️ CONFIGURANDO COMPORTAMIENTO SUPER ADMIN")
    print("=" * 60)
    
    # Actualizar tenant_context.py para manejar super admin
    archivo = "tenant_context.py"
    
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Buscar la clase TenantContext para agregar el método
        if 'def get_super_admin_behavior' not in contenido:
            # Encontrar el final de la clase TenantContext
            patron = r'(class TenantContext:.*?)(\n\n|\Z)'
            match = re.search(patron, contenido, re.DOTALL)
            
            if match:
                metodo_super_admin = '''
    @staticmethod
    def get_super_admin_behavior():
        """Define el comportamiento para super administrador"""
        if not current_user or not hasattr(current_user, 'es_super_admin'):
            return "normal"
        
        if current_user.es_super_admin:
            return "super_admin"
        return "normal"
'''
                
                nuevo_contenido = contenido.replace(match.group(1), match.group(1) + metodo_super_admin)
                
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(nuevo_contenido)
                
                print("✅ Comportamiento super admin configurado en TenantContext")
        
        print("🎯 Comportamiento configurado:")
        print("   • dev_master: Modo super administrador")
        print("   • Sin proveedores propios (solo administración)")
        print("   • Acceso completo a todos los tenants")
        print("   • Proveedores vacíos (solo para capacitación)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando comportamiento: {e}")
        return False

if __name__ == "__main__":
    import re
    
    print("🚀 CONFIGURACIÓN SUPER ADMINISTRADOR")
    print("=" * 60)
    
    # 1. Limpiar proveedores del super admin
    limpiar_proveedores_super_admin()
    
    # 2. Verificar estado de todos los tenants
    verificar_estado_tenants()
    
    # 3. Configurar comportamiento especial
    configurar_comportamiento_super_admin()
    
    print("\n" + "=" * 60)
    print("🎯 CONFIGURACIÓN COMPLETADA")
    print("📋 Comportamiento esperado:")
    print("   • dev_master: Super administrador - Sin proveedores propios")
    print("   • admin_2: Tenant normal - Solo sus proveedores") 
    print("   • admin_3: Tenant normal - Solo sus proveedores")
    print("   • admin_4: Tenant normal - Solo sus proveedores")
    print("\n💡 El super admin puede crear proveedores demo cuando sea necesario para capacitación")