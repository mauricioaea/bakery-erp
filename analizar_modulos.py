# analizar_modulos.py
import os
import re

def analizar_modulos():
    """Analiza y lista todos los módulos disponibles en el sistema"""
    
    print("🔍 ANALIZANDO MÓDULOS DEL SISTEMA")
    print("=" * 70)
    
    # 1. Buscar rutas en app.py
    app_path = 'app.py'
    if not os.path.exists(app_path):
        print("❌ No se encuentra app.py")
        return
    
    with open(app_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar rutas @app.route
    rutas = re.findall(r'@app\.route\([\'"]([^\'"]*)[\'"]', contenido)
    
    # Filtrar rutas de módulos principales
    modulos = []
    modulos_ignorar = ['/static', '/favicon', '/login', '/logout', '/dashboard', '/']
    
    for ruta in rutas:
        if ruta.startswith('/api'):
            continue
        if any(ruta.startswith(ignorar) for ignorar in modulos_ignorar):
            continue
        if ruta and ruta != '/':
            # Limpiar ruta
            nombre = ruta.replace('/', '').replace('_', ' ').title()
            if '<' not in ruta:  # Evitar rutas con parámetros
                modulos.append({
                    'ruta': ruta,
                    'nombre': nombre,
                    'archivo': 'app.py'
                })
    
    # 2. Buscar templates
    templates_dir = 'templates'
    if os.path.exists(templates_dir):
        templates = [f for f in os.listdir(templates_dir) if f.endswith('.html')]
        
        # Identificar módulos por templates
        for template in templates:
            nombre = template.replace('.html', '').replace('_', ' ').title()
            # Verificar si ya existe en la lista de rutas
            existe = any(m['nombre'] == nombre for m in modulos)
            if not existe and nombre not in ['Base', 'Login', 'Acceso Denegado']:
                modulos.append({
                    'ruta': f'/{template.replace(".html", "")}',
                    'nombre': nombre,
                    'archivo': 'templates'
                })
    
    # 3. Mostrar módulos encontrados
    print("\n📋 MÓDULOS ENCONTRADOS:")
    print("-" * 70)
    
    # Ordenar por nombre
    modulos.sort(key=lambda x: x['nombre'])
    
    for i, modulo in enumerate(modulos, 1):
        print(f"{i:2}. {modulo['nombre']}")
        print(f"     Ruta: {modulo['ruta']}")
        print(f"     Archivo: {modulo['archivo']}")
        print()
    
    print("=" * 70)
    print(f"📊 Total módulos: {len(modulos)}")
    
    return modulos

if __name__ == "__main__":
    modulos = analizar_modulos()