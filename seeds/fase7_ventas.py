"""
Fase 7 — Ventas del tenant Demo.
Genera ~3.500 ventas en 90 días que consumen el stock de Fase 6.

Depende de:
  - Fase 5 (productos con precio_venta)
  - Fase 6 (stock de productos)
  - Fase 1 (usuarios admin_27, cajero_27)

Reglas de negocio:
  - 35-45 ventas/día con factor estacional (sáb +20%, dom -30%).
  - 1-3 productos por venta, ponderados por popularidad.
  - Cantidades 1-5 (ponderado a 1-2).
  - Métodos de pago: 60% efectivo, 30% transferencia, 10% tarjeta.
  - Horarios con picos 7-9am y 4-6pm.
  - Cliente: siempre NULL (no hay clientes en el tenant).
  - Usuario: 70% cajero_27, 30% admin_27.
  - Descuenta stock. Si no alcanza, reduce cantidad. Si stock=0, salta producto.
  - Genera 1 fila en jornadas_ventas por cada día con ventas.
"""
import random
from datetime import datetime, timedelta, date


DIAS_TOTALES = 90
COMMIT_CADA_N_DIAS = 10

# IDs de usuarios del tenant_27
CAJERO_ID = 3   # cajero_27
ADMIN_ID = 1    # admin_27

# Ponderación de productos por popularidad (peso relativo)
# Alta rotación: 60% del volumen. Media: 30%. Baja: 10%.
PESO_PRODUCTOS = {
    1: 20,   # Pan de Yema
    2: 15,   # Pan Blandito
    7: 15,   # Pan Francés
    13: 10,  # Roscon
    3: 6,    # Pan de Bono
    4: 5,    # Pan de Yuca
    5: 5,    # Buñuelos
    6: 5,    # Almojábanas
    10: 4,   # Empanada de Carne
    11: 4,   # Empanada de Pollo
    12: 5,   # Arepa de Choclo
    8: 1,    # Ponqué Casero
    9: 1,    # Milhojas
}

# Ponderación de métodos de pago
METODOS_PAGO = [
    ('efectivo', 60),
    ('transferencia', 30),
    ('tarjeta', 10),
]

# Horas con picos (7-9am y 4-6pm)
HORAS_PICO_MANANA = list(range(7, 10))   # 7, 8, 9
HORAS_PICO_TARDE = list(range(16, 19))   # 16, 17, 18
HORAS_RESTO = [6, 10, 11, 12, 13, 14, 15, 19, 20]


def run(schema_name, cursor, dry_run=False):
    """Ejecuta Fase 7. Retorna (filas_insertadas, mensaje)."""
    filas = 0

    # --- 1. Obtener panaderia_id ---
    cursor.execute(f"SELECT id FROM {schema_name}.panaderias LIMIT 1")
    row = cursor.fetchone()
    if not row:
        raise Exception(f"No hay panadería en {schema_name}")
    panaderia_id = row[0]
    if panaderia_id != 27:
        print(f"      ⚠️  Fase 7 diseñada para tenant_27, se encontró {panaderia_id}. Continuando...")

    # --- 2. Cargar productos con stock + precio ---
    cursor.execute(f"""
        SELECT id, nombre, stock_actual, precio_venta
        FROM {schema_name}.productos
        WHERE activo = TRUE AND panaderia_id = %s AND precio_venta > 0
        ORDER BY id
    """, (panaderia_id,))
    productos_raw = cursor.fetchall()
    productos = {}
    for pid, nombre, stock, precio in productos_raw:
        productos[pid] = {
            'id': pid,
            'nombre': nombre,
            'stock': int(stock or 0),
            'precio': float(precio or 0),
        }
    if not productos:
        raise Exception("No hay productos activos con precio")

    # --- 3. Construir lista ponderada de productos ---
    ids_disponibles = list(PESO_PRODUCTOS.keys())
    pesos = [PESO_PRODUCTOS[pid] for pid in ids_disponibles]
    # Filtrar solo los que existen en BD
    ids_disponibles = [pid for pid in ids_disponibles if pid in productos]
    pesos = [PESO_PRODUCTOS[pid] for pid in ids_disponibles]

    # --- 4. Rango de fechas ---
    hoy = date.today()
    fecha_inicio = hoy - timedelta(days=DIAS_TOTALES)

    print(f"      Rango: {fecha_inicio} → {hoy} ({DIAS_TOTALES} días)")
    print(f"      Productos activos: {len(productos)}")

    # --- 5. Bucle por día ---
    for i in range(DIAS_TOTALES):
        fecha_dia = fecha_inicio + timedelta(days=i)

        # Idempotencia: ¿ya hay ventas ese día?
        cursor.execute(f"""
            SELECT COUNT(*) FROM {schema_name}.ventas
            WHERE DATE(fecha_hora) = %s AND panaderia_id = %s
        """, (fecha_dia, panaderia_id))
        if cursor.fetchone()[0] > 0:
            continue

        # Factor estacional
        dia_semana = fecha_dia.weekday()  # 0=lunes, 6=domingo
        if dia_semana == 5:    # sábado
            num_ventas = random.randint(42, 50)
        elif dia_semana == 6:  # domingo
            num_ventas = random.randint(25, 30)
        else:                  # lunes-viernes
            num_ventas = random.randint(35, 42)

        # Acumuladores del día
        total_dia = 0.0
        total_efectivo = 0.0
        total_transferencia = 0.0
        total_tarjeta = 0.0
        ventas_dia = 0

        for _ in range(num_ventas):
            resultado = _crear_venta(
                cursor, schema_name, panaderia_id, fecha_dia,
                productos, ids_disponibles, pesos, dry_run,
            )
            if resultado is None:
                continue
            filas_detalle, total, metodo = resultado
            filas += 1 + filas_detalle
            total_dia += total
            ventas_dia += 1
            if metodo == 'efectivo':
                total_efectivo += total
            elif metodo == 'transferencia':
                total_transferencia += total
            elif metodo == 'tarjeta':
                total_tarjeta += total

        # --- Jornada del día ---
        if ventas_dia > 0:
            if not dry_run:
                # Hora de cierre: 20:30
                cerrada_at = datetime.combine(
                    fecha_dia, datetime.min.time()
                ) + timedelta(hours=20, minutes=30)

                cursor.execute(f"""
                    INSERT INTO {schema_name}.jornadas_ventas
                    (total_ventas, estado, panaderia_id, fecha,
                     total_efectivo, total_transferencia, total_tarjeta,
                     cerrada_at)
                    VALUES (%s, 'CERRADA', %s, %s, %s, %s, %s, %s)
                """, (
                    total_dia, panaderia_id, fecha_dia,
                    total_efectivo, total_transferencia, total_tarjeta,
                    cerrada_at,
                ))
                filas += 1

        # Commit parcial
        if not dry_run and (i + 1) % COMMIT_CADA_N_DIAS == 0:
            cursor.connection.commit()
            print(f"      💾 Checkpoint día {i+1}/{DIAS_TOTALES} — {filas} filas")

    if not dry_run:
        cursor.connection.commit()

    return filas, f"{filas} filas en {DIAS_TOTALES} días"


