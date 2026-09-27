"""
Fase 3 — Materias primas del tenant Demo.
Inserta 17 materias primas.

IMPORTANTE: costo_promedio está en $/GRAMO, stock_actual está en GRAMOS.
Basado en Excel real de producción.
"""


# ============================================
# DATOS — 17 MATERIAS PRIMAS
# costo_promedio = $/gramo
# stock_actual   = gramos totales
# ============================================
MATERIAS_PRIMAS = [
    {
        'nombre': 'Harina de trigo',
        'unidad_medida': 'kg',
        'unidad_compra': 'Bulto 50 kg',
        'gramos_por_empaque': 50000,
        'costo_promedio': 2.42,          # $/gramo
        'stock_actual': 250000,          # gramos (250 kg)
        'stock_minimo': 50000,           # gramos (50 kg)
        'stock_minimo_empaques': 1,
        'proveedor_nombre': 'Distribuidora El Trigal S.A.S',
    },
    {
        'nombre': 'Harina de maíz',
        'unidad_medida': 'kg',
        'unidad_compra': 'Bulto 50 kg',
        'gramos_por_empaque': 50000,
        'costo_promedio': 2.80,
        'stock_actual': 100000,
        'stock_minimo': 25000,
        'stock_minimo_empaques': 1,
        'proveedor_nombre': 'Distribuidora El Trigal S.A.S',
    },
    {
        'nombre': 'Azúcar',
        'unidad_medida': 'kg',
        'unidad_compra': 'Bulto 25 kg',
        'gramos_por_empaque': 25000,
        'costo_promedio': 2.88,
        'stock_actual': 150000,
        'stock_minimo': 25000,
        'stock_minimo_empaques': 1,
        'proveedor_nombre': 'Distribuidora La 18',
    },
    {
        'nombre': 'Levadura',
        'unidad_medida': 'kg',
        'unidad_compra': 'Paquete 500 g',
        'gramos_por_empaque': 500,
        'costo_promedio': 23.40,
        'stock_actual': 5000,
        'stock_minimo': 1000,
        'stock_minimo_empaques': 2,
        'proveedor_nombre': 'Insumos Panaderos del Sur',
    },
    {
        'nombre': 'Margarina',
        'unidad_medida': 'kg',
        'unidad_compra': 'Balde 15 kg',
        'gramos_por_empaque': 15000,
        'costo_promedio': 10.80,
        'stock_actual': 30000,
        'stock_minimo': 5000,
        'stock_minimo_empaques': 1,
        'proveedor_nombre': 'Distribuidora El Trigal S.A.S',
    },
    {
        'nombre': 'Huevos',
        'unidad_medida': 'unidad',
        'unidad_compra': 'Cubeta 30 (1.500 g)',
        'gramos_por_empaque': 1500,      # 30 huevos × 50g
        'costo_promedio': 7.67,          # $/gramo ($11.500/1.500g)
        'stock_actual': 15000,           # gramos (300 huevos)
        'stock_minimo': 3000,
        'stock_minimo_empaques': 2,
        'proveedor_nombre': 'Avícola Los Andes',
    },
    {
        'nombre': 'Leche',
        'unidad_medida': 'litro',
        'unidad_compra': 'Caja 12 L',
        'gramos_por_empaque': 12000,
        'costo_promedio': 2.30,
        'stock_actual': 60000,
        'stock_minimo': 12000,
        'stock_minimo_empaques': 1,
        'proveedor_nombre': 'Lácteos La Pradera',
    },
    {
        'nombre': 'Agua',
        'unidad_medida': 'litro',
        'unidad_compra': 'Botella 5 L',
        'gramos_por_empaque': 5000,
        'costo_promedio': 0.002,         # $/gramo ($10 / 5.000g)
        'stock_actual': 100000,
        'stock_minimo': 10000,
        'stock_minimo_empaques': 2,
        'proveedor_nombre': 'Distribuidora El Trigal S.A.S',
    },
    {
        'nombre': 'Ojaldre (grasa)',
        'unidad_medida': 'kg',
        'unidad_compra': 'Bloque 15 kg',
        'gramos_por_empaque': 15000,
        'costo_promedio': 10.2467,
        'stock_actual': 15000,
        'stock_minimo': 3000,
        'stock_minimo_empaques': 1,
        'proveedor_nombre': 'Distribuidora El Trigal S.A.S',
    },
    {
        'nombre': 'Margarina Hojaldre',
        'unidad_medida': 'kg',
        'unidad_compra': 'Balde 15 kg',
        'gramos_por_empaque': 15000,
        'costo_promedio': 8.4667,
        'stock_actual': 15000,
        'stock_minimo': 3000,
        'stock_minimo_empaques': 1,
        'proveedor_nombre': 'Distribuidora El Trigal S.A.S',
    },
    {
        'nombre': 'Esencia de mantequilla',
        'unidad_medida': 'ml',
        'unidad_compra': 'Frasco 500 ml',
        'gramos_por_empaque': 500,
        'costo_promedio': 32.00,         # $/gramo
        'stock_actual': 1000,
        'stock_minimo': 100,
        'stock_minimo_empaques': 1,
        'proveedor_nombre': 'Insumos Panaderos del Sur',
    },
    {
        'nombre': 'Sal',
        'unidad_medida': 'kg',
        'unidad_compra': 'Paquete 1 kg',
        'gramos_por_empaque': 1000,
        'costo_promedio': 2.00,
        'stock_actual': 10000,
        'stock_minimo': 2000,
        'stock_minimo_empaques': 2,
        'proveedor_nombre': 'Distribuidora La 18',
    },
    {
        'nombre': 'Mantequilla',
        'unidad_medida': 'kg',
        'unidad_compra': 'Bloque 5 kg',
        'gramos_por_empaque': 5000,
        'costo_promedio': 18.00,
        'stock_actual': 20000,
        'stock_minimo': 5000,
        'stock_minimo_empaques': 1,
        'proveedor_nombre': 'Lácteos La Pradera',
    },
    {
        'nombre': 'Queso costeño',
        'unidad_medida': 'kg',
        'unidad_compra': 'Bloque 1 kg',
        'gramos_por_empaque': 1000,
        'costo_promedio': 16.00,
        'stock_actual': 8000,
        'stock_minimo': 2000,
        'stock_minimo_empaques': 2,
        'proveedor_nombre': 'Lácteos La Pradera',
    },
    {
        'nombre': 'Bocadillo',
        'unidad_medida': 'unidad',
        'unidad_compra': 'Barra 500 g',
        'gramos_por_empaque': 500,
        'costo_promedio': 7.00,          # $/gramo ($3.500 / 500g)
        'stock_actual': 2000,
        'stock_minimo': 500,
        'stock_minimo_empaques': 1,
        'proveedor_nombre': 'Distribuidora La 18',
    },
    {
        'nombre': 'Panela',
        'unidad_medida': 'kg',
        'unidad_compra': 'Panela 500 g',
        'gramos_por_empaque': 500,
        'costo_promedio': 4.00,
        'stock_actual': 15000,
        'stock_minimo': 3000,
        'stock_minimo_empaques': 2,
        'proveedor_nombre': 'Distribuidora La 18',
    },
    {
        'nombre': 'Café molido',
        'unidad_medida': 'kg',
        'unidad_compra': 'Bolsa 500 g',
        'gramos_por_empaque': 500,
        'costo_promedio': 22.00,
        'stock_actual': 3000,
        'stock_minimo': 500,
        'stock_minimo_empaques': 1,
        'proveedor_nombre': 'Café de Nariño',
    },
]


