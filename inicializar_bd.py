# inicializar_bd.py
from app import app, db
from models import *

def inicializar_base_datos():
    with app.app_context():
        try:
            print("🔄 Creando tablas en la base de datos...")
            db.create_all()
            print("✅ Tablas creadas exitosamente!")
            
            # Verificar algunas tablas
            print("📊 Tablas verificadas:")
            tablas = ['panaderias', 'usuarios', 'productos', 'recetas', 'ventas']
            for tabla in tablas:
                try:
                    # Intentar contar registros para verificar que la tabla existe
                    if tabla == 'panaderias':
                        count = Panaderia.query.count()
                    elif tabla == 'usuarios':
                        count = Usuario.query.count()
                    elif tabla == 'productos':
                        count = Producto.query.count()
                    elif tabla == 'recetas':
                        count = Receta.query.count()
                    elif tabla == 'ventas':
                        count = Venta.query.count()
                    print(f"   - {tabla}: {count} registros")
                except Exception as e:
                    print(f"   - {tabla}: ERROR - {e}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    inicializar_base_datos()