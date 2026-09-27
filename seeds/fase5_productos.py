"""
Fase 5 — Productos del tenant Demo.
Crea 12 productos (uno por receta).
Depende de Fase 4 (recetas) y Fase 1 (categorías).
"""


# ============================================
# MAPEO: Receta → Producto (nombre producto = nombre receta)
# ============================================
def run(schema_name, cursor, dry_run=False):
    """
    Ejecuta la Fase 5.
    Retorna: (filas_insertadas, mensaje)
    """
    filas = 0

    # Obtener panaderia_id
    cursor.execute(f"SELECT id FROM {schema_name}.panaderias LIMIT 1")
    row = cursor.fetchone()
    if not row:
        raise Exception(f"No hay panadería en {schema_name}")
    panaderia_id = row[0]

    # Cache de categorías por nombre
    cursor.execute(f"SELECT id, nombre FROM {schema_name}.categorias")
    categorias_por_nombre = {row[1]: row[0] for row in cursor.fetchall()}

    # Obtener recetas
    cursor.execute(f"""
        SELECT id, nombre, descripcion, categoria, precio_venta_real, precio_venta_unitario
        FROM {schema_name}.recetas
        WHERE activo = TRUE
        ORDER BY id
    """)
    recetas = cursor.fetchall()

    for rec in recetas:
        receta_id, nombre, descripcion, categoria, pvp_real, pvp_teorico = rec

        # Precio final: usar PVP real si existe, sino el teórico
        precio_venta = pvp_real if pvp_real and pvp_real > 0 else (pvp_teorico or 0)
        if precio_venta <= 0:
            print(f"      ! {nombre}: sin precio de venta, saltando")
            continue

        # ¿Ya existe el producto?
        cursor.execute(f"""
            SELECT COUNT(*) FROM {schema_name}.productos
            WHERE nombre = %s AND panaderia_id = %s
        """, (nombre, panaderia_id))
        existe = cursor.fetchone()[0] > 0

        if existe:
            print(f"      - {nombre} (ya existe)")
            continue

        # Buscar categoria_id
        cat_id = categorias_por_nombre.get(categoria)
        if not cat_id:
            print(f"      ! {nombre}: categoría '{categoria}' no encontrada")
            continue

        # ¿Es pan?
        es_pan = 'pan' in nombre.lower()

        if not dry_run:
            codigo_barras = f"PROD{receta_id:06d}"

            # Insertar producto
            cursor.execute(f"""
                INSERT INTO {schema_name}.productos
                (nombre, descripcion, categoria_id, stock_actual, stock_minimo,
                 precio_venta, codigo_barras, activo, vida_util_dias, es_pan,
                 tipo_producto, costo_compra, receta_id, panaderia_id, fecha_creacion)
                VALUES (%s, %s, %s, 0, 10, %s, %s, TRUE, 3, %s,
                        'produccion', 0, %s, %s, NOW())
                RETURNING id
            """, (
                nombre,
                descripcion,
                cat_id,
                precio_venta,
                codigo_barras,
                es_pan,
                receta_id,
                panaderia_id,
            ))
            producto_id = cursor.fetchone()[0]
            filas += 1

            # Actualizar receta con el producto_id (bidireccional)
            cursor.execute(f"""
                UPDATE {schema_name}.recetas
                SET producto_id = %s
                WHERE id = %s
            """, (producto_id, receta_id))

            print(f"      + {nombre} (${precio_venta:,.0f})")
        else:
            filas += 1

    return filas, f"{filas} productos insertados"