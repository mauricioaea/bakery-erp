from app import app, db
from models import Receta, Producto

def verificar_recetas():
    with app.app_context():
        recetas = Receta.query.all()
        print("🔍 VERIFICANDO RECETAS Y PRODUCTOS:")
        
        for receta in recetas:
            print(f"📋 Receta: {receta.nombre}")
            print(f"   - Tiene producto: {'SÍ' if receta.producto else 'NO'}")
            if receta.producto:
                print(f"   - Producto: {receta.producto.nombre}")
                print(f"   - Stock del producto: {receta.producto.stock_actual}")
            print("---")

if __name__ == '__main__':
    verificar_recetas()