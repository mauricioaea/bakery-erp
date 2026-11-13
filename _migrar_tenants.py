# _migrar_tenants.py
# Script manual de migración de esquema para tenants existentes.
# Uso:
#   python _migrar_tenants.py              # migra TODOS los tenants activos
#   python _migrar_tenants.py 34           # migra SOLO tenant_34
#   python _migrar_tenants.py --dry-run    # muestra qué haría sin ejecutar
#
# Estrategia:
#   - Reutiliza _sincronizar_columnas_tenant() y db.create_all() de app.py.
#   - Se ejecuta MANUALMENTE en el deploy (no en el arranque del servidor).
#   - Idempotente: se puede correr 2 veces sin daño.
#
# Ver _test_tenant_schema.py para verificar que un tenant está alineado.

import sys
import os

# Importar la app y los modelos
from app import app, db
from app import _sincronizar_columnas_tenant, set_tenant_schema
from models import Tenant


def migrar_tenant(tenant, dry_run=False):
    """Aplica db.create_all() + _sincronizar_columnas_tenant() a un tenant."""
    tenant_id = tenant.id
    schema_name = f"tenant_{tenant_id}"

    print(f"\n📋 Tenant {tenant_id} ({tenant.nombre}) → schema {schema_name}")

    # 1. Verificar que el schema existe
    from sqlalchemy import text
    result = db.session.execute(
        text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema"),
        {'schema': schema_name}
    ).fetchone()

    if not result:
        print(f"   ⚠️  Schema {schema_name} NO existe. Saltando.")
        return 0, 0

    if dry_run:
        print(f"   [DRY-RUN] Haría: set_tenant_schema({tenant_id}) + db.create_all() + _sincronizar_columnas_tenant()")
        return 0, 0

    # 2. Configurar search_path
    set_tenant_schema(tenant_id)

    # 3. Crear tablas faltantes (db.create_all es idempotente)
    db.create_all()
    print(f"   ✅ Tablas verificadas")

    # 4. Sincronizar columnas faltantes
    columnas_agregadas, errores = _sincronizar_columnas_tenant(schema_name)
    if columnas_agregadas > 0:
        print(f"   ✅ {columnas_agregadas} columnas agregadas")
    if errores > 0:
        print(f"   ⚠️  {errores} errores")

    return columnas_agregadas, errores


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if not a.startswith("--")]

    with app.app_context():
        if args:
            # Tenant específico
            tenant_id = int(args[0])
            tenant = Tenant.query.filter_by(id=tenant_id).first()
            if not tenant:
                print(f"❌ Tenant {tenant_id} no encontrado")
                sys.exit(1)
            tenants = [tenant]
        else:
            # Todos los activos
            tenants = Tenant.query.filter_by(activo=True).all()
            if not tenants:
                print("⚠️ No hay tenants activos")
                sys.exit(0)

        print(f"🔧 Migrando {len(tenants)} tenant(s){' [DRY-RUN]' if dry_run else ''}")

        total_cols = 0
        total_errors = 0
        for tenant in tenants:
            try:
                cols, errs = migrar_tenant(tenant, dry_run=dry_run)
                total_cols += cols
                total_errors += errs
            except Exception as e:
                print(f"   ❌ Error migrando tenant {tenant.id}: {e}")
                db.session.rollback()
                total_errors += 1

        print(f"\n{'=' * 60}")
        print(f"✅ MIGRACIÓN COMPLETA")
        print(f"   📊 Columnas agregadas: {total_cols}")
        if total_errors > 0:
            print(f"   ⚠️  Errores: {total_errors}")
        print(f"{'=' * 60}")

        sys.exit(0 if total_errors == 0 else 1)


if __name__ == "__main__":
    main()