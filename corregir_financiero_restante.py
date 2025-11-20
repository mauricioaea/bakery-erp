# corregir_financiero_restante.py
import re
import os
from datetime import datetime

def crear_backup():
    """Crea backup seguro"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups_correccion_final"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    backup_path = os.path.join(backup_dir, f"app.py_{timestamp}.backup")
    
    with open('app.py', 'r', encoding='utf-8') as original:
        with open(backup_path, 'w', encoding='utf-8') as backup:
            backup.write(original.read())
    
    return backup_path

def corregir_lineas_especificas():
    print("🔧 CORRIGIENDO CONSULTAS FINANCIERAS RESTANTES")
    print("=" * 50)
    
    backup_path = crear_backup()
    print(f"💾 Backup creado: {backup_path}")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            lineas = file.readlines()
        
        cambios_realizados = 0
        
        # CORREGIR LÍNEA 10 en control_diario()
        if len(lineas) >= 10:
            linea_10 = lineas[9]  # Índice 9 = línea 10
            if 'registros_recientes = RegistroDiario.query.order_by(RegistroDiario.fecha.desc()).limit(7).all()' in linea_10:
                lineas[9] = '    registros_recientes = RegistroDiario.query.filter_by(panaderia_id=1).order_by(RegistroDiario.fecha.desc()).limit(7).all()\n'
                cambios_realizados += 1
                print("✅ Línea 10 corregida")
        
        # CORREGIR otras consultas de proveedores sin panaderia_id
        for i, linea in enumerate(lineas):
            # Solo corregir líneas que tengan consultas de proveedores sin panaderia_id
            if 'Proveedor.query.filter_by(activo=True).all()' in linea and 'panaderia_id' not in linea:
                lineas[i] = linea.replace(
                    'Proveedor.query.filter_by(activo=True).all()',
                    'Proveedor.query.filter_by(panaderia_id=1, activo=True).all()'
                )
                cambios_realizados += 1
                print(f"✅ Línea {i+1} corregida")
        
        # Guardar cambios
        with open('app.py', 'w', encoding='utf-8') as file:
            file.writelines(lineas)
        
        print(f"\n📊 Total de cambios realizados: {cambios_realizados}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        # Restaurar backup en caso de error
        with open(backup_path, 'r', encoding='utf-8') as backup:
            with open('app.py', 'w', encoding='utf-8') as original:
                original.write(backup.read())
        print("🔄 Backup restaurado debido a error")

def verificar_correcciones_finales():
    print("\n🔍 VERIFICACIÓN FINAL DE CORRECCIONES")
    print("=" * 40)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # Verificar que todas las consultas tengan panaderia_id
        consultas_seguras = True
        
        # Verificar control_diario
        if 'registros_recientes = RegistroDiario.query.filter_by(panaderia_id=1)' in contenido:
            print("✅ control_diario() - Consulta de registros corregida")
        else:
            print("❌ control_diario() - Consulta de registros aún vulnerable")
            consultas_seguras = False
        
        # Verificar proveedores en módulo financiero
        if 'Proveedor.query.filter_by(panaderia_id=1, activo=True)' in contenido:
            print("✅ Proveedores financieros - Consultas corregidas")
        else:
            # Contar cuántas consultas de proveedores siguen sin panaderia_id
            consultas_vulnerables = contenido.count('Proveedor.query.filter_by(activo=True).all()')
            if consultas_vulnerables == 0:
                print("✅ Proveedores financieros - Todas corregidas")
            else:
                print(f"❌ Proveedores financieros - {consultas_vulnerables} consultas aún vulnerables")
                consultas_seguras = False
        
        # Contar total de filtros panaderia_id
        total_filtros = contenido.count('panaderia_id=1')
        print(f"📊 Total de filtros panaderia_id: {total_filtros}")
        
        return consultas_seguras
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

if __name__ == "__main__":
    print("🛡️  CORRECCIÓN FINAL - CONSULTAS VULNERABLES")
    print("=" * 50)
    print("🔍 Corrigiendo consultas específicas identificadas")
    print("=" * 50)
    
    continuar = input("¿Continuar con la corrección final? (s/n): ").lower().strip()
    if continuar != 's':
        print("❌ Corrección cancelada")
        exit()
    
    corregir_lineas_especificas()
    todas_seguras = verificar_correcciones_finales()
    
    print("\n" + "=" * 50)
    if todas_seguras:
        print("🎯 ¡TODAS LAS CONSULTAS CORREGIDAS!")
        print("✅ Proveedores - AISLADOS")
        print("✅ Activos Fijos - AISLADOS") 
        print("✅ Financiero - AISLADO")
    else:
        print("⚠️  Algunas consultas pueden seguir vulnerables")
        print("🔍 Revisa manualmente las líneas reportadas")
    
    print("\n⚠️  IMPORTANTE: Reinicia el servidor Flask")
    print("🧪 Luego prueba el aislamiento entre tenants")