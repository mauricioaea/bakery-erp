# audit_columns.py
# Fase C.3 - Auditoría de columnas huérfanas
# Uso: python audit_columns.py [tenant_id]
# Por defecto audita tenant_27.

import sys
from sqlalchemy import inspect, text

# Importar la app y db
from app import app, db
import models  # noqa: F401  (registra los modelos en db.metadata)

TENANT_ID = sys.argv[1] if len(sys.argv) > 1 else "27"
SCHEMA = f"tenant_{TENANT_ID}"

# Modelos que NO viven en el schema del tenant
SKIP_MODELOS = {"tenants"}  # se van a public


def columnas_bd(schema: str, tabla: str) -> dict:
    """Devuelve {columna: {type, nullable, default}} desde information_schema."""
    sql = text("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema = :schema AND table_name = :tabla
        ORDER BY ordinal_position
    """)
    rows = db.session.execute(sql, {"schema": schema, "tabla": tabla}).fetchall()
    return {r[0]: {"type": r[1], "nullable": r[2], "default": r[3]} for r in rows}


def columnas_modelo(model) -> dict:
    """Devuelve {columna: {type, nullable, default}} desde SQLAlchemy."""
    out = {}
    for col in model.__table__.columns:
        out[col.name] = {
            "type": str(col.type),
            "nullable": "YES" if col.nullable else "NO",
            "default": str(col.default.arg) if col.default is not None else None,
        }
    return out


def main():
    with app.app_context():
        # Recolectar modelos por __tablename__
        modelos = {}
        for cls in db.Model.__subclasses__():
            tabla = getattr(cls, "__tablename__", None)
            if not tabla:
                continue
            if tabla in SKIP_MODELOS:
                continue
            modelos[tabla] = cls

        print(f"=== AUDITORÍA DE COLUMNAS · schema={SCHEMA} ===")
        print(f"Modelos con __tablename__: {len(modelos)}\n")

        total_ok = 0
        total_solo_modelo = 0
        total_solo_bd = 0

        for tabla, cls in sorted(modelos.items()):
            cols_modelo = columnas_modelo(cls)
            cols_bd = columnas_bd(SCHEMA, tabla)

            if not cols_bd:
                print(f"⚠️  {tabla}: NO EXISTE en {SCHEMA} (pero sí en el ORM)")
                continue

            solo_modelo = set(cols_modelo) - set(cols_bd)
            solo_bd = set(cols_bd) - set(cols_modelo)
            en_ambos = set(cols_modelo) & set(cols_bd)

            if not solo_modelo and not solo_bd:
                total_ok += 1
                continue

            print(f"\n📋 {tabla}")
            print(f"   columnas ORM={len(cols_modelo)}  BD={len(cols_bd)}  comunes={len(en_ambos)}")

            if solo_modelo:
                total_solo_modelo += len(solo_modelo)
                print(f"   🟡 En ORM, NO en BD ({len(solo_modelo)}):")
                for c in sorted(solo_modelo):
                    print(f"        - {c}  ({cols_modelo[c]['type']})")

            if solo_bd:
                total_solo_bd += len(solo_bd)
                print(f"   🔴 En BD, NO en ORM ({len(solo_bd)}):")
                for c in sorted(solo_bd):
                    print(f"        - {c}  ({cols_bd[c]['type']}, nullable={cols_bd[c]['nullable']})")

        print("\n=== RESUMEN ===")
        print(f"Tablas 100% sincronizadas: {total_ok}")
        print(f"Columnas solo en ORM (faltan en BD): {total_solo_modelo}")
        print(f"Columnas solo en BD (huérfanas):     {total_solo_bd}")


if __name__ == "__main__":
    main()