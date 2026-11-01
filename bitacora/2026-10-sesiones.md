# 📓 BITÁCORA — Octubre 2026 (PanaderíaPro)

> **Append-only.** Histórico de sesiones de octubre 2026. Extraído de `HANDOFF_v9.5.md` (v9.4 + actualización del 31 Oct).
> Para el estado actual del proyecto ver `HANDOFF.md`. Las sesiones de noviembre están en `bitacora/2026-11-sesiones.md`.

---

## Sesiones

**Sesión 2 Oct:** DT-11, DT-12, DT-13, DT-14, DT-16, DT-26, DT-27, DT-3, DT-4

**Sesión 3 Oct:** DT-1, DT-6, DT-9, DT-20 Fase C (Tanda 1+2+3), DT-30, DT-31

**Sesión 4 Oct:** DT-10, DT-22, DT-24, DT-17, DT-33, DT-34, DT-32, DT-18

**Sesión 5 Oct (mañana):** Fase C.3 parcial + DT-38 (4/5 lotes) + DT-40 + DT-39 + DT-36

**Sesión 5 Oct (noche):** Borrado tenants 25/26 + DT-35 + DT-5 + DT-5-quater + DT-5-ter + DT-21 + DT-25 (refactor before_request) + DT-29

**Sesión 6 Oct (mediodía):** DT-28 + DT-45 + DT-42 + DT-43 + DT-44 (documentada → eliminada en v8.7)

**Sesión 7 Oct (noche):** DT-46 + DT-5-bis + DT-5-quinquies + DT-5-quater-bis (reformulada) — **Opción Rápida 100%**

**Sesión 8 Oct (tarde):** DT-19 (CSRF completo con flask-wtf) — **Producción-ready en seguridad**

**Sesión 12 Oct (mañana):** DT-47 (logging centralizado) — **Producción-ready en observabilidad**

**Sesión 15 Oct (tarde):** DT-37 F0 + F1 + F2 + F3 (reporte piloto) + Papiamento — **Pipeline i18n funcional (es/en/pap)**

**Sesión 16 Oct (mañana):** DT-37 F4 partes 1-5 (`estado_resultados` + `flujo_caja` + `conciliacion_bancaria` + `analisis_gastos` + `analisis_inventarios`) + fix crítico de f-strings con emoji — **5/13 reportes migrados**

**Sesión 16 Oct (noche):** DT-37 F4.6 (`ia_predictivo` método principal + 3 helpers) — **6/13 reportes migrados**

**Sesión 18 Oct (mañana):** DT-37 F4.7 (`historial_pagos` + `historial_depositos`) + DT-37 F4.8 (`tesoreria_unificado` método principal + 4 helpers + `_generar_reporte_error`) — **10/10 reportes UI migrados**

**Sesión 20-23 Oct:** DT-37 F5 (i18n de reportes HTML en templates/). Migración de 6 templates: `reportes.html`, `cierre_caja.html`, `productos_populares.html`, `reporte_activos.html`, `reporte_inventario_externo.html` (+ fix export PDF), `reporte_ventas_externas.html` (+ fix export PDF). Corrección de `babel.cfg` y `app.py` (import `_`).

**Sesión 23 Oct (tarde):** DT-37 F5.7 (`ventas_periodo.html`) + fix multi-tenant nombre panadería (`config.nombre_panaderia`).

**Sesión 24 Oct (tarde):** DT-37 F5 — migración de `analisis_predictivo.html`, `reporte_produccion.html`, y los 4 parciales de `secciones/` (`analisis_productos`, `recomendaciones`, `resumen_ventas`, `analisis_ia`) + padre `ventas_avanzado.html`. **F5 COMPLETADO AL 100%.**

**Sesión 24 Oct (noche):** **Feature: Toppings en recetas.** Nueva tabla `receta_toppings` (con CHECK constraint), cálculo de costos (gramos por lote × $/gramo), descuento de stock (base + toppings) + historial de inventario, UI (formulario crear/editar, detalle, modal producción), endpoint `/api/calcular_ingredientes`. **Fixes preexistentes:** `Panaderia(panaderia_id=...)`, `producto_id NOT NULL`, `search_path`, modelo `HistorialInventario`, JS roto en `crear_receta.html` y `produccion_diaria.html`. Commit `9e645ba`.

