# corregir_proveedores_especifico.py
def corregir_funcion_proveedores():
    print("🔧 CORRECCIÓN ESPECÍFICA - FUNCIÓN proveedores()")
    print("=" * 50)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            lineas = file.readlines()
        
        # Buscar la función proveedores (línea ~1568)
        funcion_encontrada = False
        for i, linea in enumerate(lineas):
            if 'def proveedores():' in linea:
                funcion_encontrada = True
                print(f"✅ Función proveedores encontrada en línea {i+1}")
                
                # Buscar donde insertar panaderia_actual (después de docstring/comentarios)
                pos_insertar = i + 1
                while pos_insertar < len(lineas) and (
                    lineas[pos_insertar].strip() == '' or 
                    lineas[pos_insertar].strip().startswith('"""') or 
                    lineas[pos_insertar].strip().startswith('#') or
                    lineas[pos_insertar].strip().startswith('@')
                ):
                    pos_insertar += 1
                
                # Insertar la línea para obtener panaderia_actual
                if pos_insertar < len(lineas):
                    lineas.insert(pos_insertar, '    panaderia_actual = session.get(\'panaderia_id\', 1)\n')
                    print(f"✅ Línea insertada en posición {pos_insertar+1}")
                
                break
        
        if not funcion_encontrada:
            print("❌ No se encontró la función proveedores")
            return False
        
        # Guardar cambios
        with open('app.py', 'w', encoding='utf-8') as file:
            file.writelines(lineas)
        
        print("💾 Cambios guardados")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verificar_correccion():
    print("\n🔍 VERIFICANDO CORRECCIÓN")
    print("=" * 30)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # Buscar la función proveedores
        inicio = contenido.find('def proveedores():')
        if inicio == -1:
            print("❌ Función proveedores no encontrada")
            return False
        
        fin = contenido.find('def ', inicio + 1)
        if fin == -1:
            fin = len(contenido)
        
        funcion = contenido[inicio:fin]
        
        if 'panaderia_actual = session.get' in funcion:
            print("✅ Variable panaderia_actual definida correctamente")
            
            # Mostrar las primeras líneas de la función corregida
            lineas = funcion.split('\n')[:10]
            print("\n📝 Primeras líneas de la función:")
            for linea in lineas:
                print(f"   {linea}")
            
            return True
        else:
            print("❌ Variable panaderia_actual NO definida")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🛡️  CORRECCIÓN INMEDIATA - ERROR UnboundLocalError")
    print("=" * 60)
    
    print("🎯 Problema: panaderia_actual no definida en proveedores()")
    print("🔧 Solución: Agregar 'panaderia_actual = session.get(...)'")
    print("=" * 60)
    
    confirmacion = input("¿Aplicar corrección? (s/N): ").lower().strip()
    
    if confirmacion == 's':
        exito = corregir_funcion_proveedores()
        if exito:
            verificacion = verificar_correccion()
            if verificacion:
                print("\n🎯 ¡CORRECCIÓN APLICADA!")
                print("🔄 Reinicia el servidor y prueba el módulo proveedores")
            else:
                print("\n⚠️  La corrección no se verificó correctamente")
        else:
            print("\n❌ Error en la corrección")
    else:
        print("❌ Corrección cancelada")