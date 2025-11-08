# crear_super_admin.py
from app import app, db
from models import Usuario
from werkzeug.security import generate_password_hash

def main():
    with app.app_context():
        # Verificar si ya existe
        existe = Usuario.query.filter_by(username='dev_master').first()
        if not existe:
            # Crear SUPER ADMIN
            super_admin = Usuario(
                username='dev_master',
                password_hash=generate_password_hash('MasterSecure2025!'),
                nombre_completo='Soporte Tecnico Principal',
                rol='super_admin',
                panaderia_id=1
            )
            db.session.add(super_admin)
            db.session.commit()
            print('SUPER ADMIN CREADO:')
            print('   Usuario: dev_master')
            print('   Contraseña: MasterSecure2025!')
            print('   Rol: super_admin')
            print('   Este es tu usuario MAESTRO - Guardalo seguro!')
        else:
            print('El usuario dev_master ya existe')

if __name__ == '__main__':
    main()