**Sesión 28 Oct (tarde):** **Feature: Anulación de Recibos POS.** Migraciones BD (campos de anulación en ventas y cierres), modelo `Venta.estado` + helper `puede_anularse()`, endpoint `/anular_venta`, UI `ventas_del_dia.html` + botón en navbar, blindaje de 11 consultas en reportes financieros y cierres. Commit `4ecfde9`.

**Sesión 31 Oct (mañana/tarde):** **Feature: Baja de Inventario + Fix FK diferida + Smoke test tenants nuevos.**

- Modelo `BajaInventario` (tabla `bajas_inventario` con CHECK `motivo IN ('VENCIMIENTO', 'ROTURA')`).
- Endpoints `GET /baja_inventario`, `GET /api/productos_vitrina`, `POST /registrar_baja`.
- Frontend `templates/baja_inventario.html` (carrito estilo POS) + botón en navbar.
- Costo real desde receta (`receta.costo_total / receta.unidades_obtenidas`).
- Estado de Resultados (PDF): línea "Pérdidas por Baja de Inventario".
- Análisis de Gastos (PDF): categoría "Bajas" en gráfico de torta + barras.
- Cierre de Caja (HTML): panel "Bajas de Inventario del Turno" (informativo).
- i18n completo (es/en/pap) con fixes de `%` sueltos en `msgstr`.
- **Fix CRÍTICO en `crear_tenant_saas()`:** FK diferida `fk_historial_inventario_orden_produccion` con `ALTER TABLE` (bug preexistente que rompía tenants nuevos).
- **Smoke test tenant básico (`tenant_29`) + premium (`tenant_30`):** 16 puntos OK en ambos.
- **7 hallazgos documentados** (DT-nueva-CRÍTICA × 3, MEDIA-ALTA × 1, MEDIA × 1, MEDIA-BAJA × 1, BAJA × 1) — ver sección 2️⃣7️⃣.
- Commits: `ba48503` + `52696be`.


---

## Deuda técnica resuelta (por fecha)

### ✅ RESUELTAS el 31 Octubre 2026 — Feature Baja de Inventario + Fix FK diferida

| # | Descripción | Commit |
|---|-------------|--------|
| Feature | Schema BD `bajas_inventario` + CHECK `motivo IN ('VENCIMIENTO','ROTURA')` + modelo `BajaInventario` + migración base | `ba48503` |
| Feature | Endpoints `/baja_inventario`, `/api/productos_vitrina`, `/registrar_baja` | `52696be` |
| Feature | Frontend `baja_inventario.html` (carrito POS-style) + botón en navbar | `52696be` |
| Feature | Costo real desde receta (`costo_total / unidades_obtenidas`) | `52696be` |
| Feature | Estado de Resultados (PDF): línea "Pérdidas por Baja de Inventario" | `52696be` |
| Feature | Análisis de Gastos (PDF): categoría "Bajas" (torta + barras) | `52696be` |
| Feature | Cierre de Caja (HTML): panel informativo "Bajas de Inventario del Turno" | `52696be` |
| i18n | Traducciones es/en/pap + fix de `%` sueltos en `msgstr` | `52696be` |
| Bug CRÍTICO | `crear_tenant_saas()`: FK `fk_historial_inventario_orden_produccion` ahora se agrega con `ALTER TABLE` diferido (rompía tenants nuevos) | `52696be` |
| QA | Smoke test tenant básico (`tenant_29`) + premium (`tenant_30`): 16 puntos OK | — |

> Nota: los hashes se asignan según el registro de commits del 31 Oct (`ba48503` + `52696be`). Verificar con `git log --oneline -5` la distribución exacta por commit.

### ✅ RESUELTAS el 28 Octubre 2026 (tarde) — Feature Anulación POS

| # | Descripción | Commit |
|---|-------------|--------|
| Feature | Migración BD: campos de anulación en ventas y cierres | 722beb5 |
| Feature | Modelo Venta.estado + helper puede_anularse() | 494f190 |
| Bug | AmbiguousForeignKeysError en Usuario.ventas_realizadas | 494f190 |
| Feature | Endpoint /anular_venta/<id> con reversión de stock | 1513c9a |
| Fix | realizar_cierre y obtener_ventas_dia excluyen anuladas | 1513c9a |
| Feature | UI: ventas_del_dia.html + botón en navbar | 4ecfde9 |
| Fix | Blindaje de 11 consultas en reportes financieros | 4ecfde9 |

