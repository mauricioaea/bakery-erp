# limpiar_cache.py
import os
import shutil
import glob

print("🧹 LIMPIANDO CACHE COMPLETAMENTE...")

# Eliminar todos los archivos __pycache__
for root, dirs, files in os.walk('.'):
    for dir_name in dirs:
        if dir_name == '__pycache__':
            cache_path = os.path.join(root, dir_name)
            try:
                shutil.rmtree(cache_path)
                print(f"✅ Eliminado: {cache_path}")
            except Exception as e:
                print(f"⚠️ No se pudo eliminar {cache_path}: {e}")

print("✅ Cache limpiado completamente")