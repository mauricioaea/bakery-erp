# crear_usuario_vencido.py
from app import app, db
from models import Usuario
from werkzeug.security import generate_password_hash

def main():
    with app.app_context():
        try:
            # Crear usuario para el CLIENTE VENCIDO (ID: 4)
            usuario_vencido = Usuario(
                username='cliente_vencido',
                password_hash=generate_password_hash('test123'),
                nombre_completo='Usuario Cliente Vencido - Panadería La Esperanza',
                rol='cajero',
                panaderia_id=4  # ← ID del cliente vencido
            )
            
            db.session.add(usuario_vencido)
            db.session.commit()
            
            print('✅ USUARIO CREADO EXITOSAMENTE!')
            print('=' * 40)
            print('📧 USUARIO: cliente_vencido')
            print('🔑 CONTRASEÑA: test123')
            print('🏪 CLIENTE: Panadería La Esperanza (VENCIDO)')
            print('=' * 40)
            print('\n💡 INSTRUCCIONES PARA PROBAR:')
            print('1. Ve al navegador donde tienes la aplicación')
            print('2. Cierra sesión del usuario admin')
            print('3. Inicia sesión con: cliente_vencido / test123')
            print('4. Deberías ser REDIRIGIDO a la página de "Suscripción Vencida"')
            
        except Exception as e:
            print(f'❌ Error: {e}')
            db.session.rollback()

if __name__ == '__main__':
    main()