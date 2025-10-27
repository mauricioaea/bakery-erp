# crear_usuarios_definitivos.py
from app import app, db
from models import Usuario, ConfiguracionPanaderia
from werkzeug.security import generate_password_hash

def main():
    with app.app_context():
        print("=== CREANDO USUARIOS DEFINITIVOS ===")
        
        # 1. Crear SUPER ADMIN
        super_admin = Usuario(
            username='dev_master',
            password_hash=generate_password_hash('MasterSecure2025!'),
            nombre_completo='Soporte Técnico Principal',
            rol='super_admin',
            panaderia_id=1
        )
        db.session.add(super_admin)
        
        # 2. Crear ADMIN_CLIENTE
        admin_cliente = Usuario(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            nombre_completo='Administrador Panadería Principal',
            rol='admin_cliente',  # ← IMPORTANTE: Este rol
            panaderia_id=1
        )
        db.session.add(admin_cliente)
        
        db.session.commit()
        
        print("✅ USUARIOS CREADOS EXITOSAMENTE:")
        print("   👑 SUPER_ADMIN: dev_master / MasterSecure2025!")
        print("   👨‍💼 ADMIN_CLIENTE: admin / admin123")
        
        # Verificar
        usuarios = Usuario.query.all()
        print("\n=== VERIFICACIÓN ===")
        for usuario in usuarios:
            print(f'👤 {usuario.username} | 🎯 {usuario.rol}')

if __name__ == '__main__':
    main()