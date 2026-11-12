# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP) — v9.19

**Última actualización:** 12 de Noviembre, 2026
**Último commit:** `9b71016` (fix: Fase E — HistorialInventario producto + Fase E cerrada)
**HANDOFF anterior:** `HANDOFF_v9.5.md` (histórico congelado, ver raíz del proyecto)
**Bitácoras históricas:** `bitacora/2026-10-sesiones.md`, `bitacora/2026-11-sesiones.md`
**Tenants de prueba:** `bitacora/tenants_prueba.md` (incluye `tenant_31` y `tenant_34`)

**Sesión 12 Nov:** Fases A + B + C (auditorías de alineación ORM ↔ BD ↔ modelo) 100% cerradas. DT-Fase C-1 (`total_anulaciones` faltaba en DDL de `crear_tenant_saas()`) resuelta y validada empíricamente con `tenant_34`. Commit `1ef3579`. Detalle en `bitacora/2026-11-sesiones.md`.
**Sesión 12 Nov:** Fases A + B + C (auditorías de alineación ORM ↔ BD ↔ modelo) 100% cerradas. DT-Fase C-1 (`total_anulaciones` faltaba en DDL de `crear_tenant_saas()`) resuelta y validada empíricamente con `tenant_34`. Commit `1ef3579`. Detalle en `bitacora/2026-11-sesiones.md`.
**Sesión 12 Nov (tarde):** Fase E cerrada (`tenant_34` smoke test completo: login → POS → venta → anulación → producción → reportes → PDFs). Bug A no reproducido. Bug `HistorialInventario` de producto fixeado (`9b71016`). 6 DTs nuevas de Fase E. Detalle en `bitacora/2026-11-sesiones.md`.
**Sesión 11 Nov (noche):** ...
**Sesión 11 Nov (noche):** CRÍTICA-2 (`d32a7f3`) + MEDIA-F2.5 (`e50f992`) cerradas. Fase D 100% cerrada.
**Sesión 11 Nov (tarde/noche):** MEDIA-BAJA (cierre jornada) + limpieza JS huérfano. Commit `7ce0156`.
**Sesión 11 Nov (mañana):** DT-nueva-MEDIA (desconciliación + ANULADO + whitelist) 100% + DT-nueva-BAJA (endpoint huérfano). 6 commits: `6b5485f`, `17d0b83`, `5368b1a`, `a403c90`, `b0efa27`, `29a4e03`.
**Sesión 8 Nov (tarde):** DT-nueva-MEDIA-F2.6 reformulada a BAJA (falso positivo: werkzeug no ensucia `panaderia.log`). Código limpio, solo docs.
**Sesión 8 Nov:** F3 logging — hash de contraseña truncado. Commit `53fc3f3`. DT-nueva-MEDIA-logging-ruido cerrada al 100% (F1+F1.5+F2+F3).
**Sesión 7 Nov:** DT-nueva-MEDIA-logging-ruido (F1: `buscar_producto` + F1.5: `consultas_filtradas.py`). Commits `51000fc` + `68f8856`.
**Sesión 6 Nov:** Commit 2 COMPLETO — rediseño "menos es más" + filtro `?producto=` en `/reporte/ventas` + i18n en/pap. 5 commits: `320881b` (B1+B2+H1+H2.1), `5d8e2b4` (H2.2), `b6a1908` (H2.3+H4), `e3b48e0` (H3), `7ff556f` (i18n). Working tree clean. Cero DT del Commit 2.
**Sesión 5 Nov:** Fix CRÍTICA-4 (colisión IDs int/ext en Productos Populares) + Bug B (rotación <7d → "—") + IA KeyError. Commit `6e7dbbf`. Tenant_31 conservado como tenant de pruebas.
**Sesión 4 Nov:** Fix MEDIA-BAJA (Ventas del Día no distingue donaciones). Badge + tooltip + guard de rol. Commit `607ac75`.
**Sesión 3 Nov:** Fix MEDIA-ALTA (donaciones en "Ingresos") + auditoría completa de cadena financiera (15 fixes) + fix `fecha_fin` a medianoche. Commit `8304a16`.
**Sesión 1 Nov (noche):** Fix CRÍTICA-1 (depósitos CONCILIADOS editables) — backend 403 + frontend solo-lectura + smoke test 7/7. Commit `5d289fd`.
**Sesión 1 Nov (mañana):** Fix de raíz `current_user` detached (`db.session.merge()` en `load_user`) + test de regresión 6/6 + commit `6173cfe`.
**Sesión 31 Oct:** Feature Baja de Inventario + fix FK diferida en `crear_tenant_saas()` + smoke test tenants nuevos (commits `ba48503` + `52696be`).

> Este archivo es **contexto actual** (liviano). Detalle de sesiones, tablas de DT resueltas y registros de features: `bitacora/`. Todo lo anterior al 1 Nov, completo: `HANDOFF_v9.5.md`.

---

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp) — **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.9.4 — **11/11 módulos completos (100%)** + i18n PDF/HTML 100% + Features Toppings, Anulación POS, Baja de Inventario y Commit 2 (rediseño Productos Populares) 100%.
- **Arquitectura:** Multi-tenant con PostgreSQL (un schema por tenant).
- **Seguridad:** Producción-ready (CSRF con tokens firmados + Origin/Referer). ✅ CRÍTICA-1 resuelta. ✅ CRÍTICA-2 resuelta (`d32a7f3`).
- **Observabilidad:** logger con rotación + `LOG_LEVEL` configurable vía `.env`. ✅ DT-nueva-MEDIA-logging-ruido cerrada al 100% (4 fases).
- **i18n:** es/en/pap operativos. Diccionarios Python pendientes (deuda baja).
- **Fases pre-Docker:** ✅ Fases A + B + C cerradas (12 Nov). ✅ Fase D cerrada (11 Nov noche). Próximo: **Fase E** (tenant virgen).

### 📋 Próximos pasos

1. **Fase F — Documentación + limpieza** (~8-12 h). 6 DTs nuevas de Fase E (E-1, E-2, E-4 MEDIA, E-5, E-6, + `docs/ESTRUCTURA_TENANT.md`) + 15 DTs de Fase C/B + limpieza legacy (`sucursales`, `seed_demo_history`, columnas legacy en `tenant_1`). No bloquea Docker.
2. **Fase G — Dockerización** (~22-32 h).
3. (Opcional/baja) **i18n de diccionarios Python** (~2-4 h).

**Fases completadas:** A+B+C+D (11-12 Nov) + **E (12 Nov, tarde)**. Bug `HistorialInventario` de producto fixeado (`9b71016`). Bug A del 5 Nov cerrado como "no reproducido". **Fase E 100%.**

