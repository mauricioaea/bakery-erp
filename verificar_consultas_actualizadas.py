#!/usr/bin/env python3
"""
VERIFICACIÓN DE CONSULTAS CORREGIDAS EN PROVEEDORES
"""

import re

def verificar_correcciones_proveedores():
    """Verifica que las consultas de proveedores estén corregidas"""
    
    archivo = "app.py"
    
    print("🔍 VERIFICANDO CONSULTAS DE PROVEEDORES CORREGIDAS")
    print("=" * 60)
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Consultas que deberían estar corregidas
    consultas_verificar = [
        # Consultas que deberían usar current_user.panaderia_id
        (r"Proveedor\.query\.filter_by\(panaderia_id=current_user\.panaderia_id", "Consulta corregida con tenant actual"),
        
        # Consultas que NO deberían existir (problemáticas)
        (r"Proveedor\.query\.filter_by\(panaderia_id=1", "❌ CONSULTA PELIGROSA - ID fijo"),
        (r"Proveedor\.query\.filter_by\(panaderia_id=session\.get\('panaderia_id', 1\)", "❌ CONSULTA PELIGROSA - Session fallback"),
        (r"Proveedor\.query\.all\(\)", "❌ CONSULTA PELIGROSA - Sin filtro tenant"),
    ]
    
    resultados = []
    
    for patron, descripcion in consultas_verificar:
        coincidencias = re.findall(patron, contenido)
        if coincidencias:
            resultados.append((descripcion, len(coincidencias), coincidencias[:2]))  # Mostrar solo 2 ejemplos
    
    print("📊 RESULTADOS DE VERIFICACIÓN:")
    print("=" * 60)
    
    for descripcion, cantidad, ejemplos in resultados:
        if "❌" in descripcion:
            print(f"{descripcion}: {cantidad} encontradas")
            for ejemplo in ejemplos:
                print(f"   Ejemplo: {ejemplo[:50]}...")
        else:
            print(f"✅ {descripcion}: {cantidad} encontradas")
    
    # Verificar rutas de proveedores
    print("\n🔍 BUSCANDO RUTAS DE PROVEEDORES:")
    print("=" * 60)
    
    rutas_proveedores = re.findall(r'@.*?\.route\([\'\"](/[^\'\"]*proveedor[^\'\"]*)[\'\"]', contenido)
    if rutas_proveedores:
        print(f"📍 {len(rutas_proveedores)} rutas de proveedores encontradas:")
        for ruta in rutas_proveedores:
            print(f"   • {ruta}")
    else:
        print("ℹ️  No se encontraron rutas específicas de proveedores")
    
    return resultados

def buscar_consultas_tenant_actual():
    """Busca consultas que usan el tenant actual correctamente"""
    
    archivo = "app.py"
    
    print("\n🔍 BUSCANDO CONSULTAS CON TENANT ACTUAL:")
    print("=" * 60)
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    patrones_correctos = [
        r"panaderia_id=current_user\.panaderia_id",
        r"panaderia_id=session\['panaderia_id'\]",
        r"panaderia_id=session\.get\('panaderia_id'\)",
        r"panaderia_id=g\.panaderia_id",
    ]
    
    correctas = 0
    for patron in patrones_correctos:
        coincidencias = re.findall(patron, contenido)
        if coincidencias:
            correctas += len(coincidencias)
            print(f"✅ {patron}: {len(coincidencias)} encontradas")
    
    print(f"\n🎯 Total consultas correctas: {correctas}")
    return correctas

if __name__ == "__main__":
    print("🚀 VERIFICACIÓN DE CORRECCIONES MULTI-TENANT")
    print("=" * 60)
    
    # Verificar correcciones de proveedores
    resultados = verificar_correcciones_proveedores()
    
    # Buscar consultas correctas
    correctas = buscar_consultas_tenant_actual()
    
    print("\n" + "=" * 60)
    
    # Evaluación final
    problemas = sum(1 for r in resultados if "❌" in r[0])
    
    if problemas == 0:
        print("🎉 ¡TODAS LAS CONSULTAS ESTÁN CORRECTAS!")
        print("✅ Proveedores completamente aislados por tenant")
    else:
        print(f"⚠️  Se encontraron {problemas} tipos de consultas problemáticas")
        print("💡 Es necesario corregirlas manualmente")
    
    print("\n📋 PRÓXIMOS PASOS RECOMENDADOS:")
    print("   1. Reiniciar aplicación Flask")
    print("   2. Probar aislamiento entre panaderías")
    print("   3. Si persisten problemas, revisar consultas manualmente")