# analisis_exhaustivo_seguro.py
import re
import os

def analizar_tipos_consultas():
    """Analiza TODOS los tipos de consultas en app.py"""
    print("🔍 ANÁLISIS EXHAUSTIVO DE CONSULTAS")
    print("=" * 50)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        print("📊 PATRONES DE CONSULTAS ENCONTRADOS:")
        print("-" * 40)
        
        patrones = {
            'filter_by simple': r'\.filter_by\([^)]*panaderia_id=1[^)]*\)',
            'filter múltiple': r'\.filter\([^)]*panaderia_id[^)]*\)', 
            'query.all() sin filtro': r'\.query\.all\(\)',
            'query.get()': r'\.query\.get\([^)]*\)',
            'query.first()': r'\.query\.first\(\)',
            'session.query': r'db\.session\.query\([^)]*\)',
            'consultas SQL directo': r'SELECT.*FROM.*WHERE',
            'JOINs': r'\.join\([^)]*\)',
            'consultas con order_by': r'\.order_by\([^)]*\)',
            'consultas con limit': r'\.limit\([^)]*\)'
        }
        
        resultados = {}
        for nombre, patron in patrones.items():
            matches = re.findall(patron, contenido, re.IGNORECASE)
            resultados[nombre] = len(matches)
            if matches:
                print(f"   📍 {nombre}: {len(matches)}")
                if len(matches) <= 3:  # Mostrar ejemplos si son pocos
                    for match in matches[:2]:
                        print(f"      Ej: {match[:80]}...")
        
        return resultados
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

def analizar_funciones_criticas():
    """Analiza funciones que podrían romperse"""
    print("\n🎯 ANÁLISIS DE FUNCIONES CRÍTICAS:")
    print("-" * 40)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        funciones_problematicas = []
        
        # Buscar funciones que puedan tener lógica entre tenants
        patrones_problematicos = [
            r'def .*reporte.*\(.*\):',
            r'def .*dashboard.*\(.*\):', 
            r'def .*estadistica.*\(.*\):',
            r'def .*consolidado.*\(.*\):',
            r'def .*total.*\(.*\):'
        ]
        
        for patron in patrones_problematicos:
            matches = re.findall(patron, contenido, re.IGNORECASE)
            for match in matches:
                funciones_problematicas.append(match)
                print(f"   ⚠️  {match} - Posible función crítica")
        
        return funciones_problematicas
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def crear_plan_seguro():
    """Crea un plan de corrección seguro y por fases"""
    print("\n🛡️ PLAN DE CORRECCIÓN SEGURO:")
    print("=" * 50)
    
    print("""
FASE 1: PREPARACIÓN (0% riesgo)
✅ Completar estructura BD - Tablas con panaderia_id
✅ Crear backups completos
✅ Documentar estado actual

FASE 2: CORRECCIÓN PROGRESIVA (riesgo controlado)
🔧 Módulo por módulo, empezando por los más simples:
   1. Proveedores
   2. Activos Fijos  
   3. Productos
   4. Módulos financieros
   5. Reportes (más complejo)

FASE 3: PRUEBAS INTENSIVAS
🧪 Probar cada módulo después de corrección
🔍 Verificar aislamiento tenant por tenant
📊 Confirmar que cálculos y reportes funcionan

FASE 4: IMPLEMENTACIÓN COMPLETA
🚀 Una vez confirmado que todo funciona
🔄 Implementar en todos los módulos restantes
""")

def sugerir_enfoque_alternativo():
    """Sugiere enfoques más seguros"""
    print("\n💡 ENFOQUES ALTERNATIVOS MÁS SEGUROS:")
    print("=" * 50)
    
    print("""
OPCIÓN A: Corrección módulo por módulo
   • Elegir UN módulo simple (ej: Proveedores)
   • Corregir solo ese módulo
   • Probar exhaustivamente
   • Continuar con el siguiente

OPCIÓN B: Implementar filtro automático
   • Crear un wrapper para db.session.query
   • Aplicar filtro panaderia_id automáticamente
   • Menos cambios en código existente

OPCIÓN C: Corrección con feature flags
   • Implementar sistema para activar/desactivar filtros
   • Poder revertir rápidamente si hay problemas
   • Mayor control durante transición
""")

if __name__ == "__main__":
    print("🛡️ ANÁLISIS DE SEGURIDAD COMPLETO")
    print("=" * 60)
    print("🔍 Evaluando riesgos antes de cualquier cambio")
    print("=" * 60)
    
    consultas = analizar_tipos_consultas()
    funciones_criticas = analizar_funciones_criticas()
    crear_plan_seguro()
    sugerir_enfoque_alternativo()
    
    print(f"\n🎯 RECOMENDACIÓN BASADA EN ANÁLISIS:")
    if len(funciones_criticas) > 5:
        print("   ⚠️  Sistema complejo - Recomiendo OPCIÓN A (módulo por módulo)")
    else:
        print("   ✅ Sistema manejable - Podemos proceder con plan seguro por fases")