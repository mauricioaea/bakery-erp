#!/usr/bin/env python3
"""
LIMPIEZA SEGURA - Solo limpiar datos del tenant Norte (nuevo)
"""

import sqlite3
import os
import shutil
from datetime import datetime

class LimpiadorDatosTenant:
    def __init__(self):
        self.tenant_id = 2  # Solo limpiar el tenant Norte
        self.tenant_nombre = "panaderia Norte"
        self.bd_tenant = "databases_tenants/panaderia_panaderia_norte.db"
    
    def crear_backup(self):
        """Crear backup seguro del tenant a limpiar"""
        if os.path.exists(self.bd_tenant):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backups_saas/panaderia_norte_pre_limpieza_{timestamp}.db"
            shutil.copy2(self.bd_tenant, backup_path)
            print(f"✅ Backup creado: {backup_path}")
            return True
        return False
    
    def verificar_datos_actuales(self):
        """Verificar datos actuales en el tenant"""
        print(f"🔍 DATOS ACTUALES EN {self.tenant_nombre}:")
        
        try:
            conn = sqlite3.connect(self.bd_tenant)
            cursor = conn.cursor()
            
            # Contar registros en tablas clave
            tablas_verificar = [
                ('proveedor', 'Proveedores'),
                ('activos_fijos', 'Activos Fijos'),
                ('productos', 'Productos'),
                ('clientes', 'Clientes'),
                ('usuarios', 'Usuarios')
            ]
            
            for tabla, nombre in tablas_verificar:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                    count = cursor.fetchone()[0]
                    print(f"   📊 {nombre}: {count} registros")
                    
                    # Mostrar algunos ejemplos
                    if count > 0 and tabla in ['proveedor', 'activos_fijos']:
                        cursor.execute(f"SELECT nombre FROM {tabla} LIMIT 3")
                        ejemplos = cursor.fetchall()
                        print(f"      Ejemplos: {[e[0] for e in ejemplos]}")
                except Exception as e:
                    print(f"   ⚠️  {nombre}: Error - {e}")
            
            conn.close()
        except Exception as e:
            print(f"❌ Error verificando datos: {e}")
    
    def limpiar_datos_tenant(self):
        """Limpiar datos del tenant nuevo (dejar solo estructura)"""
        print(f"\n🧹 LIMPIANDO DATOS DE {self.tenant_nombre}...")
        
        try:
            conn = sqlite3.connect(self.bd_tenant)
            cursor = conn.cursor()
            
            # Tablas a limpiar (dejar vacías para nuevo tenant)
            tablas_limpiar = [
                'proveedor',           # Proveedores
                'activos_fijos',       # Activos fijos  
                'productos',           # Productos
                'clientes',            # Clientes
                'compras',             # Compras
                'ventas',              # Ventas
                'gastos',              # Gastos
                'recetas',             # Recetas
                # NOTA: NO limpiar 'usuarios' - son los usuarios del tenant
                # NOTA: NO limpiar tablas de configuración
            ]
            
            for tabla in tablas_limpiar:
                try:
                    cursor.execute(f"DELETE FROM {tabla}")
                    print(f"   ✅ {tabla}: datos limpiados")
                except Exception as e:
                    print(f"   ⚠️  {tabla}: no se pudo limpiar - {e}")
            
            conn.commit()
            conn.close()
            print("✅ Limpieza completada")
            return True
            
        except Exception as e:
            print(f"❌ Error en limpieza: {e}")
            return False
    
    def verificar_limpieza(self):
        """Verificar que la limpieza fue exitosa"""
        print(f"\n🔍 VERIFICANDO LIMPIEZA DE {self.tenant_nombre}:")
        
        try:
            conn = sqlite3.connect(self.bd_tenant)
            cursor = conn.cursor()
            
            tablas_verificar = ['proveedor', 'activos_fijos', 'productos', 'clientes']
            
            for tabla in tablas_verificar:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                    count = cursor.fetchone()[0]
                    status = "✅ VACÍO" if count == 0 else "❌ TIENE DATOS"
                    print(f"   {status} {tabla}: {count} registros")
                except Exception as e:
                    print(f"   ⚠️  {tabla}: Error - {e}")
            
            # Verificar que los usuarios SÍ se mantienen
            try:
                cursor.execute("SELECT COUNT(*) FROM usuarios")
                count_usuarios = cursor.fetchone()[0]
                print(f"   ✅ usuarios: {count_usuarios} registros (se mantienen)")
                
                # Mostrar usuarios del tenant
                cursor.execute("SELECT username, rol FROM usuarios WHERE panaderia_id = ?", (self.tenant_id,))
                usuarios = cursor.fetchall()
                for usuario in usuarios:
                    print(f"      👤 {usuario[0]} ({usuario[1]})")
            except Exception as e:
                print(f"   ⚠️  usuarios: Error - {e}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error verificando limpieza: {e}")
            return False
    
    def ejecutar_limpieza_segura(self):
        """Ejecutar limpieza completa de forma segura"""
        print("🚀 LIMPIEZA SEGURA - TENANT NUEVO")
        print("=" * 50)
        print("SOLO se limpiará el tenant Norte (nuevo)")
        print("NO se tocarán: usuarios, configuración, estructura")
        print("=" * 50)
        
        # 1. Backup
        if not self.crear_backup():
            print("❌ No se pudo crear backup - cancelando")
            return False
        
        # 2. Verificar datos actuales
        self.verificar_datos_actuales()
        
        # 3. Confirmación
        respuesta = input(f"\n¿Continuar con la limpieza de {self.tenant_nombre}? (s/N): ").lower()
        if respuesta not in ['s', 'si', 'y', 'yes']:
            print("Limpieza cancelada.")
            return False
        
        # 4. Limpiar datos
        if self.limpiar_datos_tenant():
            # 5. Verificar resultado
            self.verificar_limpieza()
            print(f"\n🎉 ¡LIMPIEZA COMPLETADA EXITOSAMENTE!")
            print(f"✅ {self.tenant_nombre} ahora está VACÍO (como debe ser un tenant nuevo)")
            return True
        
        return False

def main():
    """Función principal"""
    print("🏪 SAAS - LIMPIEZA SEGURA DE TENANT NUEVO")
    print("Este script limpiará solo los datos del tenant Norte")
    print("=" * 50)
    
    limpiador = LimpiadorDatosTenant()
    if limpiador.ejecutar_limpieza_segura():
        print("\n🚀 PRÓXIMO PASO:")
        print("   1. Reiniciar la aplicación")
        print("   2. Acceder como admin_3 (tenant Norte)")
        print("   3. Verificar que los módulos están VACÍOS")
    else:
        print("\n❌ Limpieza no completada")

if __name__ == "__main__":
    main()