### 📌 Estructura del HANDOFF (v9.6+)

- `HANDOFF.md` — **contexto actual** (se reescribe por sesión, ~400-500 líneas).
- `HANDOFF_v9.5.md` — **histórico congelado** (consulta para Dockerización o dudas históricas).
- `bitacora/2026-10-sesiones.md` — bitácora octubre (append-only).
- `bitacora/2026-11-sesiones.md` — bitácora noviembre (append-only).
- `bitacora/tenants_prueba.md` — tenants de prueba (append-only, sin contraseñas).

**Regla:** cada sesión agrega su bitácora al final de `bitacora/YYYY-MM-sesiones.md` y actualiza `HANDOFF.md` (solo el estado, no el histórico).

---

## 2️⃣ Stack y estructura

- **Backend:** Python 3.10+, Flask 3.1.2, SQLAlchemy 2.0, PostgreSQL 17.10 (puerto **5433**), Flask-Login, Flask-WTF, Werkzeug, ReportLab, Matplotlib, **Flask-Babel 4.0.0** + **Babel 2.18.0**, logging con `RotatingFileHandler`.
- **BD:** `panaderia_master` — credenciales en `.env` (la contraseña local de postgres está en `HANDOFF_v9.5.md`; ⚠️ no copiarla a documentos públicos).
- **Frontend:** HTML5/CSS3, JS vanilla, Bootstrap 5.1.3, Chart.js, Font Awesome 6.

**Archivos clave**
- `app.py` (~13.500 líneas), `models.py` (~3.250), `reportes.py` (~3.600), `seed_demo.py` + `seeds/`.
- Multi-tenant: `middleware_saas.py`, `tenant_decorators.py`, `tenant_context.py`, `security_utils.py`.
- `migrations/sql/` — scripts SQL versionados (toppings, anulación ventas, total_anulaciones, idioma, `bajas_inventario`, depositos_auditoria).
- `babel.cfg` (`[jinja2: **.html]`), `locales/{es,en,pap}/LC_MESSAGES/messages.{po,mo}` (los `.mo` se commitean).
- `templates/` (~56 + `_csrf_head.html` + `secciones/` con 4 parciales), `static/js/csrf-auto-inject.js`, `logs/` (ignorado por git).
- `.env` (protegido), `.env.example`, `requirements.txt`.
- Utilidades: `_limpiar_fuzzy.py` (CRÍTICO), `_ver_untraducciones.py` (bug conocido), `_audit_schema.py`, `_test_jinja.py` (usar solo nombre de archivo, no ruta), `_test_mo.py`, `_test_descuento.py`.

---

## 3️⃣ Tenants

| ID | Nombre | Subdominio | Plan | Licencia | Estado | Notas |
|----|--------|-----------|------|----------|--------|-------|
| 1 | Panadería Principal | principal | basico | local | Producción | Plantilla multi-tenant. `base_datos=tenant_1` (saneado `d32a7f3`). |
| 27 | **Panadería Demo** | panadería_demo | premium | nube_premium | Producción | Demo comercial, `demo2026`. `base_datos=tenant_27` (saneado `d32a7f3`). |
| 31 | **Diagnóstico Productos Populares** | diagnóstico_producto | basico | nube_basica | **Pruebas** | **Tenant de pruebas** (diagnóstico 5 Nov). Usuario `admin_31`. Sin acceso a reportes premium. Detalle en `bitacora/tenants_prueba.md`. |
| 34 | **Test Fase C Fix** | test_fase_c_fix | basico | nube_basica | **Pruebas** | **Tenant virgen** (12 Nov), creado con `crear_tenant_saas()` fixeado (42 tablas, 55 columnas). Usuario `admin_34`. Conservado para Fase E (smoke test completo). |

- **Producción real:** `tenant_1` + `tenant_27` (Demo, ~9.972 filas, `idioma = pap`).
- **Pruebas:** `tenant_31` (básico, ~10 filas, diagnóstico) + `tenant_34` (básico, virgen, Fase E).
- `public` tiene SOLO 3 tablas: `tenants` (sin columna `licencia`), `usuarios` (fallback `dev_master`), `configuracion_panaderia` (licencias/suscripciones/facturación, 27 columnas).
- `idioma` vive en `tenant_X.configuracion_sistema` (`VARCHAR(5) NOT NULL DEFAULT 'es'`; valores `es`, `en`, `pap`, `pt` futuro).
- `tenant_1.configuracion_sistema` tiene 6 filas con `panaderia_id` = 1, 5, 22, 24, 27, 28 (posible data legacy, no bloquea).

---

## 4️⃣ Usuarios

- **Roles:** `super_admin` (dev_master, todos los tenants), `admin_cliente` (total en su tenant), `supervisor` (producción, recetas, MP, proveedores, reportes), `cajero` (POS y cierre).
- **Usuarios:** tenant 1 → `dev_master`, `admin`, `admin_1`. Tenant 27 → `admin_27`, `super_27`, `cajero_27`. Tenant 31 → `admin_31`, `super_31`, `cajero_31`. Tenant 34 → `admin_34`, `super_34`, `cajero_34`.
- **Demo:** todos los usuarios del tenant_27 usan **`demo2026`**. `admin_27` tiene nombre `Administrador Panadería Demo` (sin espacio final).
- **Tenants de pruebas:** `admin_31` (pass en `bitacora/tenants_prueba.md`, rotada 5 Nov). `admin_34` (pass temporal generada al crear el tenant, rotar al primer login).
- **Creación:** NO desde el frontend; al alta del tenant en `crear_tenant_saas()`. Viven en `tenant_X.usuarios`.
- **Contraseñas:** `/mi_perfil` (✅ arreglado el 1 Nov) y `POST /resetear_password/<id>` (app.py:~11981; desde `gestion_clientes.html` y `gestion_usuarios.html`).
- **Facturación por tenant:** `/configuracion/facturacion` → `ConfiguracionSistema` (fallback `ConfiguracionPanaderia`).

---

## 5️⃣ Módulos (11/11)

| # | Módulo | Estado |
|---|--------|--------|
| 1 | Punto de Venta | ✅ (anulación + baja de inventario + donación con guard de rol) |
| 2 | Producción Diaria | ✅ (toppings) |
| 3 | Productos Externos | ✅ |
| 4 | Recetas y Fórmulas | ✅ (toppings) |
| 5 | Materias Primas | ✅ |
| 6 | Proveedores | ✅ |
| 7 | Gestión de Clientes (solo dev_master) | ✅ |
| 8 | Activos Fijos | ✅ |
| 9 | Gestión de Usuarios + Mi Perfil | ✅ |
| 10 | Gestión Financiera | ✅ (CRÍTICA-1 resuelta + desconciliación + ANULADO + auditoría) |
| 11 | Reportes Profesionales | ✅ (i18n PDF y HTML 100% + donaciones separadas + rotación <7d + rediseño Productos Populares) |

