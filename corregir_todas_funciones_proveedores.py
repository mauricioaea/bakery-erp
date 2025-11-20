# corregir_todas_funciones_proveedores.py
def corregir_funcion_proveedores():
    """Corrige la función principal proveedores()"""
    print("🔧 CORRIGIENDO FUNCIÓN proveedores()")
    print("=" * 40)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            lineas = file.readlines()
        
        # Buscar la función proveedores
        for i, linea in enumerate(lineas):
            if 'def proveedores():' in linea:
                print(f"✅ Función proveedores encontrada en línea {i+1}")
                
                # Buscar donde insertar panaderia_actual
                pos_insertar = i + 1
                while pos_insertar < len(lineas) and (
                    lineas[pos_insertar].strip() == '' or 
                    lineas[pos_insertar].strip().startswith('"""') or 
                    lineas[pos_insertar].strip().startswith('#') or
                    lineas[pos_insertar].strip().startswith('@')
                ):
                    pos_insertar += 1
                
                # Insertar la línea
                if pos_insertar < len(lineas):
                    lineas.insert(pos_insertar, '    panaderia_actual = session.get(\'panaderia_id\', 1)\n')
                    print(f"✅ panaderia_actual insertada en línea {pos_insertar+1}")
                
                break
        
        # Guardar cambios
        with open('app.py', 'w', encoding='utf-8') as file:
            file.writelines(lineas)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def corregir_agregar_proveedor():
    """Corrige la función agregar_proveedor()"""
    print("\n🔧 CORRIGIENDO FUNCIÓN agregar_proveedor()")
    print("=" * 40)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # Buscar y corregir la función agregar_proveedor
        inicio = contenido.find('def agregar_proveedor():')
        if inicio == -1:
            print("❌ Función agregar_proveedor no encontrada")
            return False
        
        # Encontrar el final de la función
        fin = contenido.find('@app.route', inicio + 1)
        if fin == -1:
            fin = len(contenido)
        
        funcion_actual = contenido[inicio:fin]
        
        # CORREGIR PROBLEMA 1: Remover línea duplicada después del return
        if 'return render_template' in funcion_actual and 'panaderia_actual = session.get' in funcion_actual:
            # Dividir en líneas y remover la línea duplicada
            lineas_funcion = funcion_actual.split('\n')
            lineas_corregidas = []
            encontro_return = False
            
            for linea in lineas_funcion:
                if 'return render_template' in linea:
                    encontro_return = True
                    lineas_corregidas.append(linea)
                elif encontro_return and 'panaderia_actual = session.get' in linea:
                    # Saltar esta línea (código inalcanzable)
                    continue
                else:
                    lineas_corregidas.append(linea)
            
            funcion_corregida = '\n'.join(lineas_corregidas)
            
            # CORREGIR PROBLEMA 2: Cambiar panaderia_id=1 por panaderia_actual
            funcion_corregida = funcion_corregida.replace(
                'nuevo_proveedor = Proveedor(panaderia_id=1,',
                'nuevo_proveedor = Proveedor(panaderia_id=panaderia_actual,'
            )
            
            # Reemplazar en el contenido completo
            contenido_corregido = contenido[:inicio] + funcion_corregida + contenido[fin:]
            
            with open('app.py', 'w', encoding='utf-8') as file:
                file.write(contenido_corregido)
            
            print("✅ Línea duplicada removida y panaderia_id corregido")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def corregir_editar_toggle_proveedor():
    """Corrige editar_proveedor y toggle_proveedor"""
    print("\n🔧 CORRIGIENDO editar_proveedor() y toggle_proveedor()")
    print("=" * 40)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        cambios = 0
        
        # CORREGIR PROBLEMA 3: Agregar panaderia_actual a editar_proveedor
        inicio_editar = contenido.find('def editar_proveedor(id):')
        if inicio_editar != -1:
            # Buscar donde insertar en editar_proveedor
            fin_busqueda = contenido.find('def ', inicio_editar + 1)
            if fin_busqueda == -1:
                fin_busqueda = len(contenido)
            
            funcion_editar = contenido[inicio_editar:fin_busqueda]
            
            if 'panaderia_actual = session.get' not in funcion_editar:
                # Insertar después de la definición de función
                pos_insertar = contenido.find('\n', inicio_editar) + 1
                while pos_insertar < len(contenido) and contenido[pos_insertar] in ['\n', ' ', '\t', '#', '"']:
                    pos_insertar = contenido.find('\n', pos_insertar) + 1
                
                if pos_insertar < len(contenido):
                    contenido = contenido[:pos_insertar] + '    panaderia_actual = session.get(\'panaderia_id\', 1)\n' + contenido[pos_insertar:]
                    cambios += 1
                    print("✅ panaderia_actual agregada a editar_proveedor")
            
            # Cambiar panaderia_id=1 por panaderia_actual
            contenido = contenido.replace(
                'proveedor = Proveedor.query.filter_by(panaderia_id=1, id=id).first_or_404()',
                'proveedor = Proveedor.query.filter_by(panaderia_id=panaderia_actual, id=id).first_or_404()'
            )
            cambios += 1
        
        # CORREGIR PROBLEMA 4: Agregar panaderia_actual a toggle_proveedor
        inicio_toggle = contenido.find('def toggle_proveedor(id):')
        if inicio_toggle != -1:
            # Buscar donde insertar en toggle_proveedor
            fin_busqueda = contenido.find('def ', inicio_toggle + 1)
            if fin_busqueda == -1:
                fin_busqueda = len(contenido)
            
            funcion_toggle = contenido[inicio_toggle:fin_busqueda]
            
            if 'panaderia_actual = session.get' not in funcion_toggle:
                # Insertar después de la definición de función
                pos_insertar = contenido.find('\n', inicio_toggle) + 1
                while pos_insertar < len(contenido) and contenido[pos_insertar] in ['\n', ' ', '\t', '#', '"']:
                    pos_insertar = contenido.find('\n', pos_insertar) + 1
                
                if pos_insertar < len(contenido):
                    contenido = contenido[:pos_insertar] + '    panaderia_actual = session.get(\'panaderia_id\', 1)\n' + contenido[pos_insertar:]
                    cambios += 1
                    print("✅ panaderia_actual agregada a toggle_proveedor")
            
            # Cambiar panaderia_id=1 por panaderia_actual
            contenido = contenido.replace(
                'proveedor = Proveedor.query.filter_by(panaderia_id=1, id=id).first_or_404()',
                'proveedor = Proveedor.query.filter_by(panaderia_id=panaderia_actual, id=id).first_or_404()'
            )
            cambios += 1
        
        if cambios > 0:
            with open('app.py', 'w', encoding='utf-8') as file:
                file.write(contenido)
            print(f"✅ Total de cambios: {cambios}")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verificar_correcciones():
    print("\n🔍 VERIFICANDO CORRECCIONES")
    print("=" * 30)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        funciones = [
            'def proveedores():',
            'def agregar_proveedor():', 
            'def editar_proveedor(id):',
            'def toggle_proveedor(id):'
        ]
        
        todas_correctas = True
        
        for funcion in funciones:
            inicio = contenido.find(funcion)
            if inicio == -1:
                print(f"❌ {funcion} - No encontrada")
                todas_correctas = False
                continue
            
            fin = contenido.find('def ', inicio + 1)
            if fin == -1:
                fin = len(contenido)
            
            codigo_funcion = contenido[inicio:fin]
            
            if 'panaderia_actual = session.get' in codigo_funcion:
                print(f"✅ {funcion} - Variable definida")
            else:
                print(f"❌ {funcion} - Variable NO definida")
                todas_correctas = False
            
            if 'panaderia_id=1' in codigo_funcion:
                print(f"❌ {funcion} - Aún tiene panaderia_id=1")
                todas_correctas = False
            else:
                print(f"✅ {funcion} - Sin panaderia_id=1")
        
        return todas_correctas
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🛡️  CORRECCIÓN COMPLETA - MÓDULO PROVEEDORES")
    print("=" * 60)
    
    print("🎯 Corrigiendo TODAS las funciones del módulo proveedores")
    print("=" * 60)
    
    confirmacion = input("¿Aplicar corrección completa? (s/N): ").lower().strip()
    
    if confirmacion == 's':
        # Aplicar todas las correcciones
        c1 = corregir_funcion_proveedores()
        c2 = corregir_agregar_proveedor() 
        c3 = corregir_editar_toggle_proveedor()
        
        # Verificar
        verificacion = verificar_correcciones()
        
        if verificacion:
            print("\n🎯 ¡TODAS LAS FUNCIONES CORREGIDAS!")
            print("🔄 Reinicia el servidor y prueba el módulo proveedores")
        else:
            print("\n⚠️  Algunas funciones pueden necesitar corrección manual")
    else:
        print("❌ Corrección cancelada")