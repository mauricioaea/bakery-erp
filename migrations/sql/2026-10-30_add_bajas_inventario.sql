-- ============================================================
-- Migración: Feature "Baja de Inventario"
-- Fecha: 2026-10-30
-- Feature: Registro de pérdidas de productos de vitrina
--          por VENCIMIENTO o ROTURA/Daño.
--
-- Aplica a: tenant_1, tenant_27 (y cualquier tenant existente).
-- Futuros tenants: se crean automáticamente vía
--                  crear_tenant_saas() (app.py, bloque # 11.1)
--                  y por db.create_all() (modelo BajaInventario
--                  en models.py).
--
-- IMPORTANTE:
--   - NO reemplaza ni afecta el flujo "Consumo Interno/Donaciones"
--     del POS (ese es uso autorizado, no pérdida).
--   - NO descuenta materias primas (solo productos de vitrina,
--     tipo_producto = 'produccion').
--   - Impacta estado_resultados como línea separada
--     "Pérdidas por Baja de Inventario".
--
-- Esta migración es IDEMPOTENTE: se puede ejecutar múltiples veces
-- sin efectos secundarios (CREATE TABLE IF NOT EXISTS + CREATE INDEX
-- IF NOT EXISTS).
-- ============================================================


-- ------------------------------------------------------------
-- PARTE 1: tenant_1 (plantilla de referencia)
-- ------------------------------------------------------------
BEGIN;

CREATE TABLE IF NOT EXISTS tenant_1.bajas_inventario (
    id SERIAL PRIMARY KEY,
    panaderia_id INTEGER NOT NULL REFERENCES tenant_1.panaderias(id),
    producto_id INTEGER NOT NULL REFERENCES tenant_1.productos(id),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    motivo VARCHAR(20) NOT NULL CHECK (motivo IN ('VENCIMIENTO', 'ROTURA')),
    costo_unitario DOUBLE PRECISION NOT NULL DEFAULT 0,
    costo_total DOUBLE PRECISION NOT NULL DEFAULT 0,
    usuario_id INTEGER REFERENCES tenant_1.usuarios(id),
    fecha_baja TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    observaciones TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_baja_motivo_1 CHECK (motivo IN ('VENCIMIENTO', 'ROTURA'))
);

CREATE INDEX IF NOT EXISTS idx_bajas_inventario_fecha_1
    ON tenant_1.bajas_inventario (panaderia_id, fecha_baja);

CREATE INDEX IF NOT EXISTS idx_bajas_inventario_producto_1
    ON tenant_1.bajas_inventario (producto_id);

COMMIT;


-- ------------------------------------------------------------
-- PARTE 2: tenant_27 (demo comercial)
-- ------------------------------------------------------------
BEGIN;

CREATE TABLE IF NOT EXISTS tenant_27.bajas_inventario (
    id SERIAL PRIMARY KEY,
    panaderia_id INTEGER NOT NULL REFERENCES tenant_27.panaderias(id),
    producto_id INTEGER NOT NULL REFERENCES tenant_27.productos(id),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    motivo VARCHAR(20) NOT NULL CHECK (motivo IN ('VENCIMIENTO', 'ROTURA')),
    costo_unitario DOUBLE PRECISION NOT NULL DEFAULT 0,
    costo_total DOUBLE PRECISION NOT NULL DEFAULT 0,
    usuario_id INTEGER REFERENCES tenant_27.usuarios(id),
    fecha_baja TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    observaciones TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_baja_motivo_27 CHECK (motivo IN ('VENCIMIENTO', 'ROTURA'))
);

CREATE INDEX IF NOT EXISTS idx_bajas_inventario_fecha_27
    ON tenant_27.bajas_inventario (panaderia_id, fecha_baja);

CREATE INDEX IF NOT EXISTS idx_bajas_inventario_producto_27
    ON tenant_27.bajas_inventario (producto_id);

COMMIT;


-- ============================================================
-- FIN
-- ============================================================
-- Verificación posterior (ejecutar a mano si querés confirmar):
--
-- SELECT table_schema, column_name, data_type, is_nullable, column_default
-- FROM information_schema.columns
-- WHERE table_name = 'bajas_inventario'
--   AND table_schema IN ('tenant_1', 'tenant_27')
-- ORDER BY table_schema, ordinal_position;
--
-- SELECT conname, pg_get_constraintdef(oid)
-- FROM pg_constraint
-- WHERE conrelid IN (
--   'tenant_1.bajas_inventario'::regclass,
--   'tenant_27.bajas_inventario'::regclass
-- )
-- ORDER BY conname;
-- ============================================================