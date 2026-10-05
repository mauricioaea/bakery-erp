# audit_columns_classify_v2.py
# Fase C.3.3b - Re-clasificación con criterio correcto (COUNT DISTINCT)
# Uso: python audit_columns_classify_v2.py [tenant_id]

import sys
from sqlalchemy import text

from app import app, db
import models  # noqa: F401

TENANT_ID = sys.argv[1] if len(sys.argv) > 1 else "27"
SCHEMA = f"tenant_{TENANT_ID}"

HUERFANAS = {
    "categorias": ["descripcion"],
    "compras": ["estado", "fecha_compra", "observaciones", "proveedor_id"],
    "configuracion_produccion": [
        "activar_alertas", "alerta_stock_minimo", "dias_historial_ventas",
        "inventario_seguridad", "produccion_automatica", "rotacion_recomendada",
        "vida_util_pan_dias",
    ],
    "configuracion_sistema": [
        "modo_mantenimiento", "nombre_sistema", "ultima_actualizacion", "version",
    ],
    "control_vida_util": ["dias_restantes", "fecha_control"],
    "depositos_bancarios": [
        "fecha_registro", "observaciones", "tipo", "usuario_id",
    ],
    "detalle_compras": ["producto_id", "subtotal"],
    "gastos": ["concepto", "fecha_gasto", "observaciones", "usuario_id"],
    "historial_inventario": [
        "cantidad_anterior", "cantidad_nueva", "observaciones",
        "producto_id", "usuario_id",
    ],
    "historial_mantenimientos": ["activo_fijo_id", "realizado_por"],
    "historial_rotacion_producto": ["fecha_calculo", "rotacion"],
    "jornadas_ventas": ["total_tarjeta"],
    "logs_sistema": ["fecha_log", "ip_origen"],
    "ordenes_produccion": [
        "cantidad_real", "fecha_orden", "usuario_creacion_id",
    ],
    "pagos_individuales": ["usuario_id"],
    "productos_externos": ["proveedor"],
    "registros_diarios": [
        "observaciones", "saldo_final", "saldo_inicial",
        "total_donaciones", "total_gastos", "total_ventas",
    ],
    "registros_financieros": [
        "descripcion", "egreso", "fecha", "ingreso",
        "saldo", "tipo", "usuario_id",
    ],
    "stock_productos": ["producto_id", "stock_maximo"],
    "sucursales": ["email"],
    "ventas": [
        "consecutivo", "descuento", "estado", "impuesto",
        "observaciones", "total_donacion", "total_venta",
    ],
}


def analizar_columna(schema: str, tabla: str, columna: str) -> dict:
    """Devuelve estadísticas reales de una columna."""
    sql = text(f"""
        SELECT
            COUNT(*) AS total_filas,
            COUNT("{columna}") AS no_null,
            COUNT(DISTINCT "{columna}") AS distintos,
            MIN("{columna}"::text) AS min_val,
            MAX("{columna}"::text) AS max_val
        FROM {schema}."{tabla}"
    """)
    r = db.session.execute(sql).fetchone()
    return {
        "total": r[0],
        "no_null": r[1],
        "distintos": r[2],
        "min_val": r[3],
        "max_val": r[4],
    }


def clasificar(stats: dict) -> str:
    """Clasificación correcta:
    - MUERTA: 0 no_null o todos NULL, o 0 distintos.
    - CONSTANTE: distintos==1 y no_null>0 → todos el mismo valor.
    - REAL: distintos>1 → variedad real.
    """
    if stats["total"] == 0:
        return "⚪ SIN FILAS"
    if stats["no_null"] == 0:
        return "🔴 MUERTA (todo NULL)"
    if stats["distintos"] == 0:
        return "🔴 MUERTA (0 distintos)"
    if stats["distintos"] == 1:
        return "🟡 CONSTANTE (1 valor)"
    return "🟢 REAL (variedad)"


def main():
    with app.app_context():
        print(f"=== RE-CLASIFICACIÓN v2 · schema={SCHEMA} ===\n")
        print(f"{'TABLA':<28} {'COLUMNA':<24} {'TOT':>6} {'NN':>6} {'DIST':>5}  {'VALOR ÚNICO':<20} CLASE")
        print("-" * 130)

        resumen = {"MUERTA": 0, "CONSTANTE": 0, "REAL": 0, "SIN FILAS": 0}
        detalle = []

        for tabla in sorted(HUERFANAS):
            for col in HUERFANAS[tabla]:
                st = analizar_columna(SCHEMA, tabla, col)
                clase = clasificar(st)
                resumen[clase.split()[1] if " " in clase else clase] = resumen.get(clase.split()[1] if " " in clase else clase, 0) + 1
                valor_unico = ""
                if st["distintos"] == 1 and st["no_null"] > 0:
                    valor_unico = str(st["min_val"])[:18]
                print(f"{tabla:<28} {col:<24} {st['total']:>6} {st['no_null']:>6} {st['distintos']:>5}  {valor_unico:<20} {clase}")
                detalle.append((tabla, col, clase, st))

        print("\n=== RESUMEN ===")
        for k, v in resumen.items():
            print(f"  {k}: {v}")

        print("\n=== DETALLE POR GRUPO ===")
        for grupo in ["REAL", "CONSTANTE", "MUERTA", "SIN FILAS"]:
            columnas = [(t, c) for (t, c, cl, _) in detalle if grupo in cl]
            if columnas:
                print(f"\n{grupo} ({len(columnas)}):")
                for t, c in columnas:
                    print(f"  - {t}.{c}")


if __name__ == "__main__":
    main()