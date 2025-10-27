from app import app

print('=== RUTAS DE CLIENTES ===')
routes = [rule.rule for rule in app.url_map.iter_rules() if 'cliente' in rule.rule.lower()]
for r in routes:
    print(r)

print('\n=== RUTAS DE USUARIOS ===')
user_routes = [rule.rule for rule in app.url_map.iter_rules() if 'user' in rule.rule.lower() or 'usuario' in rule.rule.lower()]
for r in user_routes:
    print(r)