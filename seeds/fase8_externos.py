"""
Fase 8 — Productos externos del tenant Demo.

Crea 12 productos externos (bebidas, snacks, pasabocas) que la panaderia
compra y revende. NO se generan ventas asociadas en esta fase.

Depende de:
  - Fase 1 (categorias)
  - Fase 2 (proveedores, para proveedor_id)
  - Fase 9 (no, es independiente)

Reglas:
  - panaderia_id SIEMPRE explicito
  - Precios en COP
  - categoria_id usado como texto: Bebidas / Snacks / Pasabocas
"""
import random
from datetime import datetime, timedelta, date


PRODUCTOS_EXTERNOS = [
    # (nombre, categoria, marca, precio_compra, precio_venta, stock_inicial)
    ('Coca-Cola 400ml', 'Bebidas', 'Coca-Cola', 2000, 3500, 30),
    ('Postobon Manzana 400ml', 'Bebidas', 'Postobon', 1700, 3000, 30),
    ('Agua Cristal 600ml', 'Bebidas', 'Cristal', 1000, 2000, 40),
    ('Jugo Hit Mora 500ml', 'Bebidas', 'Hit', 2200, 3500, 25),
    ('Te Frio Lipton 500ml', 'Bebidas', 'Lipton', 2500, 4000, 20),
    ('Papas Margarita 105g', 'Snacks', 'Margarita', 3500, 5500, 25),
    ('De Todito 120g', 'Snacks', 'De Todito', 3800, 6000, 20),
    ('Chitos 100g', 'Snacks', 'Chitos', 2500, 4000, 25),
    ('Mani La Especial 50g', 'Snacks', 'La Especial', 1800, 3000, 30),
    ('Chocolate Corona 30g', 'Pasabocas', 'Corona', 2200, 3500, 25),
    ('Chocorramo 65g', 'Pasabocas', 'Ramo', 2500, 4000, 20),
    ('Galletas Festival x6', 'Pasabocas', 'Festival', 2000, 3500, 30),
]

PROVEEDORES_EXTERNOS = [
    'Distribuidora El Trigal S.A.S',
    'Lácteos La Pradera',
    'Avícola Los Andes',
    'Distribuidora La 18',
    'Café de Nariño',
    'Insumos Panaderos del Sur',
]

MARCAS_PREFIX = 'EXT'


def run(schema_name, cursor, dry_run=False):
    """Ejecuta Fase 8. Retorna (filas, mensaje)."""
    filas = 0

    # --- 1. Obtener panaderia_id ---
    cursor.execute(f"SELECT id FROM {schema_name}.panaderias LIMIT 1")
    row = cursor.fetchone()
    if not row:
        raise Exception(f"No hay panaderia en {schema_name}")
    panaderia_id = row[0]
    if panaderia_id != 27:
        print(f"      ⚠️  Fase 8 diseñada para tenant_27, se encontró {panaderia_id}. Continuando...")

    # --- 2. Cargar proveedores para mapear por nombre ---
    cursor.execute(f"SELECT id, nombre FROM {schema_name}.proveedor")
    prov_por_nombre = {row[1]: row[0] for row in cursor.fetchall()}

    hoy = date.today()

    print(f"      Productos externos a crear: {len(PRODUCTOS_EXTERNOS)}")

    for idx, (nombre, categoria, marca, precio_compra, precio_venta, stock_inicial) in enumerate(PRODUCTOS_EXTERNOS):
        # Codigo de barras unico
        codigo_barras = f"{MARCAS_PREFIX}-{panaderia_id}-{idx+1:03d}"

        # Verificar si ya existe
        cursor.execute(f"""
            SELECT COUNT(*) FROM {schema_name}.productos_externos
            WHERE codigo_barras = %s AND panaderia_id = %s
        """, (codigo_barras, panaderia_id))
        if cursor.fetchone()[0] > 0:
            print(f"      - {nombre} (ya existe)")
            continue

        # Fecha de vencimiento: 30-180 dias desde hoy
        fecha_vencimiento = hoy + timedelta(days=random.randint(30, 180))

        # Fecha ultima compra: hace 5-30 dias
        fecha_ultima_compra = datetime.now() - timedelta(days=random.randint(5, 30))

        # Proveedor aleatorio (resolver a ID via mapeo de Fase 2)
        proveedor_nombre = random.choice(PROVEEDORES_EXTERNOS)
        proveedor_id = prov_por_nombre.get(proveedor_nombre)

        if dry_run:
            filas += 1
            continue

        cursor.execute(f"""
            INSERT INTO {schema_name}.productos_externos
            (codigo_barras, nombre, descripcion, categoria, marca,
             proveedor_id, panaderia_id, stock_actual, stock_minimo,
             fecha_vencimiento, precio_compra, precio_venta,
             total_ventas, total_ingresos, utilidad_total,
             activo, fecha_ultima_compra)
            VALUES (%s, %s, %s, %s, %s,
                    %s, %s, %s, 5,
                    %s, %s, %s,
                    0, 0.0, 0.0,
                    TRUE, %s)
        """, (
            codigo_barras, nombre, f'{marca} - {categoria}', categoria, marca,
            proveedor_id, panaderia_id, stock_inicial,
            fecha_vencimiento, precio_compra, precio_venta,
            fecha_ultima_compra,
        ))
        filas += 1
        print(f"      + {nombre} ({categoria}) - ${precio_venta:,.0f}")

    if not dry_run:
        cursor.connection.commit()

    return filas, f"{filas} productos externos creados"