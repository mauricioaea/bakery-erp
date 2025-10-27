# verificar_usuarios.py
from app import app, db
from models import Usuario

def main():
    with app.app_context():
        usuarios = Usuario.query.all()
        print('=== LISTA ACTUAL DE USUARIOS ===')
        for usuario in usuarios:
            print(f'👤 {usuario.username} | 🎯 {usuario.rol} | 🏪 Panadería: {usuario.panaderia_id}')
        print('=================================')

if __name__ == '__main__':
    main()