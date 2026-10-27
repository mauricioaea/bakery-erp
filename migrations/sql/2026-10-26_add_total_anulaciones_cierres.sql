-- ============================================================
-- Migración: agregar total_anulaciones a cierres_diarios
-- Fecha: 2026-10-26
-- Feature: Anulación de Recibos POS
-- Aplica a: tenant_1, tenant_27 (y cualquier tenant existente)
-- Futuros tenants: se crean automáticamente vía db.create_all()
--                  (modelo CierreDiario actualizado en models.py)
-- ============================================================
-- Idempotente.
-- ============================================================

BEGIN;

-- tenant_1
ALTER TABLE tenant_1.cierres_diarios
  ADD COLUMN IF NOT EXISTS total_anulaciones FLOAT DEFAULT 0;

-- tenant_27
ALTER TABLE tenant_27.cierres_diarios
  ADD COLUMN IF NOT EXISTS total_anulaciones FLOAT DEFAULT 0;

COMMIT;

-- ============================================================
-- Verificación posterior:
-- SELECT table_schema, column_name, data_type, column_default
-- FROM information_schema.columns
-- WHERE table_name='cierres_diarios'
--   AND column_name='total_anulaciones'
--   AND table_schema IN ('tenant_1','tenant_27');
-- ============================================================