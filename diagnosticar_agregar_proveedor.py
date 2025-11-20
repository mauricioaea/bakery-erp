# diagnosticar_agregar_proveedor.py
def diagnosticar_funcion_especifica():
    print("🔍 DIAGNÓSTICO ESPECÍFICO - agregar_proveedor")
    print("=" * 50)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # Buscar la función agregar_proveedor
        inicio = contenido.find('def agregar_proveedor():')
        if inicio == -1:
            print("❌ No se encontró la función agregar_proveedor")
            return
        
        fin = contenido.find('def ', inicio + 1)
        if fin == -1:
            fin = len(contenido)
        
        funcion = contenido[inicio:fin]
        
        print("📝 CÓDIGO COMPLETO DE agregar_proveedor:")
        print("=" * 40)
        print(funcion)
        print("=" * 40)
        
        # Analizar problemas específicos
        if 'panaderia_id=1' in funcion:
            print("\n🚨 PROBLEMAS ENCONTRADOS:")
            print("-" * 30)
            lineas = funcion.split('\n')
            for i, linea in enumerate(lineas, 1):
                if 'panaderia_id=1' in linea:
                    print(f"   Línea {i}: {linea.strip()}")
        
        if 'panaderia_actual = session.get' not in funcion:
            print("\n❌ FALTA: Obtención de panaderia_actual")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def corregir_agregar_proveedor_manual():
    """Corrección manual específica para agregar_proveedor"""
    print("\n🔧 CORRECCIÓN MANUAL DE agregar_proveedor")
    print("=" * 50)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            lineas = file.readlines()
        
        # Encontrar la función agregar_proveedor
        inicio_funcion = -1
        for i, linea in enumerate(lineas):
            if 'def agregar_proveedor():' in linea:
                inicio_funcion = i
                break
        
        if inicio_funcion == -1:
            print("❌ No se encontró la función")
            return False
        
        # Encontrar donde insertar panaderia_actual (después de docstring/comentarios)
        linea_insertar = inicio_funcion + 1
        while linea_insertar < len(lineas) and (
            lineas[linea_insertar].strip() == '' or 
            lineas[linea_insertar].strip().startswith('"""') or 
            lineas[linea_insertar].strip().startswith('#')
        ):
            linea_insertar += 1
        
        # Insertar obtención de panaderia_actual
        if linea_insertar < len(lineas):
            lineas.insert(linea_insertar, '    panaderia_actual = session.get(\'panaderia_id\', 1)\n')
            print("✅ Línea panaderia_actual insertada")
        
        # Buscar y corregir la creación del proveedor
        for i, linea in enumerate(lineas):
            if 'nuevo_proveedor = Proveedor(' in linea and 'panaderia_id' not in linea:
                # Reemplazar la línea
                lineas[i] = lineas[i].replace(
                    'nuevo_proveedor = Proveedor(',
                    'nuevo_proveedor = Proveedor(panaderia_id=panaderia_actual, '
                )
                print("✅ Creación de proveedor corregida")
        
        # Guardar cambios
        with open('app.py', 'w', encoding='utf-8') as file:
            file.writelines(lineas)
        
        print("💾 Cambios guardados")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    diagnosticar_funcion_especifica()
    
    print("\n⚠️  ¿Aplicar corrección manual?")
    confirmacion = input("¿Continuar? (s/N): ").lower().strip()
    
    if confirmacion == 's':
        exito = corregir_agregar_proveedor_manual()
        if exito:
            print("\n🎯 ¡Corrección aplicada! Reinicia el servidor y prueba.")
        else:
            print("\n❌ Error en la corrección")