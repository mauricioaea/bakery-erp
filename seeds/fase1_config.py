"""
Fase 1 — Configuración base del tenant Demo.
Actualiza los datos base que el sistema crea vacíos.
"""
from datetime import datetime


# ============================================
# DATOS DE CONFIGURACIÓN
# ============================================
CONFIG_PANADERIA = {
    'nombre_panaderia': 'Panadería Demo',
    'razon_social': 'Panadería Demo S.A.S',
    'nit': '900123456-7',
    'direccion': 'Calle 18 #25-45, Centro, Pasto, Nariño',
    'telefono_contacto': '+57 320 555 1234',
    'email_facturacion': 'contacto@panaderiademo.co',
    'tipo_licencia': 'nube_premium',
    'max_usuarios': 3,
    'estado_suscripcion': 'activa',
    'dias_gracia': 7,
    'activo': True,
    'sistema_activo': True,
}

CONFIG_SISTEMA = {
    'nombre_empresa': 'Panadería Demo',
    'nit_empresa': '900123456-7',
    'direccion_empresa': 'Calle 18 #25-45, Centro, Pasto, Nariño',
    'telefono_empresa': '+57 320 555 1234',
    'ciudad_empresa': 'Pasto',
    'regimen_empresa': 'Simplificado',
    'tipo_facturacion': 'POS',
    'moneda': 'COP',
    'usa_centavos': False,
    'simbolo_moneda': '$',
}

CATEGORIAS = [
    {'nombre': 'Panadería', 'descripcion': 'Pan fresco del día'},
    {'nombre': 'Pastelería', 'descripcion': 'Tortas, ponqués y postres'},
    {'nombre': 'Pasabocas', 'descripcion': 'Empanadas, arepas y más'},
    {'nombre': 'Bebidas', 'descripcion': 'Café, gaseosas y jugos'},
    {'nombre': 'Snacks', 'descripcion': 'Papas, galletas y mecato'},
]

SUCURSAL = {
    'nombre': 'Sede Principal',
    'direccion': 'Calle 18 #25-45, Centro, Pasto, Nariño',
    'telefono': '+57 320 555 1234',
    'email': 'principal@panaderiademo.co',
}


