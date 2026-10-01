"""
Fase 6 — Producción diaria del tenant Demo.
Genera 90 días de órdenes de producción realistas con reposición semanal de MP.

Depende de:
  - Fase 3 (materias primas con stock)
  - Fase 4 (recetas + receta_ingredientes)
  - Fase 5 (productos con receta_id)

Reglas de negocio:
  - 1-2 órdenes por día, 2-3 recetas por orden, 1-3 lotes por receta.
  - Verifica stock antes de descontar (nunca deja negativo).
  - costo_promedio está en $/gramo, stock_actual en gramos.
  - panaderia_id SIEMPRE explícito (evitar default=1).
  - REPOSICIÓN SEMANAL: cada 7 días se rellena el stock de MP hasta
    el 150% del stock inicial (simula compras del dueño).
"""
import random
from datetime import datetime, timedelta, date


DIAS_TOTALES = 90
USUARIO_CREADOR_ID = 1  # admin_27
COMMIT_CADA_N_DIAS = 10  # Punto de guardado parcial
FACTOR_STOCK_OBJETIVO = 1.5  # 150% del stock inicial
DIAS_ENTRE_REPOSICIONES = 7  # Reposición semanal


def run(schema_name, cursor, dry_run=False):
    """Ejecuta la Fase 6 con reposición semanal. Retorna (filas, mensaje)."""
    filas = 0

    # --- 1. Obtener panaderia_id ---
    cursor.execute(f"SELECT id FROM {schema_name}.panaderias LIMIT 1")
    row = cursor.fetchone()
    if not row:
        raise Exception(f"No hay panadería en {schema_name}")
    panaderia_id = row[0]

    if panaderia_id != 27:
        print(f"      ⚠️  Fase 6 diseñada para tenant_27, se encontró {panaderia_id}. Continuando...")

    # --- 2. Cargar recetas activas con su producto_id ---
    cursor.execute(f"""
        SELECT id, nombre, unidades_obtenidas, producto_id
        FROM {schema_name}.recetas
        WHERE activo = TRUE AND producto_id IS NOT NULL
        ORDER BY id
    """)
    recetas = cursor.fetchall()
    if not recetas:
        raise Exception("No hay recetas activas con producto_id")

    # --- 3. Cargar ingredientes por receta (cache en memoria) ---
    cursor.execute(f"""
        SELECT receta_id, materia_prima_id, cantidad_gramos
        FROM {schema_name}.receta_ingredientes
        ORDER BY receta_id, id
    """)
    ingredientes_por_receta = {}
    for receta_id, mp_id, gramos in cursor.fetchall():
        ingredientes_por_receta.setdefault(receta_id, []).append(
            (mp_id, float(gramos or 0))
        )

    # --- 4. Cargar stock y costo de MP (cache) ---
    cursor.execute(f"""
        SELECT id, stock_actual, costo_promedio
        FROM {schema_name}.materias_primas
        WHERE activo = TRUE AND panaderia_id = %s
    """, (panaderia_id,))
    mp_stock = {}
    mp_costo = {}
    for mp_id, stock, costo in cursor.fetchall():
        mp_stock[mp_id] = float(stock or 0)
        mp_costo[mp_id] = float(costo or 0)

    # --- 5. Definir stock objetivo por MP (1.5x stock actual de arranque) ---
    # Se asume que el stock_actual actual es el "inicial" del seed.
    # Si lo quieres basar en los valores de Fase 3, hay que resetear antes.
    mp_objetivo = {
        mp_id: stock * FACTOR_STOCK_OBJETIVO
        for mp_id, stock in mp_stock.items()
    }

    # --- 6. Cargar stock actual de productos (cache) ---
    cursor.execute(f"""
        SELECT id, stock_actual
        FROM {schema_name}.productos
        WHERE panaderia_id = %s
    """, (panaderia_id,))
    producto_stock = {}
    for prod_id, stock in cursor.fetchall():
        producto_stock[prod_id] = int(stock or 0)

    # --- 7. Rango de fechas ---
    hoy = date.today()
    fecha_inicio = hoy - timedelta(days=DIAS_TOTALES)

    print(f"      Rango: {fecha_inicio} → {hoy} ({DIAS_TOTALES} días)")
    print(f"      Recetas activas: {len(recetas)}")
    print(f"      MP con stock: {len(mp_stock)}")
    print(f"      Reposición cada {DIAS_ENTRE_REPOSICIONES} días "
          f"(objetivo = {int(FACTOR_STOCK_OBJETIVO*100)}% del inicial)")

    # --- 8. Bucle principal por día ---
    for i in range(DIAS_TOTALES):
        fecha_dia = fecha_inicio + timedelta(days=i)

        # Idempotencia: ¿ya hay órdenes ese día?
        cursor.execute(f"""
            SELECT COUNT(*) FROM {schema_name}.ordenes_produccion
            WHERE fecha_produccion = %s AND panaderia_id = %s
        """, (fecha_dia, panaderia_id))
        if cursor.fetchone()[0] > 0:
            continue

        # Reposición semanal (día 7, 14, 21, ..., 84)
        if (i + 1) % DIAS_ENTRE_REPOSICIONES == 0:
            filas_rep = _reponer_mp(
                cursor, schema_name, panaderia_id, fecha_dia,
                mp_stock, mp_objetivo, dry_run,
            )
            filas += filas_rep
            if filas_rep > 0:
                print(f"      📦 Día {i+1}: reposición de {filas_rep} MP")

        # ¿Cuántas órdenes hoy? 1-2
        num_ordenes = random.choice([1, 1, 2])
        for _ in range(num_ordenes):
            filas += _crear_orden(
                cursor, schema_name, panaderia_id, fecha_dia,
                recetas, ingredientes_por_receta,
                mp_stock, mp_costo, producto_stock,
                USUARIO_CREADOR_ID, dry_run,
            )

        # Commit parcial cada N días
        if not dry_run and (i + 1) % COMMIT_CADA_N_DIAS == 0:
            cursor.connection.commit()
            print(f"      💾 Checkpoint día {i+1}/{DIAS_TOTALES} — {filas} filas")

    if not dry_run:
        cursor.connection.commit()

    return filas, f"{filas} filas en {DIAS_TOTALES} días (con reposición semanal)"


