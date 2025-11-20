# verificar_rutas_problematicas.py
import re
import sys

def analizar_rutas_app():
    print("🔍 ANALIZANDO RUTAS PROBLEMÁTICAS EN app.py")
    print("=" * 60)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # Definir las rutas problemáticas a buscar
        rutas_problematicas = [
            '/proveedores',
            '/activos', 
            '/financiero',
            '/reportes'
        ]
        
        # También buscar variaciones
        patrones_rutas = [
            r'@app\.route\([\'"](/proveedores[^\'"]*)[\'"]',
            r'@app\.route\([\'"](/activos[^\'"]*)[\'"]',
            r'@app\.route\([\'"](/financiero[^\'"]*)[\'"]', 
            r'@app\.route\([\'"](/reportes[^\'"]*)[\'"]',
            r'@app\.route\([\'"](/gestion_financiera[^\'"]*)[\'"]'
        ]
        
        print("📋 BUSCANDO RUTAS PROBLEMÁTICAS...")
        print("-" * 50)
        
        rutas_encontradas = []
        
        for patron in patrones_rutas:
            matches = re.finditer(patron, contenido, re.IGNORECASE)
            for match in matches:
                ruta = match.group(1)
                rutas_encontradas.append(ruta)
                print(f"📍 Ruta encontrada: {ruta}")
                
                # Encontrar la función asociada a esta ruta
                inicio_ruta = match.start()
                # Buscar la definición de función después de esta ruta
                funcion_patron = r'def\s+(\w+)\s*\('
                funcion_match = re.search(funcion_patron, contenido[inicio_ruta:inicio_ruta+1000])
                
                if funcion_match:
                    nombre_funcion = funcion_match.group(1)
                    print(f"   🏷️  Función: {nombre_funcion}")
                    
                    # Buscar consultas SQL en esta función
                    analizar_consultas_sql(contenido, inicio_ruta, nombre_funcion)
        
        print("\n" + "=" * 60)
        print("🔎 BUSCANDO CONSULTAS SQL ESPECÍFICAS...")
        print("-" * 50)
        
        # Buscar consultas SQL genéricas sin panaderia_id
        consultas_sin_filtro = [
            r'SELECT\s+\*\s+FROM\s+(\w+)(?!.*WHERE.*panaderia_id)',
            r'SELECT.*FROM\s+(\w+)(?!.*WHERE.*panaderia_id)',
            r'db\.session\.query\([^)]+\)(?!.*filter.*panaderia_id)'
        ]
        
        for patron in consultas_sin_filtro:
            matches = re.finditer(patron, contenido, re.IGNORECASE | re.DOTALL)
            for match in matches:
                print(f"🚨 POSIBLE CONSULTA SIN FILTRO:")
                contexto = contenido[max(0, match.start()-100):match.end()+100]
                lineas = contexto.split('\n')
                for linea in lineas:
                    if match.group(0) in linea:
                        print(f"   ❌ {linea.strip()}")
        
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE VULNERABILIDADES ENCONTRADAS")
        print("-" * 50)
        
        # Contar ocurrencias de panaderia_id
        total_panaderia_id = len(re.findall(r'panaderia_id', contenido, re.IGNORECASE))
        print(f"🔢 Total de 'panaderia_id' en app.py: {total_panaderia_id}")
        
        # Verificar módulos específicos
        modulos_verificar = ['proveedor', 'activo', 'financiero', 'reporte']
        for modulo in modulos_verificar:
            patron_modulo = rf'{modulo}.*panaderia_id'
            tiene_filtro = len(re.findall(patron_modulo, contenido, re.IGNORECASE)) > 0
            if tiene_filtro:
                print(f"✅ {modulo.upper()}: TIENE filtros panaderia_id")
            else:
                print(f"❌ {modulo.upper()}: NO TIENE filtros panaderia_id")
                
    except Exception as e:
        print(f"❌ Error analizando app.py: {e}")

def analizar_consultas_sql(contenido, inicio_ruta, nombre_funcion):
    """Analiza consultas SQL en una función específica"""
    
    # Encontrar el bloque de la función
    funcion_patron = rf'def\s+{nombre_funcion}\s*\([^)]*\):'
    funcion_match = re.search(funcion_patron, contenido)
    
    if funcion_match:
        inicio_funcion = funcion_match.start()
        # Buscar el final de la función (próxima def o EOF)
        next_func = re.search(r'\ndef\s+\w+\s*\(', contenido[inicio_funcion+50:])
        
        if next_func:
            fin_funcion = inicio_funcion + 50 + next_func.start()
        else:
            fin_funcion = len(contenido)
            
        codigo_funcion = contenido[inicio_funcion:fin_funcion]
        
        print(f"   📝 Analizando función {nombre_funcion}...")
        
        # Buscar consultas SELECT
        selects = re.findall(r'SELECT.*?FROM.*?(?:WHERE|$)', codigo_funcion, re.IGNORECASE | re.DOTALL)
        for select in selects[:3]:  # Mostrar solo las primeras 3
            if 'panaderia_id' in select.lower():
                print(f"      ✅ CONSULTA SEGURA (con panaderia_id)")
            else:
                print(f"      🚨 CONSULTA VULNERABLE (sin panaderia_id)")
                # Mostrar línea específica
                lineas = select.split('\n')
                for linea in lineas:
                    if 'SELECT' in linea.upper() or 'FROM' in linea.upper():
                        print(f"         📄 {linea.strip()}")
        
        # Buscar consultas SQLAlchemy
        queries = re.findall(r'\.query\(.*?\)\.(?:all|first|filter|get)\(', codigo_funcion, re.DOTALL)
        for query in queries[:3]:
            if 'panaderia_id' in query.lower() or 'filter' in query.lower():
                print(f"      ✅ SQLALCHEMY SEGURO")
            else:
                print(f"      🚨 SQLALCHEMY VULNERABLE")
                print(f"         📄 {query.strip()}")

def buscar_vulnerabilidades_especificas():
    print("\n" + "=" * 60)
    print("🎯 BUSCANDO VULNERABILIDADES ESPECÍFICAS")
    print("-" * 50)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            lineas = file.readlines()
        
        vulnerabilidades = []
        
        for num_linea, linea in enumerate(lineas, 1):
            # Buscar consultas problemáticas
            if any(palabra in linea.lower() for palabra in ['select', 'from', 'query(']) and 'session' in linea.lower():
                # Si es una consulta pero no tiene filtro de tenant
                if 'panaderia_id' not in linea.lower() and 'filter' not in linea.lower():
                    # Verificar que no sea una consulta inocua
                    if not any(excluida in linea.lower() for excluida in ['count()', 'first()', 'get(']):
                        vulnerabilidades.append((num_linea, linea.strip()))
        
        if vulnerabilidades:
            print("🚨 VULNERABILIDADES ENCONTRADAS:")
            for num_linea, linea in vulnerabilidades[:10]:  # Mostrar solo las primeras 10
                print(f"   Línea {num_linea}: {linea}")
        else:
            print("✅ No se encontraron vulnerabilidades evidentes")
            
    except Exception as e:
        print(f"❌ Error en búsqueda específica: {e}")

if __name__ == "__main__":
    analizar_rutas_app()
    buscar_vulnerabilidades_especificas()
    
    print("\n" + "=" * 60)
    print("🎯 INSTRUCCIONES:")
    print("1. Ejecuta este script: python verificar_rutas_problematicas.py")
    print("2. Comparte la salida completa")
    print("3. Luego ejecuta los scripts de diagnóstico anteriores")
    print("4. NO uses los módulos problemáticos hasta la corrección")