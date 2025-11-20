#!/usr/bin/env python3
"""
DIAGNÓSTICO AUTOMATIZADO DE CONSULTAS SIN FILTRO TENANT
Analiza app.py para identificar consultas que no usan panaderia_id
"""

import re
import os
from pathlib import Path

def analizar_consultas_problematicas(archivo_app):
    """Analiza app.py para encontrar consultas sin filtro tenant"""
    
    print("🔍 INICIANDO DIAGNÓSTICO AUTOMATIZADO...")
    print("=" * 60)
    
    with open(archivo_app, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Patrones para buscar consultas problemáticas
    patrones_problematicos = [
        # Consultas sin filtro tenant
        (r'(\w+)\.query\.(all|first|get\([^)]+\))', "CONSULTA SIN FILTRO"),
        (r'(\w+)\.query\.filter\([^)]*\)(?!.*panaderia_id)', "FILTER SIN panaderia_id"),
        (r'(\w+)\.query\.filter_by\([^)]*\)(?!.*panaderia_id)', "FILTER_BY SIN panaderia_id"),
        
        # Consultas con filtro tenant (para comparar)
        (r'(\w+)\.query\.filter_by\([^)]*panaderia_id[^)]*\)', "CON FILTRO TENANT"),
        (r'(\w+)\.query\.filter\([^)]*panaderia_id[^)]*\)', "CON FILTRO TENANT"),
    ]
    
    resultados = {
        'problematicas': [],
        'correctas': [],
        'rutas_afectadas': []
    }
    
    # Buscar todas las rutas y sus consultas
    rutas = re.findall(r'@[a-z_]+\.route\([^)]+\)\s*\n\s*def\s+(\w+)', contenido)
    
    print(f"📊 ENCONTRADAS {len(rutas)} RUTAS EN app.py")
    print("=" * 60)
    
    for patron, descripcion in patrones_problematicos:
        matches = re.finditer(patron, contenido)
        for match in matches:
            linea = contenido[:match.start()].count('\n') + 1
            contexto = contenido[max(0, match.start()-50):match.end()+50].replace('\n', ' ')
            
            # Determinar si es problemática o correcta
            if "SIN" in descripcion:
                resultados['problematicas'].append({
                    'linea': linea,
                    'consulta': match.group(0),
                    'descripcion': descripcion,
                    'contexto': contexto[:100] + "..."
                })
            else:
                resultados['correctas'].append({
                    'linea': linea,
                    'consulta': match.group(0),
                    'descripcion': descripcion
                })
    
    # Encontrar en qué rutas están las consultas problemáticas
    for problema in resultados['problematicas']:
        # Buscar la función más cercana antes de la línea problemática
        lineas_antes = contenido[:contenido.find('\n', contenido.find('\n' * (problema['linea'] - 3)))].split('\n')
        for i in range(min(10, len(lineas_antes))):
            if '@' in lineas_antes[-i] and 'route' in lineas_antes[-i]:
                resultados['rutas_afectadas'].append({
                    'ruta': lineas_antes[-i].strip(),
                    'problema': problema
                })
                break
    
    return resultados

def generar_reporte(resultados):
    """Genera un reporte detallado del diagnóstico"""
    
    print("\n🚨 CONSULTAS PROBLEMÁTICAS ENCONTRADAS:")
    print("=" * 60)
    
    if not resultados['problematicas']:
        print("✅ ¡EXCELENTE! No se encontraron consultas problemáticas")
        return
    
    for i, problema in enumerate(resultados['problematicas'], 1):
        print(f"\n{i}. Línea {problema['linea']}: {problema['descripcion']}")
        print(f"   Consulta: {problema['consulta']}")
        print(f"   Contexto: {problema['contexto']}")
    
    print(f"\n📊 RESUMEN:")
    print(f"   ❌ Consultas problemáticas: {len(resultados['problematicas'])}")
    print(f"   ✅ Consultas correctas: {len(resultados['correctas'])}")
    
    print(f"\n🎯 RUTAS AFECTADAS:")
    for ruta_afectada in resultados['rutas_afectadas']:
        print(f"   • {ruta_afectada['ruta']}")
        print(f"     Problema: {ruta_afectada['problema']['descripcion']}")

def analizar_modulos_especificos(archivo_app):
    """Analiza módulos específicos críticos"""
    
    print("\n🔍 ANALIZANDO MÓDULOS CRÍTICOS...")
    print("=" * 60)
    
    modulos_criticos = {
        'proveedores': ['proveedor', 'proveedores'],
        'productos_externos': ['producto_externo', 'productos_externos'],
        'financiero': ['financiero', 'transaccion', 'cuenta', 'balance'],
        'reportes': ['reporte', 'reportes', 'dashboard']
    }
    
    with open(archivo_app, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    for modulo, palabras_clave in modulos_criticos.items():
        print(f"\n📦 MÓDULO: {modulo.upper()}")
        
        # Buscar rutas relacionadas con este módulo
        rutas_modulo = []
        for palabra in palabras_clave:
            patron_rutas = rf'@[a-z_]+\.route\([^)]*{palabra}[^)]*\)\s*\n\s*def\s+(\w+)'
            rutas = re.findall(patron_rutas, contenido, re.IGNORECASE)
            rutas_modulo.extend(rutas)
        
        print(f"   Rutas encontradas: {len(set(rutas_modulo))}")
        
        # Buscar consultas en estas rutas
        for ruta in set(rutas_modulo):
            # Encontrar la función completa
            patron_funcion = rf'def {ruta}\(.*?\):(.*?)(?=def\s+\w+|$)'
            match_funcion = re.search(patron_funcion, contenido, re.DOTALL)
            
            if match_funcion:
                cuerpo_funcion = match_funcion.group(1)
                # Buscar consultas sin filtro tenant en esta función
                consultas_sin_filtro = re.findall(r'(\w+)\.query\.(all|first|get\([^)]+\))', cuerpo_funcion)
                if consultas_sin_filtro:
                    print(f"   ⚠️  Ruta '{ruta}': {len(consultas_sin_filtro)} consultas sin filtro")

if __name__ == "__main__":
    archivo_app = "app.py"
    
    if not os.path.exists(archivo_app):
        print("❌ Error: app.py no encontrado")
        exit(1)
    
    print("🚀 DIAGNÓSTICO AUTOMATIZADO DE CONSULTAS SAAS")
    print("=" * 60)
    
    # Ejecutar diagnóstico principal
    resultados = analizar_consultas_problematicas(archivo_app)
    generar_reporte(resultados)
    
    # Ejecutar análisis de módulos específicos
    analizar_modulos_especificos(archivo_app)
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNÓSTICO COMPLETADO")
    print("=" * 60)