# limpiar_ventas.py
from app import app, db
from models import Venta, DetalleVenta, Factura

print("🧹 INICIANDO LIMPIEZA DE VENTAS EXISTENTES...")

with app.app_context():
    # Contar ventas antes de eliminar
    total_ventas = Venta.query.count()
    print(f"📊 Ventas encontradas: {total_ventas}")
    
    # Eliminar en orden para evitar errores de clave foránea
    DetalleVenta.query.delete()
    Factura.query.delete()
    Venta.query.delete()
    
    db.session.commit()
    print("🎉 BASE DE DATOS LIMPIADA - LISTA PARA NUEVAS VENTAS")

print("✅ Puedes comenzar a registrar nuevas ventas con fechas correctas")