-- ============================================================
-- DT-36: Limpieza de tablas huérfanas en public.*
-- Fecha: 2026-10-05
-- Autor: Mauricio
-- Contexto: ver HANDOFF.md v8.2 sección 9️⃣ (DT-36)
-- ============================================================
-- A lo largo del desarrollo se crearon 50+ tenants de prueba
-- que fueron borrados desde la UI. El endpoint /eliminar_cliente
-- solo hacía DROP SCHEMA + DELETE en 3 tablas de public, dejando
-- restos acumulados en 42 tablas más.
--
-- Auditoría realizada:
-- - 45 tablas en public.
-- - 3 críticas (usadas por el código): tenants, usuarios, configuracion_panaderia.
-- - 42 huérfanas: 30 vacías + 6 con datos huérfanos + 3 backups + 3 residuos.
-- - 110 filas huérfanas acumuladas.
--
-- Este script DROPea las 42 tablas huérfanas respetando FKs internas.
-- Conserva las 3 tablas críticas intactas.
--
-- Idempotente (IF EXISTS). Aplicado manualmente el 5 Oct 2026.
-- ============================================================

-- ------------------------------------------------------------
-- PASO 0: Soltar FK de public.usuarios hacia sucursales
--         (la única FK saliente de una tabla que CONSERVAMOS)
-- ------------------------------------------------------------
ALTER TABLE public.usuarios DROP CONSTRAINT IF EXISTS usuarios_sucursal_id_fkey;
ALTER TABLE public.usuarios DROP COLUMN IF EXISTS sucursal_id;

-- ------------------------------------------------------------
-- PASO 1: Backups manuales
-- ------------------------------------------------------------
DROP TABLE IF EXISTS public.configuracion_panaderia_backup_20260916 CASCADE;
DROP TABLE IF EXISTS public.tenants_backup_20260916 CASCADE;
DROP TABLE IF EXISTS public.tenants_backup_tenant20 CASCADE;

-- ------------------------------------------------------------
-- PASO 2: Tablas hoja (sin hijos apuntándoles)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS public.historial_precios_recetas CASCADE;
DROP TABLE IF EXISTS public.historial_rotacion_producto CASCADE;
DROP TABLE IF EXISTS public.historial_mantenimientos CASCADE;
DROP TABLE IF EXISTS public.historial_inventario CASCADE;
DROP TABLE IF EXISTS public.historial_compras CASCADE;
DROP TABLE IF EXISTS public.control_vida_util CASCADE;
DROP TABLE IF EXISTS public.stock_productos CASCADE;
DROP TABLE IF EXISTS public.receta_ingredientes CASCADE;
DROP TABLE IF EXISTS public.detalle_compras CASCADE;
DROP TABLE IF EXISTS public.detalle_venta CASCADE;
DROP TABLE IF EXISTS public.facturas CASCADE;
DROP TABLE IF EXISTS public.pagos_individuales CASCADE;
DROP TABLE IF EXISTS public.logs_sistema CASCADE;
DROP TABLE IF EXISTS public.permisos_usuario CASCADE;
DROP TABLE IF EXISTS public.cierres_diarios CASCADE;
DROP TABLE IF EXISTS public.registros_diarios CASCADE;
DROP TABLE IF EXISTS public.registros_financieros CASCADE;
DROP TABLE IF EXISTS public.depositos_bancarios CASCADE;
DROP TABLE IF EXISTS public.saldos_banco CASCADE;

-- ------------------------------------------------------------
-- PASO 3: Tablas intermedias
-- ------------------------------------------------------------
DROP TABLE IF EXISTS public.jornadas_ventas CASCADE;
DROP TABLE IF EXISTS public.ventas CASCADE;
DROP TABLE IF EXISTS public.compras CASCADE;
DROP TABLE IF EXISTS public.compras_externas CASCADE;
DROP TABLE IF EXISTS public.ordenes_produccion CASCADE;
DROP TABLE IF EXISTS public.productos_externos CASCADE;
DROP TABLE IF EXISTS public.productos CASCADE;
DROP TABLE IF EXISTS public.categorias CASCADE;
DROP TABLE IF EXISTS public.recetas CASCADE;
DROP TABLE IF EXISTS public.materias_primas CASCADE;
DROP TABLE IF EXISTS public.proveedor CASCADE;
DROP TABLE IF EXISTS public.gastos CASCADE;
DROP TABLE IF EXISTS public.activos_fijos CASCADE;
DROP TABLE IF EXISTS public.clientes CASCADE;
DROP TABLE IF EXISTS public.consecutivos_pos CASCADE;
DROP TABLE IF EXISTS public.configuracion_produccion CASCADE;
DROP TABLE IF EXISTS public.configuracion_sistema CASCADE;
DROP TABLE IF EXISTS public.sucursales CASCADE;

-- ------------------------------------------------------------
-- PASO 4: Padre raíz
-- ------------------------------------------------------------
DROP TABLE IF EXISTS public.panaderias CASCADE;

-- ------------------------------------------------------------
-- PASO 5: Residuo
-- ------------------------------------------------------------
DROP TABLE IF EXISTS public.alembic_version CASCADE;

-- ------------------------------------------------------------
-- PASO 6: Secuencias huérfanas (38, excluyendo las 3 críticas)
--         NO se dropean: tenants_id_seq, usuarios_id_seq,
--                        configuracion_panaderia_id_seq
-- ------------------------------------------------------------
DROP SEQUENCE IF EXISTS public.activos_fijos_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.categorias_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.cierres_diarios_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.clientes_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.compras_externas_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.compras_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.configuracion_produccion_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.configuracion_sistema_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.consecutivos_pos_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.control_vida_util_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.depositos_bancarios_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.detalle_compras_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.detalle_venta_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.facturas_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.gastos_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.historial_compras_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.historial_inventario_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.historial_mantenimientos_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.historial_precios_recetas_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.historial_rotacion_producto_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.jornadas_ventas_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.logs_sistema_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.materias_primas_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.ordenes_produccion_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.pagos_individuales_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.panaderias_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.permisos_usuario_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.productos_externos_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.productos_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.proveedor_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.receta_ingredientes_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.recetas_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.registros_diarios_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.registros_financieros_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.saldos_banco_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.stock_productos_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.sucursales_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.ventas_id_seq CASCADE;

-- ------------------------------------------------------------
-- PASO 7: Verificación final
-- ------------------------------------------------------------
-- Después de correr este script, public debe tener SOLO 3 tablas:
--   tenants, usuarios, configuracion_panaderia
-- Y 3 secuencias:
--   tenants_id_seq, usuarios_id_seq, configuracion_panaderia_id_seq
-- ============================================================