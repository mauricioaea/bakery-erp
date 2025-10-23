# reparar_bd.py - ARCHIVO DE REPARACIÓN DE BASE DE DATOS
import os

print("🔧 INICIANDO REPARACIÓN DE BASE DE DATOS...")

# Eliminar archivo de base de datos si existe
db_path = os.path.join(os.path.dirname(__file__), 'panaderia.db')
if os.path.exists(db_path):
    os.remove(db_path)
    print("✅ Base de datos anterior eliminada")

print("🎉 Reparación completada. Ahora corrige models.py y ejecuta: python app.py")