### ✅ RESUELTAS el 24 Octubre 2026 (noche) — Feature Toppings

| # | Descripción | Commit |
|---|-------------|--------|
| Feature | Nueva tabla receta_toppings + CHECK constraint | 9e645ba |
| Feature | Cálculo de costos con toppings (gramos por lote) | 9e645ba |
| Feature | Descuento de stock (ingredientes + toppings) | 9e645ba |
| Feature | Historial de inventario (con toppings) | 9e645ba |
| Feature | Formulario de toppings en crear/editar receta | 9e645ba |
| Feature | Sección "Toppings" en detalle de receta | 9e645ba |
| Feature | Modal de producción con toppings (en gramos) | 9e645ba |
| Feature | Endpoint /api/calcular_ingredientes con toppings | 9e645ba |
| Bug | Panaderia(panaderia_id=...) — argumento inválido | 9e645ba |
| Bug | producto_id NOT NULL en historial_inventario | 9e645ba |
| Bug | search_path no seteado en _descontar_ingredientes() | 9e645ba |
| Bug | Modelo HistorialInventario desalineado con BD | 9e645ba |
| Bug | JS roto en crear_receta.html (âO DEL FORMULARIO) | 9e645ba |
| Bug | JS roto en produccion_diaria.html (âPIDAS) | 9e645ba |
| Migración | SQL para tenants existentes (tenant_1, tenant_27) | 9e645ba |

### ✅ RESUELTAS el 24 Octubre 2026 (tarde) — DT-37 F5 (parte 2 y final)

| # | Descripción | Commit |
|---|-------------|--------|
| DT-37 F5.7 | Migrar ventas_periodo.html + fix multi-tenant | 0af8fcf |
| DT-37 F5.8 | Migrar analisis_predictivo.html + fix CSS @media print + badge traducción | d0fd6bb |
| DT-37 F5.9 | Migrar reporte_produccion.html | b660db7 |
| DT-37 F5.10 | Migrar secciones/analisis_productos.html + fix traducciones heredadas | 7582770 |
| DT-37 F5.11 | Migrar secciones/recomendaciones.html | 84b9080 |
| DT-37 F5.12 | Migrar secciones/resumen_ventas.html | ec2687e |
| DT-37 F5.13 | Migrar secciones/analisis_ia.html | 61edb44 |
| DT-37 F5.14 | Migrar ventas_avanzado.html (padre) — F5 COMPLETADO | c54d9eb |

### ✅ RESUELTAS el 23 Octubre 2026 — DT-37 F5 (parte 1)

| # | Descripción | Commit |
|---|-------------|--------|
| DT-37 F5.1 | Migrar reportes.html (menú principal) | a0de295 |
| DT-37 F5.2 | Migrar cierre_caja.html | a0de295 |
| DT-37 F5.3 | Migrar productos_populares.html | a796290 |
| DT-37 F5.4 | Migrar reporte_activos.html | 0ebb3de |
| DT-37 F5.5 | Migrar reporte_inventario_externo.html + fix export PDF | 2f9a5fe |
| DT-37 F5.6 | Migrar reporte_ventas_externas.html + fix export PDF | 3ea5612 |
| DT-babel-fix | babel.cfg corregido a [jinja2: **.html] | a0de295 |
| DT-app-import | from flask_babel import Babel, gettext as _ en app.py:1264 | 2f9a5fe |

### ✅ RESUELTAS el 18 Octubre 2026 — DT-37 F4.6 + F4.7 + F4.8

| # | Descripción | Commit |
|---|-------------|--------|
| DT-37 F4.6 | ia_predictivo (método + 3 helpers) | b7d76b9 |
| DT-37 F4.7 | historial_pagos + historial_depositos | 89c2568 |
| DT-37 F4.8 | tesoreria_unificado (método + 4 helpers) + _generar_reporte_error | 6b6204b |

### ✅ RESUELTAS el 16 Octubre 2026 — DT-37 F4 (parte 1-5 + fix)

