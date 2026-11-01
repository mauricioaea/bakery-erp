# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP)

**Última actualización:** 31 de Octubre, 2026
**Último commit:** `52696be` (cierre de Feature Baja de Inventario + fix FK diferida) — precedido por `ba48503` (feat(baja-inventario): schema BD + modelo ORM + migracion base)
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

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp)
- **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.9.3 — **11/11 módulos completados (100%)** + **DT-37 F4 100%** + **DT-37 F5 100%** + **Feature Toppings 100%** + **Feature Anulación POS 100%** + **Feature Baja de Inventario 100%**.
- **Arquitectura:** Multi-tenant con PostgreSQL (schemas por tenant).
- **Seguridad:** Producción-ready (CSRF con tokens firmados + Origin/Referer + logging centralizado). ⚠️ Con 2 DT críticas abiertas (CRÍTICA-1 depósitos conciliados editables, CRÍTICA-3 cambio de contraseña) — ver sección 2️⃣7️⃣.
- **Observabilidad:** Producción-ready (logger con rotación de archivos, niveles configurables).
- **i18n:** 3 idiomas operativos (es/en/pap) en PDF reportes (100%) y HTML reportes (100%). Diccionarios Python pendientes (DT-nueva-media-baja).

### 📋 Próximos pasos planificados (ver secciones 2️⃣6️⃣ y 2️⃣8️⃣)

1. **Fase D — Pre-Dockerización: resolver las 7 DT del smoke test** (~8-10 h) — CRÍTICA. (Prioridad actualizada en sección 2️⃣8️⃣.)
2. **Fase E — Prueba de "tenant virgen"** (~2 h), post-Fase D.
3. **Fase G — Dockerización** (~22-32 h).
4. (Opcional/baja) **i18n de diccionarios Python** (~2-4 h).

> Nota: la "Auditoría ORM ↔ BD" y el "Tenant test + smoke test" del plan del 28 Oct quedaron cubiertos parcialmente por el smoke test del 31 Oct (tenants 29 y 30). La auditoría ORM ↔ BD formal sigue en Fases A-C de pre-Dockerización.

---

## 2️⃣ Stack tecnológico

### Backend
- Python 3.10+, Flask 3.1.2, SQLAlchemy 2.0
- PostgreSQL 17.10 (puerto 5433)
- Flask-Login, Flask-WTF, Werkzeug (pbkdf2:sha256, scrypt), ReportLab, Matplotlib
- **Flask-Babel 4.0.0** + **Babel 2.18.0**
- **Logging:** `logging` + `RotatingFileHandler` (built-in, sin dependencias)
- **BD:** `panaderia_master` — credenciales en `.env`
- **Password postgres (local):** `PanaderiaPro2026!` (⚠️ NO incluir en HANDOFFs públicos)

### Frontend
- HTML5/CSS3, JavaScript vanilla, Bootstrap 5.1.3, Chart.js, Font Awesome 6

### Estructura de archivos
- `app.py` (~12.800 líneas) — aplicación principal
- `models.py` (~3.200 líneas) — modelos SQLAlchemy
- `reportes.py` (~3.600 líneas) — generación PDF
- `seed_demo.py` (~450 líneas) — seed del Demo
- `seeds/` — 11 fases del seed
- `middleware_saas.py`, `tenant_decorators.py`, `tenant_context.py` — multi-tenant
- `security_utils.py` — utilidades de seguridad multi-tenant
- `migrations/sql/` — scripts SQL versionados
  - `2026-10-24_add_receta_toppings.sql` (nuevo)
  - `2026-10-26_add_anulacion_ventas.sql` (nuevo)
  - `2026-10-26_add_total_anulaciones_cierres.sql` (nuevo)
  - Migración base de `bajas_inventario` (nuevo, commit `ba48503`; verificar nombre exacto con `dir migrations\sql`)
- **`babel.cfg`** — config extracción strings (`[jinja2: **.html]`)
- **`locales/`** — catálogos de traducción
  - `locales/messages.pot` — plantilla (**~771 msgids**, + los de Baja de Inventario)
  - `locales/es/LC_MESSAGES/messages.{po,mo}` — español (fallback)
  - `locales/en/LC_MESSAGES/messages.{po,mo}` — inglés (**~767 traducidos, 99%** + Baja de Inventario)
  - `locales/pap/LC_MESSAGES/messages.{po,mo}` — papiamentu Curazao (**~766 traducidos, 99%** + Baja de Inventario)
- `templates/` (56 templates incl. `baja_inventario.html` + `_csrf_head.html` partial + subcarpeta `secciones/` con 4 parciales)
- `static/js/` — incluye `csrf-auto-inject.js`
- `logs/` — archivo rotativo `panaderia.log` (ignorado por git)
- `.env` (protegido), `.env.example` (plantilla)
- `requirements.txt` — incluye `Flask-WTF==1.3.0`, `WTForms==3.2.2`, `Flask-Babel==4.0.0`, `Babel==2.18.0`
- `HANDOFF.md` — este archivo
- **`_limpiar_fuzzy.py`** — script de utilidad (CRÍTICO en F5)
- **`_ver_untraducciones.py`** — script de utilidad (diagnóstico i18n — tiene bug conocido, ver DT-nueva-baja)
- **`_audit_schema.py`** — script de utilidad (auditoría de BD profunda)

---

## 3️⃣ Tenants activos

| ID | Nombre | Subdominio | Plan | Licencia |
|----|--------|-----------|------|----------|
| 1 | Panadería Principal | principal | basico | local |
| 27 | **Panadería Demo** | panadería_demo | premium | nube_premium |

**Tenant principal del Demo:** `tenant_27` ("Panadería Demo").
**Tenants de producción real:** `tenant_1` (Principal) + `tenant_27` (Demo).
**Estado de `tenant_1`:** ✅ Alineado (tiene `receta_toppings` + `historial_inventario` con 12 columnas + `producto_id` nullable + columnas de anulación). ⚠️ Pendiente confirmar que tenga `bajas_inventario` (aplicar migración si falta).
**Estado de `tenant_27`:** ✅ Re-seedeado el 5 Oct (9.968 filas) + ventas acumuladas + toppings + anulación. `idioma = pap`. ⚠️ Pendiente confirmar que tenga `bajas_inventario`.

