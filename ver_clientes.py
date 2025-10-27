# ver_clientes.py
from app import app, db
from models import ConfiguracionPanaderia

with app.app_context():
    clientes = ConfiguracionPanaderia.query.all()
    print('=== LISTA DE CLIENTES ===')
    for cliente in clientes:
        print(f'ID: {cliente.id} | Nombre: {cliente.nombre_panaderia} | Tipo: {cliente.tipo_licencia}')
    print('=========================')