-- MIGRACIÓN PARA SISTEMA MULTI-TENANT PANADERÍAS
-- FECHA: 2025-11-20 11:38:29

BEGIN TRANSACTION;

-- Migración para sucursales
ALTER TABLE sucursales ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para configuracion_panaderia
ALTER TABLE configuracion_panaderia ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para panaderias
ALTER TABLE panaderias ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para compras_externas
ALTER TABLE compras_externas ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para historial_compras
ALTER TABLE historial_compras ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para clientes
ALTER TABLE clientes ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para detalle_venta
ALTER TABLE detalle_venta ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para compras
ALTER TABLE compras ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para detalle_compras
ALTER TABLE detalle_compras ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para gastos
ALTER TABLE gastos ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para receta_ingredientes
ALTER TABLE receta_ingredientes ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para historial_inventario
ALTER TABLE historial_inventario ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para stock_productos
ALTER TABLE stock_productos ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para configuracion_produccion
ALTER TABLE configuracion_produccion ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para historial_rotacion_producto
ALTER TABLE historial_rotacion_producto ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para control_vida_util
ALTER TABLE control_vida_util ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para facturas
ALTER TABLE facturas ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para jornadas_ventas
ALTER TABLE jornadas_ventas ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para cierres_diarios
ALTER TABLE cierres_diarios ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para permisos_usuario
ALTER TABLE permisos_usuario ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

-- Migración para consecutivos_pos
ALTER TABLE consecutivos_pos ADD COLUMN panaderia_id INTEGER NOT NULL DEFAULT 1;

COMMIT;

-- ✅ MIGRACIÓN COMPLETADA