| # | Descripción | Commit |
|---|-------------|--------|
| DT-37 F4.1 | estado_resultados | 41dc685 + 186d78b |
| DT-37 F4.2 | flujo_caja | 8c53f4a |
| DT-37 F4.3 | conciliacion_bancaria | 9ddc83f |
| DT-37 F4.4 | analisis_gastos | 4cbc257 |
| DT-37 F4.5 | analisis_inventarios | 8430027 |

### ✅ RESUELTAS el 15 Octubre 2026 — DT-37 (parcial)

| # | Descripción | Commit |
|---|-------------|--------|
| DT-37 F0 | Campo idioma en ConfiguracionSistema + migración BD + UI | 85f8cf5 |
| DT-37 F1 | Instalación Flask-Babel + Babel | fbea5d8 |
| DT-37 F2 | Babel(app) + _get_locale() + hook en before_request | fbea5d8 |
| DT-37 F3 | Reporte piloto (tendencia_ventas) migrado a i18n | 9490e97 + 5860fdf |
| DT-37 Papiamento | Catálogo pap completo (53 traducciones) | 93a1e82 |

---

## 1️⃣1️⃣ Fase C.3 — Auditoría de columnas huérfanas (cerrada)

Auditoría del 5 Oct, alineación ORM↔BD:

- Fase C.3 parcial: modelos vivos (cefb33f).
- DT-38: 4 lotes de modelos muertos.
- DT-39: 25 columnas SIN FILAS.
- DT-40: 6 columnas legacy en ventas.
- DT-36: 42 tablas huérfanas en public.
- DT-5-ter: columnas legacy en gastos.
- DT-5-quinquies: alineación estructural tenant_1.gastos con tenant_27.gastos.

---

## 2️⃣0️⃣ DT-37 — i18n reportes

**Estado:** ✅ F0-F5 COMPLETADAS AL 100%.

### Resumen F4 (PDFs) — 10 reportes + 1 helper

| Reporte | Commit | Fecha |
|---|---|---|
| tendencia_ventas (piloto) | 9490e97 | 15 Oct |
| estado_resultados | 41dc685 + 186d78b | 16 Oct |
| flujo_caja (huérfano) | 8c53f4a | 16 Oct |
| conciliacion_bancaria | 9ddc83f | 16 Oct |
| analisis_gastos | 4cbc257 | 16 Oct |
| analisis_inventarios | 8430027 | 16 Oct |
| ia_predictivo | b7d76b9 | 16 Oct |
| historial_pagos | 89c2568 | 18 Oct |
| historial_depositos | 89c2568 | 18 Oct |
| tesoreria_unificado | 6b6204b | 18 Oct |
| _generar_reporte_error | 6b6204b | 18 Oct |

Total F4: 344 msgids (100% traducidos en EN y PAP).

### Resumen F5 (HTMLs) — 14 archivos

| Template | Commit | Fecha |
|---|---|---|
| reportes.html | a0de295 | 20 Oct |
| cierre_caja.html | a0de295 | 20 Oct |
| productos_populares.html | a796290 | 21 Oct |
| reporte_activos.html | 0ebb3de | 21 Oct |
| reporte_inventario_externo.html | 2f9a5fe | 22 Oct |
| reporte_ventas_externas.html | 3ea5612 | 23 Oct |
| ventas_periodo.html | 0af8fcf | 23 Oct |
| analisis_predictivo.html | d0fd6bb | 23 Oct |
| reporte_produccion.html | b660db7 | 23 Oct |
| secciones/analisis_productos.html | 7582770 | 24 Oct |
| secciones/recomendaciones.html | 84b9080 | 24 Oct |
| secciones/resumen_ventas.html | ec2687e | 24 Oct |
| secciones/analisis_ia.html | 61edb44 | 24 Oct |
| ventas_avanzado.html (padre) | c54d9eb | 24 Oct |

Total F5: ~770 msgids en el .pot, ~767 traducidos en EN (99%), ~766 traducidos en PAP (99%). (Los msgids de Baja de Inventario del 31 Oct se suman a estos totales; recalcular con `pybabel compile --statistics`.)

---

## 2️⃣1️⃣ Feature: Toppings en recetas (COMPLETADA 24 Oct 2026)

