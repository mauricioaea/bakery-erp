"""
Fase 9 — Activos fijos + mantenimientos del tenant Demo.

Pobla:
  - activos_fijos        (12): hornos, batidoras, vitrinas, vehiculo, etc.
  - historial_mantenimientos (~22): mantenimientos preventivos/correctivos

Depende de: nada (activos son independientes)
Rango: 2024-07-01 -> 2026-09-30
"""
import random
from datetime import datetime, timedelta, date


USUARIO_ID = 1  # admin_27
USUARIO_NOMBRE = 'admin_27'

ACTIVOS = [
    # (nombre, categoria, descripcion, valor, vida_util, ubicacion)
    ('Horno Rotatorio Industrial', 'Equipo de produccion',
     'Horno rotatorio de 12 bandejas para panificacion industrial',
     25000000, 15, 'Cocina principal'),
    ('Horno de Convencion', 'Equipo de produccion',
     'Horno de conveccion de 6 bandejas para pasteleria',
     8500000, 10, 'Cocina principal'),
    ('Batidora Industrial 30L', 'Equipo de produccion',
     'Batidora planetaria de 30 litros, 3 velocidades',
     6200000, 10, 'Cocina principal'),
    ('Amasadora Espiral 50L', 'Equipo de produccion',
     'Amasadora espiral profesional para masas duras',
     12000000, 12, 'Cocina principal'),
    ('Vitrina Refrigerada 2m', 'Mobiliario',
     'Vitrina exhibidora refrigerada de 2 metros con 3 niveles',
     7800000, 8, 'Vitrina'),
    ('Congelador Horizontal 500L', 'Mobiliario',
     'Congelador horizontal tipo arcón de 500 litros',
     4500000, 8, 'Almacen'),
    ('Exhibidor Vitrina 1.5m', 'Mobiliario',
     'Exhibidor de vitrina sin refrigeracion de 1.5 metros',
     3200000, 10, 'Vitrina'),
    ('Camioneta de Reparto', 'Vehiculo',
     'Camioneta cerrada para reparto de pedidos',
     45000000, 10, 'Exterior'),
    ('Balanza Digital 40kg', 'Tecnologia',
     'Balanza digital de precision con capacidad de 40 kg',
     850000, 5, 'Vitrina'),
    ('Computador POS', 'Tecnologia',
     'Equipo todo-en-uno para punto de venta con touchscreen',
     3500000, 5, 'Mostrador'),
    ('Juego de Moldes y Herramientas', 'Herramientas',
     'Set completo de moldes, espátulas y herramientas de panaderia',
     1800000, 8, 'Cocina principal'),
    ('Sistema de Seguridad CCTV', 'Tecnologia',
     'Sistema de 8 cámaras con grabador DVR y monitoreo',
     2500000, 7, 'Toda la panaderia'),
]

TECNICOS = [
    'Juan Perez', 'Carlos Gomez', 'Andres Martinez',
    'TecniServicios Ltda', 'Ferrelectricos del Sur',
    'Servicio Tecnico Industrial', 'Electro Andes',
]

TIPOS_MANTENIMIENTO = ['preventivo', 'correctivo']

DESCRIPCIONES_MANTENIMIENTO = {
    'preventivo': [
        'Limpieza general y revision de componentes',
        'Cambio de piezas de desgaste',
        'Calibracion y ajuste',
        'Engrase y lubricacion',
        'Revision anual programada',
    ],
    'correctivo': [
        'Reparacion de falla en motor',
        'Cambio de resistencia quemada',
        'Reparacion de sistema de refrigeracion',
        'Cambio de rodamiento',
        'Reparacion de sistema electrico',
    ],
}


