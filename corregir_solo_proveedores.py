# corregir_solo_proveedores.py
import re
import os
from datetime import datetime

def crear_backup_seguro():
    """Crea backup con timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups_modulo_proveedores"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    backup_path = os.path.join(backup_dir, f"app.py_{timestamp}.backup")
    
    with open('app.py', 'r', encoding='utf-8') as original:
        with open(backup_path, 'w', encoding='utf-8') as backup:
            backup.write(original.read())
    
    return backup_path

def analizar_modulo_proveedores():
    """Analiza solo las funciones del módulo proveedores"""
    print("🔍 ANÁLISIS DEL MÓDULO PROVEEDORES")
    print("=" * 50)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # Buscar todas las funciones de proveedores
        funciones_proveedores = [
            'proveedores',
            'agregar_proveedor', 
            'editar_proveedor',
            'toggle_proveedor'
        ]
        
        print("📋 FUNCIONES DE PROVEEDORES:")
        print("-" * 30)
        
        for funcion in funciones_proveedores:
            inicio = contenido.find(f'def {funcion}():')
            if inicio == -1:
                print(f"   ⚠️  {funcion} - No encontrada")
                continue
            
            fin = contenido.find('def ', inicio + 1)
            if fin == -1:
                fin = len(contenido)
            
            codigo_funcion = contenido[inicio:fin]
            
            # Analizar consultas en esta función
            consultas = re.findall(r'Proveedor\.query\.[^(]*\([^)]*\)', codigo_funcion)
            
            print(f"   🔍 {funcion}:")
            for consulta in consultas:
                if 'panaderia_id=1' in consulta:
                    print(f"      ❌ {consulta.strip()} - HARDCODEADO")
                elif 'panaderia_id' in consulta:
                    print(f"      ✅ {consulta.strip()} - Con filtro")
                else:
                    print(f"      ⚠️  {consulta.strip()} - Sin filtro")
        
        return funciones_proveedores
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def corregir_modulo_proveedores():
    """Corrige SOLO el módulo proveedores"""
    print("\n🔧 CORRIGIENDO MÓDULO PROVEEDORES")
    print("=" * 50)
    
    backup_path = crear_backup_seguro()
    print(f"💾 Backup creado: {backup_path}")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # Reemplazar consultas hardcodeadas en funciones de proveedores
        cambios_realizados = 0
        
        # 1. Reemplazar panaderia_id=1 por panaderia_actual
        contenido = contenido.replace(
            'Proveedor.query.filter_by(panaderia_id=1)',
            'Proveedor.query.filter_by(panaderia_id=panaderia_actual)'
        )
        cambios_realizados += contenido.count('panaderia_id=panaderia_actual')
        
        # 2. Agregar obtención de panaderia_actual a cada función
        funciones_proveedores = ['proveedores', 'agregar_proveedor', 'editar_proveedor', 'toggle_proveedor']
        
        for funcion in funciones_proveedores:
            # Buscar la función
            inicio = contenido.find(f'def {funcion}():')
            if inicio == -1:
                continue
            
            # Buscar el inicio del cuerpo de la función (después de docstring/comentarios)
            cuerpo_inicio = contenido.find('\n', inicio) + 1
            while cuerpo_inicio < len(contenido) and contenido[cuerpo_inicio] in ['\n', ' ', '\t', '#', '"']:
                cuerpo_inicio = contenido.find('\n', cuerpo_inicio) + 1
            
            # Insertar la línea para obtener panaderia_actual
            if cuerpo_inicio < len(contenido):
                linea_panaderia = '    panaderia_actual = session.get(\'panaderia_id\', 1)\n'
                contenido = contenido[:cuerpo_inicio] + linea_panaderia + contenido[cuerpo_inicio:]
                cambios_realizados += 1
        
        # Guardar cambios
        with open('app.py', 'w', encoding='utf-8') as file:
            file.write(contenido)
        
        print(f"✅ Cambios realizados: {cambios_realizados}")
        print("💾 Módulo proveedores corregido")
        
        return cambios_realizados > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        # Restaurar backup en caso de error
        with open(backup_path, 'r', encoding='utf-8') as backup:
            with open('app.py', 'w', encoding='utf-8') as original:
                original.write(backup.read())
        print("🔄 Backup restaurado debido a error")
        return False

def verificar_correccion_proveedores():
    """Verifica que la corrección se aplicó correctamente"""
    print("\n🔍 VERIFICANDO CORRECCIÓN")
    print("=" * 30)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # Verificar que no hay panaderia_id=1 en funciones de proveedores
        funciones_proveedores = ['def proveedores():', 'def agregar_proveedor():', 'def editar_proveedor():', 'def toggle_proveedor():']
        
        todo_correcto = True
        for funcion in funciones_proveedores:
            inicio = contenido.find(funcion)
            if inicio == -1:
                continue
            
            fin = contenido.find('def ', inicio + 1)
            if fin == -1:
                fin = len(contenido)
            
            codigo_funcion = contenido[inicio:fin]
            
            if 'panaderia_id=1' in codigo_funcion:
                print(f"   ❌ {funcion} - Aún tiene panaderia_id=1")
                todo_correcto = False
            elif 'panaderia_actual = session.get' in codigo_funcion:
                print(f"   ✅ {funcion} - Corregida correctamente")
            else:
                print(f"   ⚠️  {funcion} - Sin cambios detectados")
        
        return todo_correcto
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🛡️  CORRECCIÓN SEGURA - SOLO MÓDULO PROVEEDORES")
    print("=" * 60)
    print("🎯 Estrategia: Corregir UN módulo, probar, luego continuar")
    print("=" * 60)
    
    # Análisis
    funciones = analizar_modulo_proveedores()
    
    if not funciones:
        print("❌ No se encontraron funciones de proveedores")
        exit()
    
    # Confirmación
    print(f"\n⚠️  ¿CORREGIR SOLO {len(funciones)} FUNCIONES DE PROVEEDORES?")
    confirmacion = input("¿Continuar? (s/N): ").lower().strip()
    
    if confirmacion != 's':
        print("❌ Corrección cancelada")
        exit()
    
    # Corrección
    exito = corregir_modulo_proveedores()
    verificacion = verificar_correccion_proveedores()
    
    if exito and verificacion:
        print("\n🎯 ¡MÓDULO PROVEEDORES CORREGIDO!")
        print("🔄 Reinicia el servidor y prueba:")
        print("   • Login como admin_2 - Crear proveedor 'Proveedor Norte'")
        print("   • Login como admin_3 - Verificar que NO ves 'Proveedor Norte'")
        print("   • Si funciona, continuamos con el siguiente módulo")
    else:
        print("\n⚠️  Problemas en la corrección - Revisar manualmente")
    
    print(f"\n💾 Backup disponible en: backups_modulo_proveedores/")