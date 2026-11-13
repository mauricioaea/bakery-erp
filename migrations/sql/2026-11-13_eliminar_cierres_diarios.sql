-- 2026-11-13_eliminar_cierres_diarios.sql
-- Elimina la tabla cierres_diarios (legacy) en todos los tenants activos.
--
-- Contexto: la tabla cierres_diarios nunca se llenó (el cierre diario es un
-- reporte consultable /reporte/cierre_caja, no un INSERT). El código que la
-- usaba (realizar_cierre, endpoints /api/cierre_diario/*) se eliminó en
-- Fase F (13 Nov 2026). Este script borra la tabla de los tenants existentes.
--
-- Uso: psql -U postgres -p 5433 -h localhost -d panaderia_master -f migrations/sql/2026-11-13_eliminar_cierres_diarios.sql
--
-- ⚠️ Requiere backup previo (backup_pre_eliminar_cierres_diarios.backup).

DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT id FROM public.tenants WHERE activo = TRUE ORDER BY id
    LOOP
        EXECUTE format('DROP TABLE IF EXISTS tenant_%s.cierres_diarios CASCADE', r.id);
        RAISE NOTICE 'Tabla cierres_diarios eliminada de tenant_%', r.id;
    END LOOP;
END $$;