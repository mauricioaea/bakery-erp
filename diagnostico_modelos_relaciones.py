#!/usr/bin/env python3
"""
ANALIZADOR DE MODELOS Y RELACIONES ENTRE MÓDULOS
Verifica que todos los modelos tengan panaderia_id y las relaciones funcionen
"""

import re
import os

def analizar_modelos(archivo_models):
    """Analiza models.py para verificar estructura multi-tenant"""
    
    print("🔍 ANALIZANDO ESTRUCTURA DE MODELOS...")
    print("=" * 60)
    
    with open(archivo_models, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar todos los modelos (clases que heredan de db.Model)
    patron_modelos = r'class\s+(\w+)\(.*db\.Model.*\):'
    modelos = re.findall(patron_modelos, contenido)
    
    print(f"📋 MODELOS ENCONTRADOS: {len(modelos)}")
    print(", ".join(modelos))
    
    resultados_modelos = {}
    
    for modelo in modelos:
        # Buscar la definición de cada modelo
        patron_definicion = rf'class {modelo}\(.*?db\.Model.*?\):(.*?)(?=class\s+\w+|$)'
        match = re.search(patron_definicion, contenido, re.DOTALL)
        
        if match:
            definicion = match.group(1)
            tiene_panaderia_id = 'panaderia_id' in definicion
            tiene_relacion_db = 'db.Column' in definicion and 'db.ForeignKey' in definicion
            
            resultados_modelos[modelo] = {
                'tiene_panaderia_id': tiene_panaderia_id,
                'tiene_relaciones': tiene_relacion_db,
                'definicion': definicion[:200] + "..." if len(definicion) > 200 else definicion
            }
    
    return modelos, resultados_modelos

def generar_reporte_modelos(modelos, resultados):
    """Genera reporte de análisis de modelos"""
    
    print("\n📊 REPORTE DE MODELOS:")
    print("=" * 60)
    
    modelos_sin_tenant = []
    modelos_con_tenant = []
    
    for modelo in modelos:
        info = resultados[modelo]
        if info['tiene_panaderia_id']:
            modelos_con_tenant.append(modelo)
            print(f"✅ {modelo}: TIENE panaderia_id")
        else:
            modelos_sin_tenant.append(modelo)
            print(f"❌ {modelo}: NO TIENE panaderia_id")
    
    print(f"\n🎯 RESUMEN:")
    print(f"   ✅ Modelos con tenant: {len(modelos_con_tenant)}")
    print(f"   ❌ Modelos sin tenant: {len(modelos_sin_tenant)}")
    
    if modelos_sin_tenant:
        print(f"\n🚨 MODELOS QUE NECESITAN panaderia_id:")
        for modelo in modelos_sin_tenant:
            print(f"   • {modelo}")

def analizar_relaciones_entre_modelos(archivo_models):
    """Analiza las relaciones entre modelos para identificar dependencias"""
    
    print("\n🔗 ANALIZANDO RELACIONES ENTRE MODELOS...")
    print("=" * 60)
    
    with open(archivo_models, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar relaciones ForeignKey
    patron_foreign_keys = r'(\w+)\s*=\s*db\.Column\([^)]*db\.ForeignKey\([^)]+\)[^)]*\)'
    foreign_keys = re.findall(patron_foreign_keys, contenido)
    
    print("🔗 RELACIONES FOREIGN KEY ENCONTRADAS:")
    for fk in foreign_keys:
        print(f"   • {fk}")
    
    # Buscar relaciones de referencia entre modelos
    patron_relaciones = r'(\w+)\s*=\s*db\.relationship\([^)]*\)'
    relaciones = re.findall(patron_relaciones, contenido)
    
    print(f"\n🤝 RELACIONES DB.RELATIONSHIP ENCONTRADAS:")
    for rel in relaciones:
        print(f"   • {rel}")

if __name__ == "__main__":
    archivo_models = "models.py"
    
    if not os.path.exists(archivo_models):
        print("❌ Error: models.py no encontrado")
        exit(1)
    
    print("🚀 DIAGNÓSTICO DE MODELOS Y RELACIONES")
    print("=" * 60)
    
    # Analizar modelos
    modelos, resultados = analizar_modelos(archivo_models)
    generar_reporte_modelos(modelos, resultados)
    
    # Analizar relaciones
    analizar_relaciones_entre_modelos(archivo_models)
    
    print("\n" + "=" * 60)
    print("🎯 ANÁLISIS DE MODELOS COMPLETADO")
    print("=" * 60)