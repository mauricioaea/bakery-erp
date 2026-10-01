#!/usr/bin/env python
"""
seed_demo.py — Poblar tenant Demo con datos realistas
Bakery ERP - Fase Demo

Uso:
    python seed_demo.py --list
    python seed_demo.py --tenant=27 --fase=1
    python seed_demo.py --tenant=27 --fase=1,2,3
    python seed_demo.py --tenant=27 --fase=all
    python seed_demo.py --tenant=27 --status
    python seed_demo.py --tenant=27 --reset
"""
import argparse
import sys
import importlib
from datetime import datetime

import psycopg2


# ============================================
# CONFIGURACIÓN
# ============================================
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'panaderia_master',
    'user': 'postgres',
    'password': 'PanaderiaPro2026!'
}

# Fases disponibles: (número, nombre, módulo)
FASES = {
    1: ('Configuración base', 'seeds.fase1_config'),
    2: ('Proveedores', 'seeds.fase2_proveedores'),
    3: ('Materias primas', 'seeds.fase3_materias'),
    4: ('Recetas y fórmulas', 'seeds.fase4_recetas'),
    5: ('Productos', 'seeds.fase5_productos'),
    # Fases futuras:
    6: ('Producción diaria', 'seeds.fase6_produccion'),
    7: ('Ventas', 'seeds.fase7_ventas'),
    8: ('Productos externos', 'seeds.fase8_externos'),
    9: ('Activos fijos', 'seeds.fase9_activos'),
    10: ('Movimientos financieros', 'seeds.fase10_financieros'),
    11: ('Cierres diarios', 'seeds.fase11_cierres'),
}


# ============================================
# UTILIDADES
# ============================================
def conectar_bd():
    """Abre una conexión a PostgreSQL."""
    try:
        conn = psycopg2.connect(
            **DB_CONFIG,
            client_encoding='UTF8'
        )
        return conn
    except Exception as e:
        print(f"❌ Error conectando a la BD: {e}")
        sys.exit(1)


def verificar_tenant(cursor, tenant_id):
    """Verifica que el tenant existe y tiene su schema."""
    schema_name = f"tenant_{tenant_id}"

    # ¿Existe el schema?
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.schemata
        WHERE schema_name = %s
    """, (schema_name,))
    if cursor.fetchone()[0] == 0:
        print(f"❌ El schema {schema_name} NO existe.")
        sys.exit(1)

    # ¿Existe el tenant en public.tenants?
    cursor.execute("""
        SELECT COUNT(*) FROM public.tenants WHERE id = %s
    """, (tenant_id,))
    if cursor.fetchone()[0] == 0:
        print(f"⚠️  El tenant {tenant_id} NO existe en public.tenants (pero el schema sí).")

    return schema_name


def crear_tabla_historial(cursor, schema_name):
    """Crea la tabla de historial de seeds si no existe."""
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {schema_name}.seed_demo_history (
            id SERIAL PRIMARY KEY,
            fase INTEGER NOT NULL,
            nombre VARCHAR(100) NOT NULL,
            fecha_ejecucion TIMESTAMP DEFAULT NOW(),
            filas_insertadas INTEGER DEFAULT 0,
            estado VARCHAR(20) DEFAULT 'OK',
            mensaje TEXT
        )
    """)


def fase_ya_ejecutada(cursor, schema_name, fase_num):
    """Verifica si una fase ya se ejecutó."""
    cursor.execute(f"""
        SELECT COUNT(*) FROM {schema_name}.seed_demo_history
        WHERE fase = %s AND estado = 'OK'
    """, (fase_num,))
    return cursor.fetchone()[0] > 0


def registrar_fase(cursor, schema_name, fase_num, nombre, filas, estado, mensaje):
    """Registra una fase en el historial."""
    cursor.execute(f"""
        INSERT INTO {schema_name}.seed_demo_history
        (fase, nombre, filas_insertadas, estado, mensaje)
        VALUES (%s, %s, %s, %s, %s)
    """, (fase_num, nombre, filas, estado, mensaje))


# ============================================
# COMANDOS
# ============================================
def cmd_list():
    """Lista las fases disponibles."""
    print("=" * 60)
    print("📋 FASES DISPONIBLES")
    print("=" * 60)
    for num, (nombre, modulo) in sorted(FASES.items()):
        print(f"  Fase {num}: {nombre}")
        print(f"           módulo: {modulo}")
    print("=" * 60)


def cmd_status(tenant_id):
    """Muestra el estado de las fases ejecutadas."""
    schema_name = f"tenant_{tenant_id}"
    conn = conectar_bd()
    cursor = conn.cursor()

    verificar_tenant(cursor, tenant_id)
    crear_tabla_historial(cursor, schema_name)
    conn.commit()

    print("=" * 60)
    print(f"📊 ESTADO DEL SEED — tenant_{tenant_id}")
    print("=" * 60)

    cursor.execute(f"""
        SELECT fase, nombre, fecha_ejecucion, filas_insertadas, estado
        FROM {schema_name}.seed_demo_history
        ORDER BY fase, fecha_ejecucion DESC
    """)
    rows = cursor.fetchall()

    if not rows:
        print("  (ninguna fase ejecutada todavía)")
    else:
        for row in rows:
            fase, nombre, fecha, filas, estado = row
            icono = "✅" if estado == "OK" else "❌"
            print(f"  {icono} Fase {fase} ({nombre}) — {filas} filas — {fecha}")

    print("=" * 60)
    cursor.close()
    conn.close()