# ============================================
# RUN
# ============================================
def run(schema_name, cursor, dry_run=False):
    """
    Ejecuta la Fase 3.
    Retorna: (filas_insertadas, mensaje)
    """
    filas = 0

    # Obtener panaderia_id
    cursor.execute(f"SELECT id FROM {schema_name}.panaderias LIMIT 1")
    row = cursor.fetchone()
    if not row:
        raise Exception(f"No hay panadería en {schema_name}")
    panaderia_id = row[0]

    # Cache de proveedores por nombre
    cursor.execute(f"SELECT id, nombre FROM {schema_name}.proveedor")
    proveedores_por_nombre = {row[1]: row[0] for row in cursor.fetchall()}

    for mp in MATERIAS_PRIMAS:
        # ¿Ya existe?
        cursor.execute(f"""
            SELECT COUNT(*) FROM {schema_name}.materias_primas WHERE nombre = %s
        """, (mp['nombre'],))
        existe = cursor.fetchone()[0] > 0

        if existe:
            print(f"      - {mp['nombre']} (ya existe)")
            continue

        # Buscar proveedor
        proveedor_id = proveedores_por_nombre.get(mp['proveedor_nombre'])
        if not proveedor_id:
            print(f"      ! {mp['nombre']}: proveedor '{mp['proveedor_nombre']}' no encontrado")
            continue

        if not dry_run:
            cursor.execute(f"""
                INSERT INTO {schema_name}.materias_primas
                (nombre, proveedor_id, unidad_medida, unidad_compra, gramos_por_empaque,
                 costo_promedio, stock_actual, stock_minimo, stock_minimo_empaques,
                 activo, panaderia_id, fecha_ultima_actualizacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s, NOW())
            """, (
                mp['nombre'],
                proveedor_id,
                mp['unidad_medida'],
                mp['unidad_compra'],
                mp['gramos_por_empaque'],
                mp['costo_promedio'],
                mp['stock_actual'],
                mp['stock_minimo'],
                mp['stock_minimo_empaques'],
                panaderia_id,
            ))
            filas += cursor.rowcount
            print(f"      + {mp['nombre']}")
        else:
            filas += 1

    return filas, f"{filas} materias primas insertadas"