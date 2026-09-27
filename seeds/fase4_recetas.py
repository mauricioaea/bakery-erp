"""
Fase 4 — Recetas y fórmulas del tenant Demo.
Inserta 12 recetas con sus ingredientes.
Depende de Fase 3 (materias primas).
"""


# ============================================
# RECETAS
# Cada receta tiene: nombre, descripcion, categoria, peso_unidad_gramos,
# porcentaje_perdida, unidades_obtenidas, precio_venta, ingredientes[]
# ============================================
RECETAS = [
    {
        'nombre': 'Pan de Yema',
        'descripcion': 'Pan tradicional de yema, esponjoso y dorado',
        'categoria': 'Panadería',
        'peso_unidad_gramos': 50,
        'porcentaje_perdida': 10.0,
        'unidades_obtenidas': 42,
        'precio_venta_real': 500,
        'ingredientes': [
            {'mp': 'Harina de trigo', 'gramos': 1000},
            {'mp': 'Azúcar', 'gramos': 120},
            {'mp': 'Levadura', 'gramos': 20},
            {'mp': 'Margarina', 'gramos': 120},
            {'mp': 'Huevos', 'gramos': 100},
            {'mp': 'Agua', 'gramos': 450},
            {'mp': 'Ojaldre (grasa)', 'gramos': 127},
            {'mp': 'Margarina Hojaldre', 'gramos': 127},
            {'mp': 'Esencia de mantequilla', 'gramos': 6},
            {'mp': 'Sal', 'gramos': 20},
        ],
    },
    {
        'nombre': 'Pan Blandito',
        'descripcion': 'Pan suave y esponjoso, ideal para el desayuno',
        'categoria': 'Panadería',
        'peso_unidad_gramos': 60,
        'porcentaje_perdida': 10.0,
        'unidades_obtenidas': 30,
        'precio_venta_real': 1500,
        'ingredientes': [
            {'mp': 'Harina de trigo', 'gramos': 1500},
            {'mp': 'Azúcar', 'gramos': 100},
            {'mp': 'Levadura', 'gramos': 30},
            {'mp': 'Mantequilla', 'gramos': 100},
            {'mp': 'Huevos', 'gramos': 100},
            {'mp': 'Leche', 'gramos': 300},
            {'mp': 'Sal', 'gramos': 15},
        ],
    },
    {
        'nombre': 'Pan de Bono',
        'descripcion': 'Pan de bono con queso costeño',
        'categoria': 'Panadería',
        'peso_unidad_gramos': 65,
        'porcentaje_perdida': 8.0,
        'unidades_obtenidas': 25,
        'precio_venta_real': 1200,
        'ingredientes': [
            {'mp': 'Harina de maíz', 'gramos': 800},
            {'mp': 'Queso costeño', 'gramos': 400},
            {'mp': 'Huevos', 'gramos': 200},
            {'mp': 'Mantequilla', 'gramos': 100},
            {'mp': 'Leche', 'gramos': 200},
            {'mp': 'Sal', 'gramos': 10},
        ],
    },
    {
        'nombre': 'Pan de Yuca',
        'descripcion': 'Pan de yuca con queso, tradicional',
        'categoria': 'Panadería',
        'peso_unidad_gramos': 50,
        'porcentaje_perdida': 8.0,
        'unidades_obtenidas': 30,
        'precio_venta_real': 1500,
        'ingredientes': [
            {'mp': 'Harina de maíz', 'gramos': 1000},
            {'mp': 'Queso costeño', 'gramos': 400},
            {'mp': 'Huevos', 'gramos': 100},
            {'mp': 'Leche', 'gramos': 200},
            {'mp': 'Sal', 'gramos': 12},
        ],
    },
    {
        'nombre': 'Buñuelos',
        'descripcion': 'Buñuelos de queso, crujientes por fuera, suaves por dentro',
        'categoria': 'Panadería',
        'peso_unidad_gramos': 70,
        'porcentaje_perdida': 12.0,
        'unidades_obtenidas': 20,
        'precio_venta_real': 1000,
        'ingredientes': [
            {'mp': 'Harina de maíz', 'gramos': 600},
            {'mp': 'Queso costeño', 'gramos': 400},
            {'mp': 'Huevos', 'gramos': 200},
            {'mp': 'Azúcar', 'gramos': 80},
            {'mp': 'Mantequilla', 'gramos': 60},
            {'mp': 'Sal', 'gramos': 8},
        ],
    },
    {
        'nombre': 'Almojábanas',
        'descripcion': 'Almojábanas de queso costeño',
        'categoria': 'Panadería',
        'peso_unidad_gramos': 60,
        'porcentaje_perdida': 10.0,
        'unidades_obtenidas': 24,
        'precio_venta_real': 1500,
        'ingredientes': [
            {'mp': 'Harina de maíz', 'gramos': 700},
            {'mp': 'Queso costeño', 'gramos': 400},
            {'mp': 'Huevos', 'gramos': 200},
            {'mp': 'Leche', 'gramos': 200},
            {'mp': 'Mantequilla', 'gramos': 80},
            {'mp': 'Sal', 'gramos': 8},
        ],
    },
    {
        'nombre': 'Pan Francés',
        'descripcion': 'Pan francés crujiente',
        'categoria': 'Panadería',
        'peso_unidad_gramos': 50,
        'porcentaje_perdida': 10.0,
        'unidades_obtenidas': 20,
        'precio_venta_real': 800,
        'ingredientes': [
            {'mp': 'Harina de trigo', 'gramos': 1000},
            {'mp': 'Levadura', 'gramos': 15},
            {'mp': 'Sal', 'gramos': 20},
            {'mp': 'Agua', 'gramos': 600},
        ],
    },
    {
        'nombre': 'Ponqué Casero',
        'descripcion': 'Ponqué casero tradicional, grande',
        'categoria': 'Pastelería',
        'peso_unidad_gramos': 800,
        'porcentaje_perdida': 8.0,
        'unidades_obtenidas': 1,
        'precio_venta_real': 15000,
        'ingredientes': [
            {'mp': 'Harina de trigo', 'gramos': 500},
            {'mp': 'Azúcar', 'gramos': 400},
            {'mp': 'Mantequilla', 'gramos': 300},
            {'mp': 'Huevos', 'gramos': 400},
            {'mp': 'Leche', 'gramos': 200},
            {'mp': 'Esencia de mantequilla', 'gramos': 10},
        ],
    },
    {
        'nombre': 'Milhojas',
        'descripcion': 'Milhojas de arequipe',
        'categoria': 'Pastelería',
        'peso_unidad_gramos': 80,
        'porcentaje_perdida': 5.0,
        'unidades_obtenidas': 12,
        'precio_venta_real': 2500,
        'ingredientes': [
            {'mp': 'Harina de trigo', 'gramos': 500},
            {'mp': 'Ojaldre (grasa)', 'gramos': 300},
            {'mp': 'Bocadillo', 'gramos': 200},
            {'mp': 'Azúcar', 'gramos': 100},
            {'mp': 'Mantequilla', 'gramos': 50},
        ],
    },
    {
        'nombre': 'Empanada de Carne',
        'descripcion': 'Empanada de carne molida',
        'categoria': 'Pasabocas',
        'peso_unidad_gramos': 80,
        'porcentaje_perdida': 5.0,
        'unidades_obtenidas': 25,
        'precio_venta_real': 2000,
        'ingredientes': [
            {'mp': 'Harina de maíz', 'gramos': 800},
            {'mp': 'Margarina', 'gramos': 100},
            {'mp': 'Huevos', 'gramos': 100},
            {'mp': 'Sal', 'gramos': 10},
        ],
    },
    {
        'nombre': 'Empanada de Pollo',
        'descripcion': 'Empanada de pollo desmechado',
        'categoria': 'Pasabocas',
        'peso_unidad_gramos': 80,
        'porcentaje_perdida': 5.0,
        'unidades_obtenidas': 25,
        'precio_venta_real': 2000,
        'ingredientes': [
            {'mp': 'Harina de maíz', 'gramos': 800},
            {'mp': 'Margarina', 'gramos': 100},
            {'mp': 'Huevos', 'gramos': 100},
            {'mp': 'Sal', 'gramos': 10},
        ],
    },
    {
        'nombre': 'Arepa de Choclo',
        'descripcion': 'Arepa de choclo con queso',
        'categoria': 'Pasabocas',
        'peso_unidad_gramos': 100,
        'porcentaje_perdida': 8.0,
        'unidades_obtenidas': 20,
        'precio_venta_real': 2500,
        'ingredientes': [
            {'mp': 'Harina de maíz', 'gramos': 600},
            {'mp': 'Queso costeño', 'gramos': 300},
            {'mp': 'Mantequilla', 'gramos': 100},
            {'mp': 'Leche', 'gramos': 200},
            {'mp': 'Sal', 'gramos': 8},
        ],
    },
]