def _crear_venta(cursor, schema_name, panaderia_id, fecha_dia,
                 productos, ids_disponibles, pesos, dry_run):
    """Crea UNA venta. Retorna (filas_detalle, total, metodo_pago) o None."""
    # Elegir 1-3 productos ponderados
    num_lineas = random.choice([1, 1, 1, 2, 2, 3])  # ponderado a 1
    ids_elegidos = set()
    intentos = 0
    while len(ids_elegidos) < num_lineas and intentos < 20:
        intentos += 1
        pid = random.choices(ids_disponibles, weights=pesos, k=1)[0]
        ids_elegidos.add(pid)

    # Construir líneas verificando stock
    lineas = []
    for pid in ids_elegidos:
        prod = productos[pid]
        if prod['stock'] <= 0:
            continue
        # Cantidad 1-5 ponderada a 1-2
        cant = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5])[0]
        cant = min(cant, prod['stock'])
        if cant <= 0:
            continue
        subtotal = cant * prod['precio']
        lineas.append({
            'producto_id': pid,
            'cantidad': cant,
            'precio_unitario': prod['precio'],
            'subtotal': subtotal,
        })

    if not lineas:
        return None  # ningún producto tenía stock

    total = sum(l['subtotal'] for l in lineas)

    # Método de pago
    metodos = [m[0] for m in METODOS_PAGO]
    pesos_metodo = [m[1] for m in METODOS_PAGO]
    metodo_pago = random.choices(metodos, weights=pesos_metodo, k=1)[0]

    # Hora
    r = random.random()
    if r < 0.35:
        hora = random.choice(HORAS_PICO_MANANA)
    elif r < 0.65:
        hora = random.choice(HORAS_PICO_TARDE)
    else:
        hora = random.choice(HORAS_RESTO)
    minuto = random.randint(0, 59)
    segundo = random.randint(0, 59)
    fecha_hora = datetime.combine(
        fecha_dia, datetime.min.time()
    ) + timedelta(hours=hora, minutes=minuto, seconds=segundo)

    # Usuario
    usuario_id = CAJERO_ID if random.random() < 0.70 else ADMIN_ID

    if dry_run:
        # Simular descuento de stock
        for l in lineas:
            productos[l['producto_id']]['stock'] -= l['cantidad']
        return (len(lineas), total, metodo_pago)

    # --- INSERT venta ---
    cursor.execute(f"""
        INSERT INTO {schema_name}.ventas
        (cliente_id, usuario_id, fecha_hora, total, metodo_pago,
         estado, tipo_documento, panaderia_id)
        VALUES (NULL, %s, %s, %s, %s, 'completada', 'POS', %s)
        RETURNING id
    """, (usuario_id, fecha_hora, total, metodo_pago, panaderia_id))
    venta_id = cursor.fetchone()[0]

    # --- INSERT detalle_venta ---
    for l in lineas:
        cursor.execute(f"""
            INSERT INTO {schema_name}.detalle_venta
            (venta_id, producto_id, cantidad, precio_unitario,
             subtotal, panaderia_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            venta_id, l['producto_id'], l['cantidad'],
            l['precio_unitario'], l['subtotal'], panaderia_id,
        ))

        # Descontar stock en productos
        cursor.execute(f"""
            UPDATE {schema_name}.productos
            SET stock_actual = stock_actual - %s
            WHERE id = %s AND panaderia_id = %s
        """, (l['cantidad'], l['producto_id'], panaderia_id))

        # Actualizar cache
        productos[l['producto_id']]['stock'] -= l['cantidad']

    return (len(lineas), total, metodo_pago)