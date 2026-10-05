-- ============================================================
-- DT-40: Eliminar columnas legacy de la tabla ventas
-- Fecha: 2026-10-05
-- Autor: Mauricio
-- Contexto: ver HANDOFF.md v7.9 sección 9️⃣ (DT-40)
-- ============================================================
-- Las siguientes 6 columnas existían en la BD pero NO en el ORM.
-- Verificado: todos sus valores eran 0, NULL o constantes.
-- Verificado: 0 referencias en app.py, models.py, reportes.py,
--             seed_demo.py, seeds/*.py, templates/*.html.
-- Aplicado a: tenant_25, tenant_26, tenant_27
-- No aplicado a: tenant_1 (no tenía las columnas)
-- ============================================================

-- tenant_25
ALTER TABLE tenant_25.ventas DROP COLUMN IF EXISTS total_venta;
ALTER TABLE tenant_25.ventas DROP COLUMN IF EXISTS total_donacion;
ALTER TABLE tenant_25.ventas DROP COLUMN IF EXISTS impuesto;
ALTER TABLE tenant_25.ventas DROP COLUMN IF EXISTS descuento;
ALTER TABLE tenant_25.ventas DROP COLUMN IF EXISTS consecutivo;
ALTER TABLE tenant_25.ventas DROP COLUMN IF EXISTS observaciones;

-- tenant_26
ALTER TABLE tenant_26.ventas DROP COLUMN IF EXISTS total_venta;
ALTER TABLE tenant_26.ventas DROP COLUMN IF EXISTS total_donacion;
ALTER TABLE tenant_26.ventas DROP COLUMN IF EXISTS impuesto;
ALTER TABLE tenant_26.ventas DROP COLUMN IF EXISTS descuento;
ALTER TABLE tenant_26.ventas DROP COLUMN IF EXISTS consecutivo;
ALTER TABLE tenant_26.ventas DROP COLUMN IF EXISTS observaciones;

-- tenant_27
ALTER TABLE tenant_27.ventas DROP COLUMN IF EXISTS total_venta;
ALTER TABLE tenant_27.ventas DROP COLUMN IF EXISTS total_donacion;
ALTER TABLE tenant_27.ventas DROP COLUMN IF EXISTS impuesto;
ALTER TABLE tenant_27.ventas DROP COLUMN IF EXISTS descuento;
ALTER TABLE tenant_27.ventas DROP COLUMN IF EXISTS consecutivo;
ALTER TABLE tenant_27.ventas DROP COLUMN IF EXISTS observaciones;