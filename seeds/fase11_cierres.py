"""
Fase 11 — Cierres diarios del tenant Demo.

Genera 1 cierre por cada jornada CERRADA existente (90).
Recopila totales de jornadas_ventas, ventas, y depositos_bancarios.

Depende de:
  - Fase 7 (jornadas_ventas y ventas)
  - Fase 10 (depositos_bancarios)

Reglas:
  - Solo se procesan jornadas con estado 'CERRADA'
  - Estado del cierre: 'CERRADO' (mayusculas)
"""
import json
from datetime import datetime, timedelta, date


USUARIO_ID = 1  # admin_27


def run(schema_name, cursor, dry_run=False):
    """Ejecuta Fase 11. Retorna (filas, mensaje)."""
    filas = 0

    # --- 1. Obtener panaderia_id ---
    cursor.execute(f"SELECT id FROM {schema_name}.panaderias LIMIT 1")
    row = cursor.fetchone()
    if not row:
        raise Exception(f"No hay panaderia en {schema_name}")
    panaderia_id = row[0]
    if panaderia_id != 27:
        raise Exception(f"Fase 11 disenada para tenant_27, se encontro {panaderia_id}")

    # --- 2. Verificar que no haya cierres ya ---
    cursor.execute(f"SELECT COUNT(*) FROM {schema_name}.cierres_diarios")
    if cursor.fetchone()[0] > 0:
        print(f"      Ya existen cierres_diarios. Saltando.")
        return 0, "cierres_diarios ya poblado"

    # --- 3. Cargar jornadas CERRADAS ordenadas ---
    cursor.execute(f"""
        SELECT id, fecha, total_ventas, total_efectivo,
               total_transferencia, total_tarjeta
        FROM {schema_name}.jornadas_ventas
        WHERE estado = 'CERRADA' AND panaderia_id = %s
        ORDER BY fecha
    """, (panaderia_id,))
    jornadas = cursor.fetchall()
    if not jornadas:
        raise Exception("No hay jornadas CERRADAS")

    print(f"      Jornadas CERRADAS a procesar: {len(jornadas)}")

    # --- 4. Cargar depositos bancarios por fecha ---
    cursor.execute(f"""
        SELECT id, fecha_deposito
        FROM {schema_name}.depositos_bancarios
        WHERE panaderia_id = %s
        ORDER BY fecha_deposito
    """, (panaderia_id,))
    depositos_por_fecha = {}
    for dep_id, fecha_dep in cursor.fetchall():
        if fecha_dep not in depositos_por_fecha:
            depositos_por_fecha[fecha_dep] = dep_id

    # --- 5. Iterar jornadas y crear cierres ---
    ventas_ayer = 0
    for jornada in jornadas:
        jid, fecha, total_ventas, total_efectivo, total_transf, total_tarjeta = jornada

        # Verificar si ya existe cierre para esta fecha
        cursor.execute(f"""
            SELECT COUNT(*) FROM {schema_name}.cierres_diarios
            WHERE fecha_cierre = %s AND panaderia_id = %s
        """, (fecha, panaderia_id))
        if cursor.fetchone()[0] > 0:
            continue

        # Contar transacciones y calcular donaciones del dia
        cursor.execute(f"""
            SELECT 
                COUNT(*) AS num_transacciones,
                COALESCE(SUM(CASE WHEN es_donacion = TRUE THEN total ELSE 0 END), 0) AS total_donaciones
            FROM {schema_name}.ventas
            WHERE DATE(fecha_hora) = %s AND panaderia_id = %s
        """, (fecha, panaderia_id))
        num_trans, donaciones = cursor.fetchone()

        # Top 3 productos del dia
        cursor.execute(f"""
            SELECT p.nombre, SUM(dv.cantidad) AS total_vendido
            FROM {schema_name}.detalle_venta dv
            JOIN {schema_name}.productos p ON p.id = dv.producto_id
            JOIN {schema_name}.ventas v ON v.id = dv.venta_id
            WHERE DATE(v.fecha_hora) = %s AND v.panaderia_id = %s
              AND dv.producto_id IS NOT NULL
            GROUP BY p.nombre
            ORDER BY total_vendido DESC
            LIMIT 3
        """, (fecha, panaderia_id))
        top_productos = [{'nombre': r[0], 'cantidad': int(r[1])} for r in cursor.fetchall()]
        productos_top_json = json.dumps(top_productos, ensure_ascii=False) if top_productos else None

        # Tendencia vs dia anterior
        if ventas_ayer > 0:
            tendencia = ((total_ventas - ventas_ayer) / ventas_ayer) * 100
        else:
            tendencia = 0.0

        # Deposito bancario del dia (si existe)
        deposito_id = depositos_por_fecha.get(fecha)

        # Observaciones
        observaciones = f'Cierre automatico - {num_trans} transacciones'

        if dry_run:
            filas += 1
            ventas_ayer = total_ventas
            continue

        cursor.execute(f"""
            INSERT INTO {schema_name}.cierres_diarios
            (fecha_cierre, total_ventas, total_efectivo, total_tarjeta,
             total_transferencia, total_donaciones, total_transacciones,
             productos_top, ventas_dia_anterior, tendencia,
             deposito_bancario_id, observaciones, usuario_id,
             estado, panaderia_id)
            VALUES (%s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    'CERRADO', %s)
        """, (
            fecha, total_ventas, total_efectivo, total_tarjeta,
            total_transf, donaciones, num_trans,
            productos_top_json, ventas_ayer, tendencia,
            deposito_id, observaciones, USUARIO_ID,
            panaderia_id,
        ))
        filas += 1
        ventas_ayer = total_ventas

        # Commit cada 30 cierres
        if filas % 30 == 0:
            cursor.connection.commit()
            print(f"      💾 Checkpoint: {filas} cierres")

    if not dry_run:
        cursor.connection.commit()

    return filas, f"{filas} cierres diarios creados"


if __name__ == '__main__':
    print("Modulo del seed. Ejecutar con: python seed_demo.py --tenant=27 --fase=11")