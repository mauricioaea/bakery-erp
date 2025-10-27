# actualizar_usuarios_existentes.py
from app import app, db
from models import Usuario
from werkzeug.security import generate_password_hash

def main():
    with app.app_context():
        print("=== ACTUALIZANDO USUARIOS EXISTENTES ===")
        
        # 1. ACTUALIZAR el usuario admin existente
        admin = Usuario.query.filter_by(username='admin').first()
        if admin:
            admin.rol = 'admin_cliente'
            admin.nombre_completo = 'Administrador Panadería Principal'
            print('✅ ADMIN ACTUALIZADO: admin -> admin_cliente')
        else:
            print('❌ Usuario admin no encontrado')
        
        # 2. CREAR super_admin si no existe
        super_admin = Usuario.query.filter_by(username='dev_master').first()
        if not super_admin:
            super_admin = Usuario(
                username='dev_master',
                password_hash=generate_password_hash('MasterSecure2025!'),
                nombre_completo='Soporte Técnico Principal',
                rol='super_admin',
                panaderia_id=1
            )
            db.session.add(super_admin)
            print('✅ SUPER ADMIN CREADO: dev_master')
        else:
            print('⚠️  dev_master ya existe')
        
        db.session.commit()
        
        print("\n=== RESULTADO FINAL ===")
        usuarios = Usuario.query.all()
        for usuario in usuarios:
            print(f'👤 {usuario.username} | 🎯 {usuario.rol} | 🏪 Panadería: {usuario.panaderia_id}')
        
        print("\n🔐 CREDENCIALES PARA PROBAR:")
        print("   👑 SUPER_ADMIN: dev_master / MasterSecure2025!")
        print("   👨‍💼 ADMIN_CLIENTE: admin / admin123")

if __name__ == '__main__':
    main()