### Alcance
- Tabla nueva receta_toppings (con CHECK constraint chk_topping_tipo).
- Modelo RecetaTopping en models.py.
- Cálculo de costos: gramos por lote × $/gramo (NO por unidad).
- Descuento de stock: ingredientes base + toppings.
- Historial de inventario: registra ingredientes base + toppings.
- Formulario de toppings en crear_receta.html y editar_receta.html.
- Sección "Toppings" en detalle_receta.html.
- Modal de producción en produccion_diaria.html (con toppings en gramos).
- Endpoint API /api/calcular_ingredientes (con toppings).
- Migración SQL para tenants existentes (migrations/sql/2026-10-24_add_receta_toppings.sql).

### Decisiones de diseño
- Toppings = gramos por lote (no por unidad). El usuario ingresa "450g de bocadillo para todo el lote".
- NO afectan el peso total de la masa ni las unidades obtenidas.
- NO afectan el precio de venta al público (solo el costo real).
- Multi-tenant: cada topping tiene panaderia_id.

### Fixes preexistentes incluidos
- Panaderia(panaderia_id=...) — argumento inválido (columna eliminada en DT-32).
- producto_id NOT NULL en historial_inventario → ahora nullable.
- search_path no seteado en _descontar_ingredientes().
- Modelo HistorialInventario desalineado con la BD (faltaban producto_id, cantidad_anterior, cantidad_nueva, usuario_id, observaciones).
- JS roto en crear_receta.html (âO DEL FORMULARIO).
- JS roto en produccion_diaria.html (âPIDAS).

**Commit:** 9e645ba

---

## 2️⃣2️⃣ 🆕 Feature: Anulación de recibos POS (COMPLETADA 28 Oct 2026)

**Origen:** Detectado en sesión 24 Oct 2026.
**Problema resuelto:** Anular ventas POS sin romper la auditoría.

**Alcance implementado:**
- **Soft-delete:** Las ventas NUNCA se borran. Cambian a estado `ANULADA`.
- **Límite de tiempo:** Solo se puede anular dentro de las **24 horas** siguientes.
- **Cierre de caja:** NO se puede anular si el día ya tiene un cierre de caja confirmado.
- **Seguridad Legal:** Las facturas `ELECTRONICA` NUNCA se pueden anular (nota crédito DIAN).
- **Permisos:** Cualquier cajero puede anular sus propias ventas de su turno.
- **Frontend:** Botón "Ventas de Hoy" en navbar de POS. Pantalla `ventas_del_dia.html` con modal de anulación y recarga dinámica.
- **Backend:** Endpoint `POST /anular_venta/<id>` (revierte stock de productos internos y externos + HistorialInventario).
- **Blindaje Financiero:** 11 filtros `Venta.estado == 'COMPLETADA'` inyectados en el Dashboard, Cierre de Caja, Reporte Visual de Cierre, y todos los reportes PDF (`estado_resultados`, `flujo_caja`, `analisis_productos`, `rotacion`, etc).
- **Migraciones:** `2026-10-26_add_anulacion_ventas.sql` y `2026-10-26_add_total_anulaciones_cierres.sql`.
- **Modelos:** `Venta.estado` + método `puede_anularse()`. `CierreDiario.total_anulaciones`.
- **Fixes:** `AmbiguousForeignKeysError` en `Usuario.ventas_realizadas`.

**Commit:** `4ecfde9`

---

## Hallazgos del smoke test del 31 Oct (texto original)

> Los hallazgos **abiertos** viven en `HANDOFF.md`. La CRÍTICA-3 se resolvió el 1 Nov (ver `bitacora/2026-11-sesiones.md`).


Durante el smoke test de tenants nuevos (básico `tenant_29` + premium `tenant_30`), se detectaron 7 hallazgos que **NO son de la Feature Baja de Inventario**, sino deuda técnica preexistente. **Todos se resuelven en Fase D de Pre-Dockerización.**

### 🚨 CRÍTICAS (bloqueantes para Docker)

#### DT-nueva-CRÍTICA-1: Modal "Ver" de depósitos conciliados permite edición
- **Módulo:** Gestión Financiera → Gestión de Depósitos Bancarios → Acciones → "Ver".
- **Bug:** Modal permite editar monto/fecha/referencia de depósitos con `estado = 'CONCILIADO'`.
- **Impacto:** Vulnerabilidad contable. Un usuario no autorizado podría modificar un depósito ya conciliado.
- **Fix:** Poner todos los inputs en `disabled` si `estado == 'CONCILIADO'`. Backend debe validar 403.
- **Ubicación:** `templates/gestion_financiera.html` + `app.py` (endpoint de actualización).