**Features recientes (detalle en bitácoras)**
- Toppings: `9e645ba` — tabla `receta_toppings`, costos por gramos/lote, descuento de stock, `/api/calcular_ingredientes`.
- Anulación POS: `4ecfde9` — soft-delete `Venta.estado`, `/ventas_del_dia`, `POST /anular_venta/<id>`, blindaje de 11 consultas.
- Baja de Inventario: `ba48503` + `52696be` — `bajas_inventario` (motivo `VENCIMIENTO`/`ROTURA`), `/baja_inventario`, `/api/productos_vitrina`, `POST /registrar_baja`, costo desde receta; integrado en Estado de Resultados, Análisis de Gastos y Cierre de Caja.
- **Fix CRÍTICA-1 (1 Nov):** `5d289fd` — depósitos CONCILIADOS inmutables (backend 403 + frontend solo-lectura).
- **Fix MEDIA-ALTA (3 Nov):** `8304a16` — auditoría completa de donaciones/anuladas en cadena financiera (15 fixes) + fix `fecha_fin` a medianoche.
- **Fix MEDIA-BAJA (4 Nov):** `607ac75` — Ventas del Día distingue donaciones (badge, tooltip, guard de rol).
- **Fix CRÍTICA-4 + Bug B + IA (5 Nov):** `6e7dbbf` — colisión IDs int/ext en Productos Populares + rotación <7d → "—" + KeyError en `_generar_recomendaciones_ia`.
- **Commit 2 — rediseño Productos Populares (6 Nov):** 5 commits (`320881b`, `5d8e2b4`, `b6a1908`, `e3b48e0`, `7ff556f`).
- **Depósitos bancarios (11 Nov):** 4 commits (`6b5485f`, `17d0b83`, `5368b1a`, `a403c90`) — whitelist, auditoría, anulación, desconciliación.
- **Cierre jornada + JS huérfano (11 Nov):** `7ce0156` — código muerto eliminado + filtro `es_donacion` en `obtener_ventas_dia` vivo + early-return en polling JS.
- **CRÍTICA-2 + F2.5 (11 Nov noche):** `d32a7f3` + `e50f992` — `base_datos` saneado + `LOG_LEVEL` configurable.
- **Fase A+B+C (12 Nov):** `1ef3579` — DT-Fase C-1 resuelta (`total_anulaciones` en DDL de `cierres_diarios`). Fases A+B+C cerradas. `tenant_34` conservado para Fase E.

- **Fase E + fix HistorialInventario (12 Nov):** `9b71016` — `OrdenProduccion.completar_produccion()` ahora registra movimiento de producto terminado en `HistorialInventario` (`producto_id`, `cantidad_anterior`, `cantidad_nueva`, `cantidad_utilizada`). Patrón copiado de `anular_venta()`. Validado con `tenant_34`.

---

## 6️⃣ Últimos commits

