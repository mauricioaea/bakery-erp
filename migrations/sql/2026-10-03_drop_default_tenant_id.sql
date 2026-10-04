-- ============================================================
-- DT-31: Eliminar DEFAULT 1 de columnas tenant_id y panaderia_id
-- ============================================================
-- Fecha: 3 de Octubre, 2026
--
-- CONTEXTO
-- --------
-- DT-20 Fase C Tanda 2 y 3 eliminaron default=1 en los modelos
-- SQLAlchemy (models.py). Sin embargo, la definicion de las columnas
-- en PostgreSQL seguia teniendo DEFAULT 1, por lo que cualquier
-- INSERT SQL directo que omitiera el campo caia silenciosamente
-- en tenant_1 / panaderia_id=1.
--
-- Este script elimina el DEFAULT a nivel PostgreSQL para completar
-- el fix de raiz: si un INSERT olvida el campo, PostgreSQL ahora
-- falla con NOT NULL violation (fail-fast), igual que el ORM.
--
-- TABLAS AFECTADAS (7 columnas en 4 schemas)
-- ------------------------------------------
--   tenant_1.usuarios.tenant_id
--   tenant_25.panaderias.panaderia_id
--   tenant_25.usuarios.tenant_id
--   tenant_26.panaderias.panaderia_id
--   tenant_26.usuarios.tenant_id
--   tenant_27.panaderias.panaderia_id
--   tenant_27.usuarios.tenant_id
--
-- TENANTS FUTUROS
-- ---------------
-- Los tenants nuevos nacen limpios: como models.py ya no tiene
-- default=1, db.create_all() crea las columnas SIN DEFAULT.
-- Este script NO necesita ejecutarse para tenants futuros.
--
-- VERIFICACION
-- ------------
-- Despues de ejecutar, verificar con:
--   SELECT table_schema, table_name, column_name, column_default
--   FROM information_schema.columns
--   WHERE table_schema IN ('tenant_1','tenant_25','tenant_26','tenant_27')
--     AND column_name IN ('tenant_id','panaderia_id')
--     AND column_default IS NOT NULL;
-- Esperado: 0 filas.
--
-- REVERSION (si fuera necesario)
-- -----------------------------
-- No hay reversion automatica. El default original era 1,
-- que permitia caer silenciosamente en tenant_1. Ese comportamiento
-- es lo que estamos eliminando (bug sistemico).
--
-- HANDOFF: v7.4.1
-- ============================================================

ALTER TABLE tenant_1.usuarios     ALTER COLUMN tenant_id    DROP DEFAULT;
ALTER TABLE tenant_25.panaderias  ALTER COLUMN panaderia_id DROP DEFAULT;
ALTER TABLE tenant_25.usuarios    ALTER COLUMN tenant_id    DROP DEFAULT;
ALTER TABLE tenant_26.panaderias  ALTER COLUMN panaderia_id DROP DEFAULT;
ALTER TABLE tenant_26.usuarios    ALTER COLUMN tenant_id    DROP DEFAULT;
ALTER TABLE tenant_27.panaderias  ALTER COLUMN panaderia_id DROP DEFAULT;
ALTER TABLE tenant_27.usuarios    ALTER COLUMN tenant_id    DROP DEFAULT;