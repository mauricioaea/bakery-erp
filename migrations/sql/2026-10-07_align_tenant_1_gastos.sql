-- =============================================
-- DT-5-quinquies: Alinear tenant_1.gastos con estructura canónica
-- Fecha: 7 Oct 2026
-- Contexto:
--   - tenant_1.gastos tenía estructura legacy:
--     * categoria: text NOT NULL (debe ser varchar(50) nullable)
--     * concepto: varchar(100) nullable (debe ser NOT NULL)
--     * Sin FK a panaderias(id) ni usuarios(id)
--   - tenant_27.gastos ya está alineada con el ORM Gasto post-DT-38.
--   - Tabla vacía (0 filas) → DROP + CREATE es seguro.
--   - Verificado: sin FKs externas apuntando a la tabla.
--   - Backup previo: backup_pre_dt5quinquies.backup
-- =============================================

BEGIN;

-- 1. Eliminar tabla legacy (vacía)
DROP TABLE tenant_1.gastos CASCADE;

-- 2. Recrear con estructura idéntica a tenant_27.gastos
CREATE TABLE tenant_1.gastos (
    id              SERIAL PRIMARY KEY,
    panaderia_id    INTEGER NOT NULL REFERENCES tenant_1.panaderias(id),
    concepto        VARCHAR(100) NOT NULL,
    fecha_gasto     TIMESTAMP DEFAULT now(),
    categoria       VARCHAR(50),
    monto           DOUBLE PRECISION NOT NULL,
    observaciones   TEXT,
    usuario_id      INTEGER REFERENCES tenant_1.usuarios(id)
);

COMMIT;