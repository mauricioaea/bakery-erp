-- ============================================================
-- DT-37: i18n reportes (Fase 0.3)
-- Agrega columna 'idioma' a configuracion_sistema por tenant.
-- 
-- Motivo: soportar multi-idioma en reportes PDF (Flask-Babel).
-- Fallback: 'es' (comportamiento actual).
-- 
-- Fecha: 12 de Octubre, 2026
-- Autor: Mauricio + asistente
-- ============================================================

-- Tenant 1 (Panadería Principal)
ALTER TABLE tenant_1.configuracion_sistema
    ADD COLUMN IF NOT EXISTS idioma VARCHAR(5) NOT NULL DEFAULT 'es';

-- Tenant 27 (Panadería Demo)
ALTER TABLE tenant_27.configuracion_sistema
    ADD COLUMN IF NOT EXISTS idioma VARCHAR(5) NOT NULL DEFAULT 'es';

-- ============================================================
-- Verificación post-migración:
-- SELECT table_schema, column_name, data_type, column_default, is_nullable
-- FROM information_schema.columns
-- WHERE table_name='configuracion_sistema'
--   AND column_name='idioma'
-- ORDER BY table_schema;
-- 
-- Esperado: 2 filas (tenant_1, tenant_27) con default 'es'::character varying
-- ============================================================