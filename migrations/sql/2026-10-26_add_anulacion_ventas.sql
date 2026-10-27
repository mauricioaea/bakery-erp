-- ============================================================
-- Migración: Feature Anulación de Recibos POS
-- Fecha: 2026-10-26
-- Aplica a: tenant_1, tenant_27 (y cualquier tenant existente)
-- Futuros tenants: se crean automáticamente vía db.create_all()
--                  (modelo Venta actualizado en models.py)
-- ============================================================
-- Esta migración es IDEMPOTENTE: se puede ejecutar múltiples veces
-- sin efectos secundarios.
-- ============================================================

-- ------------------------------------------------------------
-- PARTE 1: tenant_27
--   - Normalizar 'estado' existente ('completada' -> 'COMPLETADA')
--   - Ajustar default
--   - Agregar 4 columnas de auditoría de anulación
-- ------------------------------------------------------------
BEGIN;

-- 1.1 Normalizar valores existentes a mayúscula
UPDATE tenant_27.ventas
SET estado = UPPER(estado)
WHERE estado IS NOT NULL AND estado <> UPPER(estado);

-- 1.2 Ajustar default
ALTER TABLE tenant_27.ventas
  ALTER COLUMN estado SET DEFAULT 'COMPLETADA';

-- 1.3 Asegurar NOT NULL (actualmente es nullable)
--     Solo si no hay NULLs; los datos actuales son 'completada' (no NULL)
UPDATE tenant_27.ventas SET estado = 'COMPLETADA' WHERE estado IS NULL;
ALTER TABLE tenant_27.ventas
  ALTER COLUMN estado SET NOT NULL;

-- 1.4 Agregar columnas de auditoría de anulación
ALTER TABLE tenant_27.ventas
  ADD COLUMN IF NOT EXISTS motivo_anulacion VARCHAR(50),
  ADD COLUMN IF NOT EXISTS observacion_anulacion TEXT,
  ADD COLUMN IF NOT EXISTS fecha_anulacion TIMESTAMP,
  ADD COLUMN IF NOT EXISTS usuario_anulacion_id INTEGER;

COMMIT;

-- ------------------------------------------------------------
-- PARTE 2: tenant_1
--   - Agregar 'estado' (no la tiene)
--   - Agregar 4 columnas de auditoría de anulación
-- ------------------------------------------------------------
BEGIN;

-- 2.1 Agregar 'estado' con default para filas existentes
ALTER TABLE tenant_1.ventas
  ADD COLUMN IF NOT EXISTS estado VARCHAR(20) NOT NULL DEFAULT 'COMPLETADA';

-- 2.2 Agregar columnas de auditoría de anulación
ALTER TABLE tenant_1.ventas
  ADD COLUMN IF NOT EXISTS motivo_anulacion VARCHAR(50),
  ADD COLUMN IF NOT EXISTS observacion_anulacion TEXT,
  ADD COLUMN IF NOT EXISTS fecha_anulacion TIMESTAMP,
  ADD COLUMN IF NOT EXISTS usuario_anulacion_id INTEGER;

COMMIT;

-- ============================================================
-- FIN
-- ============================================================
-- Verificación posterior (ejecutar a mano):
--
-- SELECT table_schema, column_name, data_type, is_nullable, column_default
-- FROM information_schema.columns
-- WHERE table_name='ventas'
--   AND table_schema IN ('tenant_1','tenant_27')
--   AND column_name IN ('estado','motivo_anulacion','observacion_anulacion',
--                       'fecha_anulacion','usuario_anulacion_id')
-- ORDER BY table_schema, column_name;
-- ============================================================