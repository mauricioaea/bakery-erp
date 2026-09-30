"""
Fase 10 — Movimientos financieros del tenant Demo.

Pobla:
  - historial_compras    (~200): compras semanales de MP
  - pagos_individuales   (~26):  pagos a proveedores
  - depositos_bancarios  (~18):  depositos a bancos cada 5 dias
  - saldos_banco         (4):    saldos de Bancolombia, Davivienda, Nequi, Efectivo
  - gastos               (~48):  nomina, servicios, alquiler, otros

Depende de:
  - Fase 2 (proveedores ids 13-19)
  - Fase 3 (materias primas con gramos_por_empaque y costo_promedio)
  - Fase 7 (ventas en los mismos 90 dias)

Reglas de negocio:
  - 90 dias, mismo rango que Fase 7 (2026-07-01 -> 2026-09-29)
  - panaderia_id SIEMPRE explicito
  - Precios y montos en COP
"""
import random
from datetime import datetime, timedelta, date


DIAS_TOTALES = 90
USUARIO_ID = 1  # admin_27
COMMIT_CADA_N_DIAS = 10
FACTOR_STOCK_OBJETIVO = 1.5

# Bancos (deben coincidir con depositos_bancarios.banco y saldos_banco.banco)
BANCOS = ['Bancolombia', 'Davivienda', 'Nequi']

# Categorias de pagos_individuales
CATEGORIAS_PAGO = [
    ('insumos', 'Compra de insumos'),
    ('servicios', 'Servicios publicos'),
    ('nomina', 'Nomina semanal'),
    ('alquiler', 'Arriendo local'),
    ('otros', 'Gastos varios'),
]

# Conceptos por categoria (para variedad)
CONCEPTOS_PAGO = {
    'insumos': ['Compra de insumos', 'Reposicion de MP', 'Compra urgente'],
    'servicios': ['Energia electrica', 'Agua y alcantarillado', 'Gas natural', 'Internet'],
    'nomina': ['Nomina semanal', 'Pago ayudante', 'Pago panadero'],
    'alquiler': ['Arriendo local', 'Arriendo bodega'],
    'otros': ['Mantenimiento', 'Aseo', 'Papeleria', 'Domicilios'],
}


