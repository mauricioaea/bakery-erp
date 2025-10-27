from app import app, db
from models import ConfiguracionPanaderia, Usuario
from datetime import datetime

print("=== DEPURACIÓN DE RUTAS SUPER ADMIN ===")

# Verificar que las rutas estén registradas
print("\n=== RUTAS REGISTRADAS ===")
for rule in app.url_map.iter_rules():
    if 'super' in rule.rule:
        print(f"✅ {rule.rule} -> {rule.endpoint}")

# Probar la función de renovación manualmente
print("\n=== PROBANDO RENOVACIÓN ===")
try:
    with app.app_context():
        # Tomar un cliente de prueba
        cliente = ConfiguracionPanaderia.query.first()
        if cliente:
            print(f"Cliente de prueba: {cliente.nombre_panaderia}")
            print(f"Tipo licencia: {cliente.tipo_licencia}")
            print(f"Fecha actual: {cliente.fecha_expiracion}")
            print("✅ Modelos cargados correctamente")
        else:
            print("❌ No hay clientes en la base de datos")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n=== DEPURACIÓN COMPLETADA ===")