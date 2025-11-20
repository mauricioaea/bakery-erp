# diagnosticar_problema_real.py
import re

def diagnosticar_tenant_en_sesion():
    print("🔍 DIAGNÓSTICO DEL PROBLEMA REAL")
    print("=" * 50)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        print("🎯 VERIFICANDO DETECCIÓN DE TENANT:")
        print("-" * 30)
        
        # Buscar cómo se detecta el tenant
        if 'session.get(\'panaderia_id\'' in contenido:
            print("✅ Session detecta panaderia_id")
        else:
            print("❌ NO se detecta panaderia_id desde session")
        
        # Buscar consultas con panaderia_id hardcodeado
        consultas_hardcodeadas = re.findall(r'filter_by\(panaderia_id=1\)', contenido)
        print(f"🚨 Consultas con panaderia_id=1 (HARDCODEADO): {len(consultas_hardcodeadas)}")
        
        # Buscar consultas con tenant dinámico
        consultas_dinamicas = re.findall(r'panaderia_id=.*session', contenido)
        print(f"✅ Consultas con tenant dinámico: {len(consultas_dinamicas)}")
        
        print("\n📊 ANÁLISIS DE CONSULTAS:")
        print("-" * 30)
        
        # Ejemplos de consultas problemáticas
        ejemplos = re.findall(r'\w+\.query\.filter_by\(panaderia_id=1\)\.\w+\(\)', contenido)
        for ejemplo in ejemplos[:5]:  # Mostrar solo 5 ejemplos
            print(f"   ❌ {ejemplo}")
        
        print(f"\n🎯 CONCLUSIÓN:")
        if consultas_hardcodeadas and not consultas_dinamicas:
            print("   ❌ TODAS las consultas usan panaderia_id=1 (HARDCODEADO)")
            print("   🔧 NECESITAMOS: Reemplazar por panaderia_id dinámico")
        else:
            print("   ⚠️  Mezcla de consultas hardcodeadas y dinámicas")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def mostrar_solucion_propuesta():
    print("\n🔧 SOLUCIÓN PROPUESTA:")
    print("=" * 50)
    
    print("""
❌ PROBLEMA ACTUAL:
   Proveedor.query.filter_by(panaderia_id=1).all()

✅ SOLUCIÓN:
   panaderia_actual = session.get('panaderia_id', 1)
   Proveedor.query.filter_by(panaderia_id=panaderia_actual).all()

🎯 CAMBIOS NECESARIOS:
1. Obtener panaderia_id de la sesión del usuario
2. Reemplazar TODOS los panaderia_id=1 por la variable dinámica
3. Asegurar que el middleware guarde correctamente el tenant_id
    """)

if __name__ == "__main__":
    diagnosticar_tenant_en_sesion()
    mostrar_solucion_propuesta()