def run(schema_name, cursor, dry_run=False):
    """Ejecuta Fase 10. Retorna (filas, mensaje)."""
    filas = 0

    # --- 1. Obtener panaderia_id ---
    cursor.execute(f"SELECT id FROM {schema_name}.panaderias LIMIT 1")
    row = cursor.fetchone()
    if not row:
        raise Exception(f"No hay panaderia en {schema_name}")
    panaderia_id = row[0]
    if panaderia_id != 27:
        raise Exception(f"Fase 10 disenada para tenant_27, se encontro {panaderia_id}")

    # --- 2. Cargar proveedores ---
    cursor.execute(f"SELECT id, nombre FROM {schema_name}.proveedor ORDER BY id")
    proveedores = cursor.fetchall()
    if not proveedores:
        raise Exception("No hay proveedores")
    proveedor_ids = [p[0] for p in proveedores]

    # --- 3. Cargar MP con gramos_por_empaque y costo_promedio ---
    cursor.execute(f"""
        SELECT id, nombre, gramos_por_empaque, costo_promedio
        FROM {schema_name}.materias_primas
        WHERE activo = TRUE AND panaderia_id = %s
        ORDER BY id
    """, (panaderia_id,))
    materias = []
    for mp_id, nombre, gramos_empaque, costo_promedio in cursor.fetchall():
        if not gramos_empaque or not costo_promedio:
            continue
        materias.append({
            'id': mp_id,
            'nombre': nombre,
            'gramos_empaque': float(gramos_empaque),
            'costo_promedio': float(costo_promedio),
        })
    if not materias:
        raise Exception("No hay MP con gramos_por_empaque y costo_promedio")

    # --- 4. Rango de fechas ---
    hoy = date.today()
    fecha_inicio = hoy - timedelta(days=DIAS_TOTALES)

    print(f"      Rango: {fecha_inicio} -> {hoy} ({DIAS_TOTALES} dias)")
    print(f"      Proveedores: {len(proveedor_ids)}")
    print(f"      MP disponibles: {len(materias)}")

    # --- 5. Generar historial_compras (semanal, dias 7, 14, 21, ..., 84) ---
    for semana in range(1, DIAS_TOTALES // 7 + 1):
        dia_offset = semana * 7 - 1  # dia 6, 13, 20, ...
        if dia_offset >= DIAS_TOTALES:
            break
        fecha_compra = fecha_inicio + timedelta(days=dia_offset)
        hora_compra = datetime.combine(
            fecha_compra, datetime.min.time()
        ) + timedelta(hours=random.randint(7, 10), minutes=random.randint(0, 59))

        # Comprar la mayoria de MP
        num_mps = random.randint(12, len(materias))
        mps_a_comprar = random.sample(materias, num_mps)

        for mp in mps_a_comprar:
            cantidad_empaques = random.randint(1, 3)
            precio_unitario = mp['gramos_empaque'] * mp['costo_promedio']
            precio_total = precio_unitario * cantidad_empaques

            if dry_run:
                filas += 1
                continue

            cursor.execute(f"""
                INSERT INTO {schema_name}.historial_compras
                (panaderia_id, materia_prima_id, fecha_compra,
                 cantidad_empaques, precio_total, precio_unitario_empaque,
                 usuario_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                panaderia_id, mp['id'], hora_compra,
                cantidad_empaques, precio_total, precio_unitario,
                USUARIO_ID,
            ))
            filas += 1

    # --- 6. Generar pagos_individuales (~2 por semana) ---
    for semana in range(DIAS_TOTALES // 7 + 1):
        fecha_semana = fecha_inicio + timedelta(days=semana * 7)
        for _ in range(random.randint(2, 3)):
            fecha_pago = datetime.combine(
                fecha_semana, datetime.min.time()
            ) + timedelta(
                days=random.randint(0, 6),
                hours=random.randint(8, 17),
                minutes=random.randint(0, 59),
            )
            # Elegir categoria con pesos (mas nomina y servicios)
            cat = random.choices(
                [c[0] for c in CATEGORIAS_PAGO],
                weights=[25, 25, 20, 10, 20],
                k=1,
            )[0]
            concepto = random.choice(CONCEPTOS_PAGO[cat])
            proveedor_id = random.choice(proveedor_ids) if cat != 'nomina' else None
            metodo_pago = random.choice(['efectivo', 'transferencia'])

            # Monto por categoria
            if cat == 'nomina':
                monto = random.randint(250000, 400000)
            elif cat == 'alquiler':
                monto = random.randint(500000, 700000)
            elif cat == 'servicios':
                monto = random.randint(100000, 200000)
            elif cat == 'insumos':
                monto = random.randint(80000, 250000)
            else:  # otros
                monto = random.randint(30000, 80000)

            if dry_run:
                filas += 1
                continue

            cursor.execute(f"""
                INSERT INTO {schema_name}.pagos_individuales
                (panaderia_id, concepto, categoria, proveedor_id, monto,
                 fecha_pago, metodo_pago, observaciones, usuario_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                panaderia_id, concepto, cat, proveedor_id, monto,
                fecha_pago, metodo_pago, None, USUARIO_ID,
            ))
            filas += 1

    # --- 7. Generar depositos_bancarios (cada 5 dias) ---
    for i in range(0, DIAS_TOTALES, 5):
        fecha_deposito = fecha_inicio + timedelta(days=i)
        banco = random.choice(BANCOS)
        monto = random.randint(500000, 2000000)
        tipo = random.choice(['traslado', 'recaudo', 'ahorro'])
        metodo = random.choice(['ventanilla', 'cajero', 'app'])

        if dry_run:
            filas += 1
            continue

        cursor.execute(f"""
            INSERT INTO {schema_name}.depositos_bancarios
            (panaderia_id, banco, fecha_deposito, monto, descripcion,
             metodo_deposito, estado, tipo, usuario_id)
            VALUES (%s, %s, %s, %s, %s, %s, 'REGISTRADO', %s, %s)
        """, (
            panaderia_id, banco, fecha_deposito, monto,
            f'Deposito {tipo} a {banco}',
            metodo, tipo, USUARIO_ID,
        ))
        filas += 1

    # --- 8. Generar saldos_banco (4 filas: 3 bancos + efectivo) ---
    for banco, saldo in [
        ('Bancolombia', 3500000),
        ('Davivienda', 2200000),
        ('Nequi', 850000),
        ('Efectivo', 1500000),
    ]:
        if dry_run:
            filas += 1
            continue

        cursor.execute(f"""
            INSERT INTO {schema_name}.saldos_banco
            (panaderia_id, banco, saldo_actual, comentario)
            VALUES (%s, %s, %s, %s)
        """, (
            panaderia_id, banco, saldo,
            f'Saldo inicial {banco}',
        ))
        filas += 1

    # --- 9. Generar gastos ---
    # Nomina semanal (cada 7 dias)
    for semana in range(DIAS_TOTALES // 7 + 1):
        fecha_gasto = fecha_inicio + timedelta(days=semana * 7)
        fecha_gasto_dt = datetime.combine(
            fecha_gasto, datetime.min.time()
        ) + timedelta(hours=random.randint(8, 17))
        monto = random.randint(250000, 400000)

        if dry_run:
            filas += 1
        else:
            cursor.execute(f"""
                INSERT INTO {schema_name}.gastos
                (panaderia_id, concepto, monto, fecha_gasto, categoria,
                 usuario_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                panaderia_id, 'Nomina semanal', monto,
                fecha_gasto_dt, 'nomina', USUARIO_ID,
            ))
            filas += 1

    # Servicios mensuales (cada 30 dias)
    for mes in range(3):
        fecha_gasto = fecha_inicio + timedelta(days=mes * 30 + 5)
        fecha_gasto_dt = datetime.combine(
            fecha_gasto, datetime.min.time()
        ) + timedelta(hours=random.randint(8, 17))
        monto = random.randint(120000, 200000)

        if dry_run:
            filas += 1
        else:
            cursor.execute(f"""
                INSERT INTO {schema_name}.gastos
                (panaderia_id, concepto, monto, fecha_gasto, categoria,
                 usuario_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                panaderia_id, 'Servicios publicos', monto,
                fecha_gasto_dt, 'servicios', USUARIO_ID,
            ))
            filas += 1

    # Alquiler mensual
    for mes in range(3):
        fecha_gasto = fecha_inicio + timedelta(days=mes * 30 + 1)
        fecha_gasto_dt = datetime.combine(
            fecha_gasto, datetime.min.time()
        ) + timedelta(hours=random.randint(8, 12))
        monto = 600000

        if dry_run:
            filas += 1
        else:
            cursor.execute(f"""
                INSERT INTO {schema_name}.gastos
                (panaderia_id, concepto, monto, fecha_gasto, categoria,
                 usuario_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                panaderia_id, 'Arriendo local', monto,
                fecha_gasto_dt, 'alquiler', USUARIO_ID,
            ))
            filas += 1

    # Otros gastos esporadicos (~30)
    for _ in range(30):
        dia_offset = random.randint(0, DIAS_TOTALES - 1)
        fecha_gasto = fecha_inicio + timedelta(days=dia_offset)
        fecha_gasto_dt = datetime.combine(
            fecha_gasto, datetime.min.time()
        ) + timedelta(hours=random.randint(8, 18))
        monto = random.randint(30000, 80000)
        concepto = random.choice([
            'Mantenimiento', 'Aseo', 'Papeleria',
            'Domicilios', 'Imprevisto', 'Reparacion',
        ])

        if dry_run:
            filas += 1
        else:
            cursor.execute(f"""
                INSERT INTO {schema_name}.gastos
                (panaderia_id, concepto, monto, fecha_gasto, categoria,
                 usuario_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                panaderia_id, concepto, monto,
                fecha_gasto_dt, 'otros', USUARIO_ID,
            ))
            filas += 1

    if not dry_run:
        cursor.connection.commit()

    return filas, f"{filas} movimientos financieros en {DIAS_TOTALES} dias"