**Tenants de smoke test (31 Oct):** `tenant_29` (plan básico) y `tenant_30` (plan premium), creados con `crear_tenant_saas()` para validar el fix de FK diferida. 16 puntos de verificación OK en ambos. **No son tenants de producción** — confirmar si fueron eliminados o se conservan como referencia.

### 📌 Arquitectura de `public.*` (post-DT-36)

**`public` tiene SOLO 3 tablas:**

| Tabla | Rol | Filas |
|---|---|---|
| `public.tenants` | Maestra de tenants | 2 (+ los de smoke test si siguen vivos) |
| `public.usuarios` | Fallback de `dev_master` (login) | 3 |
| `public.configuracion_panaderia` | Espejo de config por tenant | 1 |

**Columnas reales de `public.tenants`:**
`id`, `nombre`, `subdominio`, `base_datos`, `fecha_creacion`, `activo`, `plan`, `fecha_vencimiento`, `fecha_expiracion`.
**NO tiene columna `licencia`.**

⚠️ **Hallazgo 31 Oct (DT-nueva-CRÍTICA-2):** `base_datos` se genera como `tenant_{subdominio}` pero el schema real se crea como `tenant_{id}`. Ver sección 2️⃣7️⃣.

### 📌 Arquitectura del campo `idioma` (post-DT-37 F0)

- Vive en `tenant_X.configuracion_sistema` (dentro del schema del tenant).
- Tipo: `VARCHAR(5) NOT NULL DEFAULT 'es'`.
- Valores soportados: `es`, `en`, `pap`, `pt` (futuro).
- Migración: `migrations/sql/2026-10-12_add_idioma_configuracion_sistema.sql`.

**⚠️ Nota:** `tenant_1.configuracion_sistema` tiene **6 filas** con `panaderia_id` = 1, 5, 22, 24, 27, 28 (posible data legacy). No bloquea.

---

## 4️⃣ Usuarios del sistema

### Roles
- **super_admin** (dev_master) → gestiona TODOS los tenants
- **admin_cliente** → acceso TOTAL a su tenant
- **supervisor** → producción, recetas, MP, proveedores, reportes
- **cajero** → solo POS y cierre de caja

### Usuarios actuales
- **Tenant 1:** `dev_master` (super_admin), `admin`, `admin_1`
- **Tenant 27:** `admin_27`, `super_27`, `cajero_27`

### Contraseña del Demo
- **Todos los usuarios del tenant_27:** contraseña **`demo2026`**.

### Creación de usuarios
- **NO se crean desde el frontend.**
- Se crean al **alta del tenant** en `crear_tenant_saas()`.
- Los usuarios viven en `tenant_X.usuarios`.
- **NO se escriben en `public.usuarios`** salvo los 3 del `tenant_1`.

### Reseteo de contraseñas
- **Endpoint:** `POST /resetear_password/<int:usuario_id>` (`app.py:11362`).
- **UI desde dev_master:** `templates/gestion_clientes.html:787`.
- **UI desde admin_cliente:** `templates/gestion_usuarios.html:296`.
- ⚠️ **Cambio de contraseña desde Mi Perfil NO persiste** (DT-nueva-CRÍTICA-3, hallazgo 31 Oct). El reseteo por admin/dev_master sí funciona.

### Datos de facturación (por tenant)
- Configurables en `/configuracion/facturacion`.
- Se guardan en `ConfiguracionSistema` (dentro del schema del tenant). Fallback: `ConfiguracionPanaderia`.
- Incluye: tipo_facturacion, nombre_empresa, moneda, usa_centavos, simbolo_moneda, **idioma**.

---

## 5️⃣ Estado de los módulos (11/11 = 100%)

| # | Módulo | Estado |
|---|--------|--------|
| 1 | Punto de Venta | ✅ COMPLETO (con anulación + baja de inventario) |
| 2 | Producción Diaria | ✅ COMPLETO (con toppings) |
| 3 | Productos Externos | ✅ COMPLETO |
| 4 | Recetas y Fórmulas | ✅ COMPLETO (**con toppings**) |
| 5 | Materias Primas | ✅ COMPLETO |
| 6 | Proveedores | ✅ COMPLETO |
| 7 | Gestión de Clientes (solo dev_master) | ✅ COMPLETO |
| 8 | Activos Fijos | ✅ COMPLETO |
| 9 | Gestión de Usuarios + Mi Perfil | ✅ COMPLETO (⚠️ bug cambio de contraseña, DT-nueva-CRÍTICA-3) |
| 10 | Gestión Financiera | ✅ COMPLETO (⚠️ bug modal depósitos conciliados, DT-nueva-CRÍTICA-1) |
| 11 | Reportes Profesionales | ✅ COMPLETO (i18n PDF: 100%; HTML: 100%) |

---

## 6️⃣ Últimos commits pusheados

```text
52696be (cierre Feature Baja de Inventario + fix FK diferida fk_historial_inventario_orden_produccion en crear_tenant_saas)
ba48503 feat(baja-inventario): schema BD + modelo ORM + migracion base
4ecfde9 feat(anulacion-pos): UI frontend, modal y blindaje de reportes financieros (bloques 6 y 7)
1513c9a fix(anulacion-pos): cierre diario y vista excluyen ventas anuladas (bloque 4/7)
494f190 feat(anulacion-pos): helper Venta.puede_anularse() + fix FK ambigua (bloque 2/7)
722beb5 feat(anulacion-pos): agregar total_anulaciones a cierres_diarios (bloque 1/7)
9e645ba feat: agregar toppings a recetas con calculo de costos, descuento de stock, historial de inventario y visualizacion en modal de produccion
f213e33 docs: HANDOFF v9.2 - DT-37 F5 COMPLETADO (100%) + nuevo plan pre-Dockerizacion (fases A-G) + 2 features pendientes (recetas/toppings, anulacion POS) - DT-CREDITOS eliminada
c54d9eb feat(DT-37 F5): migrar ventas_avanzado.html a i18n (es/en/pap) — F5 COMPLETADO (100%)
61edb44 feat(DT-37 F5): migrar secciones/analisis_ia.html a i18n (es/en/pap)
ec2687e feat(DT-37 F5): migrar secciones/resumen_ventas.html a i18n (es/en/pap)
84b9080 feat(DT-37 F5): migrar secciones/recomendaciones.html a i18n (es/en/pap)
7582770 feat(DT-37 F5): migrar secciones/analisis_productos.html a i18n + corregir traducciones heredadas
b660db7 feat(DT-37 F5): migrar reporte_produccion.html a i18n (es/en/pap)
d0fd6bb feat(DT-37 F5): migrar analisis_predictivo.html a i18n + fix CSS @media print + badge traducción
0af8fcf feat(DT-37 F5): migrar ventas_periodo.html a i18n + fix multi-tenant nombre panadería
cf81b34 docs: HANDOFF v9.1 - DT-37 F5 parte 1 completada (6/11 templates)
3ea5612 feat(DT-37 F5): migrar reporte_ventas_externas.html a i18n + fix export PDF
2f9a5fe feat(DT-37 F5): migrar reporte_inventario_externo.html a i18n + fix export PDF
0ebb3de feat(DT-37 F5): migrar reporte_activos.html a i18n + fix placeholders
a796290 feat(DT-37 F5): migrar productos_populares.html a i18n + fixes de script
a0de295 feat(DT-37 F5): migrar reportes.html y cierre_caja.html a i18n
```