def cmd_reset(tenant_id):
    """Borra los datos del seed (pero NO el schema ni las tablas)."""
    schema_name = f"tenant_{tenant_id}"
    conn = conectar_bd()
    cursor = conn.cursor()

    verificar_tenant(cursor, tenant_id)

    print("=" * 60)
    print(f"🗑️  RESET — tenant_{tenant_id}")
    print("=" * 60)
    print("⚠️  Esto borrará los datos de seed (NO el schema ni las tablas base).")
    confirm = input("   ¿Continuar? (escribe 'SI' para confirmar): ")
    if confirm.strip().upper() != 'SI':
        print("❌ Cancelado.")
        cursor.close()
        conn.close()
        return

    # Orden inverso a las dependencias
    tablas_a_limpiar = [
        'detalle_venta', 'ventas', 'jornadas_ventas', 'cierres_diarios',
        'productos', 'receta_ingredientes', 'recetas',
        'materias_primas', 'proveedor',
        'categorias',
        # 'configuracion_panaderia',  ← NO borrar
        'seed_demo_history'
    ]

    for tabla in tablas_a_limpiar:
        try:
            cursor.execute(f"DELETE FROM {schema_name}.{tabla}")
            print(f"   ✅ {tabla}: {cursor.rowcount} filas borradas")
        except Exception as e:
            print(f"   ⚠️  {tabla}: {e}")
            conn.rollback()
            continue

    conn.commit()
    print("=" * 60)
    print("✅ RESET completado.")
    cursor.close()
    conn.close()


def cmd_run_fases(tenant_id, fases_a_correr, dry_run=False):
    """Ejecuta las fases indicadas."""
    schema_name = f"tenant_{tenant_id}"
    conn = conectar_bd()
    cursor = conn.cursor()

    verificar_tenant(cursor, tenant_id)
    crear_tabla_historial(cursor, schema_name)
    conn.commit()

    print("=" * 60)
    print(f"🌱 SEED DEMO — tenant_{tenant_id}")
    if dry_run:
        print("   [MODO DRY-RUN]")
    print("=" * 60)

    total_filas = 0
    errores = 0

    for fase_num in fases_a_correr:
        if fase_num not in FASES:
            print(f"⚠️  Fase {fase_num} no existe. Saltando.")
            continue

        nombre, modulo_path = FASES[fase_num]

        if fase_ya_ejecutada(cursor, schema_name, fase_num):
            print(f"⏭️  Fase {fase_num} ({nombre}) — ya ejecutada. Saltando.")
            continue

        print(f"\n▶️  Ejecutando Fase {fase_num}: {nombre}...")

        try:
            modulo = importlib.import_module(modulo_path)
            filas, mensaje = modulo.run(schema_name, cursor, dry_run=dry_run)

            if not dry_run:
                registrar_fase(cursor, schema_name, fase_num, nombre, filas, 'OK', mensaje)
                conn.commit()

            print(f"   ✅ {filas} filas — {mensaje}")
            total_filas += filas

        except Exception as e:
            errores += 1
            conn.rollback()
            print(f"   ❌ Error en Fase {fase_num}: {e}")
            import traceback
            traceback.print_exc()

            if not dry_run:
                registrar_fase(cursor, schema_name, fase_num, nombre, 0, 'ERROR', str(e))
                conn.commit()
            break  # Detener en el primer error

    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    print(f"   Total filas: {total_filas}")
    if errores > 0:
        print(f"   ⚠️  Errores: {errores}")
    print("=" * 60)

    cursor.close()
    conn.close()


# ============================================
# MAIN
# ============================================
def main():
    parser = argparse.ArgumentParser(
        description="Poblar tenant Demo con datos realistas."
    )
    parser.add_argument('--tenant', type=int, help='ID del tenant (ej: 27)')
    parser.add_argument('--fase', type=str, help='Fases a correr: 1, 1,2,3, o "all"')
    parser.add_argument('--list', action='store_true', help='Lista las fases disponibles')
    parser.add_argument('--status', action='store_true', help='Muestra el estado de las fases')
    parser.add_argument('--reset', action='store_true', help='Borra los datos del seed')
    parser.add_argument('--dry-run', action='store_true', help='Simula sin ejecutar')

    args = parser.parse_args()

    if args.list:
        cmd_list()
        return

    if not args.tenant:
        print("❌ Debes especificar --tenant=N (ej: --tenant=27)")
        parser.print_help()
        sys.exit(1)

    if args.status:
        cmd_status(args.tenant)
        return

    if args.reset:
        cmd_reset(args.tenant)
        return

    if not args.fase:
        print("❌ Debes especificar --fase=N o --fase=all")
        parser.print_help()
        sys.exit(1)

    # Determinar las fases a correr
    if args.fase.lower() == 'all':
        fases_a_correr = sorted(FASES.keys())
    else:
        try:
            fases_a_correr = [int(f.strip()) for f in args.fase.split(',')]
        except ValueError:
            print(f"❌ Formato inválido en --fase: {args.fase}")
            sys.exit(1)

    cmd_run_fases(args.tenant, fases_a_correr, dry_run=args.dry_run)


if __name__ == '__main__':
    main()