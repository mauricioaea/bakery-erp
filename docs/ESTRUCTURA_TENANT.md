# 🗂️ Estructura de un Tenant — PanaderíaPro

**Última actualización:** 15 Nov 2026
**Generado a partir de:** `tenant_34` (creado el 12 Nov 2026 con `crear_tenant_saas()` fixeado)
**Fuente de verdad del DDL:** `app.py` → `crear_tablas_en_orden()` + `db/schema_tenant_canonical.sql`
**Fuente de verdad del ORM:** `models.py` (43 modelos)

---

## 1. Visión general

- **Un tenant = un schema PostgreSQL** (`tenant_{id}`). El `id` es el de `public.tenants.id`.
- **`public` tiene 3 tablas:** `tenants`, `usuarios` (fallback `dev_master`), `configuracion_panaderia`.
- **Cada tenant tiene 42 tablas** (las que crea `crear_tablas_en_orden()`).
- **No se usa `db.create_all()`** para tenants. El DDL es raw, tabla por tabla.
- **Auto-reparación en runtime:** eliminada en Fase F (commit `6905d84`). El schema solo se modifica con `crear_tenant_saas()` (tenant nuevo) o `_migrar_tenants.py` (tenant existente).

## 2. Convenciones

| Aspecto | Convención |
|---|---|
| **Naming tablas** | plural (`productos`, `ventas`), excepto `proveedor` y `detalle_venta` (legacy singular) |
| **PK** | `id SERIAL` (auto-incremental) |
| **FK** | `{tabla_singular}_id` (ej. `producto_id`, `venta_id`) |
| **Multi-tenant** | toda tabla de negocio tiene `panaderia_id INTEGER NOT NULL` |
| **Timestamps** | `fecha_creacion` / `created_at` (TIMESTAMP DEFAULT NOW()) |
| **Soft-delete** | `estado VARCHAR` (COMPLETADA / ANULADA), nunca `DELETE` |
| **Multi-moneda** | `configuracion_sistema`: `moneda`, `usa_centavos`, `simbolo_moneda` |
| **Multi-idioma** | `configuracion_sistema.idioma VARCHAR(5) DEFAULT 'es'` |
| **FK diferidas** | si una tabla referencia a otra creada después, la FK se agrega con `ALTER TABLE ... ADD CONSTRAINT` al final |

## 3. Las 42 tablas por módulo

### 3.1. Core / Autenticación (4 tablas)

| Tabla | Columnas principales | Notas |
|---|---|---|
| `usuarios` | `id`, `username`, `password_hash`, `nombre_completo`, `rol`, `activo`, `tenant_id`, `panaderia_id`, `sucursal_id` | `sucursal_id` es legacy (no se usa, Fase F lo deja) |
| `permisos_usuario` | `id`, `usuario_id`, `modulo`, `accion`, `permitido` | |
| `configuracion_sistema` | `id`, `idioma`, `moneda`, `usa_centavos`, `simbolo_moneda`, `tipo_facturacion`, `nombre_empresa`, `nit_empresa` | 4 columnas muertas pendientes (DT-Fase F-C3-resto) |
| `configuracion_panaderia` | `id`, `nombre_panaderia`, `telefono_contacto`, `direccion`, `tipo_licencia`, `max_usuarios`, `estado_suscripcion` | |

### 3.2. Productos y Recetas (7 tablas)

| Tabla | Columnas principales | Notas |
|---|---|---|
| `categorias` | `id`, `nombre`, `descripcion` | |
| `productos` | `id`, `nombre`, `precio_venta`, `stock_actual`, `stock_minimo`, `categoria_id`, `receta_id`, `vida_util_dias` | |
| `productos_externos` | `id`, `nombre`, `precio_compra`, `precio_venta`, `stock_actual`, `proveedor_id` | |
| `recetas` | `id`, `nombre`, `unidades_obtenidas`, `costo_total`, `precio_venta`, `producto_id` | |
| `receta_ingredientes` | `id`, `receta_id`, `materia_prima_id`, `cantidad_gramos`, `costo_ingrediente` | ingrediente base |
| `receta_toppings` | `id`, `receta_id`, `materia_prima_id`, `sub_receta_id`, `cantidad_por_unidad` | toppings (siempre en gramos) |
| `historial_precios_recetas` | `id`, `receta_id`, `precio_anterior`, `precio_nuevo`, `fecha_cambio` | |

