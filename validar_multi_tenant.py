# validar_multi_tenant.py
import os
import re
import sqlite3

def validar_multi_tenant():
    """Valida que todos los módulos respeten el aislamiento multi-tenant"""
    
    print("🔍 VALIDANDO AISLAMIENTO MULTI-TENANT")
    print("=" * 70)
    
    app_path = 'app.py'
    if not os.path.exists(app_path):
        print("❌ No se encuentra app.py")
        return
    
    with open(app_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # 1. Verificar filtros panaderia_id en consultas
    print("\n📋 VERIFICANDO FILTROS 'panaderia_id':")
    print("-" * 50)
    
    # Buscar consultas SQL con WHERE
    patrones = [
        r'WHERE.*panaderia_id\s*=\s*[^\s]+',
        r'filter_by\(panaderia_id\s*=\s*[^\)]+\)',
        r'filter\(.*panaderia_id\s*==\s*[^\)]+\)'
    ]
    
    encontrados = []
    for patron in patrones:
        matches = re.findall(patron, contenido, re.IGNORECASE)
        encontrados.extend(matches)
    
    if encontrados:
        print(f"✅ Se encontraron {len(encontrados)} consultas con filtro panaderia_id")
        for i, match in enumerate(encontrados[:5], 1):
            print(f"   {i}. {match[:80]}...")
        if len(encontrados) > 5:
            print(f"   ... y {len(encontrados) - 5} más")
    else:
        print("⚠️ No se encontraron consultas con filtro panaderia_id")
    
    # 2. Verificar rutas que podrían tener fugas de datos
    print("\n\n📋 VERIFICANDO RUTAS CRÍTICAS:")
    print("-" * 50)
    
    rutas_criticas = [
        '/reportes',
        '/ventas',
        '/clientes',
        '/productos',
        '/inventario',
        '/produccion',
        '/gestion_clientes'
    ]
    
    for ruta in rutas_criticas:
        if ruta in contenido:
            print(f"  ✅ Ruta {ruta} encontrada")
        else:
            print(f"  ⚠️ Ruta {ruta} no encontrada")
    
    # 3. Verificar módulos con IA
    print("\n\n🤖 VERIFICANDO MÓDULOS CON IA:")
    print("-" * 50)
    
    patrones_ia = [
        r'predict',
        r'recomendacion',
        r'inteligencia',
        r'analisis_predictivo',
        r'tendencia',
        r'prediccion'
    ]
    
    ia_encontrados = []
    for patron in patrones_ia:
        matches = re.findall(patron, contenido, re.IGNORECASE)
        ia_encontrados.extend(matches)
    
    if ia_encontrados:
        print(f"✅ Se encontraron {len(ia_encontrados)} referencias a IA:")
        for i, match in enumerate(set(ia_encontrados), 1):
            print(f"   {i}. {match}")
    else:
        print("⚠️ No se encontraron referencias a IA")
    
    print("\n" + "=" * 70)
    print("✅ VALIDACIÓN COMPLETADA")

if __name__ == "__main__":
    validar_multi_tenant()