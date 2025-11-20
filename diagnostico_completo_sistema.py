# diagnostico_completo_sistema.py
import sqlite3
import re

def diagnosticar_tablas_en_bd():
    """Diagnostica qué tablas realmente necesitan panaderia_id"""
    print("🔍 DIAGNÓSTICO COMPLETO DE BASE DE DATOS")
    print("=" * 50)
    
    db_path = "panaderia.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener TODAS las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        todas_tablas = [tabla[0] for tabla in cursor.fetchall()]
        
        print("📊 TODAS LAS TABLAS ENCONTRADAS:")
        print("-" * 30)
        
        tablas_con_datos = []
        tablas_sin_panaderia_id = []
        
        for tabla in todas_tablas:
            cursor.execute(f"PRAGMA table_info({tabla})")
            columnas = [col[1] for col in cursor.fetchall()]
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            total_registros = cursor.fetchone()[0]
            
            tiene_panaderia_id = 'panaderia_id' in columnas
            
            if total_registros > 0:  # Solo nos interesan tablas con datos
                tablas_con_datos.append(tabla)
                
                if not tiene_panaderia_id:
                    tablas_sin_panaderia_id.append(tabla)
                
                estado = "✅" if tiene_panaderia_id else "❌"
                print(f"   {estado} {tabla}: {total_registros} registros")
        
        print(f"\n🎯 RESUMEN BD:")
        print(f"   • Tablas con datos: {len(tablas_con_datos)}")
        print(f"   • Tablas SIN panaderia_id: {len(tablas_sin_panaderia_id)}")
        
        if tablas_sin_panaderia_id:
            print(f"\n🚨 TABLAS QUE NECESITAN panaderia_id:")
            for tabla in tablas_sin_panaderia_id:
                print(f"   • {tabla}")
        
        return tablas_sin_panaderia_id
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    finally:
        conn.close()

def diagnosticar_consultas_en_app():
    """Diagnostica qué consultas se hacen en app.py"""
    print("\n🔍 DIAGNÓSTICO DE CONSULTAS EN app.py")
    print("=" * 50)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # Buscar todas las consultas SQLAlchemy
        patrones_consultas = [
            r'(\w+)\.query\.(all|filter_by|get|first|order_by)',
            r'db\.session\.query\(([^)]+)\)',
            r'SELECT.*FROM\s+(\w+)',
        ]
        
        tablas_usadas = set()
        
        for patron in patrones_consultas:
            matches = re.finditer(patron, contenido, re.IGNORECASE)
            for match in matches:
                if match.group(1):
                    tabla = match.group(1).lower()
                    # Filtrar solo nombres que parecen tablas
                    if any(keyword in tabla for keyword in ['proveedor', 'activo', 'registro', 'pago', 'saldo', 'categoria', 'configuracion', 'consecutivo', 'produccion', 'usuario', 'venta', 'receta', 'producto']):
                        tablas_usadas.add(tabla)
        
        print("📝 TABLAS USADAS EN app.py:")
        print("-" * 30)
        
        for tabla in sorted(tablas_usadas):
            # Verificar si tiene filtro panaderia_id
            if f'{tabla}.filter_by(panaderia_id' in contenido.lower():
                print(f"   ✅ {tabla} - CON filtro")
            elif f'{tabla}.query.' in contenido.lower():
                print(f"   ❌ {tabla} - SIN filtro")
            else:
                print(f"   🔍 {tabla} - Usada indirectamente")
        
        return tablas_usadas
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return set()

def diagnosticar_funciones_problematicas():
    """Diagnostica funciones específicas que tienen problemas"""
    print("\n🔍 FUNCIONES CON PROBLEMAS IDENTIFICADOS")
    print("=" * 50)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # Buscar funciones que mencionamos en el error
        funciones_problematicas = [
            'control_diario',
            'proveedores', 
            'activos_fijos',
            'productos_externos',
            'materias_primas'
        ]
        
        for funcion in funciones_problematicas:
            inicio = contenido.find(f'def {funcion}():')
            if inicio == -1:
                print(f"   ⚠️  {funcion} - No encontrada")
                continue
            
            fin = contenido.find('def ', inicio + 1)
            if fin == -1:
                fin = len(contenido)
            
            codigo_funcion = contenido[inicio:fin]
            
            # Verificar consultas en esta función
            consultas_sin_filtro = []
            
            if 'Proveedor.query' in codigo_funcion and 'panaderia_id' not in codigo_funcion:
                consultas_sin_filtro.append('Proveedor')
            if 'ActivoFijo.query' in codigo_funcion and 'panaderia_id' not in codigo_funcion:
                consultas_sin_filtro.append('ActivoFijo')
            if 'RegistroDiario.query' in codigo_funcion and 'panaderia_id' not in codigo_funcion:
                consultas_sin_filtro.append('RegistroDiario')
            if 'SaldoBanco.query' in codigo_funcion and 'panaderia_id' not in codigo_funcion:
                consultas_sin_filtro.append('SaldoBanco')
            
            if consultas_sin_filtro:
                print(f"   ❌ {funcion} - Consultas sin filtro: {', '.join(consultas_sin_filtro)}")
            else:
                print(f"   ✅ {funcion} - Consultas OK")
                
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🛡️  DIAGNÓSTICO COMPLETO DEL SISTEMA")
    print("=" * 60)
    
    # Diagnóstico 1: Base de datos
    tablas_sin_panaderia_id = diagnosticar_tablas_en_bd()
    
    # Diagnóstico 2: Consultas en app.py
    tablas_usadas = diagnosticar_consultas_en_app()
    
    # Diagnóstico 3: Funciones problemáticas
    diagnosticar_funciones_problematicas()
    
    print("\n🎯 PLAN DE ACCIÓN BASADO EN DIAGNÓSTICO:")
    print("=" * 50)
    
    if tablas_sin_panaderia_id:
        print("1. 🔧 CORREGIR estas tablas en BD:")
        for tabla in tablas_sin_panaderia_id:
            print(f"   • {tabla}")
    else:
        print("1. ✅ BASE DE DATOS - Todas las tablas tienen panaderia_id")
    
    print("\n2. 🔍 VERIFICAR filtros en app.py para:")
    for tabla in sorted(tablas_usadas):
        print(f"   • {tabla}")
    
    print("\n3. 🧪 PROBAR aislamiento después de correcciones")

if __name__ == "__main__":
    main()