def run(schema_name, cursor, dry_run=False):
    """Ejecuta Fase 9. Retorna (filas, mensaje)."""
    filas = 0

    # --- 1. Obtener panaderia_id ---
    cursor.execute(f"SELECT id FROM {schema_name}.panaderias LIMIT 1")
    row = cursor.fetchone()
    if not row:
        raise Exception(f"No hay panaderia en {schema_name}")
    panaderia_id = row[0]
    if panaderia_id != 27:
        print(f"      ⚠️  Fase 9 diseñada para tenant_27, se encontró {panaderia_id}. Continuando...")

    hoy = date.today()
    fecha_min = hoy - timedelta(days=2 * 365)   # 2 años atras
    fecha_max = hoy - timedelta(days=90)         # 3 meses atras

    print(f"      Activos a crear: {len(ACTIVOS)}")

    # --- 2. Crear activos fijos ---
    activos_creados = []  # lista de (id, nombre, valor, fecha_compra)

    for nombre, categoria, descripcion, valor, vida_util, ubicacion in ACTIVOS:
        # Fecha de compra aleatoria
        dias_atras = random.randint(90, 2 * 365)
        fecha_compra = hoy - timedelta(days=dias_atras)
        # Serie unica
        numero_serie = f"AF-{panaderia_id}-{random.randint(1000, 9999)}"
        # Proveedor aleatorio de una lista
        proveedor = random.choice([
            'Distribuidora El Trigal S.A.S',
            'Equipos Panaderos Colombia',
            'Maquinaria Industrial SAS',
            'Importadora PanamERICANA',
            'Ferreteria Industrial',
        ])
        metodo_pago = random.choice(['efectivo', 'transferencia', 'credito'])
        valor_residual = valor * 0.10  # 10% del valor

        if dry_run:
            activos_creados.append((len(activos_creados) + 1, nombre, valor, fecha_compra))
            filas += 1
            continue

        cursor.execute(f"""
            INSERT INTO {schema_name}.activos_fijos
            (panaderia_id, nombre, categoria, descripcion, numero_serie,
             fecha_compra, proveedor, valor_compra, metodo_pago, vida_util,
             valor_residual, metodo_depreciacion, ubicacion, estado,
             responsable)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    'LINEAL', %s, 'ACTIVO', %s)
            RETURNING id
        """, (
            panaderia_id, nombre, categoria, descripcion, numero_serie,
            fecha_compra, proveedor, valor, metodo_pago, vida_util,
            valor_residual, ubicacion, USUARIO_NOMBRE,
        ))
        activo_id = cursor.fetchone()[0]
        activos_creados.append((activo_id, nombre, valor, fecha_compra))
        filas += 1

    # --- 3. Crear mantenimientos ---
    # Por cada activo, 1-3 mantenimientos en el rango (fecha_compra, hoy)
    for activo_id, nombre, valor, fecha_compra in activos_creados:
        num_mant = random.randint(1, 3)

        for _ in range(num_mant):
            # Fecha entre fecha_compra y hoy
            dias_disponibles = (hoy - fecha_compra).days
            if dias_disponibles <= 0:
                continue
            dias_atras = random.randint(0, dias_disponibles)
            fecha_mant = hoy - timedelta(days=dias_atras)

            tipo = random.choices(
                TIPOS_MANTENIMIENTO, weights=[60, 40], k=1
            )[0]
            descripcion = random.choice(DESCRIPCIONES_MANTENIMIENTO[tipo])
            tecnico = random.choice(TECNICOS)

            # Costo segun valor del activo
            if valor >= 20000000:
                costo = random.randint(200000, 800000)
            elif valor >= 5000000:
                costo = random.randint(100000, 400000)
            else:
                costo = random.randint(30000, 150000)

            if dry_run:
                filas += 1
                continue

            cursor.execute(f"""
                INSERT INTO {schema_name}.historial_mantenimientos
                (activo_fijo_id, fecha_mantenimiento, descripcion, costo,
                 tipo, tecnico, panaderia_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                activo_id, fecha_mant, descripcion, costo,
                tipo, tecnico, panaderia_id,
            ))
            filas += 1

    if not dry_run:
        cursor.connection.commit()

    return filas, f"{filas} activos y mantenimientos creados"


if __name__ == '__main__':
    print("Este archivo es un modulo del seed. Ejecutar con: python seed_demo.py --tenant=27 --fase=9")