# _test_tenant_schema.py
# Test de verificación de schema: compara models.py (ORM) contra la BD real de un tenant.
# Uso: python _test_tenant_schema.py [tenant_id]
#   - Sin argumento: usa tenant_34 (tenant de pruebas actual).
# Exit code: 0 = OK, 1 = falla (schema no existe, tablas faltantes, o columnas del ORM que faltan en BD).

import sys
from sqlalchemy import inspect, text

# Importar la app y db
from app import app, db
import models  # noqa: F401  (registra los modelos en db.metadata)

TENANT_ID = sys.argv[1] if len(sys.argv) > 1 else "34"
SCHEMA = f"tenant_{TENANT_ID}"

# Modelos que NO viven en el schema del tenant
SKIP_MODELOS = {"tenants"}  # viven en public


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
        print(f"=== AUDITORÍA DE COLUMNAS · schema={SCHEMA} ===")
        
        # ✅ v3: Verificar que el schema existe
        schema_exists = db.session.execute(
            text("SELECT 1 FROM information_schema.schemata WHERE schema_name = :schema"),
            {"schema": SCHEMA}
        ).fetchone()
        
        if not schema_exists:
            print(f"❌ FALLA: schema {SCHEMA} NO existe.")
            sys.exit(1)
        
        # ✅ v3: Verificar que el schema tiene tablas
        tables_count = db.session.execute(
            text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = :schema AND table_type = 'BASE TABLE'"),
            {"schema": SCHEMA}
        ).scalar()
        
        if tables_count == 0:
            print(f"❌ FALLA: schema {SCHEMA} existe pero está vacío (0 tablas).")
            sys.exit(1)
        
        # Recolectar modelos por __tablename__
        modelos = {}
        for cls in db.Model.__subclasses__():
            tabla = getattr(cls, "__tablename__", None)
            if not tabla:
                continue
            if tabla in SKIP_MODELOS:
                continue
            modelos[tabla] = cls
        
        print(f"Modelos con __tablename__: {len(modelos)}\n")
        
        total_ok = 0
        total_solo_modelo = 0
        total_solo_bd = 0
        total_tablas_faltantes = 0  # ✅ v3
        
        for tabla, cls in sorted(modelos.items()):
            cols_modelo = columnas_modelo(cls)
            cols_bd = columnas_bd(SCHEMA, tabla)
            
            if not cols_bd:
                print(f"❌  {tabla}: NO EXISTE en {SCHEMA} (pero sí en el ORM)")
                total_solo_modelo += len(cols_modelo)  # ✅ v3: contar todas como faltantes
                total_tablas_faltantes += 1  # ✅ v3
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
        print(f"Tablas del ORM que NO existen en BD: {total_tablas_faltantes}")
        print(f"Columnas solo en ORM (faltan en BD): {total_solo_modelo}")
        print(f"Columnas solo en BD (huérfanas):     {total_solo_bd}")
        
        # Exit code: falla si hay tablas o columnas del ORM que faltan en BD
        if total_solo_modelo > 0 or total_tablas_faltantes > 0:
            print(f"\n❌ FALLA: {total_tablas_faltantes} tablas y {total_solo_modelo} columnas del ORM no existen en {SCHEMA}.")
            sys.exit(1)
        
        print(f"\n✅ {SCHEMA}: OK ({total_ok} tablas sincronizadas, 0 columnas del ORM faltantes)")
        if total_solo_bd > 0:
            print(f"   ℹ️  {total_solo_bd} columnas huérfanas en BD (legacy, no rompen el ORM).")
        sys.exit(0)


if __name__ == "__main__":
    main()