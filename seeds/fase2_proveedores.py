"""
Fase 2 — Proveedores del tenant Demo.
Inserta los 6 proveedores típicos de una panadería colombiana.
"""


# ============================================
# DATOS
# ============================================
PROVEEDORES = [
    {
        'nombre': 'Distribuidora El Trigal S.A.S',
        'contacto': 'Carlos Rodríguez',
        'telefono': '+57 315 555 0001',
        'email': 'ventas@eltrigal.co',
        'direccion': 'Bodega 12, Zona Industrial, Pasto',
        'productos_que_suministra': 'Harinas, levaduras, margarina, mejoradores',
        'tiempo_entrega_dias': 2,
        'evaluacion': 5,
    },
    {
        'nombre': 'Lácteos La Pradera',
        'contacto': 'María Gómez',
        'telefono': '+57 315 555 0002',
        'email': 'pedidos@lapradera.co',
        'direccion': 'Km 5 Vía Oriente, Pasto',
        'productos_que_suministra': 'Leche, mantequilla, queso, crema',
        'tiempo_entrega_dias': 1,
        'evaluacion': 5,
    },
    {
        'nombre': 'Avícola Los Andes',
        'contacto': 'Juan Pérez',
        'telefono': '+57 315 555 0003',
        'email': 'ventas@avicolalosandes.co',
        'direccion': 'Calle 22 #15-30, Pasto',
        'productos_que_suministra': 'Huevos, pollo, embutidos',
        'tiempo_entrega_dias': 1,
        'evaluacion': 4,
    },
    {
        'nombre': 'Distribuidora La 18',
        'contacto': 'Ana Martínez',
        'telefono': '+57 315 555 0004',
        'email': 'info@la18.com',
        'direccion': 'Carrera 18 #20-45, Centro, Pasto',
        'productos_que_suministra': 'Azúcar, panela, sal, esencias, colorantes',
        'tiempo_entrega_dias': 2,
        'evaluacion': 4,
    },
    {
        'nombre': 'Café de Nariño',
        'contacto': 'Pedro López',
        'telefono': '+57 315 555 0005',
        'email': 'ventas@cafedenarino.co',
        'direccion': 'Calle 19 #28-10, Pasto',
        'productos_que_suministra': 'Café tostado y molido, chocolate',
        'tiempo_entrega_dias': 3,
        'evaluacion': 5,
    },
    {
        'nombre': 'Insumos Panaderos del Sur',
        'contacto': 'Luisa Fernández',
        'telefono': '+57 315 555 0006',
        'email': 'pedidos@insumospanaderos.co',
        'direccion': 'Carrera 25 #18-50, Pasto',
        'productos_que_suministra': 'Levaduras, mejoradores, esencias, moldes',
        'tiempo_entrega_dias': 3,
        'evaluacion': 4,
    },
]


# ============================================
# RUN
# ============================================
def run(schema_name, cursor, dry_run=False):
    """
    Ejecuta la Fase 2.
    Retorna: (filas_insertadas, mensaje)
    """
    filas = 0

    # Obtener panaderia_id
    cursor.execute(f"SELECT id FROM {schema_name}.panaderias LIMIT 1")
    row = cursor.fetchone()
    if not row:
        raise Exception(f"No hay panadería en {schema_name}")
    panaderia_id = row[0]

    for prov in PROVEEDORES:
        # ¿Ya existe?
        cursor.execute(f"""
            SELECT COUNT(*) FROM {schema_name}.proveedor WHERE nombre = %s
        """, (prov['nombre'],))
        existe = cursor.fetchone()[0] > 0

        if existe:
            print(f"      - {prov['nombre']} (ya existe)")
            continue

        if not dry_run:
            cursor.execute(f"""
                INSERT INTO {schema_name}.proveedor
                (nombre, contacto, telefono, email, direccion,
                 productos_que_suministra, tiempo_entrega_dias, evaluacion,
                 activo, panaderia_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s)
            """, (
                prov['nombre'],
                prov['contacto'],
                prov['telefono'],
                prov['email'],
                prov['direccion'],
                prov['productos_que_suministra'],
                prov['tiempo_entrega_dias'],
                prov['evaluacion'],
                panaderia_id,
            ))
            filas += cursor.rowcount
            print(f"      + {prov['nombre']}")
        else:
            filas += 1

    return filas, f"{filas} proveedores insertados"