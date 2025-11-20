# corregir_modelos_sqlalchemy.py
import re
import os
from datetime import datetime

def crear_backup_models():
    """Crea backup seguro de models.py"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups_correccion_modelos"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    backup_path = os.path.join(backup_dir, f"models.py_{timestamp}.backup")
    
    with open('models.py', 'r', encoding='utf-8') as original:
        with open(backup_path, 'w', encoding='utf-8') as backup:
            backup.write(original.read())
    
    return backup_path

def corregir_modelo_proveedor():
    print("🔧 CORRIGIENDO MODELO PROVEEDOR")
    print("=" * 40)
    
    try:
        with open('models.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # Buscar la clase Proveedor
        inicio_proveedor = contenido.find('class Proveedor')
        if inicio_proveedor == -1:
            print("❌ No se encontró la clase Proveedor")
            return False
        
        # Encontrar el final de la clase Proveedor
        fin_proveedor = contenido.find('\nclass ', inicio_proveedor + 1)
        if fin_proveedor == -1:
            fin_proveedor = len(contenido)
        
        clase_proveedor = contenido[inicio_proveedor:fin_proveedor]
        
        # Verificar si ya tiene panaderia_id
        if 'panaderia_id' in clase_proveedor:
            print("✅ Proveedor ya tiene panaderia_id")
            return True
        
        # Encontrar donde agregar panaderia_id (después de id)
        pos_id = clase_proveedor.find('id = db.Column')
        if pos_id == -1:
            print("❌ No se encontró el campo id en Proveedor")
            return False
        
        # Encontrar el final de la línea id
        fin_linea_id = clase_proveedor.find('\n', pos_id)
        if fin_linea_id == -1:
            print("❌ No se pudo encontrar el fin de línea")
            return False
        
        # Insertar panaderia_id después de id
        nueva_linea = '\n    panaderia_id = db.Column(db.Integer, nullable=False, default=1)\n'
        clase_corregida = clase_proveedor[:fin_linea_id] + nueva_linea + clase_proveedor[fin_linea_id:]
        
        # Reemplazar en el contenido completo
        contenido_corregido = contenido[:inicio_proveedor] + clase_corregida + contenido[fin_proveedor:]
        
        with open('models.py', 'w', encoding='utf-8') as file:
            file.write(contenido_corregido)
        
        print("✅ Proveedor - panaderia_id agregado")
        return True
        
    except Exception as e:
        print(f"❌ Error corrigiendo Proveedor: {e}")
        return False

def corregir_modelo_activo_fijo():
    print("\n🔧 CORRIGIENDO MODELO ACTIVO FIJO")
    print("=" * 40)
    
    try:
        with open('models.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # Buscar la clase ActivoFijo
        inicio_activo = contenido.find('class ActivoFijo')
        if inicio_activo == -1:
            print("❌ No se encontró la clase ActivoFijo")
            return False
        
        # Encontrar el final de la clase ActivoFijo
        fin_activo = contenido.find('\nclass ', inicio_activo + 1)
        if fin_activo == -1:
            fin_activo = len(contenido)
        
        clase_activo = contenido[inicio_activo:fin_activo]
        
        # Verificar si ya tiene panaderia_id
        if 'panaderia_id' in clase_activo:
            print("✅ ActivoFijo ya tiene panaderia_id")
            return True
        
        # Encontrar donde agregar panaderia_id (después de id)
        pos_id = clase_activo.find('id = db.Column')
        if pos_id == -1:
            print("❌ No se encontró el campo id en ActivoFijo")
            return False
        
        # Encontrar el final de la línea id
        fin_linea_id = clase_activo.find('\n', pos_id)
        if fin_linea_id == -1:
            print("❌ No se pudo encontrar el fin de línea")
            return False
        
        # Insertar panaderia_id después de id
        nueva_linea = '\n    panaderia_id = db.Column(db.Integer, nullable=False, default=1)\n'
        clase_corregida = clase_activo[:fin_linea_id] + nueva_linea + clase_activo[fin_linea_id:]
        
        # Reemplazar en el contenido completo
        contenido_corregido = contenido[:inicio_activo] + clase_corregida + contenido[fin_activo:]
        
        with open('models.py', 'w', encoding='utf-8') as file:
            file.write(contenido_corregido)
        
        print("✅ ActivoFijo - panaderia_id agregado")
        return True
        
    except Exception as e:
        print(f"❌ Error corrigiendo ActivoFijo: {e}")
        return False

def corregir_modelo_registro_diario():
    print("\n🔧 CORRIGIENDO MODELO REGISTRO DIARIO")
    print("=" * 40)
    
    try:
        with open('models.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # Buscar la clase RegistroDiario
        inicio_registro = contenido.find('class RegistroDiario')
        if inicio_registro == -1:
            print("❌ No se encontró la clase RegistroDiario")
            return False
        
        # Encontrar el final de la clase
        fin_registro = contenido.find('\nclass ', inicio_registro + 1)
        if fin_registro == -1:
            fin_registro = len(contenido)
        
        clase_registro = contenido[inicio_registro:fin_registro]
        
        # Verificar si ya tiene panaderia_id
        if 'panaderia_id' in clase_registro:
            print("✅ RegistroDiario ya tiene panaderia_id")
            return True
        
        # Encontrar donde agregar panaderia_id (después de id)
        pos_id = clase_registro.find('id = db.Column')
        if pos_id == -1:
            print("❌ No se encontró el campo id en RegistroDiario")
            return False
        
        # Encontrar el final de la línea id
        fin_linea_id = clase_registro.find('\n', pos_id)
        if fin_linea_id == -1:
            print("❌ No se pudo encontrar el fin de línea")
            return False
        
        # Insertar panaderia_id después de id
        nueva_linea = '\n    panaderia_id = db.Column(db.Integer, nullable=False, default=1)\n'
        clase_corregida = clase_registro[:fin_linea_id] + nueva_linea + clase_registro[fin_linea_id:]
        
        # Reemplazar en el contenido completo
        contenido_corregido = contenido[:inicio_registro] + clase_corregida + contenido[fin_registro:]
        
        with open('models.py', 'w', encoding='utf-8') as file:
            file.write(contenido_corregido)
        
        print("✅ RegistroDiario - panaderia_id agregado")
        return True
        
    except Exception as e:
        print(f"❌ Error corrigiendo RegistroDiario: {e}")
        return False

def verificar_correcciones():
    print("\n🔍 VERIFICANDO CORRECCIONES EN MODELS.PY")
    print("=" * 40)
    
    try:
        with open('models.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        modelos_verificar = ['Proveedor', 'ActivoFijo', 'RegistroDiario']
        
        for modelo in modelos_verificar:
            if f'class {modelo}' in contenido:
                # Buscar la clase específica
                inicio = contenido.find(f'class {modelo}')
                fin = contenido.find('\nclass ', inicio + 1)
                if fin == -1:
                    fin = len(contenido)
                
                clase = contenido[inicio:fin]
                
                if 'panaderia_id = db.Column' in clase:
                    print(f"✅ {modelo} - CORREGIDO")
                else:
                    print(f"❌ {modelo} - SIN CORREGIR")
            else:
                print(f"⚠️  {modelo} - No encontrado")
                
    except Exception as e:
        print(f"❌ Error en verificación: {e}")

if __name__ == "__main__":
    print("🛡️  CORRECCIÓN DE MODELOS SQLALCHEMY")
    print("=" * 50)
    print("🔍 Este script agrega panaderia_id a los modelos:")
    print("   • Proveedor")
    print("   • ActivoFijo") 
    print("   • RegistroDiario")
    print("=" * 50)
    
    backup_path = crear_backup_models()
    print(f"💾 Backup creado: {backup_path}")
    
    continuar = input("\n¿Continuar con la corrección? (s/n): ").lower().strip()
    if continuar != 's':
        print("❌ Corrección cancelada")
        exit()
    
    exitos = 0
    exitos += corregir_modelo_proveedor()
    exitos += corregir_modelo_activo_fijo() 
    exitos += corregir_modelo_registro_diario()
    
    verificar_correcciones()
    
    print("\n" + "=" * 50)
    if exitos == 3:
        print("🎯 ¡TODOS LOS MODELOS CORREGIDOS!")
        print("🔄 Reinicia el servidor Flask para aplicar cambios")
    else:
        print(f"⚠️  {exitos}/3 modelos corregidos")
        print("🔧 Algunos modelos pueden necesitar corrección manual")
    
    print("\n📁 Backup guardado en:", backup_path)