### 3.3. Producción e Inventario (8 tablas)

| Tabla | Columnas principales | Notas |
|---|---|---|
| `ordenes_produccion` | `id`, `receta_id`, `cantidad_producir`, `cantidad_real`, `estado`, `fecha_produccion` | |
| `historial_inventario` | `id`, `producto_id`, `materia_prima_id`, `cantidad_anterior`, `cantidad_nueva`, `tipo_movimiento`, `orden_produccion_id` | `materia_prima_id` es nullable (DT-Fase E-5 pendiente) |
| `materias_primas` | `id`, `nombre`, `unidad_medida`, `stock_actual`, `stock_minimo`, `costo_promedio`, `proveedor_id`, `gramos_por_empaque` | |
| `stock_productos` | `id`, `producto_id`, `stock_actual`, `stock_minimo`, `stock_maximo` | |
| `control_vida_util` | `id`, `producto_id`, `fecha_produccion`, `stock_inicial`, `dias_sin_rotacion`, `estado` | |
| `historial_rotacion_producto` | `id`, `producto_id`, `fecha`, `ventas_dia`, `rotacion_real` | |
| `bajas_inventario` | `id`, `producto_id`, `cantidad`, `motivo`, `costo_total`, `usuario_id` | Feature Baja de Inventario (31 Oct) |
| `configuracion_produccion` | `id`, `receta_id`, `stock_objetivo`, `stock_minimo`, `stock_maximo` | 7 columnas muertas eliminadas en Fase F (`179fb0b`) |

### 3.4. Ventas / POS (4 tablas)

| Tabla | Columnas principales | Notas |
|---|---|---|
| `ventas` | `id`, `cliente_id`, `usuario_id`, `fecha_hora`, `total`, `metodo_pago`, `estado` (COMPLETADA / ANULADA), `es_donacion`, `consecutivo_pos`, `motivo_anulacion`, `usuario_anulacion_id` | Soft-delete. Donaciones con `es_donacion=TRUE` no suman ingresos. |
| `detalle_venta` | `id`, `venta_id`, `producto_id`, `producto_externo_id`, `cantidad`, `precio_unitario`, `subtotal` | `producto_id` XOR `producto_externo_id` |
| `consecutivos_pos` | `id`, `panaderia_id`, `numero_actual` | centralizado en `db/schema_tenant_canonical.sql` (Fase F B-2) |
| `facturas` | `id`, `venta_id`, `numero_factura`, `subtotal`, `iva`, `total` | |

### 3.5. Finanzas (6 tablas)

| Tabla | Columnas principales | Notas |
|---|---|---|
| `depositos_bancarios` | `id`, `banco`, `fecha_deposito`, `monto`, `estado` (REGISTRADO / CONCILIADO / ANULADO), `motivo_anulacion`, `motivo_desconciliacion` | CONCILIADO inmutable (CRÍTICA-1). Desconciliación con auditoría. |
| `pagos_individuales` | `id`, `concepto`, `monto`, `metodo_pago`, `proveedor_id`, `usuario_id` | `usuario_id` está en `models.py:1259` (DT-Fase F-C4 pendiente) |
| `gastos` | `id`, `concepto`, `monto`, `fecha_gasto`, `categoria` | |
| `registros_financieros` | `id`, `saldo_disponible`, `saldo_pendiente`, `saldo_tarjetas`, `saldo_total` | |
| `saldos_banco` | `id`, `banco`, `saldo_actual` | |
| `jornadas_ventas` | `id`, `fecha`, `estado`, `total_ventas`, `total_efectivo` | cierre de jornada (Fase E-1, legacy) |

