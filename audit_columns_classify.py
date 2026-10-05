# audit_columns_classify.py
# Fase C.3.3 - Clasificación de columnas huérfanas por % de poblado
# Uso: python audit_columns_classify.py [tenant_id]
# Por defecto tenant_27.

import sys
from sqlalchemy import text

from app import app, db
import models  # noqa: F401

TENANT_ID = sys.argv[1] if len(sys.argv) > 1 else "27"
SCHEMA = f"tenant_{TENANT_ID}"

SKIP_MODELOS = {"tenants"}

# Lista de huérfanas detectadas en el paso anterior (C.3.2)
# Formato: {tabla: [col1, col2, ...]}
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


def contar(schema: str, tabla: str, columna: str = None) -> int:
    if columna:
        sql = text(f'SELECT COUNT("{columna}") FROM {schema}."{tabla}"')
    else:
        sql = text(f'SELECT COUNT(*) FROM {schema}."{tabla}"')
    return db.session.execute(sql).scalar() or 0


def main():
    with app.app_context():
        print(f"=== CLASIFICACIÓN DE HUÉRFANAS · schema={SCHEMA} ===\n")

        total = 0
        con_datos = 0
        vacias = 0

        resultados = []

        for tabla in sorted(HUERFANAS):
            filas = contar(SCHEMA, tabla)
            for col in HUERFANAS[tabla]:
                total += 1
                no_null = contar(SCHEMA, tabla, col)
                pct = (no_null / filas * 100) if filas else 0.0
                estado = "🟡 VACÍA" if no_null == 0 else "🟢 CON DATOS"
                if no_null == 0:
                    vacias += 1
                else:
                    con_datos += 1
                resultados.append((tabla, col, filas, no_null, pct, estado))

        # Ordenar: con datos primero (mayor %), luego vacías
        resultados.sort(key=lambda r: (-r[4], r[0], r[1]))

        print(f"{'TABLA':<30} {'COLUMNA':<28} {'FILAS':>7} {'NO_NULL':>8} {'%':>7}  ESTADO")
        print("-" * 100)
        for tabla, col, filas, no_null, pct, estado in resultados:
            print(f"{tabla:<30} {col:<28} {filas:>7} {no_null:>8} {pct:>6.1f}%  {estado}")

        print("\n=== RESUMEN ===")
        print(f"Total huérfanas analizadas: {total}")
        print(f"🟢 Con datos:  {con_datos}")
        print(f"🟡 Vacías:     {vacias}")


if __name__ == "__main__":
    main()