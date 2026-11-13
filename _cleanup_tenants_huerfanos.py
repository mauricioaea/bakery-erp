# _cleanup_tenants_huerfanos.py
# Script manual de limpieza de tenants huérfanos.
#
# Uso:
#   python _cleanup_tenants_huerfanos.py            # dry-run (solo reporta)
#   python _cleanup_tenants_huerfanos.py --fix      # elimina los huérfanos (pide confirmación)
#   python _cleanup_tenants_huerfanos.py --fix --yes  # elimina sin confirmar (para CI/CD)
#
# Qué hace:
#   1. Lista todos los schemas 'tenant_*' en la BD.
#   2. Lista todos los IDs en public.tenants.
#   3. Reporta:
#      - Schemas con schema pero sin fila en public.tenants (huérfanos de DDL).
#      - Filas en public.tenants sin schema (huérfanos de metadata).
#   4. Con --fix: elimina los huérfanos (DROP SCHEMA + DELETE FROM public.*).
#
# Contexto (DT-Fase B-4): crear_tenant_saas() no es atómico. Si falla a
# mitad, el DDL (CREATE SCHEMA, CREATE TABLE) ya se ejecutó y no se
# revierte. Este script detecta y limpia esos huérfanos.

import sys
from sqlalchemy import text

# Importar la app y db
from app import app, db
import models  # noqa: F401


def listar_schemas_tenant():
    """Lista todos los schemas 'tenant_*' en la BD."""
    sql = text("""
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name LIKE 'tenant_%'
        ORDER BY schema_name
    """)
    return [r[0] for r in db.session.execute(sql).fetchall()]


def listar_tenants_public():
    """Lista todos los IDs en public.tenants."""
    sql = text("SELECT id FROM public.tenants ORDER BY id")
    return [r[0] for r in db.session.execute(sql).fetchall()]


def main():
    args = sys.argv[1:]
    fix = "--fix" in args
    yes = "--yes" in args
    dry_run = not fix

    with app.app_context():
        print("=" * 60)
        print("🔍 LIMPIEZA DE TENANTS HUÉRFANOS" + (" [DRY-RUN]" if dry_run else ""))
        print("=" * 60)

        # 1. Listar schemas y tenants
        schemas = listar_schemas_tenant()
        tenants = listar_tenants_public()

        print(f"\nSchemas 'tenant_*' en BD: {len(schemas)}")
        for s in schemas:
            print(f"  - {s}")

        print(f"\nTenants en public.tenants: {len(tenants)}")
        for t in tenants:
            print(f"  - {t}")

        # 2. Detectar huérfanos
        # Schema huérfano: schema 'tenant_X' sin fila X en public.tenants
        schemas_huerfanos = []
        for s in schemas:
            try:
                tenant_id = int(s.replace("tenant_", ""))
            except ValueError:
                print(f"  ⚠️  Schema con nombre raro: {s}")
                continue
            if tenant_id not in tenants:
                schemas_huerfanos.append((s, tenant_id))

        # Tenant huérfano: fila X en public.tenants sin schema 'tenant_X'
        tenants_huerfanos = []
        for t in tenants:
            if f"tenant_{t}" not in schemas:
                tenants_huerfanos.append(t)

        # 3. Reportar
        print("\n" + "=" * 60)
        print("📊 DIAGNÓSTICO")
        print("=" * 60)

        if not schemas_huerfanos and not tenants_huerfanos:
            print("\n✅ NO hay huérfanos. Todo limpio.")
            sys.exit(0)

        if schemas_huerfanos:
            print(f"\n🚨 Schemas huérfanos (existen en BD, no en public.tenants): {len(schemas_huerfanos)}")
            for s, t in schemas_huerfanos:
                print(f"  - {s} (id esperado: {t})")

        if tenants_huerfanos:
            print(f"\n🚨 Tenants huérfanos (existen en public.tenants, no en BD): {len(tenants_huerfanos)}")
            for t in tenants_huerfanos:
                print(f"  - id={t}")

        # 4. Limpiar si --fix
        if not fix:
            print("\n" + "=" * 60)
            print("ℹ️  Modo DRY-RUN. Para eliminar, ejecutar con --fix")
            print("=" * 60)
            sys.exit(0)

        # Confirmar
        if not yes:
            print("\n" + "=" * 60)
            print("⚠️  CONFIRMACIÓN REQUERIDA")
            print("=" * 60)
            print(f"Vas a eliminar {len(schemas_huerfanos)} schemas y {len(tenants_huerfanos)} tenants huérfanos.")
            print("Esta operación NO se puede deshacer.")
            resp = input("\n¿Confirmar? (escribí 'SI' para continuar): ").strip()
            if resp != "SI":
                print("❌ Cancelado.")
                sys.exit(0)

        # Eliminar schemas huérfanos
        errores = 0
        for s, t in schemas_huerfanos:
            try:
                db.session.execute(text(f"DROP SCHEMA IF EXISTS {s} CASCADE"))
                db.session.commit()
                print(f"  ✅ Schema {s} eliminado")
            except Exception as e:
                print(f"  ❌ Error eliminando {s}: {e}")
                db.session.rollback()
                errores += 1

        # Eliminar tenants huérfanos
        for t in tenants_huerfanos:
            try:
                # Borrar filas de public relacionadas
                db.session.execute(text("DELETE FROM public.usuarios WHERE tenant_id = :id"), {"id": t})
                db.session.execute(text("DELETE FROM public.configuracion_panaderia WHERE tenant_id = :id OR panaderia_id = :id"), {"id": t})
                db.session.execute(text("DELETE FROM public.tenants WHERE id = :id"), {"id": t})
                db.session.commit()
                print(f"  ✅ Tenant {t} eliminado de public.*")
            except Exception as e:
                print(f"  ❌ Error eliminando tenant {t}: {e}")
                db.session.rollback()
                errores += 1

        # Reparar secuencia de tenants
        try:
            db.session.execute(text(
                "SELECT setval('tenants_id_seq', (SELECT COALESCE(MAX(id), 1) FROM public.tenants))"
            ))
            db.session.commit()
            print(f"  ✅ Secuencia tenants_id_seq reparada")
        except Exception as e:
            print(f"  ⚠️  No se pudo reparar secuencia: {e}")
            db.session.rollback()

        print("\n" + "=" * 60)
        print(f"✅ LIMPIEZA COMPLETA ({errores} errores)")
        print("=" * 60)
        sys.exit(0 if errores == 0 else 1)


if __name__ == "__main__":
    main()