---

## 7️⃣ Demo — Estado de las fases del seed

| # | Fase | Estado | Filas |
|---|------|--------|-------|
| 1 | Configuración base | ✅ | 9 |
| 2 | Proveedores | ✅ | 6 |
| 3 | Materias primas | ✅ | 17 |
| 4 | Recetas y fórmulas | ✅ | 12 recetas / 80 ingredientes |
| 5 | Productos | ✅ | 12 |
| 6 | Producción diaria | ✅ | ~2.416 |
| 7 | Ventas | ✅ | ~7.033 (+4 del smoke test) (+2 de anulación) |
| 8 | Productos externos | ✅ | 12 |
| 9 | Activos fijos | ✅ | 36 |
| 10 | Movimientos financieros | ✅ | 261 |
| 11 | Cierres diarios | ✅ | 90 |
| 12 | Reset automatizado | ✅ | — |

**Total aproximado:** ~9.972 filas en tenant_27.

---

## 8️⃣ Configuración crítica

### Variables de entorno (.env)

```text
DATABASE_URL=postgresql://postgres:...@localhost:5433/panaderia_master
DB_PASSWORD=...
FLASK_ENV=development
SECRET_KEY=...
```

⚠️ `SECRET_KEY` es crítica para: sesiones Flask, firma de tokens CSRF, firma de cookies seguras.

### Rutas críticas

- **F4 (reportes.py — PDFs):** todas ✅ i18n es/en/pap.
- **F5 (templates HTML):** todas ✅ i18n es/en/pap (14 archivos migrados).

**Feature Toppings:**
- `/crear_receta` — formulario con toppings.
- `/editar_receta/<id>` — edición con toppings.
- `/detalle_receta/<id>` — sección "Toppings".
- `/produccion_diaria` — modal "Ordenar" con toppings.
- `/api/calcular_ingredientes/<id>` — API con toppings.

**Feature Anulación POS:**
- `/ventas_del_dia` — Historial del día para anulación desde frontend.
- `POST /anular_venta/<id>` — Endpoint backend de anulación.

**Feature Baja de Inventario (NUEVO, 31 Oct):**
- `GET /baja_inventario` — pantalla de registro de bajas (carrito estilo POS).
- `GET /api/productos_vitrina` — productos disponibles en vitrina para dar de baja.
- `POST /registrar_baja` — registra la baja (motivo `VENCIMIENTO` o `ROTURA`), descuenta stock y calcula costo real desde receta.

---

## 9️⃣ Deuda técnica acumulada

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

### 🚨 NUEVAS PENDIENTES (31 Oct 2026) — Hallazgos del smoke test

Ver detalle completo en la **sección 2️⃣7️⃣**. Resumen:

| Prioridad | DT | Descripción corta |
|---|---|---|
| 🚨 CRÍTICA | DT-nueva-CRÍTICA-1 | Modal "Ver" de depósitos CONCILIADOS permite edición |
| 🚨 CRÍTICA | DT-nueva-CRÍTICA-2 | `base_datos` = `tenant_{subdominio}` vs schema real `tenant_{id}` |
| 🚨 CRÍTICA | DT-nueva-CRÍTICA-3 | Cambio de contraseña en Mi Perfil no persiste |
| 🟡 MEDIA-ALTA | DT-nueva-MEDIA-ALTA | Análisis Productos suma donaciones en "Ingresos" |
| 🟡 MEDIA | DT-nueva-MEDIA | Reporte "Productos Populares" vacío en tenant nuevo |
| 🟡 MEDIA-BAJA | DT-nueva-media-baja (Ventas del Día) | No distingue donaciones (⚠️ mismo nombre que la DT de i18n de diccionarios; alias: **DT-S31-ventas-donacion**) |
| 🟢 BAJA | DT-nueva-BAJA | Mensaje "datos insuficientes" en reportes IA |

### 🟡 Medias pendientes

| # | Ubicación | Descripción |
|---|-----------|-------------|
| DT-37 F5-pulido | app.py / reportes.py | Gráficos de matplotlib (en reporte_activos.html y otros) tienen títulos en español hardcodeados en Python. Requiere i18n en funciones que generan imágenes. Estimación: ~1 h por reporte. |
| DT-37 F4.9 | reportes.py:500 | libro_diario: método huérfano (sin UI). Baja prioridad. ~30 min. |
| DT-NUEVA-1 | migrations/sql/ | Sincronizar CREATE TABLE con idioma para tenants nuevos (obligatorio antes del próximo tenant). ⚠️ Revisar si quedó cubierto por el smoke test del 31 Oct (tenants 29/30 nacieron OK). |
| DT-nueva | reportes.py | Error 'ingreso' en generar_reporte_ia_predictivo (L1936). El PDF muestra "Las recomendaciones no están disponibles temporalmente por error técnico". El except ya está i18n-ready. |
| DT-nueva | app.py:9066 | Endpoint /generar_reporte_flujo_caja huérfano: existe pero ningún template lo invoca. Además tiene bug: generador.generar_reporte_flujo_caja(fecha_inicio, fecha_fin) le falta panaderia_id (L9092). |
| DT-nueva | analisis_gastos (matplotlib) | Overlap de labels en pie chart con categorías con valores pequeños. Cosmética. (Ahora con categoría "Bajas" agregada: revisar.) |
| DT-nueva-media-baja | app.py | i18n de diccionarios Python que alimentan reportes HTML: analisis_tendencias.mensaje, analisis_tendencias.recomendaciones, predicciones_ml.mensaje, predicciones_ml.mensaje_tendencia, recomendaciones_personalizadas.mensaje, recomendacion.titulo, recomendacion.mensaje, recomendacion.accion, recomendacion.prioridad, producto.nivel_riesgo, prediccion.confianza. Los textos siguen en español en reportes PAP/EN porque vienen de Python hardcodeado. NO es F5, es deuda de app.py. NO urgente, NO rompe nada. |
| DT-nueva-baja | templates/ | Mapeo Jinja2 de badges dinámicos (prioridad/nivel_riesgo/confianza) en analisis_predictivo.html, analisis_ia.html, ventas_avanzado.html. Ej: {{ {'ALTO': _('Alto'), 'MEDIO': _('Medio'), 'BAJO': _('Bajo')}[valor] }}. |
| DT-nueva-baja | _ver_untraducciones.py | Bug: reporta 13 strings en EN cuando hay 44, y 0 en PAP cuando hay 53. Reescribir o reemplazar por findstr /c:"msgstr \"\"". Baja prioridad. |

