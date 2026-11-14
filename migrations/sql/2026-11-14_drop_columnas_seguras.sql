-- Elimina 8 columnas 100% seguras (Grupo 2, Fase F, 14 Nov).
-- NO toca sucursal_id, proveedor.email, pagos_individuales.usuario_id
-- ni configuracion_sistema.
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT id FROM public.tenants WHERE activo = TRUE ORDER BY id
    LOOP
        -- configuracion_produccion (7 columnas)
        EXECUTE format('ALTER TABLE tenant_%s.configuracion_produccion DROP COLUMN IF EXISTS produccion_automatica CASCADE', r.id);
        EXECUTE format('ALTER TABLE tenant_%s.configuracion_produccion DROP COLUMN IF EXISTS alerta_stock_minimo CASCADE', r.id);
        EXECUTE format('ALTER TABLE tenant_%s.configuracion_produccion DROP COLUMN IF EXISTS dias_historial_ventas CASCADE', r.id);
        EXECUTE format('ALTER TABLE tenant_%s.configuracion_produccion DROP COLUMN IF EXISTS inventario_seguridad CASCADE', r.id);
        EXECUTE format('ALTER TABLE tenant_%s.configuracion_produccion DROP COLUMN IF EXISTS rotacion_recomendada CASCADE', r.id);
        EXECUTE format('ALTER TABLE tenant_%s.configuracion_produccion DROP COLUMN IF EXISTS vida_util_pan_dias CASCADE', r.id);
        EXECUTE format('ALTER TABLE tenant_%s.configuracion_produccion DROP COLUMN IF EXISTS activar_alertas CASCADE', r.id);
        -- panaderias (1 columna)
        EXECUTE format('ALTER TABLE tenant_%s.panaderias DROP COLUMN IF EXISTS panaderia_id CASCADE', r.id);
        RAISE NOTICE 'Columnas seguras eliminadas de tenant_%', r.id;
    END LOOP;
END $$;