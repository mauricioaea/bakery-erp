-- Agrega la columna idioma a configuracion_sistema en los 4 tenants.
-- Idempotente (IF NOT EXISTS).
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT id FROM public.tenants WHERE activo = TRUE ORDER BY id
    LOOP
        EXECUTE format('ALTER TABLE tenant_%s.configuracion_sistema ADD COLUMN IF NOT EXISTS idioma VARCHAR(5) NOT NULL DEFAULT ''es''', r.id);
        RAISE NOTICE 'Columna idioma verificada/agregada en tenant_%', r.id;
    END LOOP;
END $$;