### 🚨 DT-nueva-CRÍTICA (heredada)

| Ubicación | Descripción |
|-----------|-------------|
| reportes.py (ReportLab) | Emojis 🔴 🟢 🟡 ⚪ 📦 📊 🚨 💡 📋 ✅ rotos en PDFs: la fuente Helvetica default de ReportLab no tiene glyphs → salen como n. Cosmética global. |

### 🟢 Bajas pendientes

| # | Descripción |
|---|-------------|
| DT-nueva | tenant_1.configuracion_sistema tiene 6 filas con panaderia_id = 1, 5, 22, 24, 27, 28 (posible data legacy). |
| DT-nueva | Imports redundantes de os en app.py (líneas 1225, 10519, 11009, 11958, 12323, 12429). |
| DT-nueva | Fluho Neto en lugar de Flusho Neto en PAP (ajuste menor de traducción). |
| DT-nueva | cierre_diario.html es huérfano. La ruta /cierre_diario (app.py:7165) existe pero NO está enlazada desde el frontend. El cierre real se hace desde el POS. Acción futura (decidir): eliminar templates/cierre_diario.html + la ruta /cierre_diario de app.py, o dejarla como utilidad oculta. NO migrar a i18n (no se usa). |
| DT-nueva | reportes.html:229 tiene el botón para ventas_periodo.html con el nombre "Historial de Ventas". Evaluar renombrar a "Ventas por Período". |
| DT-nueva-cosmética | ventas_periodo.html tiene datos demo hardcodeados en tabla Distribución por Categoría (40/35/15/10) y gráficos. Deberían venir de Python. |
| DT-nueva-traducción | al → Real en PAP (heredado). Mejor te o hasta. |
| DT-nueva-traducción | Medio → Average/Promedio (heredado). Mejor Medium/Medio. Similar para Bajo → LOW/ABOU (heredado). |
| DT-nueva | tenant_1 (plantilla de referencia) tiene una estructura de historial_inventario ligeramente diferente a tenant_27 (no tiene FK en orden_produccion_id). Evaluar alinear en la Fase A-F de pre-Dockerización. ⚠️ El fix del 31 Oct agregó la FK diferida en `crear_tenant_saas()` para tenants NUEVOS; tenant_1 sigue pendiente de alinear. |

---

## 🔟 Metodología de trabajo

### Reglas de oro (heredadas de v9.2)

