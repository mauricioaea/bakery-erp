from app import app, db
from models import Usuario

with app.app_context():
    admin = Usuario.query.filter_by(username='admin').first()
    if admin:
        print(f"🔍 DATOS DEL USUARIO ADMIN:")
        print(f"Username: {admin.username}")
        print(f"Rol: {admin.rol}")
        print(f"Activo: {admin.activo}")
        print(f"¿Puede acceder a usuarios? {admin.puede_acceder_modulo('usuarios')}")
        print(f"¿Tiene permiso para gestionar? {admin.tiene_permiso('usuarios', 'gestionar')}")
    else:
        print("❌ No se encontró el usuario admin")