```text
1ef3579 fix(fase-c): agregar total_anulaciones al DDL de cierres_diarios
a85e8d1 docs(handoff): actualizar roadmap a producción (Fases A/B/C antes de Docker)
02ed322 docs: HANDOFF v9.16 + bitácora sesión 11 Nov (noche) — Fase D cerrada
29a4e03 fix(reportes): corregir cierre de etiqueta <a> en boton Ver Reporte
b0efa27 refactor(reportes): renombrar reporte_ventas a reporte_ventas_periodo
a403c90 feat(depositos): desconciliacion con auditoria y control de rol
5368b1a feat(depositos): anulacion con motivo, auditoria visual y fix de totales
17d0b83 feat(depositos): auditoria de usuario_id en crear/editar/conciliar
6b5485f fix(depositos): whitelist de estados + auditoría (4 columnas nuevas)
7fd0cbd docs(handoff): F2.6 reformulada a BAJA — falso positivo (werkzeug no ensucia panaderia.log)
c36bbca docs: HANDOFF v9.13 + bitacora sesion 8 Nov (F3 logging cerrada)
53fc3f3 fix(logging): F3/3 — truncar hash de contrasena en logs (seguridad)
7ff556f chore(i18n): traducir cadenas del rediseno productos_populares + deuda previa
e3b48e0 feat(reportes): H3 — 4 KPI cards unificadas + elimina card de Salidas No Comerciales
b6a1908 feat(reportes): rediseno graficos — elimina Top 5 + Distribucion 30% + Rotacion 70%
5d8e2b4 feat(reportes): rediseno Top 10 — tabla unica + boton Ver detalle + badges medalla
320881b feat(reportes): recomendaciones dinamicas + filtro por producto + banner
6e7dbbf fix(reportes): CRÍTICA-4 colisión IDs int/ext + rotación <7d a '—' + IA KeyError
f694ae5 docs: HANDOFF v9.9 + bitácora sesión 4 Nov (MEDIA-BAJA + regla doble servidor)
607ac75 feat(ventas-del-dia): distinguir donaciones con badge, tooltip y guard de rol
8304a16 fix(reportes): auditoría completa de donaciones/anuladas en cadena financiera
0da8b5b docs: reemplazar PENDIENTE_HASH por 5d289fd (hash real del commit CRITICA-1)
5d289fd fix(CRITICA-1): bloquear edición de depósitos CONCILIADOS (auditoría contable)
6173cfe fix: current_user detached — db.session.merge() en load_user (CRÍTICA-3 resuelta)
7️⃣ Deuda técnica PENDIENTE
✅ Cerradas el 12 Nov (Fases A + B + C)
Prioridad	DT	Descripción	Commit
✅ Alta	DT-Fase C-1	total_anulaciones faltaba en el DDL de cierres_diarios en crear_tenant_saas(). Se agregaba solo vía migrations/sql/. Fix: 1 línea en app.py:772. Validado con tenant_34.	1ef3579
✅ Cerradas el 11 Nov (noche)
Prioridad	DT	Descripción	Commits
✅ CRÍTICA	DT-nueva-CRÍTICA-2	base_datos huérfano en public.tenants saneado (tenant_{id}) + crear_tenant_saas() / middleware_saas.py alineados con el ID.	d32a7f3
✅ MEDIA	DT-nueva-MEDIA-F2.5	Nivel de logger configurable vía LOG_LEVEL en .env.	e50f992
✅ MEDIA-BAJA	DT-nueva-MEDIA-BAJA (cierre jornada)	Eliminado cerrar_jornada_actual() (código muerto) + fix de filtro es_donacion en obtener_ventas_dia vivo.	7ce0156
✅ BAJA	DT-nueva-BAJA (JS huérfano)	Polling a /api/cierre_diario/estado en pos-moderno.js sin botón en frontend → early-return agregado.	7ce0156
✅ MEDIA	DT-nueva-MEDIA (desconciliación)	Endpoint para desconciliar depósitos (CONCILIADO inmutable tras CRÍTICA-1).	a403c90
✅ MEDIA	DT-nueva-MEDIA (estado ANULADO sin flujo)	Modal permite setear estado='ANULADO' con endpoint dedicado y auditoría.	5368b1a
✅ MEDIA	DT-nueva-MEDIA (whitelist estado backend)	editar_deposito_bancario() valida estados contra whitelist.	6b5485f
✅ BAJA	DT-nueva-BAJA (endpoint huérfano)	/reporte/ventas renombrado a reporte_ventas_periodo() + fix visual.	b0efa27, 29a4e03
✅ Cerradas el 8 Nov (DT logging ruidoso)
Prioridad	DT	Descripción	Commits
✅ Media	DT-nueva-MEDIA-logging-ruido	Logging ruidoso en producción (F1 + F1.5 + F2 + F3)	51000fc, 68f8856, 620a177, 53fc3f3
✅ Cerradas el 6 Nov (Commit 2)
Prioridad	DT	Descripción
✅ Media	Commit 2 (rediseño)	Rediseño "menos es más" + recomendaciones dinámicas en productos_populares.html
✅ Media	i18n cadenas nuevas	Strings de Commit 2 traducidos en en/pap
### 🟢 DTs BAJAS Fase F — Sesión objetivo: Fase F (post-Fase E, pre-Docker)

**Total: ~25 DTs BAJAS** (6 nuevas de Fase E + 15 de Fase B/C + 4 preexistentes del HANDOFF v9.14).
Prioridad	DT	Descripción	Estimación
### 🟡 DT MEDIA nueva (Fase E)

| Prioridad | DT | Descripción | Sesión objetivo |
|---|---|---|---|
| 🟡 MEDIA | DT-Fase E-4 | `_descontar_ingredientes()` registra MP en `HistorialInventario` con cantidades inconsistentes entre producciones similares (312.5g vs 31.25g vs 62.5g). Revisar cálculo. | Fase F |

### 🟢 DTs BAJAS Fase E

| Prioridad | DT | Descripción | Sesión objetivo |
|---|---|---|---|
| 🟢 BAJA | DT-Fase E-1 | `total_anulaciones` en `cierres_diarios` no validable hasta el job nocturno (sin `INSERT` hasta medianoche). Probar con `tenant_34` vivo post-medianoche. | Post-Fase E (con `tenant_34`). |
| 🟢 BAJA | DT-Fase E-2 | `tenant_34.configuracion_sistema` sin fila inicial. Fallback funciona. Agregar `INSERT` en `crear_tenant_saas()` o dejar lazy init. | Fase F |
| 🟢 BAJA | DT-Fase E-5 | `models.py:HistorialInventario.materia_prima_id = nullable=False` pero BD real es nullable. Inconsistencia modelo ↔ BD. | Fase F |
| 🟢 BAJA | DT-Fase E-6 | Mojibake en commit messages (CMD interpreta UTF-8 como CP1252). Usar `chcp 65001` o PowerShell. | Fase F (docs) |
| ✅ CERRADA | DT-Fase E-3 | `completar_produccion()` no registraba producto terminado en `HistorialInventario`. Fix `9b71016`. | ✅ |
🟡 Media	DT-Fase B-1	crear_tenant_saas() usa DDL raw (no db.create_all()). Riesgo: agregar modelo a models.py sin CREATE TABLE → tenant nuevo incompleto. Mitigación: test de verificación post-creación.	~2-3 h
🟢 BAJA	DT-Fase B-2	CREATE TABLE IF NOT EXISTS consecutivos_pos duplicado en 3 sitios (app.py:2640, 2868, 2943). Consolidar.	~15 min
🟢 BAJA	DT-Fase B-3	db.create_all() solo se usa en public, no en tenant_X. Patrón asimétrico.	~30 min
🟢 BAJA	DT-Fase B-4	crear_tenant_saas() no es atómico: si falla a mitad, schema huérfano (rollback SQLAlchemy revierte, pero no hay test).	~1 h
🟢 BAJA	DT-Fase C-2	7 columnas muertas en configuracion_produccion (activar_alertas, alerta_stock_minimo, dias_historial_ventas, inventario_seguridad, produccion_automatica, rotacion_recomendada, vida_util_pan_dias). Están en DDL, NO en models.py, NO en código. Quitar del DDL o implementar feature.	~30 min
🟢 BAJA	DT-Fase C-3	4 columnas muertas en configuracion_sistema (modo_mantenimiento, nombre_sistema, ultima_actualizacion, version). tenant_1 no las tiene. Quitar del DDL o migrar tenant_1.	~15 min
🟢 BAJA	DT-Fase C-4	pagos_individuales.usuario_id en DDL, no en models.py, no en tenant_1. Agregar al modelo o quitar del DDL.	~15 min
🟢 BAJA	DT-Fase C-5	panaderias.panaderia_id auto-referencia (DDL, no modelo). Revisar por qué existe.	~15 min
🟢 BAJA	DT-Fase C-6	Módulo multi-sucursal legacy (nunca implementado). sucursales.email, usuarios.sucursal_id. Eliminar del modelo + DDL.	~30 min
🟢 BAJA	DT-Fase C-7	5 columnas legacy en tenant_1 (cierres_diarios.created_at, .fecha, .jornada_id, historial_mantenimientos.activo_id, registros_diarios.tarjetas). Limpieza opcional.	~15 min
🟢 BAJA	DT-Fase C-8	seed_demo_history en tenant_27 (basura de seed_demo.py). Eliminar.	~5 min
🟢 BAJA	DT-unificar-naming	proveedor, detalle_venta en singular vs resto en plural. Cosmético.	~15 min
🟢 DTs BAJAS preexistentes (HANDOFF v9.14)
Prioridad	DT	Descripción	Estimación
🟢 BAJA	DT-nueva-BAJA-F2.6	Post-Docker: auditar que el WSGI no agregue basicConfig al root (werkzeug no ensucia panaderia.log hoy). Verificado 8 Nov.	~30 min
🟢 BAJA	DT-unificar-productos-populares	Unificar _obtener_datos_productos_populares (reportes.py:1904) con reporte_productos_populares (app.py:8371). Anotada 6 Nov.	~2-3 h
🟢 BAJA	DT-unificar-prefijos-int-ext	Unificar analizar_productos_periodo (models.py:1763, prefijos P/E) con inline de app.py:8408-8434 (prefijos int_/ext_). Anotada 6 Nov.	~1-2 h
🟢 BAJA	DT-formato-numerico-es-CO	Formato $20.000.00 (punto como separador de miles + punto decimal) incorrecto para es-CO (debería ser $20.000,00). Cosmético. Anotada 6 Nov.	~1 h
📋 Otras medias / bajas (heredadas, detalle en HANDOFF_v9.5.md sec. 9)
Medias: DT-37 F5-pulido · DT-37 F4.9 (libro_diario huérfano) · DT-NUEVA-1 (CREATE TABLE con idioma) · error 'ingreso' en generar_reporte_ia_predictivo (✅ cerrada 5 Nov) · endpoint huérfano /generar_reporte_flujo_caja · overlap de labels en pie chart · i18n de diccionarios Python · mapeo Jinja2 de badges dinámicos · bug de _ver_untraducciones.py.

Cosmética crítica: emojis rotos en PDFs de ReportLab (Helvetica sin glyphs).

Bajas: filas legacy en tenant_1.configuracion_sistema · imports redundantes de os en app.py · "Fluho Neto" → "Flusho Neto" (PAP) · cierre_diario.html y ruta /cierre_diario huérfanos · renombrar "Historial de Ventas" en reportes.html:229 · datos demo hardcodeados en ventas_periodo.html · traducciones PAP heredadas · tenant_1.historial_inventario sin FK en orden_produccion_id.

🔍 Hallazgos 5 Nov (diagnóstico con tenant_31)
✅ CRÍTICA-2 reproducida en vivo: tenant_31.base_datos = tenant_diagnóstico_producto vs schema real tenant_31. Resuelta 11 Nov noche (d32a7f3).

Bug A (nota, no CRÍTICA): En el primer día de vida del tenant, detalle_venta.producto_externo_id quedó NULL en 2 ventas con externos. Tras reiniciar servidor, las filas se "corrigieron". No reproducible. Hipótesis: caché/ORM en primer arranque. Verificar en Fase E con tenant_34.

Licencia básica: tenant_31 (nube_basica) NO tiene acceso a reportes premium (/reporte/analisis_predictivo, /reporte/recomendaciones_ia, /reporte/analisis_inventarios). Redirige a dashboard (302). Comportamiento esperado.

Reportes IA (2 distintos):

Análisis Predictivo (HTML): /reporte/analisis_predictivo → alertas + proyecciones + distribución + prioridades. "Exportar PDF" = window.print().

Recomendaciones con IA (PDF): /generar_reporte_ia_predictivo → GeneradorReportes.generar_reporte_ia_predictivo → _generar_recomendaciones_ia. Reporte separado, con secciones "RECOMENDACIONES INTELIGENTES" + "PLAN DE ACCIÓN".

Caché del navegador: screenshots desactualizados pueden confundir el diagnóstico. Regla: modo incógnito + reiniciar servidor + netstat (1 línea LISTENING) antes de cada test de template.

Mojibake en commit message: Windows usó cp1252 al escribir git commit -m. Recomendación: usar git commit -F _commit_msg.txt (UTF-8) en próximos commits.

8️⃣ Metodología de trabajo
Reglas de oro
Un paso a la vez con confirmación antes de continuar.

Diagnóstico ANTES de modificar. Soluciones de raíz, no parches.

TODO debe funcionar para futuros tenants.

Verificación con psql / findstr antes de avanzar. Commit después de cada fix verificado.

Backup (pg_dump) antes de cada cambio grande.

git status antes de commitear; git add <archivo> explícito; push tras el commit.

Detener el servidor antes de reiniciar. Verificar con tasklist | findstr python. netstat -ano | findstr :5000 → 1 sola línea LISTENING (nueva regla 5 Nov, refuerza regla 4 Nov de doble servidor).

Antes de testear templates, modo incógnito + servidor reiniciado (nueva regla 5 Nov, por caché del navegador).

Insertar bloques mostrando ANTES → DESPUÉS con número de línea exacto; compilar tras cada inserción (python -m py_compile app.py).

Deuda técnica detectada: anotarla (no tocarla), priorizar, decidir después.

Windows: findstr /c:"patrón" para búsquedas literales (con tildes/emoji puede fallar → usar powershell -Command "Select-String -Path ..." o script Python). Preferir scripts Python al copy-paste del chat (mojibake).

git commit -F _commit_msg.txt (UTF-8) para mensajes con tildes/emojis (nueva regla 5 Nov).

No acumular DT. Cuando el diagnóstico o el smoke test de un fix descubre un problema nuevo, se evalúa si está dentro del alcance del fix actual (mismo concern, mismo módulo). Si lo está, se resuelve en el mismo commit. Si es un concern distinto, se anota como DT nueva con prioridad y sesión objetivo en el HANDOFF, para que no quede en el aire.

Cero DT "en el aire". Toda DT nueva debe tener: prioridad (🚨/🟡/🟢), estimación (~X h), y sesión objetivo (próxima sesión, Fase D, Fase F, post-Docker). Si no se puede asignar una sesión objetivo, no es una DT: es una nota o un pendiente informal (que va a la bitácora, no al HANDOFF).

Un script de auditoría que devuelve ❌ uniforme en todas las filas tiene un bug de matching, no un hallazgo. Verificar el "diagnóstico del script" (cuántos bloques extrajo) antes de interpretar la tabla de resultados. (Regla nueva 12 Nov.)

Nunca poner comentarios ni texto decorativo dentro de un string text(f'''...'''). El SQL se ejecuta tal cual. Comentarios de Python (#) solo fuera del string. Nunca poner ← NUEVA LÍNEA, # TODO, etc. dentro del bloque SQL. (Regla nueva 12 Nov.)

Nunca pegar contraseñas reales en el chat del instructor. Enmascararlas (ShQ****) o borrarlas. Aplica a contraseñas de tenants, demo2026, admin_31, etc. (Regla nueva 12 Nov.)

i18n / Babel
Flask-Babel 4.0: default_translation_directories va en el constructor Babel(app, ...).

pybabel extract con lista explícita (con . escanea venv/). babel.cfg: [jinja2: **.html].

pybabel NO extrae _() dentro de f-strings ni después de emoji en f-string.

pybabel update marca #, fuzzy → SIEMPRE correr _limpiar_fuzzy.py. Los .mo se commitean.

El % NUNCA va dentro de _(). % sueltos en msgstr → escribir %% en msgid y msgstr.

Templates: proteger <style>/<script> antes de reemplazos masivos.

Reiniciar servidor + modo incógnito tras pybabel compile.

config.nombre_panaderia ya está global en templates.

Modelos, schema y multi-tenant
ORM ↔ BD DEBEN estar alineados: al agregar columna al modelo, verificar con information_schema.columns.

tenant_1 (plantilla), tenant_27 (demo) y tenant_31/tenant_34 (pruebas) DEBEN tener la misma estructura; toda migración se aplica a todos.

FK diferida: si una tabla referencia a otra creada DESPUÉS en crear_tenant_saas(), NO poner la FK en el CREATE TABLE; agregarla al final con ALTER TABLE ... ADD CONSTRAINT ... FOREIGN KEY.

Todo cambio de schema se prueba con un tenant nuevo (básico y premium, 16 puntos). tenant_31 y tenant_34 sirven como tenants de pruebas.

search_path DEBE estar seteado antes de consultar modelos fuera de request.

producto_id puede ser NULL en historial_inventario. _descontar_ingredientes() DEBE registrar en HistorialInventario.

FKs ambiguas en SQLAlchemy: declarar foreign_keys='Tabla.columna' en el relationship.

load_user() debe devolver un objeto ATTACHED (db.session.merge(user)).

Antes de cambiar un patrón global, auditar con grep quién lo toca y correr un test de regresión.

Colisión de IDs int/ext: cuando dos tablas (productos, productos_externos) tienen su propio id autoincremental, los id colisionan (ej. Pan Prueba id=1 y Agua id=1). Usar prefijos (int_, ext_) al armar claves de diccionarios. (Regla 5 Nov.)

Diagnóstico pre-commit: si git diff --stat muestra más líneas de las esperadas, verificar el diff completo antes de commitear. (Regla 6 Nov.)

crear_tenant_saas() usa DDL raw, no db.create_all(). Cualquier columna nueva en models.py DEBE agregarse también al CREATE TABLE correspondiente en app.py:~22-828. Verificar con tenant_XX de prueba. (Regla 12 Nov.)

Dinero, ventas y bajas
Soft-delete siempre: las ventas nunca se borran (COMPLETADA / ANULADA).

Toda consulta de Venta para reportes/dinero DEBE filtrar Venta.estado == 'COMPLETADA'; las donaciones (es_donacion=TRUE) se excluyen de ingresos.

Queries de reportes con fecha_fin: usar fecha_fin_inclusive = fecha_fin + timedelta(days=1) y Venta.fecha_hora < fecha_fin_inclusive. Alternativamente, db.func.date(Venta.fecha_hora) <= fecha_fin.

No se anula una venta si el día ya tiene CierreDiario confirmado. Las facturas ELECTRONICA NUNCA se anulan en el POS.

Donaciones: solo admin_cliente o super_admin pueden anularlas (backend 403 si no). El cajero puede registrarlas pero no anularlas.

Toppings: siempre en gramos; factor_escala = cantidad_producir / unidades_obtenidas.

Al agregar una nueva fuente de pérdidas/gastos (como bajas), actualizar estado_resultados y analisis_gastos en el MISMO commit.

Verificar los print y strings de JS en templates: el mojibake puede romper el JS.

Depósitos bancarios: CONCILIADO es inmutable (CRÍTICA-1, 5d289fd). Editar un depósito conciliado → 403.

Rotación <7 días: si el tenant tiene menos de 7 días de vida, rotacion_promedio = None (template muestra —). Criterio: dias_reales_tenant desde la primera venta del tenant. (Regla 5 Nov.)

Filtro ?producto= en /reporte/ventas: aplica a ventas_periodo (Python) y a detalles_periodo + donaciones_periodo (SQLAlchemy .has()). Compara nombre exacto. (Regla 6 Nov.)

Comandos útiles
cmd
chcp 65001
psql -U postgres -p 5433 -h localhost -d panaderia_master
python -m py_compile app.py
python -m py_compile reportes.py
python app.py
findstr /n /c:"patrón exacto" archivo.py
powershell -Command "Select-String -Path archivo.py -Pattern 'patrón con tildes'"
git commit -F _commit_msg.txt && del _commit_msg.txt
pg_dump -U postgres -p 5433 -h localhost -d panaderia_master -F c -f backup_pre_XXX.backup

:: Verificar procesos Python corriendo (regla 4 Nov + 5 Nov)
tasklist | findstr python
netstat -ano | findstr :5000

:: Pipeline i18n
pybabel extract -F babel.cfg -o locales/messages.pot app.py models.py reportes.py templates
pybabel update -i locales/messages.pot -d locales
python _limpiar_fuzzy.py
pybabel compile -d locales --statistics

:: Estructura / constraints de una tabla
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_schema = 'tenant_27' AND table_name = 'historial_inventario' ORDER BY ordinal_position;"

:: Diagnóstico
python _audit_schema.py
python _test_jinja.py ventas_del_dia.html   ← SOLO nombre, NO ruta
python _test_mo.py
python _ver_untraducciones.py
9️⃣ Plan pre-Dockerización (Fases A-G)
Objetivo: que models.py ↔ app.py ↔ BD estén sincronizados y que un tenant nuevo nazca 100% funcional. Prioridad CRÍTICA: no dockerizar sin completar A-F.

Fase	Alcance	Estimación	Estado
A — Auditoría de modelos	Mapear modelos, detectar huérfanos, FKs mal definidas, documentar estructura canónica	~2 h	✅ 12 Nov
B — Auditoría de app.py	Queries a tablas/columnas inexistentes, crear_tenant_saas() crea todo y en orden correcto	~2 h	✅ 12 Nov
C — Auditoría de BD	information_schema en tenant_1 vs tenant_27, modelos vs BD real, tablas huérfanas	~2 h	✅ 12 Nov (DT-Fase C-1 resuelta)
D — Sincronización + DT abiertas	Script SQL para alinear tenants, crear_tenant_saas(), models.py, migraciones; resolver DTs	~8-10 h	✅ 11 Nov noche
E — Tenant virgen	Usar tenant_34, flujo login → POS → venta → cierre → reporte, verificar Bug A.	~2 h	🟡 Próxima
F — Documentación y limpieza	docs/ESTRUCTURA_TENANT.md, eliminar código huérfano, actualizar HANDOFF, 12 DTs BAJAS	~6-8 h	⏸️ Pendiente
G — Dockerización	requirements.txt completo, .mo commiteados, .env.example con todas las variables, Dockerfile + docker-compose.yml con PostgreSQL	~22-32 h	⏸️ Pendiente
Riesgos: tablas creadas "al vuelo" en app.py sin estar en models.py (mitigado por Fase B: 42/42 alineados hoy); tenants antiguos con estructura distinta a un tenant nuevo (mitigado por Fase C: tenant_34 creado con DDL actual); código huérfano; dependencias ocultas entre tablas.

Listo para Docker: ✅ CSRF con SECRET_KEY portable · ✅ logs a archivo + consola con rotación · ✅ sin dependencias de red específicas · ✅ i18n portable (.mo en el repo) · ✅ crear_tenant_saas() sin errores de FK · ✅ CRÍTICA-1 resuelta · ✅ cadena financiera auditada (donaciones/anuladas) · ✅ Ventas del Día con guard de rol para donaciones · ✅ CRÍTICA-4 resuelta · ✅ Bug B (rotación) resuelto · ✅ IA KeyError resuelto · ✅ Commit 2 (rediseño Productos Populares) resuelto · ✅ i18n cadenas nuevas resuelto · ✅ Fases A+B+C+D cerradas · ✅ DT-Fase C-1 resuelta · 🟡 Fase E pendiente · 🟡 Fase F pendiente · 🟡 Dockerfile/compose por crear.

🔟 Notas estratégicas
Objetivo: ERP SaaS multi-tenant multi-país: POS, inventario, producción, recetas (toppings), activos fijos, reportes con IA, finanzas, i18n (es/en/pap), anulación de ventas, bajas de inventario, donaciones con auditoría; base para API REST + IA avanzada.

Mercado: 3.000-5.000 panaderías en Colombia · 10.000-30.000 en LATAM · Curazao-Antillas Holandesas (Papiamentu). Precio $60k-$600k COP/mes.

Licencias: Premium 3 usuarios · Básica 1 usuario.

Demo: fases 1-12 completas (~9.972 filas), contraseña demo2026, idioma = pap.

## 1️⃣1️⃣ Estado actual (resumen ejecutivo)

| Aspecto | Estado |
|---|---|
| Último commit | `9b71016` en `origin/main` (pusheado) |
| Módulos | 11/11 completos (100%) |
| Fase A (auditoría modelos) | ✅ 12 Nov — 43 modelos ↔ 42 tablas + `public.tenants`, cero huérfanos |
| Fase B (auditoría `app.py`) | ✅ 12 Nov — 229 queries raw clasificadas, 0 huérfanas. DDL 42/42 ↔ modelos |
| Fase C (auditoría BD) | ✅ 12 Nov — DT-Fase C-1 resuelta + 12 DTs BAJAS anotadas |
| **Fase E (tenant virgen)** | ✅ **12 Nov (tarde)** — `tenant_34` smoke test completo |
| Fix DT-Fase C-1 (`total_anulaciones`) | ✅ `1ef3579` — validado con `tenant_34` |
| **Fix DT-Fase E-3 (`HistorialInventario` producto)** | ✅ **`9b71016`** — validado con `tenant_34` (producción 5 und → `cantidad_anterior=10`, `cantidad_nueva=15`) |
| **Bug A (`producto_externo_id` NULL)** | ✅ **NO reproducido** en `tenant_34` (cierra nota del 5 Nov) |
| **Bug B (rotación <7d → "—")** | ✅ Validado en `tenant_34` |
| **Anulación POS** | ✅ Validado end-to-end (venta → anulada → stock revertido → reporte excluye) |
| Demo | ✅ `admin_27` / `demo2026` |
| Tenants productivos | `tenant_1` + `tenant_27` |
| Tenants de pruebas | `tenant_31` (diagnóstico) + `tenant_34` (virgen, Fase E) |
| DT críticas abiertas | **0** |
| DT medias abiertas | **2:** DT-Fase B-1 (DDL raw vs `db.create_all()`) + DT-Fase E-4 (MP cantidades inconsistentes) |
| DT bajas abiertas | **~25:** 5 Fase E nuevas (E-1, E-2, E-5, E-6 + `docs/ESTRUCTURA_TENANT.md`) + 15 Fase B/C + 4 preexistentes |
| Siguiente tarea | **Fase F — docs + limpieza** (~8-12 h) |
| Fase actual | **Fase F** (A-E cerradas) |
| Dockerización | Fase G, ~22-32 h (post Fase F) |
| Working tree | limpio (post commit docs) |


📞 Cómo continuar en un chat nuevo
Pegar este archivo como contexto inicial con esta instrucción:

"Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el HANDOFF.md v9.18 con el contexto actual (el histórico está en HANDOFF_v9.5.md, bitácoras en bitacora/, tenants de prueba en bitacora/tenants_prueba.md). Por favor actúa como instructor guiando paso a paso, con la metodología del HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/PowerShell Select-String, commit tras cada fix verificado. Al insertar bloques, muéstrame ANTES → DESPUÉS con número de línea exacto. Tú me das LUZ VERDE cuando los cambios estén 100% validados. Yo aplico los cambios en mi editor. Primera tarea: Fase E (tenant virgen) usando tenant_34. Smoke test completo: login → POS → venta → cierre → reporte → PDF. Verificar Bug A (producto_externo_id NULL en primer día del tenant). Empieza con diagnóstico del estado actual de tenant_34."

Orden sugerido post-Fase E: Fase F (12 DTs BAJAS + docs/ESTRUCTURA_TENANT.md) → Fase G (Dockerización).

1️⃣2️⃣ Roadmap a Producción (Nota personal de Mauricio)
Objetivo: lanzar PanaderíaPro a producción en enero 2027 (inicio de mes).
Modalidad: trabajo solo, part-time (~10-15 h/semana).
Ventana: 8 semanas (5 Nov 2026 → 1 Ene 2027), ~80-120 h disponibles.

Estado actual (12 Nov 2026)
Aspecto	% Listo
Funcionalidad (features)	~92%
Producción-ready (infra)	~30% (Fases A+B+C cerradas, sube de 25%)
Deuda técnica	✅ 0 DTs críticas, 0 medias (excepto DT-Fase B-1 estructural), 15 BAJAS cosméticas
Bloqueantes críticos	5 (bajó de 6)
Estimación total	~36-52 h (4-6 jornadas de 8 h)
Cronograma propuesto (8 semanas part-time)
Semana	Foco	Estimación	Entregable
1 (5-11 Nov)	✅ CERRADA: Commit 2 + DTs de Fase D (CRÍTICA-2 + F2.5 + cierre jornada + JS huérfano)	~12-14 h	Fase D 100% terminada.
2 (12-18 Nov)	✅ CERRADA: Fases A + B + C (auditorías ORM ↔ BD ↔ modelo)	~6 h	DT-Fase C-1 resuelta (1ef3579). 12 DTs BAJAS anotadas. tenant_34 creado.
3 (19-25 Nov)	Fase E (tenant virgen) + verificar Bug A	~2 h	Smoke test completo en tenant_34 (login → POS → venta → cierre → reporte → PDF) OK.
4 (26-2 Dic)	Fase F (12 DTs BAJAS + docs/ESTRUCTURA_TENANT.md + limpieza)	~6-8 h	docs/ESTRUCTURA_TENANT.md completo, código huérfano eliminado, DDL limpiado.
5 (3-9 Dic)	Fase G: Dockerfile + docker-compose.yml + .env.example completo	~8-12 h	Stack dockerizado local (Flask + PostgreSQL + Nginx).
6 (10-16 Dic)	Fase G: WSGI production (gunicorn/waitress) + SSL + Nginx reverse proxy	~6-8 h	Deploy reproducible en VPS local.
7 (17-23 Dic)	Fase G: Backup automático + logging a stdout + /health + monitoreo básico	~6-8 h	Observabilidad mínima operativa.
8 (24-30 Dic)	Fase G: Deploy a VPS real + hardening + documentación + smoke test producción	~8-10 h	Producción lista (o casi).
31 Dic - 1 Ene	Buffer (imprevistos) + capacitación usuarios	~4-6 h	Lanzamiento.
Total estimado: ~52-72 h + buffer. Realista con tu plan.

Prioridades (si algo se atrasa)
P0 (sin esto no hay producción):

✅ Fases A + B + C (auditorías ORM ↔ BD). Cerradas 12 Nov.

Fase E (tenant virgen + Bug A).

Docker + WSGI + SSL.

Backup automático.

/health endpoint.

Variables de entorno producción.

P1 (importante pero puede esperar 1-2 semanas post-lanzamiento):

CI/CD (GitHub Actions).

Monitoreo avanzado (Sentry, Prometheus).

Rate limiting.

Tests automatizados (pytest).

P2 (deseables, post-lanzamiento):

i18n de diccionarios Python.

API REST.

Dashboard de admin.

Rotación automática de contraseñas.

Riesgos identificados
✅ CRÍTICA-2 RESUELTA (11 Nov noche, d32a7f3). Schemas alineados, crear_tenant_saas()/middleware_saas() alineados, BD saneada.

✅ Fases A/B/C completadas (12 Nov). No se encontraron tablas huérfanas ni queries a columnas inexistentes. DT-Fase C-1 resuelta.

Bug A (caché producto_externo_id): verificar en Fase E con tenant_34. Si se reproduce, escalar a CRÍTICA-5 y fixear en el mismo commit (regla #13).

tenant_27 (demo) tiene datos inconsistentes por ser demo. Se resuelve en Fase F (o se migra a demo nueva).

Sin tests automatizados: la validación es manual (screenshots + PDFs). Post-lanzamiento, agregar pytest con 20-30 tests de humo.

Lógica <7 días en reportes: cada tenant nuevo va a ver — en rotación hasta los 7 días. Documentar en onboarding.

Decisiones pendientes (para antes del deploy)
Proveedor de VPS: Hetzner (€5/mes) vs DigitalOcean ($6/mes) vs AWS Lightsail ($5/mes). Recomendación: Hetzner CX22 (mejor relación precio/rendimiento en Europa) o DigitalOcean (más amigable, más datacenters).

Dominio: ¿ya tenés? (ej. panaderiapro.com). ¿Usarás subdominios por tenant (cliente1.panaderiapro.com)?

SSL: Let's Encrypt (gratis, auto-renovable).

Backup: pg_dump diario + retención 7 días + copia semanal a almacenamiento externo (S3, Backblaze).

tenant_27 (demo): ¿se migra a la nube o se crea una demo nueva con datos reales?

Precio final de licencias: Premium 
X
C
O
P
/
m
e
s
,
B
a
ˊ
s
i
c
a
XCOP/mes,B 
a
ˊ
 sicaY COP/mes.

Criterios de "listo para producción"
☑ Los 3 tenants productivos + tenants de prueba tienen schema correcto (tenant_{id}) + base_datos alineado. ✅ (11 Nov)

☑ Fases A/B/C completadas (auditorías ORM ↔ BD ↔ modelo). ✅ (12 Nov)

☐ Fase E OK (tenant virgen funcional end-to-end).

☐ docker-compose up levanta el stack local sin errores.

☐ HTTPS funciona con certificado válido.

☐ /health responde 200 OK.

☐ Backup automático corriendo (verificar restaurando 1 backup).

☐ Logs van a stdout + rotación.

☐ Smoke test de producción: login → POS → venta → cierre → reporte → PDF.

☐ dev_master + 2 tenants productivos creados.

☐ Documentación de deploy en docs/DEPLOY.md.

☐ Rollback plan documentado.

Notas personales
✅ Fase D cerrada el 11 Nov (noche). ✅ Fases A+B+C cerradas el 12 Nov. No dockerizar hasta completar Fase E.

✅ CRÍTICA-2 resuelta (era el mayor bloqueante transversal). ✅ DT-Fase C-1 resuelta.

Cada semana, actualizar este roadmap con lo hecho + lo pendiente.

Si algo se atrasa, priorizar P0 sobre P1 y P2.

El lanzamiento es "soft launch" (2-3 clientes beta) antes de marketing masivo.

🎯 Recomendación para no atrasarte
Semana 3 (Fase E): si Bug A se reproduce, fixealo en el mismo commit (regla #13). Si no se reproduce, anotalo como "no reproducido" y seguí. tenant_34 es el tenant ideal: virgen, 42 tablas, 55 columnas, admin funcional.

Semana 4 (Fase F): usala para las 15 DTs BAJAS + docs/ESTRUCTURA_TENANT.md. No metas código nuevo acá. Priorizá: DT-Fase B-1 (test de verificación de tenants) > unificar-productos-populares > el resto.

Semanas 5-8 (Docker): empezá por el docker-compose.yml más simple posible (Flask + Postgres), después agregá Nginx + SSL. No intentes hacer todo perfecto el día 1.

Fin del HANDOFF.md — v9.19