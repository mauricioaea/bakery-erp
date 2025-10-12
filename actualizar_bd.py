import os
import time
import sqlite3
from app import app, db
from models import *

def cerrar_conexiones_bd():
    """Intenta cerrar todas las conexiones a la base de datos"""
    print("🔒 Cerrando conexiones a la base de datos...")
    try:
        # Cerrar sesión de SQLAlchemy
        db.session.close()
        # Eliminar el engine para forzar cierre de conexiones
        db.engine.dispose()
        print("✅ Conexiones de SQLAlchemy cerradas")
    except Exception as e:
        print(f"⚠️  Error cerrando conexiones: {e}")

def actualizar_base_datos():
    print("🔄 Actualizando base de datos...")
    
    # Cerrar conexiones primero
    cerrar_conexiones_bd()
    
    # Dar tiempo para que se liberen las conexiones
    time.sleep(2)
    
    db_path = os.path.join(os.path.dirname(__file__), 'panaderia.db')
    
    # Intentar eliminar la base de datos
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ Base de datos anterior eliminada")
        else:
            print("ℹ️  No se encontró base de datos existente")
    except PermissionError:
        print("❌ ERROR: No se pudo eliminar la base de datos")
        print("💡 SOLUCIÓN: Cierra Visual Studio Code y todas las terminales, luego vuelve a ejecutar")
        return
    except Exception as e:
        print(f"❌ Error eliminando BD: {e}")
        return
    
    # Crear todas las tablas
    try:
        with app.app_context():
            db.create_all()
            print("✅ Tablas creadas exitosamente")
            
            # Crear usuario admin por defecto
            from werkzeug.security import generate_password_hash
            admin = Usuario.query.filter_by(username='admin').first()
            if not admin:
                hashed_password = generate_password_hash('admin123')
                admin_user = Usuario(username='admin', password_hash=hashed_password, rol='admin')
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Usuario admin creado")
            
            # Crear categorías y productos de prueba
            if not Categoria.query.first():
                panaderia = Categoria(nombre="Panadería")
                pasteleria = Categoria(nombre="Pastelería")
                bebidas = Categoria(nombre="Bebidas")
                
                db.session.add_all([panaderia, pasteleria, bebidas])
                db.session.commit()
                
                # Crear productos de prueba
                productos = [
                    Producto(nombre="Pan Mantequilla", categoria_id=panaderia.id, precio_venta=3000, codigo_barras="1001", stock_actual=0),
                    Producto(nombre="Pan Integral", categoria_id=panaderia.id, precio_venta=4000, codigo_barras="1002", stock_actual=0),
                    Producto(nombre="Croissant", categoria_id=panaderia.id, precio_venta=1000, codigo_barras="1003", stock_actual=0),
                    Producto(nombre="Pastel de Chocolate", categoria_id=pasteleria.id, precio_venta=30000, codigo_barras="2001", stock_actual=0),
                    Producto(nombre="Galletas", categoria_id=pasteleria.id, precio_venta=1200, codigo_barras="2002", stock_actual=0),
                ]
                
                db.session.add_all(productos)
                db.session.commit()
                print("✅ Productos de prueba creados")
            
            print("🎉 Base de datos actualizada exitosamente!")
            
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")

if __name__ == '__main__':
    actualizar_base_datos()