1. Un paso a la vez con confirmación antes de continuar.
2. Diagnóstico ANTES de modificar.
3. Soluciones de raíz (no parches).
4. TODO debe funcionar para futuros tenants.
5. Verificación con psql/findstr antes de avanzar.
6. Commit después de cada fix verificado.
7. Backup antes de cada cambio grande.
8. Siempre verificar git status antes de commitear.
9. Push después del commit.
10. Detener servidor antes de reiniciar.
11. Insertar bloques: mostrar ANTES → DESPUÉS con número de línea exacto.
12. Verificar ubicación y compilar tras cada inserción.
13. Al detectar deuda técnica: anotarla (no tocarla), priorizarla, decidir después.
14. En Windows, usar findstr /c:"patrón" para búsquedas literales.
15. findstr /c:"texto con tilde" puede fallar por encoding → usar fragmentos sin tildes o Get-Content -Encoding UTF8.
16. Al commitear, SIEMPRE usar git add <archivo> explícito.
17. En Flask-Babel 4.0: default_translation_directories DEBE pasarse al constructor Babel(app, ...).
18. pybabel extract con . escanea TODO (incl. venv/). Usar lista explícita.
19. Los .mo DEBEN commitearse al repo.
20. 🚨 pybabel NO extrae _() dentro de f-strings. Extraer a variables.
21. 🚨 pybabel NO extrae _() después de emoji dentro de f-string. Usar concatenación.
22. pybabel update marca #, fuzzy. SIEMPRE correr _limpiar_fuzzy.py después.
23. El % NUNCA va dentro de _(). Siempre afuera. (Ver también la regla ampliada de `%` sueltos en `msgstr`, abajo.)
24. babel.cfg: el pattern Jinja2 debe ser [jinja2: **.html], NO **/templates/**.html.
25. Proteger <style> y <script> ANTES de reemplazos masivos en templates. Usar placeholders.
26. Reemplazos SOLO entre etiquetas HTML (>Texto<). Nunca palabras sueltas.
27. Orden de reemplazos: primero los textos que contienen otros textos.
28. Emojis en HTML: incluirlos en el reemplazo (>📦 Texto<). Si se corrompen, eliminarlos.
29. Verificar el .mo directamente con gettext.GNUTranslations cuando el HTML no se traduce.
30. Reiniciar servidor + modo incógnito después de pybabel compile.
31. Migrar también los PDFs de exportación (/exportar_X en app.py).
32. Preferir scripts Python sobre copy-paste del chat (mojibake).
33. N/A, Ninguno, siglas universales también migrar con _().
34. config.nombre_panaderia ya está disponible globalmente en templates (vía inject_user_permissions()).
35. reporte_produccion.html es el reporte (/reporte_produccion_diaria). produccion_diaria.html (58 KB) es el dashboard del módulo (no es reporte HTML, no es F5).
36. cierre_diario.html es huérfano (nadie lo enlaza desde frontend).

### 🚨 NUEVAS Reglas de oro (Aprendidas en Feature Toppings, 24 Oct 2026)

1. Modelo ORM ↔ Tabla BD DEBEN estar alineados. Al agregar una columna a un modelo, verificar con information_schema.columns que la tabla real la tiene. Los CREATE TABLE manuales en app.py pueden quedar desalineados.
2. producto_id puede ser NULL en historial_inventario (para movimientos que no son de producto terminado). Si la tabla lo requiere NOT NULL, usar ALTER TABLE ... DROP NOT NULL.
3. search_path DEBE estar seteado antes de hacer MateriaPrima.query.get() en contextos fuera de request (scripts, tareas). Verificar con SHOW search_path.
4. Al agregar una FK a un CREATE TABLE manual, verificar el orden de creación de tablas. Si la tabla referenciada se crea después, dejar la columna sin FK (validar en aplicación) o mover el CREATE TABLE. (**Ampliada el 31 Oct:** ver regla de FK diferida con `ALTER TABLE`.)
5. _descontar_ingredientes() DEBE registrar en HistorialInventario (no solo restar del stock). Sin historial no hay trazabilidad.
6. Al procesar toppings, usar factor_escala = cantidad_producir / unidades_obtenidas para escalar correctamente si se produce más de un lote.
7. Los toppings se manejan SIEMPRE en gramos, independientemente de la unidad de medida de la materia prima. Convertir stock a gramos en el endpoint API.
8. Verificar los Print de JavaScript en templates — el mojibake puede romper el JS y hacer que aparezca como texto plano en la UI.
9. tenant_1 (plantilla) y tenant_27 (demo) DEBEN tener la misma estructura. Al agregar columnas/tablas, aplicar la migración a ambos.

### 🚨 NUEVAS Reglas de oro (Aprendidas en Feature Anulación, 28 Oct 2026)

1. **Soft-delete siempre:** Las ventas nunca se borran físicamente. Cambian de estado (`COMPLETADA` / `ANULADA`).
2. **Filtrado universal:** Cada vez que se consulte la tabla `Venta` para reportes o cálculos de dinero, se DEBE inyectar `Venta.estado == 'COMPLETADA'`.
3. **FKs ambiguas:** Al agregar una segunda FK a una tabla ya relacionada en SQLAlchemy, es obligatorio declarar `foreign_keys='Tabla.columna'` en el `relationship` para evitar `AmbiguousForeignKeysError`.
4. **Cierre de caja blindado:** El sistema no permite anular ventas si el día ya tiene un cierre de caja (`CierreDiario`) confirmado.
5. **Seguridad DIAN:** Las facturas electrónicas (`tipo_documento == 'ELECTRONICA'`) NUNCA se pueden anular en el POS; requieren nota crédito.

### 🚨 NUEVAS Reglas de oro (Aprendidas en Feature Baja de Inventario + Smoke test, 31 Oct 2026)

1. **i18n — `%` sueltos en `msgstr`:** En Python-format/`printf`, un `%` suelto dentro de un `msgstr` (ej. "10% de descuento") rompe `pybabel compile` o lanza `ValueError`/`TypeError` en runtime al formatear. Reglas: (a) el `%` NUNCA va dentro de `_()` — va afuera (regla heredada); (b) si un `msgid` debe contener `%` literal y se usa con `%` formatting, escribirlo como `%%` en `msgid` y `msgstr`; (c) `msgid` y `msgstr` deben tener los MISMOS placeholders (`%(nombre)s`, `%s`, `%d`); (d) tras `pybabel compile -d locales --statistics`, revisar warnings y buscar `%` sueltos con `findstr /n /c:"%" locales\en\LC_MESSAGES\messages.po` y el equivalente en `pap`; (e) verificar el `.mo` con `_test_mo.py`.
2. **FK diferida con `ALTER TABLE` en `crear_tenant_saas()`:** Cuando una tabla referencia a otra que se crea DESPUÉS en el mismo flujo de creación de tenant, NO incluir la FK en el `CREATE TABLE`. Crear ambas tablas y al final agregar la FK con `ALTER TABLE ... ADD CONSTRAINT fk_... FOREIGN KEY ...`. Ejemplo resuelto: `fk_historial_inventario_orden_produccion` (`historial_inventario.orden_produccion_id` → `ordenes_produccion`). Esto reemplaza la alternativa "dejar sin FK" de la regla 4 de Toppings.
3. **Todo cambio de schema de tenant se prueba con un tenant nuevo:** Un cambio que funciona en `tenant_1`/`tenant_27` (migrados a mano) puede romper `crear_tenant_saas()`. Tras cada cambio de schema, correr smoke test con un tenant básico y uno premium (16 puntos) y borrarlos después.
4. **Reportes con dinero:** Al agregar una nueva fuente de pérdidas/gastos (como bajas de inventario), actualizar `estado_resultados` y `analisis_gastos` en el MISMO commit para no dejar reportes inconsistentes.
5. **Donaciones (`es_donacion=TRUE`) deben excluirse de ingresos** en toda consulta de ventas para reportes y distinguirse visualmente en UI (ver hallazgos DT-nueva-MEDIA-ALTA y DT-S31-ventas-donacion).

### Comandos útiles (ACTUALIZADOS)

```cmd
# Pipeline i18n
pybabel extract -F babel.cfg -o locales/messages.pot app.py models.py reportes.py templates
pybabel update -i locales/messages.pot -d locales
python _limpiar_fuzzy.py
pybabel compile -d locales --statistics

# Buscar % sueltos en traducciones (nuevo, 31 Oct)
findstr /n /c:"%" locales\en\LC_MESSAGES\messages.po
findstr /n /c:"%" locales\pap\LC_MESSAGES\messages.po

# Verificar estructura de una tabla
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_schema = 'tenant_27' AND table_name = 'historial_inventario' ORDER BY ordinal_position;"

# Verificar constraints de una tabla
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = 'tenant_27.receta_toppings'::regclass;"

# Verificar FK diferida de historial_inventario en un tenant nuevo (nuevo, 31 Oct)
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = 'tenant_29.historial_inventario'::regclass;"

# Verificar historial de movimientos
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "SELECT h.id, mp.nombre, h.cantidad_utilizada, h.orden_produccion_id FROM tenant_27.historial_inventario h JOIN tenant_27.materias_primas mp ON mp.id = h.materia_prima_id WHERE h.orden_produccion_id = 301 ORDER BY h.id;"

# Scripts de diagnóstico (crear _test_XXX.py)
python _test_jinja.py <template.html>
python _test_mo.py
python _test_descuento.py
python _audit_schema.py

# Comandos heredados
chcp 65001
psql -U postgres -p 5433 -h localhost -d panaderia_master
python -m py_compile app.py
python app.py
findstr /n /c:"patrón exacto" archivo.py
pg_dump -U postgres -p 5433 -h localhost -d panaderia_master -F c -f backup_pre_XXX.backup
git commit -F _commit_msg.txt && del _commit_msg.txt
```

### Scripts de utilidad que DEBEN existir en el proyecto

- `_limpiar_fuzzy.py` — elimina líneas `#, fuzzy` de los .po. CRÍTICO.
- `_ver_untraducciones.py` — muestra msgids con `msgstr ""` en en.po (tiene bug conocido).
- `_test_jinja.py` — valida sintaxis Jinja2 de un template dentro del contexto Flask.

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

## 1️⃣2️⃣ a 1️⃣9️⃣ Bitácoras anteriores

(Se mantienen las bitácoras de sesiones previas: DT-25, DT-28/45, DT-42/43, DT-46, DT-5-bis/quinquies, DT-5-quater-bis, DT-19, DT-47. Consultar HANDOFF v9.1 si se necesita detalle.)

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

## 2️⃣3️⃣ 🆕 Plan de trabajo: Análisis pre-Dockerización (SINCRONIZACIÓN MODELOS/APP/BD)

**Origen:** Detectado en sesión 24 Oct 2026 (feedback del usuario antes de Dockerizar).

**Contexto:** Antes de dockerizar el sistema, es CRÍTICO asegurar que:
- models.py ↔ app.py ↔ Base de datos están sincronizados.
- Todos los futuros tenants nazcan completos y actualizados (sin discrepancias).
- Crear tablas en orden correcto para que app.py funcione desde el primer arranque.
- No haya tablas/columnas huérfanas en ningún schema.
- tenant_27 (Demo para marketing) y tenant_1 (Plantilla de referencia) estén sincronizados estructuralmente.

**Objetivo final:** Dejar el código y la BD limpios, sin discrepancias, listos para dockerizar con la garantía de que un tenant nuevo nace 100% funcional y estructuralmente correcto.

> 📝 **Actualización 31 Oct:** El smoke test de tenants nuevos (29 y 30) validó parcialmente la Fase E, y destapó 7 hallazgos que se integran a la **Fase D** (ver secciones 2️⃣7️⃣ y 2️⃣8️⃣). El fix de FK diferida ya está aplicado.

### Plan de trabajo propuesto (7 fases A-G)

**Fase A — Auditoría de modelos (models.py) (~2 h)**
- □ Mapear TODOS los modelos definidos en models.py (clases, tablas, columnas, relaciones, FKs).
- □ Detectar modelos huérfanos (definidos pero sin uso en app.py ni en templates).
- □ Detectar columnas huérfanas (definidas en modelo pero nunca leídas/escritas).
- □ Detectar FKs mal definidas o ausentes.
- □ Documentar la estructura "canónica" de un tenant completo.

**Fase B — Auditoría de app.py (~2 h)**
- □ Mapear TODAS las queries SQLAlchemy a modelos.
- □ Detectar queries a tablas/columnas que NO existen en models.py (bug oculto).
- □ Detectar funciones de creación de tenant (crear_tenant_saas()) — verificar que creen TODAS las tablas necesarias.
- □ Detectar rutas/endpoints que usen modelos no sincronizados.
- □ Verificar el orden de CREATE TABLE en crear_tenant_saas() (FKs antes que tablas dependientes).

**Fase C — Auditoría de BD (information_schema) (~2 h)**
- □ Ejecutar information_schema.columns en tenant_1 y tenant_27 para mapear columnas reales.
- □ Comparar columnas de tenant_1 vs tenant_27 → detectar diferencias estructurales.
- □ Comparar models.py vs BD real → detectar discrepancias.
- □ Detectar tablas huérfanas en public.*.
- □ Detectar tablas huérfanas en tenant_1 y tenant_27.
- □ Documentar la estructura "real" de la BD.

**Fase D — Sincronización (~3-4 h → ampliada a ~8-10 h con los 7 hallazgos del 31 Oct)**
- □ Crear script SQL de migración para alinear tenant_1 ↔ tenant_27.
- □ Actualizar crear_tenant_saas() para que TODAS las tablas/columnas se creen en orden correcto. (✅ FK diferida de historial_inventario ya aplicada el 31 Oct.)
- □ Actualizar models.py para eliminar huérfanos y agregar lo que falte.
- □ Actualizar migrations/sql/ con la migración de sincronización (especialmente CREATE TABLE ... idioma).
- □ Ejecutar migración en tenant_1 y tenant_27 (incluir `bajas_inventario`).
- □ Verificar con information_schema.columns que ambos están sincronizados.
- □ Resolver las 7 DT-nueva del smoke test (sección 2️⃣7️⃣) + renombrar schemas a `tenant_{subdominio}`.

**Fase E — Prueba de "tenant virgen" (~2 h)**
- □ Crear tenant de prueba (ej. tenant_test) desde cero con crear_tenant_saas(). (🟡 Hecho parcialmente el 31 Oct con tenant_29 y tenant_30; repetir tras Fase D.)
- □ Verificar que TODAS las tablas del modelo estén creadas.
- □ Verificar que information_schema.columns del tenant nuevo coincida con tenant_1 y tenant_27.
- □ Probar el flujo completo: login → dashboard → POS → venta → cierre → reporte.
- □ Si algo falla → corregir y repetir hasta que un tenant nuevo nazca 100% funcional.
- □ Borrar tenant_test (limpieza).

**Fase F — Documentación y limpieza (~2 h)**
- □ Documentar la estructura canónica del tenant (tablas, columnas, FKs, orden de creación).
- □ Eliminar código huérfano (modelos sin uso, columnas sin referencias, endpoints muertos).
- □ Actualizar HANDOFF con la estructura canónica.
- □ Crear docs/ESTRUCTURA_TENANT.md con el mapa completo.

**Fase G — Preparación para Dockerización**
- □ Verificar que requirements.txt esté completo y versionado.
- □ Verificar que los .mo estén commiteados.
- □ Verificar que .env.example tenga TODAS las variables necesarias.
- □ Confirmar que crear_tenant_saas() funciona en un entorno limpio.
- □ Crear Dockerfile + docker-compose.yml (Fase 3).

### Estimación de tiempos

| Fase | Estimación |
|---|---|
| A — Auditoría de modelos | ~2 h |
| B — Auditoría de app.py | ~2 h |
| C — Auditoría de BD | ~2 h |
| D — Sincronización (+ 7 DT del smoke test) | ~8-10 h |
| E — Prueba de "tenant virgen" | ~2 h |
| F — Documentación y limpieza | ~2 h |
| **Total pre-Dockerización** | **~18-20 h (3-4 sesiones)** |
| G — Dockerización (Fase 3) | ~22-32 h |

### Prioridad
**CRÍTICA** — no dockerizar sin completar A-F. Es la base de todo el SaaS multi-tenant.

### Riesgos identificados
- Puede haber tablas/columnas en app.py que se crean "al vuelo" sin estar en models.py.
- Puede haber tenants antiguos (1 y 27) con estructura diferente a un tenant nuevo.
- Puede haber código huérfano de features abandonadas (limpiar).
- Puede haber dependencias ocultas entre tablas (verificar FKs).
- **(Nuevo 31 Oct)** Renombrar schemas `tenant_{id}` → `tenant_{subdominio}` (DT-CRÍTICA-2) es un cambio transversal con riesgo alto: requiere backup, migración de schemas existentes y revisión de `set_tenant_schema()` + event listeners.

### Recomendación de arranque
Empezar por Fase C (auditoría de BD), porque da una foto concreta del estado actual y permite planificar el resto con datos reales. (Ver sección 2️⃣9️⃣: la recomendación para el próximo chat es arrancar por las DT críticas de fácil aislamiento antes de la auditoría completa.)

---

## 2️⃣4️⃣ Notas estratégicas

### Objetivo del ERP
ERP SaaS multi-tenant multi-país con: POS, inventario, producción, recetas (con toppings), activos fijos, reportes con IA, finanzas, i18n multi-idioma (es/en/pap), multi-país, base para API REST + IA avanzada, módulo de anulación de ventas, módulo de baja de inventario (vencimientos y roturas).

### 🎁 Tenant Demo
Fases 1-12 completadas (~9.972 filas). Contraseña: demo2026. idioma = pap.

### Mercado objetivo
- 3.000-5.000 panaderías en Colombia.
- 10.000-30.000 en LATAM.
- Clientes internacionales: Curazao-Antillas Holandesas (Papiamentu).
- Precio: $60k-$600k COP/mes.

### Modelo de licencias
- Premium: 3 usuarios.
- Básica: 1 usuario.

### Estimación de tiempos (31 Oct 2026)

| Bloque | Estimación |
|---|---|
| DT-37 F5 | ✅ COMPLETADO (100%) |
| Feature Toppings | ✅ COMPLETADO (24 Oct 2026) |
| Feature Anulación POS | ✅ COMPLETADO (28 Oct 2026) |
| Feature Baja de Inventario | ✅ COMPLETADO (31 Oct 2026) |
| Smoke test tenants nuevos (básico + premium) | ✅ COMPLETADO (31 Oct 2026) |
| 7 DT del smoke test (Fase D parcial) | ~8-10 h |
| i18n diccionarios Python | ~2-4 h (baja prioridad) |
| Auditoría ORM ↔ BD (Fases A-C) | ~6 h |
| Pre-Dockerización total (Fases A-F) | ~18-20 h |
| Dockerización (Fase G) | ~22-32 h |
| DT-37 F5-pulido (gráficos matplotlib) | ~1 h por reporte |
| DT-37 F4.9 (libro_diario huérfano) | ~30 min |

---

## 2️⃣5️⃣ 🐳 Preparación para Dockerización

El sistema está listo para Docker una vez completadas las fases A-F de pre-Dockerización:

- ✅ CSRF con SECRET_KEY (portable entre entornos).
- ✅ Logs a archivo + consola (compatible con docker logs).
- ✅ Logs con rotación (evita llenar disco).
- ✅ Sin dependencias de red específicas.
- ✅ requirements.txt actualizado.
- ✅ i18n con locales/ (portable, los .mo van en el repo).
- ✅ Feature Toppings completa.
- ✅ Feature Anulación POS completa.
- ✅ Feature Baja de Inventario completa.
- ✅ `crear_tenant_saas()` crea tenants nuevos sin errores de FK (fix 31 Oct).
- 🟡 Pre-Dockerización pendiente (fases A-F) + 7 DT del smoke test.
- 🟡 Fase G: Dockerfile + docker-compose.yml (a crear).

---

## 2️⃣6️⃣ 🆕 PLAN DE TRABAJO — Próximas sesiones (orden prioritario)

> ⚠️ **SUPERADO PARCIALMENTE por la sección 2️⃣8️⃣ (31 Oct 2026).** Se conserva como referencia histórica del plan definido por Mauricio el 28 Oct.

**Orden definido por Mauricio (28 Oct 2026):**

### Fase 1 — Auditoría ORM ↔ BD (~1-2 h)
Objetivo: Verificar con `_audit_schema.py` que no haya discrepancias entre models.py y la BD real (tenant_1 y tenant_27).
Entregable: Reporte de discrepancias + fixes.

### Fase 2 — i18n de diccionarios Python (~2-4 h)
Prioridad: Baja (si es necesario; sino dejar como está).
Alcance: Migrar los diccionarios de app.py que alimentan reportes HTML (analisis_tendencias.mensaje, recomendacion.titulo, etc.). Ver DT-nueva-media-baja.
Decisión: Evaluar si vale la pena o se deja como deuda aceptada.

### Fase 3 — Tenant test + smoke test (~1-2 h)
Objetivo: Crear un tenant nuevo desde cero con crear_tenant_saas() y verificar que TODAS las funcionalidades funcionen.
Entregable: Confirmación de que un tenant nuevo nace 100% funcional.
✅ **Ejecutado el 31 Oct** (tenant_29 básico + tenant_30 premium, 16 puntos OK). Ver sección 2️⃣7️⃣.

### Fase 4 — Pre-Dockerización (Fases A-F) (~13-15 h)
Prioridad: CRÍTICA (bloqueante para dockerizar).
Alcance: Ver sección 2️⃣3️⃣.

### Fase 5 — Dockerización (Fase G) (~22-32 h)
Prioridad: Alta.
Alcance: Crear Dockerfile + docker-compose.yml con PostgreSQL.

---

## 2️⃣7️⃣ 🆕 HALLAZGOS SMOKE TEST TENANTS NUEVOS (31 Oct 2026)

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

## 2️⃣8️⃣ 🆕 PRÓXIMOS PASOS ACTUALIZADOS (31 Oct 2026)

1. **Fase D — Pre-Dockerización** (~8-10 h): Resolver las 7 DT-nueva (3 críticas + 4 menores) + renombrar schemas a `tenant_{subdominio}` + alinear FKs (incluye aplicar `bajas_inventario` y la FK diferida a `tenant_1`/`tenant_27`).
2. **Fase E — Prueba de "tenant virgen"** (~2 h): Crear tenant nuevo, verificar 100% funcional (post-Fase D).
3. **Fase G — Dockerización** (~22-32 h).

*(Las Fases A-C de auditoría y F de documentación se intercalan según convenga; ver sección 2️⃣3️⃣. La i18n de diccionarios Python sigue como deuda baja opcional.)*

---

## 2️⃣9️⃣ 📌 NOTA FINAL — DT recomendada para iniciar el nuevo chat

### 🎯 Empezar por: **DT-nueva-CRÍTICA-3 — Cambio de contraseña en Mi Perfil no persiste**

**Por qué esta primero:**
1. **Alcance acotado:** un solo endpoint (`POST /mi_perfil`) + un template. Se diagnostica en minutos y es fácil de aislar.
2. **Impacto inmediato en clientes reales:** los usuarios no pueden cambiar su clave; es lo primero que notará un cliente nuevo.
3. **Cero riesgo de migración:** no toca schema, ni tenants existentes, ni FKs. Permite calentar la sesión con una victoria rápida y verificable.
4. **Posible causa raíz común:** si el fallo es de sesión/commit en contexto multi-tenant (`search_path`), el aprendizaje puede aplicar a otros endpoints.

**Orden sugerido para Fase D:**

| Orden | DT | Motivo | Estimación |
|---|---|---|---|
| 1 | **CRÍTICA-3** (contraseña Mi Perfil) | Rápida, aislada, impacto directo | ~30-45 min |
| 2 | **CRÍTICA-1** (depósitos CONCILIADOS editables) | Riesgo contable, fix frontend + validación 403 | ~45-60 min |
| 3 | **MEDIA-ALTA** (donaciones suman en Ingresos) | Datos financieros inflados | ~45 min |
| 4 | **MEDIA** (Productos Populares vacío en tenant nuevo) | Posible causa común con anterior (JOIN/filtros) | ~45 min |
| 5 | **MEDIA-BAJA** (Ventas del Día: badge Donación) | Relacionada con MEDIA-ALTA; UI | ~30 min |
| 6 | **BAJA** (mensaje "datos insuficientes" en IA) | Cosmética | ~30 min |
| 7 | **CRÍTICA-2** (renombrar schemas a `tenant_{subdominio}`) | La más riesgosa y transversal: hacerla al final, con backup completo (`pg_dump`) y con todo lo demás estable | ~3-4 h |

### Instrucción sugerida para pegar en el nuevo chat

> "Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el archivo HANDOFF.md **v9.5** con el contexto maestro. Vamos a continuar desde donde lo dejamos. Por favor actúa como instructor guiando paso a paso, con la metodología de trabajo descrita en el HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/findstr, commit tras cada fix verificado. Al insertar bloques, muéstrame ANTES → DESPUÉS con número de línea exacto. Tú me das LUZ VERDE cuando los cambios estén 100% validados. Yo aplico los cambios en mi editor. **Primera tarea: DT-nueva-CRÍTICA-3 (cambio de contraseña en Mi Perfil no persiste). Empieza con diagnóstico del endpoint `POST /mi_perfil` en app.py, sin modificar nada todavía.**"

---

## 📞 Cómo continuar en un chat nuevo

Al iniciar un nuevo chat, pegar este archivo como contexto inicial y usar la instrucción sugerida de la sección 2️⃣9️⃣.

**Próxima tarea (orden actualizado el 31 Oct):**
1. **DT-nueva-CRÍTICA-3** — cambio de contraseña en Mi Perfil (~30-45 min).
2. Resto de las 7 DT del smoke test (Fase D, ~8-10 h en total).
3. Fase E — tenant virgen (~2 h).
4. Fase G — Dockerización (~22-32 h).

## ✅ Última validación

- **Último commit:** `52696be` (cierre Feature Baja de Inventario + fix FK diferida), precedido por `ba48503`.
- **Última sesión:** 31 Oct 2026 — Feature Baja de Inventario COMPLETADA (100%) + smoke test de tenants nuevos (16 puntos OK en básico y premium).
- **Working tree:** verificar con `git status` (se asume clean tras el push).
- **Servidor:** detenido.
- **Sistema:** funcional end-to-end; 3 DT críticas abiertas (ver sección 2️⃣7️⃣).
- **Módulos:** 11/11 completados.
- **Demo:** ~9.972 filas. idioma = pap en tenant_27.
- **Seguridad:** Producción-ready (CSRF con tokens firmados) — pendientes CRÍTICA-1 y CRÍTICA-3.
- **Observabilidad:** Producción-ready (logger con rotación).
- **i18n:** 3 idiomas (es/en/pap). PDF reportes: 100%. HTML reportes: 100%. Baja de Inventario: 100%. Diccionarios Python pendientes (DT-nueva-media-baja).
- **DT-37:** ✅ F0-F5 COMPLETADAS (100%).
- **Feature Toppings:** ✅ COMPLETADA (100%).
- **Feature Anulación POS:** ✅ COMPLETADA (100%).
- **Feature Baja de Inventario:** ✅ COMPLETADA (100%).
- **Resueltas:** DT-19, DT-25, DT-28, DT-29, DT-42, DT-43, DT-45, DT-46, DT-47, DT-5-bis, DT-5-quinquies, DT-5-quater-bis, DT-37 F0-F5, Feature Toppings, Feature Anulación POS, Feature Baja de Inventario, Fix FK diferida en `crear_tenant_saas()`.

**Pendientes principales:**
- 7 DT del smoke test (Fase D): ~8-10 h.
- Pre-Dockerización restante (Fases A-C, E, F): ~10 h.
- i18n diccionarios Python: ~2-4 h (baja).
- Dockerización (Fase G): ~22-32 h.

---

Fin del HANDOFF.md — v9.5