# ============================================
# RUN
# ============================================
def run(schema_name, cursor, dry_run=False):
    """
    Ejecuta la Fase 1.
    Retorna: (filas_insertadas, mensaje)
    """
    filas = 0

    # -----------------------------------------
    # 0. Obtener el id de la panadería del tenant
    # -----------------------------------------
    cursor.execute(f"SELECT id FROM {schema_name}.panaderias LIMIT 1")
    row = cursor.fetchone()
    if not row:
        raise Exception(f"No hay panadería en {schema_name}")

    panaderia_id = row[0]
    print(f"      panaderia_id = {panaderia_id}")

    # -----------------------------------------
    # 1. UPSERT configuracion_panaderia
    # -----------------------------------------
    if not dry_run:
        # ¿Existe la fila?
        cursor.execute(f"""
            SELECT COUNT(*) FROM {schema_name}.configuracion_panaderia
            WHERE panaderia_id = %s
        """, (panaderia_id,))
        existe = cursor.fetchone()[0] > 0

        if existe:
            cursor.execute(f"""
                UPDATE {schema_name}.configuracion_panaderia
                SET nombre_panaderia = %s,
                    razon_social = %s,
                    nit = %s,
                    direccion = %s,
                    telefono_contacto = %s,
                    email_facturacion = %s,
                    tipo_licencia = %s,
                    max_usuarios = %s,
                    estado_suscripcion = %s,
                    dias_gracia = %s,
                    activo = %s,
                    sistema_activo = %s,
                    tenant_id = %s,
                    fecha_actualizacion = NOW()
                WHERE panaderia_id = %s
            """, (
                CONFIG_PANADERIA['nombre_panaderia'],
                CONFIG_PANADERIA['razon_social'],
                CONFIG_PANADERIA['nit'],
                CONFIG_PANADERIA['direccion'],
                CONFIG_PANADERIA['telefono_contacto'],
                CONFIG_PANADERIA['email_facturacion'],
                CONFIG_PANADERIA['tipo_licencia'],
                CONFIG_PANADERIA['max_usuarios'],
                CONFIG_PANADERIA['estado_suscripcion'],
                CONFIG_PANADERIA['dias_gracia'],
                CONFIG_PANADERIA['activo'],
                CONFIG_PANADERIA['sistema_activo'],
                panaderia_id,
                panaderia_id,
            ))
        else:
            cursor.execute(f"""
                INSERT INTO {schema_name}.configuracion_panaderia
                (panaderia_id, tenant_id, nombre_panaderia, razon_social, nit,
                 direccion, telefono_contacto, email_facturacion, tipo_licencia,
                 max_usuarios, estado_suscripcion, dias_gracia, activo, sistema_activo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                panaderia_id,
                panaderia_id,
                CONFIG_PANADERIA['nombre_panaderia'],
                CONFIG_PANADERIA['razon_social'],
                CONFIG_PANADERIA['nit'],
                CONFIG_PANADERIA['direccion'],
                CONFIG_PANADERIA['telefono_contacto'],
                CONFIG_PANADERIA['email_facturacion'],
                CONFIG_PANADERIA['tipo_licencia'],
                CONFIG_PANADERIA['max_usuarios'],
                CONFIG_PANADERIA['estado_suscripcion'],
                CONFIG_PANADERIA['dias_gracia'],
                CONFIG_PANADERIA['activo'],
                CONFIG_PANADERIA['sistema_activo'],
            ))

        filas += cursor.rowcount
        print(f"      configuracion_panaderia: {cursor.rowcount} filas")
    else:
        filas += 1

    # -----------------------------------------
    # 2. Actualizar panaderias
    # -----------------------------------------
    if not dry_run:
        cursor.execute(f"""
            UPDATE {schema_name}.panaderias
            SET nombre = %s,
                direccion = %s,
                telefono = %s
            WHERE id = %s
        """, (
            CONFIG_PANADERIA['nombre_panaderia'],
            CONFIG_PANADERIA['direccion'],
            CONFIG_PANADERIA['telefono_contacto'],
            panaderia_id,
        ))
        filas += cursor.rowcount
        print(f"      panaderias: {cursor.rowcount} filas actualizadas")
    else:
        filas += 1

    # -----------------------------------------
    # 3. UPSERT configuracion_sistema
    # -----------------------------------------
    if not dry_run:
        cursor.execute(f"""
            SELECT COUNT(*) FROM {schema_name}.configuracion_sistema
        """)
        existe = cursor.fetchone()[0] > 0

        if existe:
            cursor.execute(f"""
                UPDATE {schema_name}.configuracion_sistema
                SET nombre_empresa = %s,
                    nit_empresa = %s,
                    direccion_empresa = %s,
                    telefono_empresa = %s,
                    ciudad_empresa = %s,
                    regimen_empresa = %s,
                    tipo_facturacion = %s,
                    moneda = %s,
                    usa_centavos = %s,
                    simbolo_moneda = %s
                WHERE id = (SELECT id FROM {schema_name}.configuracion_sistema LIMIT 1)
            """, (
                CONFIG_SISTEMA['nombre_empresa'],
                CONFIG_SISTEMA['nit_empresa'],
                CONFIG_SISTEMA['direccion_empresa'],
                CONFIG_SISTEMA['telefono_empresa'],
                CONFIG_SISTEMA['ciudad_empresa'],
                CONFIG_SISTEMA['regimen_empresa'],
                CONFIG_SISTEMA['tipo_facturacion'],
                CONFIG_SISTEMA['moneda'],
                CONFIG_SISTEMA['usa_centavos'],
                CONFIG_SISTEMA['simbolo_moneda'],
            ))
        else:
            cursor.execute(f"""
                INSERT INTO {schema_name}.configuracion_sistema
                (panaderia_id, nombre_empresa, nit_empresa, direccion_empresa,
                 telefono_empresa, ciudad_empresa, regimen_empresa, tipo_facturacion,
                 moneda, usa_centavos, simbolo_moneda)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                panaderia_id,
                CONFIG_SISTEMA['nombre_empresa'],
                CONFIG_SISTEMA['nit_empresa'],
                CONFIG_SISTEMA['direccion_empresa'],
                CONFIG_SISTEMA['telefono_empresa'],
                CONFIG_SISTEMA['ciudad_empresa'],
                CONFIG_SISTEMA['regimen_empresa'],
                CONFIG_SISTEMA['tipo_facturacion'],
                CONFIG_SISTEMA['moneda'],
                CONFIG_SISTEMA['usa_centavos'],
                CONFIG_SISTEMA['simbolo_moneda'],
            ))

        filas += cursor.rowcount
        print(f"      configuracion_sistema: {cursor.rowcount} filas")
    else:
        filas += 1

    # -----------------------------------------
    # 4. Borrar TODAS las categorías y crear las 5 del Demo
    # -----------------------------------------
    # Nota: seguro, porque en un tenant recién creado no hay productos aún
    if not dry_run:
        cursor.execute(f"DELETE FROM {schema_name}.categorias")
        print(f"      categorias: {cursor.rowcount} filas borradas")

        for cat in CATEGORIAS:
            cursor.execute(f"""
                INSERT INTO {schema_name}.categorias (nombre, descripcion, panaderia_id)
                VALUES (%s, %s, %s)
            """, (cat['nombre'], cat['descripcion'], panaderia_id))
            filas += 1
        print(f"      categorias: {len(CATEGORIAS)} filas insertadas")
    else:
        filas += len(CATEGORIAS)

    # -----------------------------------------
    # 5. Sucursal (crear si no existe)
    # -----------------------------------------
    if not dry_run:
        cursor.execute(f"""
            SELECT COUNT(*) FROM {schema_name}.sucursales WHERE nombre = %s
        """, (SUCURSAL['nombre'],))
        existe = cursor.fetchone()[0] > 0

        if not existe:
            cursor.execute(f"""
                INSERT INTO {schema_name}.sucursales (nombre, direccion, telefono, email, panaderia_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                SUCURSAL['nombre'],
                SUCURSAL['direccion'],
                SUCURSAL['telefono'],
                SUCURSAL['email'],
                panaderia_id,
            ))
            filas += 1
            print(f"      sucursales: 1 fila insertada")
        else:
            print(f"      sucursales: ya existe")
    else:
        filas += 1

    # -----------------------------------------
    # 6. Reiniciar consecutivo POS a 0
    # -----------------------------------------
    if not dry_run:
        cursor.execute(f"""
            UPDATE {schema_name}.consecutivos_pos
            SET numero_actual = 0
        """)
        filas += cursor.rowcount
        print(f"      consecutivos_pos: {cursor.rowcount} filas reseteadas")
    else:
        filas += 1

    return filas, f"Configuración aplicada ({filas} filas afectadas)"