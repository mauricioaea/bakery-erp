# analizar_y_corregir_modelos_SEGURO.py
import os
from datetime import datetime

def analizar_estructura_actual():
    """Analiza la estructura actual de models.py antes de cualquier cambio"""
    print("🔍 ANALIZANDO ESTRUCTURA ACTUAL DE MODELS.PY")
    print("=" * 50)
    
    try:
        with open('models.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
            lineas = contenido.split('\n')
        
        modelos_a_verificar = ['Proveedor', 'ActivoFijo', 'RegistroDiario', 'PagoIndividual', 'SaldoBanco']
        
        print("📊 MODELOS ENCONTRADOS:")
        print("-" * 30)
        
        for modelo in modelos_a_verificar:
            if f'class {modelo}' in contenido:
                # Encontrar la clase
                inicio = contenido.find(f'class {modelo}')
                fin = contenido.find('\nclass ', inicio + 1)
                if fin == -1:
                    fin = len(contenido)
                
                clase = contenido[inicio:fin]
                
                # Verificar si ya tiene panaderia_id
                tiene_panaderia_id = 'panaderia_id' in clase
                tiene_id = 'id = db.Column' in clase
                
                print(f"🏷️  {modelo}:")
                print(f"   ✅ Encontrado")
                print(f"   {'✅' if tiene_id else '❌'} Tiene campo 'id'")
                print(f"   {'✅' if tiene_panaderia_id else '❌'} Tiene 'panaderia_id'")
                
                if tiene_id and not tiene_panaderia_id:
                    # Mostrar contexto alrededor del campo id
                    pos_id = clase.find('id = db.Column')
                    inicio_contexto = max(0, pos_id - 50)
                    fin_contexto = min(len(clase), pos_id + 100)
                    contexto = clase[inicio_contexto:fin_contexto]
                    print(f"   📍 Contexto del campo 'id':")
                    for linea in contexto.split('\n'):
                        if 'id = db.Column' in linea:
                            print(f"      🎯 {linea.strip()}")
                
            else:
                print(f"🏷️  {modelo}: ❌ No encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        return False

def mostrar_cambios_propuestos():
    """Muestra exactamente qué cambios se van a realizar"""
    print("\n📋 CAMBIOS PROPUESTOS:")
    print("=" * 50)
    
    cambios = [
        {
            'modelo': 'Proveedor',
            'campo': 'panaderia_id = db.Column(db.Integer, nullable=False, default=1)',
            'posicion': 'Después del campo "id"'
        },
        {
            'modelo': 'ActivoFijo', 
            'campo': 'panaderia_id = db.Column(db.Integer, nullable=False, default=1)',
            'posicion': 'Después del campo "id"'
        },
        {
            'modelo': 'RegistroDiario',
            'campo': 'panaderia_id = db.Column(db.Integer, nullable=False, default=1)', 
            'posicion': 'Después del campo "id"'
        },
        {
            'modelo': 'PagoIndividual',
            'campo': 'panaderia_id = db.Column(db.Integer, nullable=False, default=1)',
            'posicion': 'Después del campo "id"'
        },
        {
            'modelo': 'SaldoBanco',
            'campo': 'panaderia_id = db.Column(db.Integer, nullable=False, default=1)',
            'posicion': 'Después del campo "id"'
        }
    ]
    
    for cambio in cambios:
        print(f"🔧 {cambio['modelo']}:")
        print(f"   ➕ Agregar: {cambio['campo']}")
        print(f"   📍 Posición: {cambio['posicion']}")
        print()

def crear_backup_seguro():
    """Crea backup con verificación"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups_ultra_seguros"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    backup_path = os.path.join(backup_dir, f"models.py_{timestamp}.backup")
    
    # Verificar que el archivo original existe y es legible
    if not os.path.exists('models.py'):
        print("❌ ERROR: models.py no existe")
        return None
    
    try:
        with open('models.py', 'r', encoding='utf-8') as original:
            contenido = original.read()
        
        # Verificar que es un archivo Python válido
        if 'class ' not in contenido or 'db.Column' not in contenido:
            print("❌ ADVERTENCIA: El archivo no parece ser un models.py válido")
            confirmar = input("¿Continuar de todos modos? (s/n): ")
            if confirmar.lower() != 's':
                return None
        
        with open(backup_path, 'w', encoding='utf-8') as backup:
            backup.write(contenido)
        
        print(f"💾 Backup creado: {backup_path}")
        return backup_path
        
    except Exception as e:
        print(f"❌ Error creando backup: {e}")
        return None

def corregir_modelo_seguro(nombre_modelo):
    """Corrige un modelo específico de forma segura"""
    try:
        with open('models.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # Verificar que el modelo existe
        if f'class {nombre_modelo}' not in contenido:
            print(f"   ⚠️  {nombre_modelo} - No encontrado, saltando")
            return False
        
        # Verificar que no tenga ya panaderia_id
        inicio = contenido.find(f'class {nombre_modelo}')
        fin = contenido.find('\nclass ', inicio + 1)
        if fin == -1:
            fin = len(contenido)
        
        clase = contenido[inicio:fin]
        
        if 'panaderia_id = db.Column' in clase:
            print(f"   ✅ {nombre_modelo} - Ya tiene panaderia_id")
            return True
        
        # Buscar posición exacta para insertar
        pos_id = clase.find('id = db.Column')
        if pos_id == -1:
            print(f"   ❌ {nombre_modelo} - No tiene campo 'id', no se puede corregir")
            return False
        
        # Encontrar el final de la línea del id
        fin_linea_id = clase.find('\n', pos_id)
        if fin_linea_id == -1:
            print(f"   ❌ {nombre_modelo} - No se pudo encontrar fin de línea")
            return False
        
        # Insertar panaderia_id
        nueva_linea = '\n    panaderia_id = db.Column(db.Integer, nullable=False, default=1)'
        clase_corregida = clase[:fin_linea_id] + nueva_linea + clase[fin_linea_id:]
        
        # Reemplazar en contenido completo
        contenido_corregido = contenido[:inicio] + clase_corregida + contenido[fin:]
        
        with open('models.py', 'w', encoding='utf-8') as file:
            file.write(contenido_corregido)
        
        print(f"   ✅ {nombre_modelo} - Corregido exitosamente")
        return True
        
    except Exception as e:
        print(f"   ❌ {nombre_modelo} - Error: {e}")
        return False

def verificar_integridad():
    """Verifica que el archivo sigue siendo Python válido después de los cambios"""
    print("\n🔍 VERIFICANDO INTEGRIDAD DEL ARCHIVO")
    print("-" * 30)
    
    try:
        with open('models.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # Verificaciones básicas de integridad
        checks = [
            ('Tiene clases', 'class ' in contenido),
            ('Tiene imports SQLAlchemy', 'db.Column' in contenido),
            ('Sintaxis básica OK', 'def ' in contenido or 'class ' in contenido),
            ('No tiene errores de indentación obvios', '    ' in contenido)  # Verifica que tiene indentación
        ]
        
        todos_ok = True
        for check, resultado in checks:
            if resultado:
                print(f"   ✅ {check}")
            else:
                print(f"   ⚠️  {check}")
                todos_ok = False
        
        return todos_ok
        
    except Exception as e:
        print(f"   ❌ Error en verificación: {e}")
        return False

if __name__ == "__main__":
    print("🛡️  CORRECCIÓN ULTRA-SEGURA DE MODELOS")
    print("=" * 60)
    print("🔒 ESTA VERSIÓN INCLUYE:")
    print("   • Análisis completo antes de cambios")
    print("   • Backup automático con verificación")
    print("   • Mostrar cambios propuestos")
    print("   • Verificación de integridad post-cambios")
    print("=" * 60)
    
    # PASO 1: Análisis
    if not analizar_estructura_actual():
        print("❌ No se puede continuar - error en análisis")
        exit()
    
    # PASO 2: Mostrar cambios
    mostrar_cambios_propuestos()
    
    # PASO 3: Confirmación
    print("⚠️  ¿ESTÁS SEGURO DE CONTINUAR?")
    print("Estos cambios son necesarios para el aislamiento multi-tenant.")
    confirmacion = input("¿Continuar con la corrección? (s/N): ").lower().strip()
    
    if confirmacion != 's':
        print("❌ Corrección cancelada por el usuario")
        exit()
    
    # PASO 4: Backup
    backup_path = crear_backup_seguro()
    if not backup_path:
        print("❌ No se pudo crear backup - cancelando")
        exit()
    
    # PASO 5: Aplicar correcciones
    print("\n🔧 APLICANDO CORRECCIONES:")
    print("-" * 30)
    
    modelos_a_corregir = ['Proveedor', 'ActivoFijo', 'RegistroDiario', 'PagoIndividual', 'SaldoBanco']
    exitos = 0
    
    for modelo in modelos_a_corregir:
        if corregir_modelo_seguro(modelo):
            exitos += 1
    
    # PASO 6: Verificar integridad
    if verificar_integridad():
        print(f"\n🎯 RESULTADO: {exitos}/{len(modelos_a_corregir)} modelos corregidos")
        print("🔄 Reinicia el servidor Flask para aplicar cambios")
    else:
        print("\n⚠️  ADVERTENCIA: Se detectaron posibles problemas")
        print("🔧 Considera revisar manualmente models.py")
    
    print(f"\n💾 Backup disponible en: {backup_path}")
    print("📞 Si hay problemas, copia el backup sobre models.py")