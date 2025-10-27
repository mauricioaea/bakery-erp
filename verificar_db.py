from app import db, Usuario, ConfiguracionPanaderia  # Cambiar User por Usuario

print('=== TABLA ConfiguracionPanaderia ===')
configs = ConfiguracionPanaderia.query.all()
for c in configs:
    print(f'ID: {c.id}, Nombre: {c.nombre_panaderia}, Tipo: {c.tipo_licencia}')

print('\n=== TABLA Usuario (primeros 10) ===')
users = Usuario.query.limit(10).all()  # Cambiar User por Usuario
for u in users:
    print(f'ID: {u.id}, Usuario: {u.username}, Rol: {u.role}, Panaderia: {u.panaderia_id}')