#### DT-nueva-CRÍTICA-2: `base_datos` huérfano (schema es `tenant_{id}`)
- **Bug:** `crear_tenant_saas()` genera `base_datos = f"tenant_{subdominio}"` pero el schema real se crea como `tenant_{id}`.
- **Impacto:** Inconsistencia de diseño. En la nube, el subdominio DNS y el schema no coinciden.
- **Fix:** Cambiar `tenant_{id}` por `tenant_{subdominio}` en TODO el código (Fase D — requiere migración de schemas existentes).
- **Ubicación:** `app.py` (líneas 988, 1899, 1935 + `set_tenant_schema()` + event listeners).

#### DT-nueva-CRÍTICA-3: Cambio de contraseña en Mi Perfil no persiste
- **Módulo:** Mi Perfil → "Cambiar Contraseña".
- **Bug:** El usuario cambia contraseña, cierra sesión, intenta login con nueva → falla. Solo funciona con la anterior.
- **Impacto:** Usuarios no pueden cambiar su contraseña. Fuerza a usar contraseñas temporales difíciles.
- **Fix:** Revisar endpoint `POST /mi_perfil`. Verificar que `generate_password_hash()` + `db.session.commit()` funcionen. Agregar `db.session.refresh(current_user)`. Test unitario.
- **Ubicación:** `app.py` (endpoint `mi_perfil` POST) + `templates/mi_perfil.html`.

### 🟡 MEDIA-ALTA

#### DT-nueva-MEDIA-ALTA: Análisis Productos suma donaciones en "Ingresos"
- **Módulo:** Reporte Avanzado Ventas + IA → Sección "Análisis Productos".
- **Bug:** Suma donaciones como si fueran ventas. Ej: 2 ventas ($2400) + 1 donación ($0) → muestra $3600.
- **Impacto:** Información financiera inflada.
- **Fix:** Agregar `AND Venta.es_donacion == FALSE` en query de ingresos. Agregar columna "Donaciones".
- **Ubicación:** `reportes.py` o `app.py` (método `analizar_productos_periodo`).

### 🟡 MEDIA

#### DT-nueva-MEDIA: Reporte "Productos Populares" vacío en tenant nuevo
- **Módulo:** Reportes → Productos Populares.
- **Bug:** Carga pero no muestra productos a pesar de haber ventas registradas.
- **Impacto:** Funcionalidad de reporte inutilizable en tenant nuevo.
- **Fix:** Revisar query. Verificar `JOIN` con `detalle_venta` y filtros por `panaderia_id`.
- **Ubicación:** `app.py` (endpoint `reporte_productos_populares`) + `reportes.py`.

### 🟡 MEDIA-BAJA

#### DT-nueva-media-baja (alias DT-S31-ventas-donacion): Ventas del Día no distingue donaciones
- **Módulo:** POS → Ventas del Día.
- **Bug:** Una venta con `es_donacion=TRUE` se muestra como "Completada" con Total $0, sin distinguir de una venta normal.
- **Impacto:** Falta de trazabilidad visual. El admin no puede distinguir donación de venta $0.
- **Fix:** Columna Estado: si `es_donacion` → badge "Donación" + tooltip. Deshabilitar "Anular".
- **Ubicación:** `templates/ventas_del_dia.html` + `app.py` (endpoint `ventas_del_dia`).
- ⚠️ **Colisión de nombre:** existe otra `DT-nueva-media-baja` (i18n de diccionarios Python, sección 9). Usar el alias para distinguirlas.

### 🟢 BAJA

#### DT-nueva-BAJA: Mensaje "datos insuficientes" en reportes IA
- **Módulo:** Reportes → Gerencial con IA.
- **Bug:** Con pocos datos (1 día), los PDFs salen sin información.
- **Impacto:** Comportamiento esperado. Falta mensaje claro.
- **Fix:** Mensaje explícito "Se necesitan al menos X días de ventas para generar predicciones".
- **Ubicación:** `reportes.py` (métodos `generar_reporte_ia_predictivo`, etc.).

---