def _reponer_mp(cursor, schema_name, panaderia_id, fecha_dia,
                mp_stock, mp_objetivo, dry_run):
    """Repone MP hasta el stock objetivo (simula compras semanales)."""
    filas = 0
    hora_compra = datetime.combine(
        fecha_dia, datetime.min.time()
    ) + timedelta(hours=3)  # 3 AM, antes de la producción

    # Obtener un producto_id de referencia (historial_inventario.producto_id es NOT NULL)
    cursor.execute(f"""
        SELECT id FROM {schema_name}.productos
        WHERE panaderia_id = %s LIMIT 1
    """, (panaderia_id,))
    prod_ref_row = cursor.fetchone()
    prod_ref = prod_ref_row[0] if prod_ref_row else None

    for mp_id, objetivo in mp_objetivo.items():
        actual = mp_stock.get(mp_id, 0)
        if actual >= objetivo:
            continue
        cantidad_comprada = objetivo - actual
        nuevo_stock = objetivo

        if dry_run:
            mp_stock[mp_id] = nuevo_stock
            filas += 1
            continue

        # UPDATE stock
        cursor.execute(f"""
            UPDATE {schema_name}.materias_primas
            SET stock_actual = %s, fecha_ultima_actualizacion = NOW()
            WHERE id = %s AND panaderia_id = %s
        """, (nuevo_stock, mp_id, panaderia_id))

        # Registro en historial_inventario
        cursor.execute(f"""
            INSERT INTO {schema_name}.historial_inventario
            (panaderia_id, producto_id, cantidad_anterior, cantidad_nueva,
             tipo_movimiento, usuario_id, fecha_movimiento, observaciones,
             materia_prima_id, cantidad_utilizada)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            panaderia_id, prod_ref,
            int(actual), int(nuevo_stock),
            'COMPRA_REPOSICION', USUARIO_CREADOR_ID,
            hora_compra,
            f'Reposición semanal MP id={mp_id}',
            mp_id, cantidad_comprada,
        ))

        mp_stock[mp_id] = nuevo_stock
        filas += 1

    return filas


def _crear_orden(cursor, schema_name, panaderia_id, fecha_dia,
                 recetas, ingredientes_por_receta,
                 mp_stock, mp_costo, producto_stock,
                 usuario_id, dry_run):
    """Crea UNA orden de producción con 2-3 recetas. Retorna filas insertadas."""
    filas = 0

    # Elegir 2-3 recetas al azar
    num_recetas = random.choice([2, 2, 3])
    recetas_del_dia = random.sample(recetas, min(num_recetas, len(recetas)))

    # Hora aleatoria de producción
    hora = random.randint(4, 6)
    minuto = random.randint(0, 59)
    fecha_hora_orden = datetime.combine(
        fecha_dia, datetime.min.time()
    ) + timedelta(hours=hora, minutes=minuto)

    for receta in recetas_del_dia:
        receta_id, nombre, unidades_obtenidas, producto_id = receta
        ingredientes = ingredientes_por_receta.get(receta_id, [])
        if not ingredientes:
            continue

        # ¿Cuántos lotes? 1-3
        lotes_deseados = random.randint(1, 3)

        # Verificar stock: ¿cuántos lotes puedo hacer?
        lotes_posibles = lotes_deseados
        for mp_id, gramos_por_lote in ingredientes:
            if gramos_por_lote <= 0:
                continue
            stock_disp = mp_stock.get(mp_id, 0)
            max_lotes_mp = int(stock_disp // gramos_por_lote)
            lotes_posibles = min(lotes_posibles, max_lotes_mp)

        if lotes_posibles <= 0:
            continue

        lotes = lotes_posibles
        unidades = int(unidades_obtenidas or 0) * lotes

        # Calcular costo total y consumo
        costo_real = 0.0
        for mp_id, gramos_por_lote in ingredientes:
            gramos_total = gramos_por_lote * lotes
            costo_mp = gramos_total * mp_costo.get(mp_id, 0)
            costo_real += costo_mp

        if dry_run:
            # Simular descuento en cache
            for mp_id, gramos_por_lote in ingredientes:
                mp_stock[mp_id] = mp_stock.get(mp_id, 0) - gramos_por_lote * lotes
                if mp_stock[mp_id] < 0:
                    mp_stock[mp_id] = 0
            producto_stock[producto_id] = producto_stock.get(producto_id, 0) + unidades
            filas += 1
            continue

        # --- INSERT orden_produccion ---
        cursor.execute(f"""
            INSERT INTO {schema_name}.ordenes_produccion
            (receta_id, cantidad_producir, cantidad_real,
             fecha_orden, fecha_produccion, estado,
             costo_real, stock_generado,
             usuario_creacion_id, panaderia_id)
            VALUES (%s, %s, %s, %s, %s, 'COMPLETADA',
                    %s, TRUE, %s, %s)
            RETURNING id
        """, (
            receta_id, unidades, unidades,
            fecha_hora_orden, fecha_dia,
            costo_real, usuario_id, panaderia_id,
        ))
        orden_id = cursor.fetchone()[0]
        filas += 1

        # --- Descontar MP + registrar historial ---
        for mp_id, gramos_por_lote in ingredientes:
            gramos_total = gramos_por_lote * lotes
            stock_antes = mp_stock.get(mp_id, 0)
            stock_despues = stock_antes - gramos_total
            if stock_despues < 0:
                stock_despues = 0

            cursor.execute(f"""
                UPDATE {schema_name}.materias_primas
                SET stock_actual = %s, fecha_ultima_actualizacion = NOW()
                WHERE id = %s AND panaderia_id = %s
            """, (stock_despues, mp_id, panaderia_id))

            mp_stock[mp_id] = stock_despues

            cursor.execute(f"""
                INSERT INTO {schema_name}.historial_inventario
                (panaderia_id, producto_id, cantidad_anterior, cantidad_nueva,
                 tipo_movimiento, usuario_id, fecha_movimiento, observaciones,
                 materia_prima_id, orden_produccion_id, cantidad_utilizada)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                panaderia_id, producto_id,
                int(stock_antes), int(stock_despues),
                'CONSUMO_PRODUCCION', usuario_id,
                fecha_hora_orden,
                f'Consumo para orden #{orden_id} ({nombre})',
                mp_id, orden_id, gramos_total,
            ))
            filas += 1

        # --- Sumar stock de producto terminado ---
        prod_stock_antes = producto_stock.get(producto_id, 0)
        prod_stock_despues = prod_stock_antes + unidades

        cursor.execute(f"""
            UPDATE {schema_name}.productos
            SET stock_actual = %s
            WHERE id = %s AND panaderia_id = %s
        """, (prod_stock_despues, producto_id, panaderia_id))
        producto_stock[producto_id] = prod_stock_despues

        # --- stock_productos: INSERT si no existe, UPDATE si existe ---
        cursor.execute(f"""
            SELECT id FROM {schema_name}.stock_productos
            WHERE producto_id = %s AND panaderia_id = %s
        """, (producto_id, panaderia_id))
        sp_row = cursor.fetchone()

        if sp_row:
            cursor.execute(f"""
                UPDATE {schema_name}.stock_productos
                SET stock_actual = %s, fecha_actualizacion = NOW()
                WHERE id = %s
            """, (prod_stock_despues, sp_row[0]))
        else:
            cursor.execute(f"""
                INSERT INTO {schema_name}.stock_productos
                (panaderia_id, producto_id, stock_actual, stock_minimo,
                 stock_maximo, fecha_actualizacion, receta_id)
                VALUES (%s, %s, %s, 10, 0, NOW(), %s)
            """, (panaderia_id, producto_id, prod_stock_despues, receta_id))

        # --- Registro ENTRADA en historial_inventario ---
        cursor.execute(f"""
            INSERT INTO {schema_name}.historial_inventario
            (panaderia_id, producto_id, cantidad_anterior, cantidad_nueva,
             tipo_movimiento, usuario_id, fecha_movimiento, observaciones,
             orden_produccion_id, cantidad_utilizada)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            panaderia_id, producto_id,
            prod_stock_antes, prod_stock_despues,
            'ENTRADA_PRODUCCION', usuario_id,
            fecha_hora_orden,
            f'Producción orden #{orden_id} ({nombre}) — {lotes} lote(s)',
            orden_id, unidades,
        ))
        filas += 1

    return filas