-- ============================================================
-- Migración: auditoría de anulación y desconciliación
-- Fecha: 2026-11-09
-- Autor: Mauricio (PanaderíaPro)
-- Contexto: DT-nueva-MEDIA (desconciliación + ANULADO + whitelist)
-- Aplica a: tenant_1 (plantilla), tenant_27 (demo), tenant_31 (pruebas)
-- ============================================================

-- tenant_1 (plantilla)
ALTER TABLE tenant_1.depositos_bancarios ADD COLUMN IF NOT EXISTS motivo_anulacion TEXT;
ALTER TABLE tenant_1.depositos_bancarios ADD COLUMN IF NOT EXISTS fecha_anulacion TIMESTAMP;
ALTER TABLE tenant_1.depositos_bancarios ADD COLUMN IF NOT EXISTS motivo_desconciliacion TEXT;
ALTER TABLE tenant_1.depositos_bancarios ADD COLUMN IF NOT EXISTS fecha_desconciliacion TIMESTAMP;

-- tenant_27 (demo)
ALTER TABLE tenant_27.depositos_bancarios ADD COLUMN IF NOT EXISTS motivo_anulacion TEXT;
ALTER TABLE tenant_27.depositos_bancarios ADD COLUMN IF NOT EXISTS fecha_anulacion TIMESTAMP;
ALTER TABLE tenant_27.depositos_bancarios ADD COLUMN IF NOT EXISTS motivo_desconciliacion TEXT;
ALTER TABLE tenant_27.depositos_bancarios ADD COLUMN IF NOT EXISTS fecha_desconciliacion TIMESTAMP;

-- tenant_31 (pruebas)
ALTER TABLE tenant_31.depositos_bancarios ADD COLUMN IF NOT EXISTS motivo_anulacion TEXT;
ALTER TABLE tenant_31.depositos_bancarios ADD COLUMN IF NOT EXISTS fecha_anulacion TIMESTAMP;
ALTER TABLE tenant_31.depositos_bancarios ADD COLUMN IF NOT EXISTS motivo_desconciliacion TEXT;
ALTER TABLE tenant_31.depositos_bancarios ADD COLUMN IF NOT EXISTS fecha_desconciliacion TIMESTAMP;