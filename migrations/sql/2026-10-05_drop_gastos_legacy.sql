-- ============================================================
-- DT-5-ter: DROP columnas legacy en tabla gastos
-- Fecha: 2026-10-05
--
-- Contexto:
--   - `fecha` (timestamp): es basura del re-seed.
--     Las 49 filas de tenant_27 tienen el MISMO valor (hora del
--     último --reset-all). El DEFAULT CURRENT_TIMESTAMP la
--     rellenó sin que ningún INSERT la nombrara.
--     Los datos reales viven en `fecha_gasto`.
--   - `descripcion` (varchar): 100% vacía en todos los schemas
--     (0/49 en tenant_27, 0/0 en tenant_1).
--   - Ninguna columna es leída por app.py, reportes.py ni templates.
--   - El CREATE TABLE en app.py:730 ya NO las declara (post DT-38 Lote B).
--
-- Ejecutado tras backup: backup_pre_dt5ter.backup (377 KB)
-- ============================================================

BEGIN;

-- tenant_1 (0 filas)
ALTER TABLE tenant_1.gastos DROP COLUMN IF EXISTS fecha;
ALTER TABLE tenant_1.gastos DROP COLUMN IF EXISTS descripcion;

-- tenant_27 (49 filas)
ALTER TABLE tenant_27.gastos DROP COLUMN IF EXISTS fecha;
ALTER TABLE tenant_27.gastos DROP COLUMN IF EXISTS descripcion;

COMMIT;

-- Verificación post-DROP
-- Esperado: solo 'concepto' y 'fecha_gasto' (las nuevas)
SELECT table_schema, column_name
FROM information_schema.columns
WHERE table_name = 'gastos'
  AND column_name IN ('fecha', 'descripcion', 'fecha_gasto', 'concepto')
ORDER BY table_schema, column_name;