# convertir_admin.py
from app import app, db
from models import Usuario

def main():
    with app.app_context():
        admin_actual = Usuario.query.filter_by(username='admin').first()
        if admin_actual:
            admin_actual.rol = 'admin_cliente'
            admin_actual.nombre_completo = 'Administrador Panadería Principal'
            db.session.commit()
            print('✅ ADMIN ACTUAL ACTUALIZADO:')
            print('   👤 Usuario: admin')
            print('   🎯 Nuevo rol: admin_cliente')
            print('   📝 Nombre: Administrador Panadería Principal')
            print('   💡 Ahora solo podrá ver SU panadería')
        else:
            print('❌ No se encontró el usuario admin')

if __name__ == '__main__':
    main()