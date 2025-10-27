from app import app

print("=== VERIFICANDO RUTAS DUPLICADAS ===")
routes = {}
duplicados = []

for rule in app.url_map.iter_rules():
    if rule.endpoint in routes:
        duplicados.append(f'❌ DUPLICADO: {rule.endpoint} - {rule.rule}')
        duplicados.append(f'   Ya existe: {routes[rule.endpoint]}')
    else:
        routes[rule.endpoint] = rule.rule

if duplicados:
    print("\n".join(duplicados))
else:
    print("✅ No hay rutas duplicadas")

print(f"\n✅ Total de rutas: {len(routes)}")