# buscar_inventario.py
import os
import re

def buscar_inventario():
    """Busca el módulo de inventario en el sistema"""
    
    print("🔍 BUSCANDO MÓDULO DE INVENTARIO")
    print("=" * 70)
    
    app_path = 'app.py'
    if not os.path.exists(app_path):
        print("❌ No se encuentra app.py")
        return
    
    with open(app_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar rutas relacionadas con inventario/stock
    patrones = [
        r'@app\.route\([\'"]/inventario[^\'"]*[\'"]',
        r'@app\.route\([\'"]/stock[^\'"]*[\'"]',
        r'@app\.route\([\'"]/productos[^\'"]*[\'"]',
        r'@app\.route\([\'"]/materias_primas[^\'"]*[\'"]',
    ]
    
    encontrados = []
    for patron in patrones:
        matches = re.findall(patron, contenido)
        encontrados.extend(matches)
    
    if encontrados:
        print("\n📋 RUTAS DE INVENTARIO ENCONTRADAS:")
        for ruta in encontrados:
            print(f"  {ruta}")
    else:
        print("\n❌ No se encontraron rutas de inventario")
    
    # Buscar referencias en templates
    templates_dir = 'templates'
    if os.path.exists(templates_dir):
        templates = [f for f in os.listdir(templates_dir) if f.endswith('.html')]
        templates_inventario = [t for t in templates if 'inventario' in t.lower() or 'stock' in t.lower() or 'producto' in t.lower()]
        
        if templates_inventario:
            print("\n📋 TEMPLATES DE INVENTARIO:")
            for t in templates_inventario:
                print(f"  - {t}")
        else:
            print("\n❌ No se encontraron templates de inventario")
    
    print("\n" + "=" * 70)
    print("💡 RECOMENDACIÓN:")
    print("  El inventario puede estar implementado como parte de:")
    print("  - Productos (/productos)")
    print("  - Materias Primas (/materias_primas)")
    print("  - Stock Vitrina (/stock_vitrina)")

if __name__ == "__main__":
    buscar_inventario()