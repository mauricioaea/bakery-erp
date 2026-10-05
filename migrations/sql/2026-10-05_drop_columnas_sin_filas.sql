-- ============================================================
-- DT-39: Eliminar 25 columnas huérfanas SIN FILAS
-- Fecha: 2026-10-05
-- Autor: Mauricio
-- Contexto: ver HANDOFF.md v8.1 sección 9️⃣ (DT-39)
-- ============================================================
-- 25 columnas huérfanas identificadas en 7 tablas de tenant_27.
-- Todas las tablas estaban VACÍAS (0 filas).
-- Todas las columnas tenían 0 referencias en app.py, models.py,
-- reportes.py, seed_demo.py, seeds/*.py y templates/*.html.
-- Clasificación: 100% RUIDO PURO (sin features del dominio).
--
-- Aplicado a: tenant_25, tenant_26, tenant_27
-- No aplicado a: tenant_1 (no tenía las columnas)
--
-- Script idempotente (IF EXISTS). Aplicado manualmente el 5 Oct 2026.
-- ============================================================

-- 1. logs_sistema (2 columnas)
ALTER TABLE tenant_25.logs_sistema DROP COLUMN IF EXISTS ip_origen;
ALTER TABLE tenant_25.logs_sistema DROP COLUMN IF EXISTS fecha_log;
ALTER TABLE tenant_26.logs_sistema DROP COLUMN IF EXISTS ip_origen;
ALTER TABLE tenant_26.logs_sistema DROP COLUMN IF EXISTS fecha_log;
ALTER TABLE tenant_27.logs_sistema DROP COLUMN IF EXISTS ip_origen;
ALTER TABLE tenant_27.logs_sistema DROP COLUMN IF EXISTS fecha_log;

-- 2. control_vida_util (2 columnas)
ALTER TABLE tenant_25.control_vida_util DROP COLUMN IF EXISTS dias_restantes;
ALTER TABLE tenant_25.control_vida_util DROP COLUMN IF EXISTS fecha_control;
ALTER TABLE tenant_26.control_vida_util DROP COLUMN IF EXISTS dias_restantes;
ALTER TABLE tenant_26.control_vida_util DROP COLUMN IF EXISTS fecha_control;
ALTER TABLE tenant_27.control_vida_util DROP COLUMN IF EXISTS dias_restantes;
ALTER TABLE tenant_27.control_vida_util DROP COLUMN IF EXISTS fecha_control;

-- 3. historial_rotacion_producto (2 columnas)
ALTER TABLE tenant_25.historial_rotacion_producto DROP COLUMN IF EXISTS rotacion;
ALTER TABLE tenant_25.historial_rotacion_producto DROP COLUMN IF EXISTS fecha_calculo;
ALTER TABLE tenant_26.historial_rotacion_producto DROP COLUMN IF EXISTS rotacion;
ALTER TABLE tenant_26.historial_rotacion_producto DROP COLUMN IF EXISTS fecha_calculo;
ALTER TABLE tenant_27.historial_rotacion_producto DROP COLUMN IF EXISTS rotacion;
ALTER TABLE tenant_27.historial_rotacion_producto DROP COLUMN IF EXISTS fecha_calculo;

-- 4. detalle_compras (2 columnas)
ALTER TABLE tenant_25.detalle_compras DROP COLUMN IF EXISTS producto_id;
ALTER TABLE tenant_25.detalle_compras DROP COLUMN IF EXISTS subtotal;
ALTER TABLE tenant_26.detalle_compras DROP COLUMN IF EXISTS producto_id;
ALTER TABLE tenant_26.detalle_compras DROP COLUMN IF EXISTS subtotal;
ALTER TABLE tenant_27.detalle_compras DROP COLUMN IF EXISTS producto_id;
ALTER TABLE tenant_27.detalle_compras DROP COLUMN IF EXISTS subtotal;

-- 5. compras (4 columnas)
ALTER TABLE tenant_25.compras DROP COLUMN IF EXISTS proveedor_id;
ALTER TABLE tenant_25.compras DROP COLUMN IF EXISTS fecha_compra;
ALTER TABLE tenant_25.compras DROP COLUMN IF EXISTS estado;
ALTER TABLE tenant_25.compras DROP COLUMN IF EXISTS observaciones;
ALTER TABLE tenant_26.compras DROP COLUMN IF EXISTS proveedor_id;
ALTER TABLE tenant_26.compras DROP COLUMN IF EXISTS fecha_compra;
ALTER TABLE tenant_26.compras DROP COLUMN IF EXISTS estado;
ALTER TABLE tenant_26.compras DROP COLUMN IF EXISTS observaciones;
ALTER TABLE tenant_27.compras DROP COLUMN IF EXISTS proveedor_id;
ALTER TABLE tenant_27.compras DROP COLUMN IF EXISTS fecha_compra;
ALTER TABLE tenant_27.compras DROP COLUMN IF EXISTS estado;
ALTER TABLE tenant_27.compras DROP COLUMN IF EXISTS observaciones;

-- 6. registros_diarios (6 columnas)
ALTER TABLE tenant_25.registros_diarios DROP COLUMN IF EXISTS total_ventas;
ALTER TABLE tenant_25.registros_diarios DROP COLUMN IF EXISTS total_gastos;
ALTER TABLE tenant_25.registros_diarios DROP COLUMN IF EXISTS total_donaciones;
ALTER TABLE tenant_25.registros_diarios DROP COLUMN IF EXISTS saldo_inicial;
ALTER TABLE tenant_25.registros_diarios DROP COLUMN IF EXISTS saldo_final;
ALTER TABLE tenant_25.registros_diarios DROP COLUMN IF EXISTS observaciones;
ALTER TABLE tenant_26.registros_diarios DROP COLUMN IF EXISTS total_ventas;
ALTER TABLE tenant_26.registros_diarios DROP COLUMN IF EXISTS total_gastos;
ALTER TABLE tenant_26.registros_diarios DROP COLUMN IF EXISTS total_donaciones;
ALTER TABLE tenant_26.registros_diarios DROP COLUMN IF EXISTS saldo_inicial;
ALTER TABLE tenant_26.registros_diarios DROP COLUMN IF EXISTS saldo_final;
ALTER TABLE tenant_26.registros_diarios DROP COLUMN IF EXISTS observaciones;
ALTER TABLE tenant_27.registros_diarios DROP COLUMN IF EXISTS total_ventas;
ALTER TABLE tenant_27.registros_diarios DROP COLUMN IF EXISTS total_gastos;
ALTER TABLE tenant_27.registros_diarios DROP COLUMN IF EXISTS total_donaciones;
ALTER TABLE tenant_27.registros_diarios DROP COLUMN IF EXISTS saldo_inicial;
ALTER TABLE tenant_27.registros_diarios DROP COLUMN IF EXISTS saldo_final;
ALTER TABLE tenant_27.registros_diarios DROP COLUMN IF EXISTS observaciones;

-- 7. registros_financieros (7 columnas)
ALTER TABLE tenant_25.registros_financieros DROP COLUMN IF EXISTS fecha;
ALTER TABLE tenant_25.registros_financieros DROP COLUMN IF EXISTS tipo;
ALTER TABLE tenant_25.registros_financieros DROP COLUMN IF EXISTS descripcion;
ALTER TABLE tenant_25.registros_financieros DROP COLUMN IF EXISTS ingreso;
ALTER TABLE tenant_25.registros_financieros DROP COLUMN IF EXISTS egreso;
ALTER TABLE tenant_25.registros_financieros DROP COLUMN IF EXISTS saldo;
ALTER TABLE tenant_25.registros_financieros DROP COLUMN IF EXISTS usuario_id;
ALTER TABLE tenant_26.registros_financieros DROP COLUMN IF EXISTS fecha;
ALTER TABLE tenant_26.registros_financieros DROP COLUMN IF EXISTS tipo;
ALTER TABLE tenant_26.registros_financieros DROP COLUMN IF EXISTS descripcion;
ALTER TABLE tenant_26.registros_financieros DROP COLUMN IF EXISTS ingreso;
ALTER TABLE tenant_26.registros_financieros DROP COLUMN IF EXISTS egreso;
ALTER TABLE tenant_26.registros_financieros DROP COLUMN IF EXISTS saldo;
ALTER TABLE tenant_26.registros_financieros DROP COLUMN IF EXISTS usuario_id;
ALTER TABLE tenant_27.registros_financieros DROP COLUMN IF EXISTS fecha;
ALTER TABLE tenant_27.registros_financieros DROP COLUMN IF EXISTS tipo;
ALTER TABLE tenant_27.registros_financieros DROP COLUMN IF EXISTS descripcion;
ALTER TABLE tenant_27.registros_financieros DROP COLUMN IF EXISTS ingreso;
ALTER TABLE tenant_27.registros_financieros DROP COLUMN IF EXISTS egreso;
ALTER TABLE tenant_27.registros_financieros DROP COLUMN IF EXISTS saldo;
ALTER TABLE tenant_27.registros_financieros DROP COLUMN IF EXISTS usuario_id;