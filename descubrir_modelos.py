from app import db
from sqlalchemy import inspect

# Crear inspector para la base de datos
inspector = inspect(db.engine)

print('=== TABLAS EN LA BASE DE DATOS ===')
tablas = inspector.get_table_names()
for tabla in tablas:
    print(f'📊 {tabla}')

print('\n=== COLUMNAS DE CADA TABLA ===')
for tabla in tablas:
    print(f'\n📋 TABLA: {tabla}')
    columnas = inspector.get_columns(tabla)
    for columna in columnas:
        print(f'   └─ {columna["name"]} ({columna["type"]})')

print('\n=== CLAVES FORÁNEAS ===')
for tabla in tablas:
    print(f'\n🔗 CLAVES FORÁNEAS EN: {tabla}')
    fks = inspector.get_foreign_keys(tabla)
    for fk in fks:
        print(f'   └─ {fk}')