# ============================================
# HELPERS
# ============================================
def _costo_ingrediente(mp_data, gramos):
    """
    Calcula el costo de un ingrediente.

    REGLA DEL PROYECTO: costo_promedio está en $/GRAMO.
    Fórmula: costo = gramos * costo_por_gramo
    (igual que app.py: costo_ingrediente = cantidad_gramos * materia_prima.costo_promedio)
    """
    return gramos * mp_data['costo_promedio']

# ============================================
# RUN
# ============================================
def run(schema_name, cursor, dry_run=False):
    """
    Ejecuta la Fase 4.
    Retorna: (filas_insertadas, mensaje)
    """
    filas = 0

    # Obtener panaderia_id
    cursor.execute(f"SELECT id FROM {schema_name}.panaderias LIMIT 1")
    row = cursor.fetchone()
    if not row:
        raise Exception(f"No hay panadería en {schema_name}")
    panaderia_id = row[0]

    # Cache de materias primas
    cursor.execute(f"""
        SELECT id, nombre, unidad_medida, costo_promedio, gramos_por_empaque
        FROM {schema_name}.materias_primas
    """)
    mps = {}
    for row in cursor.fetchall():
        mps[row[1]] = {
            'id': row[0],
            'unidad_medida': row[2],
            'costo_promedio': row[3],
            'gramos_por_empaque': row[4],
        }

    for rec in RECETAS:
        # ¿Ya existe?
        cursor.execute(f"""
            SELECT id FROM {schema_name}.recetas WHERE nombre = %s
        """, (rec['nombre'],))
        row = cursor.fetchone()
        if row:
            print(f"      - {rec['nombre']} (ya existe)")
            continue

        # Calcular peso total de la masa y costo de materias primas
        peso_total_masa = sum(ing['gramos'] for ing in rec['ingredientes'])
        costo_mp = 0
        for ing in rec['ingredientes']:
            mp = mps.get(ing['mp'])
            if not mp:
                print(f"      ! {rec['nombre']}: MP '{ing['mp']}' no encontrada")
                continue
            costo_mp += _costo_ingrediente(mp, ing['gramos'])

        # Calcular CIF (45%) y costo total
        porcentaje_cif = 45.0
        costo_indirecto = costo_mp * (porcentaje_cif / 100.0)
        costo_total = costo_mp + costo_indirecto

        # Precio unitario teórico
        unidades = rec['unidades_obtenidas']
        precio_unitario = (costo_total / unidades * 1.45) if unidades > 0 else 0

        if not dry_run:
            # Insertar receta
            cursor.execute(f"""
                INSERT INTO {schema_name}.recetas
                (nombre, descripcion, categoria, peso_unidad_gramos, porcentaje_perdida,
                 costo_total, precio_venta, activo, porcentaje_cif, porcentaje_merma_manejo,
                 margen_deseado, precio_venta_real, precio_venta_unitario,
                 peso_total_masa, unidades_obtenidas, peso_horneado_unidad,
                 costo_materias_primas, costo_indirecto, margen_ganancia,
                 panaderia_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, NOW())
                RETURNING id
            """, (
                rec['nombre'],
                rec['descripcion'],
                rec['categoria'],
                rec['peso_unidad_gramos'],
                rec['porcentaje_perdida'],
                costo_total,
                rec['precio_venta_real'],
                porcentaje_cif,
                2.0,
                30.0,
                rec['precio_venta_real'],
                precio_unitario,
                peso_total_masa,
                unidades,
                rec['peso_unidad_gramos'] * (1 - rec['porcentaje_perdida'] / 100.0),
                costo_mp,
                costo_indirecto,
                30.0,
                panaderia_id,
            ))
            receta_id = cursor.fetchone()[0]
            filas += 1

            # Insertar ingredientes
            for ing in rec['ingredientes']:
                mp = mps.get(ing['mp'])
                if not mp:
                    continue

                costo_ing = _costo_ingrediente(mp, ing['gramos'])
                porcentaje_aplicado = (ing['gramos'] / peso_total_masa) * 100.0 if peso_total_masa > 0 else 0
                costo_unitario = (costo_ing / ing['gramos']) if ing['gramos'] > 0 else 0

                cursor.execute(f"""
                    INSERT INTO {schema_name}.receta_ingredientes
                    (panaderia_id, receta_id, materia_prima_id, cantidad,
                     porcentaje_aplicado, cantidad_gramos, costo_ingrediente,
                     unidad_medida, costo_unitario, costo_total)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    panaderia_id,
                    receta_id,
                    mp['id'],
                    ing['gramos'],
                    porcentaje_aplicado,
                    ing['gramos'],
                    costo_ing,
                    'g',
                    costo_unitario,
                    costo_ing,
                ))
                filas += 1

            print(f"      + {rec['nombre']} ({len(rec['ingredientes'])} ingredientes, costo ${costo_total:.0f})")
        else:
            filas += 1 + len(rec['ingredientes'])

    return filas, f"{filas} filas insertadas (12 recetas + ingredientes)"