### 3.6. Compras y Proveedores (5 tablas)

| Tabla | Columnas principales | Notas |
|---|---|---|
| `proveedor` | `id`, `nombre`, `email`, `telefono`, `contacto` | naming singular (DT-unificar-naming) |
| `compras` | `id`, `total`, `fecha`, `proveedor` (VARCHAR, no FK) | |
| `detalle_compras` | `id`, `compra_id`, `materia_prima_id`, `cantidad`, `precio_unitario` | |
| `compras_externas` | `id`, `producto_externo_id`, `proveedor_id`, `cantidad`, `precio_unitario` | |
| `historial_compras` | `id`, `materia_prima_id`, `fecha_compra`, `cantidad_empaques` | |

### 3.7. Activos Fijos (2 tablas)

| Tabla | Columnas principales | Notas |
|---|---|---|
| `activos_fijos` | `id`, `nombre`, `categoria`, `fecha_compra`, `valor_compra`, `vida_util`, `estado` | |
| `historial_mantenimientos` | `id`, `activo_fijo_id`, `fecha_mantenimiento`, `costo`, `tipo` | |

### 3.8. Clientes (1 tabla)

| Tabla | Columnas principales | Notas |
|---|---|---|
| `clientes` | `id`, `documento`, `nombre`, `tipo_documento`, `email`, `ciudad`, `regimen` | |

### 3.9. Multi-sucursal (legacy) (2 tablas)

| Tabla | Columnas principales | Notas |
|---|---|---|
| `panaderias` | `id`, `nombre`, `moneda`, `activa` | `panaderia_id` auto-referencia eliminada en Fase F (`179fb0b`) |
| `sucursales` | `id`, `nombre`, `email`, `panaderia_id` | `email` no se usa (DT-Fase F-C6 pendiente) |

### 3.10. Sistema / Logs (2 tablas)

| Tabla | Columnas principales | Notas |
|---|---|---|
| `logs_sistema` | `id`, `usuario_id`, `accion`, `modulo`, `fecha_hora`, `ip_address` | |
| `registros_diarios` | `id`, `fecha`, `venta_total`, `efectivo`, `total_ingresos` | 1 columna legacy `tarjetas` (DT-Fase C-7) |

---

**Total: 42 tablas.**

## 4. Tablas y columnas eliminadas en Fase F

| Elemento | Motivo | Commit |
|---|---|---|
| `cierres_diarios` (tabla completa) | Legacy. Nadie llamaba a `realizar_cierre()`. | `99bb28f` |
| `configuracion_produccion`: 7 columnas | Columnas muertas (DDL, no modelo, no código) | `179fb0b` |
| `panaderias.panaderia_id` | Auto-referencia sin uso | `179fb0b` |
| `configuracion_sistema.idioma` | **Agregada** al DDL (faltaba) | `d8f703d` |

## 5. DTs BAJAS pendientes (no bloquean lanzamiento)

- `sucursales.email` (DT-Fase F-C6)
- `pagos_individuales.usuario_id` (DT-Fase F-C4)
- `configuracion_sistema` 4 columnas muertas (DT-Fase F-C3-resto)
- `historial_inventario.materia_prima_id` nullable en modelo (DT-Fase E-5)
- `proveedor` / `detalle_venta` naming singular (DT-unificar-naming)
- ~39 archivos `.bak` en working tree (DT-Fase F-BAK)

## 6. Comandos útiles

```cmd
:: Listar tablas de un tenant
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'tenant_34' AND table_type = 'BASE TABLE' ORDER BY table_name;"

:: Listar columnas de una tabla
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_schema = 'tenant_34' AND table_name = 'productos' ORDER BY ordinal_position;"

:: Verificar ORM ↔ BD
python _test_tenant_schema.py 34

:: Migrar tenant existente
python _migrar_tenants.py 34

:: Limpiar tenants huérfanos
python _cleanup_tenants_huerfanos.py --fix