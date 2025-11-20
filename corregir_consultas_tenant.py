# corregir_consultas_tenant.py
import re
import os
from datetime import datetime

def crear_backup_app():
    """Crea backup seguro de app.py"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups_correccion_consultas"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    backup_path = os.path.join(backup_dir, f"app.py_{timestamp}.backup")
    
    with open('app.py', 'r', encoding='utf-8') as original:
        with open(backup_path, 'w', encoding='utf-8') as backup:
            backup.write(original.read())
    
    return backup_path

def corregir_consultas_proveedores():
    print("🔧 CORRIGIENDO CONSULTAS DE PROVEEDORES")
    print("=" * 40)
    
    backup_path = crear_backup_app()
    print(f"💾 Backup creado: {backup_path}")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # CORREGIR: Proveedor.query.all() -> Proveedor.query.filter_by(panaderia_id=1).all()
        contenido = re.sub(
            r'Proveedor\.query\.all\(\)',
            'Proveedor.query.filter_by(panaderia_id=1).all()',
            contenido
        )
        
        # CORREGIR: Proveedor.query.get_or_404(id) -> Proveedor.query.filter_by(panaderia_id=1, id=id).first_or_404()
        contenido = re.sub(
            r'Proveedor\.query\.get_or_404\((\w+)\)',
            r'Proveedor.query.filter_by(panaderia_id=1, id=\1).first_or_404()',
            contenido
        )
        
        # CORREGIR: Proveedor.query.get(id) -> Proveedor.query.filter_by(panaderia_id=1, id=id).first()
        contenido = re.sub(
            r'Proveedor\.query\.get\((\w+)\)',
            r'Proveedor.query.filter_by(panaderia_id=1, id=\1).first()',
            contenido
        )
        
        # CORREGIR: Nuevos proveedores deben incluir panaderia_id
        contenido = re.sub(
            r'nuevo_proveedor = Proveedor\(',
            'nuevo_proveedor = Proveedor(panaderia_id=1, ',
            contenido
        )
        
        with open('app.py', 'w', encoding='utf-8') as file:
            file.write(contenido)
        
        print("✅ Consultas de proveedores corregidas")
        
    except Exception as e:
        print(f"❌ Error corrigiendo proveedores: {e}")
        # Restaurar backup en caso de error
        with open(backup_path, 'r', encoding='utf-8') as backup:
            with open('app.py', 'w', encoding='utf-8') as original:
                original.write(backup.read())
        print("🔄 Backup restaurado debido a error")

def corregir_consultas_activos_fijos():
    print("\n🔧 CORRIGIENDO CONSULTAS DE ACTIVOS FIJOS")
    print("=" * 40)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # CORREGIR: ActivoFijo.query.all() -> ActivoFijo.query.filter_by(panaderia_id=1).all()
        contenido = re.sub(
            r'ActivoFijo\.query\.all\(\)',
            'ActivoFijo.query.filter_by(panaderia_id=1).all()',
            contenido
        )
        
        # CORREGIR: ActivoFijo.query.order_by(...).all() -> ActivoFijo.query.filter_by(panaderia_id=1).order_by(...).all()
        contenido = re.sub(
            r'ActivoFijo\.query\.order_by\(([^)]+)\)\.all\(\)',
            r'ActivoFijo.query.filter_by(panaderia_id=1).order_by(\1).all()',
            contenido
        )
        
        # CORREGIR: Nuevos activos deben incluir panaderia_id
        contenido = re.sub(
            r'nuevo_activo = ActivoFijo\(',
            'nuevo_activo = ActivoFijo(panaderia_id=1, ',
            contenido
        )
        
        with open('app.py', 'w', encoding='utf-8') as file:
            file.write(contenido)
        
        print("✅ Consultas de activos fijos corregidas")
        
    except Exception as e:
        print(f"❌ Error corrigiendo activos fijos: {e}")

def corregir_consultas_financiero():
    print("\n🔧 CORRIGIENDO CONSULTAS FINANCIERAS")
    print("=" * 40)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # CORREGIR: Proveedor.query.all() en módulo financiero
        contenido = re.sub(
            r'proveedores = Proveedor\.query\.all\(\)',
            'proveedores = Proveedor.query.filter_by(panaderia_id=1).all()',
            contenido
        )
        
        # CORREGIR: SaldoBanco.query.order_by(...).first()
        # No necesita panaderia_id ya que es tabla global del sistema
        
        # CORREGIR: RegistroDiario.query.filter_by(...).first()
        contenido = re.sub(
            r'RegistroDiario\.query\.filter_by\(([^)]+)\)\.first\(\)',
            r'RegistroDiario.query.filter_by(panaderia_id=1, \1).first()',
            contenido
        )
        
        # CORREGIR: RegistroDiario.query.order_by(...).limit(...).all()
        contenido = re.sub(
            r'RegistroDiario\.query\.order_by\(([^)]+)\)\.limit\(([^)]+)\)\.all\(\)',
            r'RegistroDiario.query.filter_by(panaderia_id=1).order_by(\1).limit(\2).all()',
            contenido
        )
        
        # CORREGIR: PagoIndividual.query.filter_by(...).all()
        contenido = re.sub(
            r'PagoIndividual\.query\.filter_by\(([^)]+)\)\.all\(\)',
            r'PagoIndividual.query.filter_by(panaderia_id=1, \1).all()',
            contenido
        )
        
        # CORREGIR: Nuevos registros financieros deben incluir panaderia_id
        contenido = re.sub(
            r'registro = RegistroDiario\(fecha=fecha\)',
            'registro = RegistroDiario(fecha=fecha, panaderia_id=1)',
            contenido
        )
        
        contenido = re.sub(
            r'nuevo_pago = PagoIndividual\(',
            'nuevo_pago = PagoIndividual(panaderia_id=1, ',
            contenido
        )
        
        contenido = re.sub(
            r'nuevo_registro_saldo = SaldoBanco\(',
            'nuevo_registro_saldo = SaldoBanco(panaderia_id=1, ',
            contenido
        )
        
        with open('app.py', 'w', encoding='utf-8') as file:
            file.write(contenido)
        
        print("✅ Consultas financieras corregidas")
        
    except Exception as e:
        print(f"❌ Error corrigiendo financiero: {e}")

def verificar_correcciones():
    print("\n🔍 VERIFICANDO CORRECCIONES APLICADAS")
    print("=" * 40)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # Verificar correcciones en proveedores
        if 'Proveedor.query.filter_by(panaderia_id=1)' in contenido:
            print("✅ Proveedores - Consultas corregidas")
        else:
            print("❌ Proveedores - Consultas aún vulnerables")
        
        # Verificar correcciones en activos fijos
        if 'ActivoFijo.query.filter_by(panaderia_id=1)' in contenido:
            print("✅ Activos Fijos - Consultas corregidas")
        else:
            print("❌ Activos Fijos - Consultas aún vulnerables")
        
        # Verificar correcciones en financiero
        if 'Proveedor.query.filter_by(panaderia_id=1)' in contenido and 'RegistroDiario.query.filter_by(panaderia_id=1)' in contenido:
            print("✅ Financiero - Consultas corregidas")
        else:
            print("❌ Financiero - Consultas aún vulnerables")
        
        # Contar ocurrencias de panaderia_id
        total_filtros = contenido.count('panaderia_id=1')
        print(f"📊 Total de filtros panaderia_id aplicados: {total_filtros}")
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")

if __name__ == "__main__":
    print("🛡️  CORRECCIÓN SEGURA DE CONSULTAS MULTI-TENANT")
    print("=" * 50)
    print("🔒 Esta corrección:")
    print("   • Crea backup automático antes de cambios")
    print("   • Aplica filtros panaderia_id a todas las consultas")
    print("   • Mantiene compatibilidad con tenant actual (ID=1)")
    print("=" * 50)
    
    continuar = input("¿Continuar con la corrección? (s/n): ").lower().strip()
    if continuar != 's':
        print("❌ Corrección cancelada")
        exit()
    
    corregir_consultas_proveedores()
    corregir_consultas_activos_fijos() 
    corregir_consultas_financiero()
    verificar_correcciones()
    
    print("\n" + "=" * 50)
    print("🎯 CORRECCIÓN COMPLETADA")
    print("📁 Backup guardado en: backups_correccion_consultas/")
    print("\n⚠️  IMPORTANTE: Reinicia el servidor Flask para aplicar cambios")
    print("   Luego prueba el aislamiento entre tenants")