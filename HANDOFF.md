# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP) — v9.20

**Última actualización:** 13 de Noviembre, 2026
**Último commit:** `99bb28f` (refactor: Fase F — cierre diario legacy eliminado)
**HANDOFF anterior:** `HANDOFF_v9.5.md` (histórico congelado, ver raíz del proyecto)
**Bitácoras históricas:** `bitacora/2026-10-sesiones.md`, `bitacora/2026-11-sesiones.md`
**Tenants de prueba:** `bitacora/tenants_prueba.md` (incluye `tenant_31` y `tenant_34`)

**Sesión 13 Nov:** Fase F (parte 1). 7 DTs cerradas: B-1 (`_test_tenant_schema.py`), B-2/B-3 (centralizar DDL + eliminar auto-reparación en runtime), B-4 (`_cleanup_tenants_huerfanos.py`), E-1 (cierre diario legacy eliminado, 563 líneas), E-2/E-4 (no reproducido). Commits: `15bc439`, `6905d84`, `9ad0030`, `99bb28f`.
**Sesión 12 Nov:** Fases A + B + C (auditorías de alineación ORM ↔ BD ↔ modelo) 100% cerradas. DT-Fase C-1 (`total_anulaciones` faltaba en DDL de `crear_tenant_saas()`) resuelta y validada empíricamente con `tenant_34`. Commit `1ef3579`.
**Sesión 12 Nov (tarde):** Fase E cerrada (`tenant_34` smoke test completo: login → POS → venta → anulación → producción → reportes → PDFs). Bug A no reproducido. Bug `HistorialInventario` de producto fixeado (`9b71016`). 6 DTs nuevas de Fase E.
**Sesión 11 Nov (noche):** CRÍTICA-2 (`d32a7f3`) + MEDIA-F2.5 (`e50f992`) cerradas. Fase D 100% cerrada.
**Sesión 11 Nov (tarde/noche):** MEDIA-BAJA (cierre jornada) + limpieza JS huérfano. Commit `7ce0156`.
**Sesión 11 Nov (mañana):** DT-nueva-MEDIA (desconciliación + ANULADO + whitelist) 100% + DT-nueva-BAJA (endpoint huérfano). 6 commits: `6b5485f`, `17d0b83`, `5368b1a`, `a403c90`, `b0efa27`, `29a4e03`.
**Sesión 8 Nov (tarde):** DT-nueva-MEDIA-F2.6 reformulada a BAJA (falso positivo: werkzeug no ensucia `panaderia.log`). Código limpio, solo docs.
**Sesión 8 Nov:** F3 logging — hash de contraseña truncado. Commit `53fc3f3`. DT-nueva-MEDIA-logging-ruido cerrada al 100%.
**Sesión 7 Nov:** DT-nueva-MEDIA-logging-ruido (F1: `buscar_producto` + F1.5: `consultas_filtradas.py`). Commits `51000fc` + `68f8856`.
**Sesión 6 Nov:** Commit 2 COMPLETO — rediseño "menos es más" + filtro `?producto=` en `/reporte/ventas` + i18n en/pap. 5 commits.
**Sesión 5 Nov:** Fix CRÍTICA-4 (colisión IDs int/ext en Productos Populares) + Bug B (rotación <7d → "—") + IA KeyError. Commit `6e7dbbf`. Tenant_31 conservado.
**Sesión 4 Nov:** Fix MEDIA-BAJA (Ventas del Día no distingue donaciones). Commit `607ac75`.
**Sesión 3 Nov:** Fix MEDIA-ALTA (donaciones en "Ingresos") + auditoría completa de cadena financiera (15 fixes). Commit `8304a16`.
**Sesión 1 Nov (noche):** Fix CRÍTICA-1 (depósitos CONCILIADOS editables). Commit `5d289fd`.
**Sesión 1 Nov (mañana):** Fix de raíz `current_user` detached (`db.session.merge()` en `load_user`). Commit `6173cfe`.
**Sesión 31 Oct:** Feature Baja de Inventario + fix FK diferida en `crear_tenant_saas()`. Commits `ba48503` + `52696be`.

> Este archivo es **contexto actual** (liviano). Detalle de sesiones, tablas de DT resueltas y registros de features: `bitacora/`. Todo lo anterior al 1 Nov, completo: `HANDOFF_v9.5.md`.

---

▼▼▼ SECCIÓN 1: INFORMACIÓN GENERAL ▼▼▼

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp) — **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.9.4 — **11/11 módulos completos (100%)** + i18n PDF/HTML 100% + Features Toppings, Anulación POS, Baja de Inventario y Commit 2 (rediseño Productos Populares) 100%.
- **Arquitectura:** Multi-tenant con PostgreSQL (un schema por tenant).
- **Seguridad:** Producción-ready (CSRF con tokens firmados + Origin/Referer). ✅ CRÍTICA-1 resuelta. ✅ CRÍTICA-2 resuelta (`d32a7f3`).
- **Observabilidad:** logger con rotación + `LOG_LEVEL` configurable vía `.env`. ✅ DT-nueva-MEDIA-logging-ruido cerrada al 100% (4 fases).
- **i18n:** es/en/pap operativos. Diccionarios Python pendientes (deuda baja).
- **Fases pre-Docker:** ✅ Fases A + B + C + D + E cerradas. Fase F (parte 1) cerrada (13 Nov: B-1, B-2, B-3, B-4, E-1, E-2, E-4).

### 📋 Próximos pasos

1. **Fase F (parte 2)** (~6-8 h). DTs BAJAS de Fase C (C-2 a C-8: columnas muertas en DDL, `sucursales` legacy, `seed_demo_history`), `docs/ESTRUCTURA_TENANT.md`, DTs BAJAS de Fase E (E-5, E-6).
2. **Fase G — Dockerización** (~22-32 h).
3. (Opcional/baja) **i18n de diccionarios Python** (~2-4 h).

---

▼▼▼ SECCIÓN 2: STACK Y ESTRUCTURA ▼▼▼

## 2️⃣ Stack y estructura

- **Backend:** Python 3.10+, Flask 3.1.2, SQLAlchemy 2.0, PostgreSQL 17.10 (puerto **5433**), Flask-Login, Flask-WTF, Werkzeug, ReportLab, Matplotlib, **Flask-Babel 4.0.0** + **Babel 2.18.0**, logging con `RotatingFileHandler`.
- **BD:** `panaderia_master` — credenciales en `.env` (la contraseña local de postgres está en `HANDOFF_v9.5.md`; ⚠️ no copiarla a documentos públicos).
- **Frontend:** HTML5/CSS3, JS vanilla, Bootstrap 5.1.3, Chart.js, Font Awesome 6.

**Archivos clave**
- `app.py` (~13.250 líneas), `models.py` (~3.233), `reportes.py` (~3.600), `seed_demo.py` + `seeds/`.
- Multi-tenant: `middleware_saas.py`, `tenant_decorators.py`, `tenant_context.py`, `security_utils.py`.
- `migrations/sql/` — scripts SQL versionados.
- `db/schema_tenant_canonical.sql` — **NUEVO** (Fase F): fuente única de verdad del DDL de un tenant (migración progresiva).
- `babel.cfg`, `locales/{es,en,pap}/LC_MESSAGES/messages.{po,mo}`.
- Utilidades: `_limpiar_fuzzy.py`, `_ver_untraducciones.py`, `_audit_schema.py`, `_test_jinja.py` (solo nombre, no ruta), `_test_mo.py`, `_test_descuento.py`.
- **Nuevas utilidades Fase F:** `_test_tenant_schema.py` (test ORM ↔ BD), `_migrar_tenants.py` (script de migración), `_cleanup_tenants_huerfanos.py` (limpieza de tenants huérfanos).

---

▼▼▼ SECCIÓN 3: TENANTS ▼▼▼

## 3️⃣ Tenants

| ID | Nombre | Subdominio | Plan | Licencia | Estado | Notas |
|----|--------|-----------|------|----------|--------|-------|
| 1 | Panadería Principal | principal | basico | local | Producción | Plantilla multi-tenant. `base_datos=tenant_1` (saneado `d32a7f3`). |
| 27 | **Panadería Demo** | panadería_demo | premium | nube_premium | Producción | Demo comercial, `demo2026`. `base_datos=tenant_27` (saneado `d32a7f3`). |
| 31 | **Diagnóstico Productos Populares** | diagnóstico_producto | basico | nube_basica | **Pruebas** | **Tenant de pruebas** (diagnóstico 5 Nov). Usuario `admin_31`. |
| 34 | **Test Fase C Fix** | test_fase_c_fix | basico | nube_basica | **Pruebas** | **Tenant virgen** (12 Nov), creado con `crear_tenant_saas()` fixeado. Usuario `admin_34`. |

- **Producción real:** `tenant_1` + `tenant_27` (Demo, ~9.972 filas, `idioma = pap`).
- **Pruebas:** `tenant_31` + `tenant_34`.
- `public` tiene SOLO 3 tablas: `tenants`, `usuarios` (fallback `dev_master`), `configuracion_panaderia`.
- `idioma` vive en `tenant_X.configuracion_sistema` (`VARCHAR(5) NOT NULL DEFAULT 'es'`).

---

▼▼▼ SECCIÓN 4: USUARIOS ▼▼▼

## 4️⃣ Usuarios

- **Roles:** `super_admin` (dev_master, todos los tenants), `admin_cliente` (total en su tenant), `supervisor` (producción, recetas, MP, proveedores, reportes), `cajero` (POS y cierre).
- **Usuarios:** tenant 1 → `dev_master`, `admin`, `admin_1`. Tenant 27 → `admin_27`, `super_27`, `cajero_27`. Tenant 31 → `admin_31`, `super_31`, `cajero_31`. Tenant 34 → `admin_34`, `super_34`, `cajero_34`.
- **Demo:** todos los usuarios del tenant_27 usan **`demo2026`**. `admin_27` tiene nombre `Administrador Panadería Demo`.
- **Contraseñas:** `/mi_perfil` (✅ arreglado 1 Nov) y `POST /resetear_password/<id>`.

---

▼▼▼ SECCIÓN 5: MÓDULOS Y FEATURES ▼▼▼

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
| 11 | Reportes Profesionales | ✅ (i18n 100% + donaciones separadas + rotación <7d + rediseño Productos Populares) |

**Features recientes (detalle en bitácoras)**
- **Fase F (13 Nov):** `15bc439` (`_test_tenant_schema.py`), `6905d84` (DDL canónico + `_migrar_tenants.py` + eliminar auto-reparación en runtime), `9ad0030` (`_cleanup_tenants_huerfanos.py`), `99bb28f` (eliminar cierre diario legacy: 563 líneas).
- **Fase E + fix HistorialInventario (12 Nov):** `9b71016` — `OrdenProduccion.completar_produccion()` ahora registra movimiento de producto terminado en `HistorialInventario`.
- **Fase A+B+C (12 Nov):** `1ef3579` — DT-Fase C-1 resuelta (`total_anulaciones` en DDL de `cierres_diarios`).
- **CRÍTICA-2 + F2.5 (11 Nov noche):** `d32a7f3` + `e50f992` — `base_datos` saneado + `LOG_LEVEL` configurable.
- **Cierre jornada + JS huérfano (11 Nov):** `7ce0156` — código muerto eliminado + filtro `es_donacion`.
- **Depósitos bancarios (11 Nov):** `6b5485f`, `17d0b83`, `5368b1a`, `a403c90`.
- **Commit 2 — rediseño Productos Populares (6 Nov):** `320881b`, `5d8e2b4`, `b6a1908`, `e3b48e0`, `7ff556f`.
- **Fix CRÍTICA-4 + Bug B + IA (5 Nov):** `6e7dbbf`.
- **Fix MEDIA-BAJA (4 Nov):** `607ac75`.
- **Fix MEDIA-ALTA (3 Nov):** `8304a16`.
- **Fix CRÍTICA-1 (1 Nov):** `5d289fd`.

---

▼▼▼ SECCIÓN 6: ÚLTIMOS COMMITS ▼▼▼

## 6️⃣ Últimos commits

```text
99bb28f refactor(fase-f): eliminar cierre diario legacy (CierreDiario + endpoints + tabla)
9ad0030 feat(fase-f): _cleanup_tenants_huerfanos.py + .gitignore excepciones
6905d84 refactor(fase-f): eliminar auto-reparación de esquema en runtime + migraciones manuales
15bc439 feat(fase-f): _test_tenant_schema.py — test de verificación ORM ↔ BD
b798950 docs(handoff): Fase E cerrada + HistorialInventario producto fixeado
9b71016 fix(fase-e): registrar movimiento de producto en HistorialInventario al completar producción
17c1033 docs(bitacora): agregar sesión 12 Nov — Fases A/B/C cerradas
a314682 docs(handoff): HANDOFF v9.18 + bitácora sesión 12 Nov — Fases A/B/C cerradas
1ef3579 fix(fase-c): agregar total_anulaciones al DDL de cierres_diarios
a85e8d1 docs(handoff): actualizar roadmap a producción (Fases A/B/C antes de Docker)
02ed322 docs: HANDOFF v9.16 + bitácora sesión 11 Nov (noche) — Fase D cerrada
29a4e03 fix(reportes): corregir cierre de etiqueta <a> en boton Ver Reporte
b0efa27 refactor(reportes): renombrar reporte_ventas a reporte_ventas_periodo
a403c90 feat(depositos): desconciliacion con auditoria y control de rol
5368b1a feat(depositos): anulacion con motivo, auditoria visual y fix de totales
17d0b83 feat(depositos): auditoria de usuario_id en crear/editar/conciliar
6b5485f fix(depositos): whitelist de estados + auditoría (4 columnas nuevas)
7fd0cbd docs(handoff): F2.6 reformulada a BAJA — falso positivo
c36bbca docs: HANDOFF v9.13 + bitacora sesion 8 Nov (F3 logging cerrada)
53fc3f3 fix(logging): F3/3 — truncar hash de contrasena en logs (seguridad)
▼▼▼ SECCIÓN 7: DEUDA TÉCNICA ▼▼▼

7️⃣ Deuda técnica PENDIENTE
✅ Cerradas el 13 Nov (Fase F, parte 1)
Prioridad	DT	Descripción	Commit
✅ Media	DT-Fase B-1	_test_tenant_schema.py compara models.py ↔ BD real por tenant con exit code 0/1.	15bc439
✅ BAJA	DT-Fase B-2	consecutivos_pos centralizado en db/schema_tenant_canonical.sql.	6905d84
✅ Media	DT-Fase B-3	Auto-reparación de esquema en runtime eliminada.	6905d84
✅ BAJA	DT-Fase B-4	_cleanup_tenants_huerfanos.py (limpieza de tenants huérfanos).	9ad0030
✅ BAJA	DT-Fase E-1	Cierre diario legacy eliminado (563 líneas).	99bb28f
✅ BAJA	DT-Fase E-2	configuracion_sistema vacía (no reproducido, lazy init).	—
✅ Media	DT-Fase E-4	Cantidades inconsistentes (no reproducido, fórmula correcta).	—
✅ Cerradas el 12 Nov (Fases A + B + C)
Prioridad	DT	Descripción	Commit
✅ Alta	DT-Fase C-1	total_anulaciones faltaba en el DDL de cierres_diarios.	1ef3579
✅ Cerradas el 11 Nov (noche)
Prioridad	DT	Descripción	Commits
✅ CRÍTICA	DT-nueva-CRÍTICA-2	base_datos huérfano saneado.	d32a7f3
✅ MEDIA	DT-nueva-MEDIA-F2.5	LOG_LEVEL configurable.	e50f992
✅ MEDIA-BAJA	DT-nueva-MEDIA-BAJA (cierre jornada)	Código muerto eliminado.	7ce0156
✅ BAJA	DT-nueva-BAJA (JS huérfano)	Polling eliminado.	7ce0156
✅ MEDIA	DT-nueva-MEDIA (desconciliación)	Endpoint agregado.	a403c90
✅ MEDIA	DT-nueva-MEDIA (estado ANULADO)	Endpoint dedicado.	5368b1a
✅ MEDIA	DT-nueva-MEDIA (whitelist)	Validación agregada.	6b5485f
✅ BAJA	DT-nueva-BAJA (endpoint huérfano)	Renombrado.	b0efa27, 29a4e03
✅ Cerradas el 8 Nov (DT logging ruidoso)
Prioridad	DT	Descripción	Commits
✅ Media	DT-nueva-MEDIA-logging-ruido	Logging ruidoso (F1 + F1.5 + F2 + F3)	51000fc, 68f8856, 620a177, 53fc3f3
✅ Cerradas el 6 Nov (Commit 2)
Prioridad	DT	Descripción
✅ Media	Commit 2 (rediseño)	Rediseño "menos es más" + recomendaciones dinámicas.
✅ Media	i18n cadenas nuevas	Strings de Commit 2 traducidos en en/pap.
🟢 DTs BAJAS Fase F — Pendientes (para Fase F parte 2)
Prioridad	DT	Descripción	Estimación
🟢 BAJA	DT-Fase C-2	7 columnas muertas en configuracion_produccion (en DDL, no en modelo).	~30 min
🟢 BAJA	DT-Fase C-3	4 columnas muertas en configuracion_sistema (en DDL, no en modelo).	~15 min
🟢 BAJA	DT-Fase C-4	pagos_individuales.usuario_id (DDL, no modelo).	~15 min
🟢 BAJA	DT-Fase C-5	panaderias.panaderia_id auto-referencia (DDL, no modelo).	~15 min
🟢 BAJA	DT-Fase C-6	Módulo multi-sucursal legacy (sucursales, usuarios.sucursal_id).	~30 min
🟢 BAJA	DT-Fase C-7	5 columnas legacy en tenant_1 (cierres_diarios.created_at, etc.).	~15 min
🟢 BAJA	DT-Fase C-8	seed_demo_history en tenant_27 (basura de seed).	~5 min
🟢 BAJA	DT-unificar-naming	proveedor, detalle_venta en singular vs plural.	~15 min
🟢 BAJA	DT-Fase E-5	HistorialInventario.materia_prima_id modelo vs BD (nullable).	~15 min
🟢 BAJA	DT-Fase E-6	Mojibake en commit messages (CMD).	~5 min
🟢 BAJA	DT-nueva-BAJA-F2.6	Post-Docker: auditar WSGI basicConfig.	~30 min
🟢 BAJA	DT-unificar-productos-populares	Unificar _obtener_datos_productos_populares.	~2-3 h
🟢 BAJA	DT-unificar-prefijos-int-ext	Unificar analizar_productos_periodo.	~1-2 h
🟢 BAJA	DT-formato-numerico-es-CO	Formato $20.000.00 → $20.000,00.	~1 h
Nota: También hay ~39 archivos .bak acumulados (oct/nov) que no deberían estar en el repo. DT-Fase F-BAK (nueva, 🟢 BAJA, ~30 min, Fase F): agregar *.bak* a .gitignore y limpiar.

📋 Otras medias / bajas (heredadas, detalle en HANDOFF_v9.5.md sec. 9)
Medias: DT-37 F5-pulido · DT-37 F4.9 (libro_diario huérfano) · DT-NUEVA-1 (CREATE TABLE con idioma) · error 'ingreso' (✅ cerrada 5 Nov) · endpoint huérfano /generar_reporte_flujo_caja · overlap de labels en pie chart · i18n de diccionarios Python · mapeo Jinja2 de badges dinámicos · bug de _ver_untraducciones.py.

Cosmética crítica: emojis rotos en PDFs de ReportLab.

Bajas: filas legacy en tenant_1.configuracion_sistema · imports redundantes de os · "Fluho Neto" → "Flusho Neto" (PAP) · renombrar "Historial de Ventas" en reportes.html:229 · datos demo hardcodeados en ventas_periodo.html · traducciones PAP heredadas · tenant_1.historial_inventario sin FK en orden_produccion_id.

🔍 Hallazgos 5 Nov (diagnóstico con tenant_31)
✅ CRÍTICA-2 reproducida en vivo: tenant_31.base_datos = tenant_diagnóstico_producto. Resuelta 11 Nov noche.

Bug A (cerrado como no reproducido en Fase E): detalle_venta.producto_externo_id NULL en 2 ventas con externos en tenant_31. No se reprodujo en tenant_34 (12 Nov). Se cierra.

Licencia básica: tenant_31 no tiene acceso a reportes premium. Comportamiento esperado.

Reportes IA (2 distintos): /reporte/analisis_predictivo (HTML) + /generar_reporte_ia_predictivo (PDF).

Caché del navegador: screenshots desactualizados confunden diagnóstico. Regla: modo incógnito + reiniciar servidor + netstat.

Mojibake en commit message: usar git commit -F _commit_msg.txt (UTF-8).

▼▼▼ SECCIÓN 8: METODOLOGÍA DE TRABAJO ▼▼▼

8️⃣ Metodología de trabajo
Reglas de oro
Un paso a la vez con confirmación antes de continuar.

Diagnóstico ANTES de modificar. Soluciones de raíz, no parches.

TODO debe funcionar para futuros tenants.

Verificación con psql / findstr antes de avanzar. Commit después de cada fix verificado.

Backup (pg_dump) antes de cada cambio grande.

git status antes de commitear; git add <archivo> explícito; push tras el commit.

Detener el servidor antes de reiniciar. Verificar con tasklist | findstr python. netstat -ano | findstr :5000 → 1 sola línea LISTENING.

Antes de testear templates, modo incógnito + servidor reiniciado.

Insertar bloques mostrando ANTES → DESPUÉS con número de línea exacto; compilar tras cada inserción (python -m py_compile app.py).

Deuda técnica detectada: anotarla (no tocarla), priorizar, decidir después.

Windows: findstr /c:"patrón" para literales; PowerShell Select-String para tildes. Preferir scripts Python al copy-paste.

git commit -F _commit_msg.txt (UTF-8) para mensajes con tildes/emojis.

No acumular DT. Si el fix descubre un problema nuevo: si es mismo concern → mismo commit; si es distinto → DT nueva.

Cero DT "en el aire". Toda DT debe tener: prioridad, estimación, y sesión objetivo.

Script de auditoría con ❌ uniforme = bug de matching. Verificar el diagnóstico del script.

No poner texto decorativo dentro de text(f'''...'''). El SQL se ejecuta tal cual.

Nunca pegar contraseñas reales en el chat del instructor.

db.create_all() solo en public, no en tenant_X. El DDL de tenant_X es raw (crear_tablas_en_orden).

Antes de git add de un archivo _*, verificar .gitignore. Si es utilidad permanente, agregar excepción !<archivo>.

Para borrar bloques de código, NO usar regex. Usar borrado por líneas exactas o cortar/pegar en el editor con verificación después de cada bloque. La regex es frágil con decoradores, indentación, strings multilínea.

i18n / Babel
Flask-Babel 4.0: default_translation_directories va en el constructor Babel(app, ...).

pybabel extract con lista explícita. babel.cfg: [jinja2: **.html].

pybabel NO extrae _() dentro de f-strings ni después de emoji.

pybabel update marca #, fuzzy → SIEMPRE _limpiar_fuzzy.py. Los .mo se commitean.

El % NUNCA va dentro de _(). % sueltos → %%.

Templates: proteger <style>/<script> antes de reemplazos masivos.

Reiniciar servidor + modo incógnito tras pybabel compile.

config.nombre_panaderia ya está global en templates.

Modelos, schema y multi-tenant
ORM ↔ BD DEBEN estar alineados. Al agregar columna al modelo, verificar con information_schema.columns.

tenant_1, tenant_27, tenant_31, tenant_34 DEBEN tener la misma estructura.

FK diferida: si una tabla referencia a otra creada DESPUÉS en crear_tenant_saas(), agregar la FK al final con ALTER TABLE ... ADD CONSTRAINT.

Todo cambio de schema se prueba con un tenant nuevo (tenant_31 o tenant_34).

search_path DEBE estar seteado antes de consultar modelos fuera de request.

producto_id puede ser NULL en historial_inventario. _descontar_ingredientes() DEBE registrar en HistorialInventario.

FKs ambiguas en SQLAlchemy: declarar foreign_keys='Tabla.columna' en el relationship.

load_user() debe devolver un objeto ATTACHED (db.session.merge(user)).

Antes de cambiar un patrón global, auditar con grep quién lo toca y correr un test de regresión.

Colisión de IDs int/ext: usar prefijos (int_, ext_) al armar claves de diccionarios.

Diagnóstico pre-commit: si git diff --stat muestra más líneas de las esperadas, verificar el diff completo antes de commitear.

crear_tenant_saas() usa DDL raw, no db.create_all(). Cualquier columna nueva en models.py DEBE agregarse también al CREATE TABLE correspondiente en app.py. Verificar con _test_tenant_schema.py.

Dinero, ventas y bajas
Soft-delete siempre: las ventas nunca se borran (COMPLETADA / ANULADA).

Toda consulta de Venta para reportes/dinero DEBE filtrar Venta.estado == 'COMPLETADA'; las donaciones (es_donacion=TRUE) se excluyen de ingresos.

Queries de reportes con fecha_fin: usar fecha_fin_inclusive = fecha_fin + timedelta(days=1) y Venta.fecha_hora < fecha_fin_inclusive.

No se anula una venta si el día ya tiene CierreDiario confirmado (esta regla se eliminó en Fase F, porque CierreDiario es legacy).

Las facturas ELECTRONICA NUNCA se anulan en el POS.

Donaciones: solo admin_cliente o super_admin pueden anularlas (backend 403). El cajero puede registrarlas pero no anularlas.

Toppings: siempre en gramos; factor_escala = cantidad_producir / unidades_obtenidas.

Al agregar una nueva fuente de pérdidas/gastos (como bajas), actualizar estado_resultados y analisis_gastos en el MISMO commit.

Verificar los print y strings de JS en templates: el mojibake puede romper el JS.

Depósitos bancarios: CONCILIADO es inmutable (CRÍTICA-1). Editar un depósito conciliado → 403.

Rotación <7 días: si el tenant tiene <7 días de vida, rotacion_promedio = None (template muestra —). Criterio: dias_reales_tenant desde la primera venta.

Filtro ?producto= en /reporte/ventas: aplica a ventas_periodo (Python) y a detalles_periodo + donaciones_periodo (SQLAlchemy .has()).

Comandos útiles
cmd
chcp 65001
psql -U postgres -p 5433 -h localhost -d panaderia_master
python -m py_compile app.py
python -m py_compile models.py
python -m py_compile reportes.py
python app.py
findstr /n /c:"patrón exacto" archivo.py
powershell -Command "Select-String -Path archivo.py -Pattern 'patrón con tildes'"
git commit -F _commit_msg.txt && del _commit_msg.txt
pg_dump -U postgres -p 5433 -h localhost -d panaderia_master -F c -f backup_pre_XXX.backup

:: Verificar procesos Python corriendo
tasklist | findstr python
netstat -ano | findstr :5000

:: Pipeline i18n
pybabel extract -F babel.cfg -o locales/messages.pot app.py models.py reportes.py templates
pybabel update -i locales/messages.pot -d locales
python _limpiar_fuzzy.py
pybabel compile -d locales --statistics

:: Estructura / constraints de una tabla
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_schema = 'tenant_34' AND table_name = 'historial_inventario' ORDER BY ordinal_position;"

:: Diagnóstico (Fase F)
python _test_tenant_schema.py 34           (test ORM ↔ BD, exit 0/1)
python _migrar_tenants.py --dry-run        (migración de esquema, dry-run)
python _migrar_tenants.py 34               (migración de esquema, real)
python _cleanup_tenants_huerfanos.py       (dry-run)
python _cleanup_tenants_huerfanos.py --fix (limpieza real)
python _audit_schema.py
python _test_jinja.py ventas_del_dia.html  (SOLO nombre, NO ruta)
python _test_mo.py
python _ver_untraducciones.py
▼▼▼ SECCIÓN 9: PLAN PRE-DOCKERIZACIÓN ▼▼▼

9️⃣ Plan pre-Dockerización (Fases A-G)
Objetivo: que models.py ↔ app.py ↔ BD estén sincronizados y que un tenant nuevo nazca 100% funcional.

Fase	Alcance	Estimación	Estado
A — Auditoría de modelos	Mapear modelos, detectar huérfanos, FKs mal definidas	~2 h	✅ 12 Nov
B — Auditoría de app.py	Queries a tablas/columnas inexistentes, crear_tenant_saas()	~2 h	✅ 12 Nov
C — Auditoría de BD	information_schema en tenant_1 vs tenant_27, modelos vs BD real	~2 h	✅ 12 Nov
D — Sincronización + DT abiertas	Script SQL para alinear tenants, resolver DTs	~8-10 h	✅ 11 Nov noche
E — Tenant virgen	tenant_34, flujo login → POS → venta → cierre → reporte	~2 h	✅ 12 Nov (tarde)
F — Documentación y limpieza	docs/ESTRUCTURA_TENANT.md, eliminar código huérfano, DTs BAJAS	~6-8 h	🟡 Parte 1 cerrada (13 Nov) — parte 2 pendiente
G — Dockerización	requirements.txt completo, .mo commiteados, .env.example, Dockerfile + docker-compose.yml	~22-32 h	⏸️ Pendiente
Listo para Docker: ✅ CSRF portable · ✅ logs a archivo + rotación · ✅ i18n portable · ✅ crear_tenant_saas() OK · ✅ CRÍTICA-1 resuelta · ✅ cadena financiera auditada · ✅ Anulación POS · ✅ Bug B resuelto · ✅ IA KeyError · ✅ Commit 2 · ✅ Fases A+B+C+D+E cerradas · ✅ DT-Fase C-1 resuelta · ✅ Fase F parte 1 cerrada · 🟡 Fase F parte 2 pendiente · 🟡 Dockerfile/compose por crear.

▼▼▼ SECCIÓN 10: NOTAS ESTRATÉGICAS ▼▼▼

🔟 Notas estratégicas
Objetivo: ERP SaaS multi-tenant multi-país: POS, inventario, producción, recetas (toppings), activos fijos, reportes con IA, finanzas, i18n (es/en/pap), anulación de ventas, bajas de inventario, donaciones con auditoría; base para API REST + IA avanzada.

Mercado: 3.000-5.000 panaderías en Colombia · 10.000-30.000 en LATAM · Curazao-Antillas Holandesas (Papiamentu). Precio $60k-$600k COP/mes.

Licencias: Premium 3 usuarios · Básica 1 usuario.

Demo: fases 1-12 completas (~9.972 filas), contraseña demo2026, idioma = pap.

▼▼▼ SECCIÓN 11: ESTADO ACTUAL (RESUMEN EJECUTIVO) ▼▼▼

1️⃣1️⃣ Estado actual (resumen ejecutivo)
Aspecto	Estado
Último commit	99bb28f en origin/main (pusheado)
Módulos	11/11 completos (100%)
Fase A (auditoría modelos)	✅ 12 Nov — 43 modelos ↔ 42 tablas, cero huérfanos
Fase B (auditoría app.py)	✅ 12 Nov — 229 queries raw clasificadas, 0 huérfanas
Fase C (auditoría BD)	✅ 12 Nov — DT-Fase C-1 resuelta + 12 DTs BAJAS anotadas
Fase E (tenant virgen)	✅ 12 Nov (tarde) — tenant_34 smoke test completo
Fase F (parte 1)	✅ 13 Nov — 7 DTs cerradas (B-1, B-2, B-3, B-4, E-1, E-2, E-4)
Fix DT-Fase C-1 (total_anulaciones)	✅ 1ef3579
Fix DT-Fase E-3 (HistorialInventario producto)	✅ 9b71016
Fix DT-Fase B-1 (_test_tenant_schema.py)	✅ 15bc439
Fix DT-Fase B-2/B-3 (DDL + auto-reparación)	✅ 6905d84
Fix DT-Fase B-4 (_cleanup_tenants_huerfanos.py)	✅ 9ad0030
Fix DT-Fase E-1 (cierre diario legacy)	✅ 99bb28f
Bug A (producto_externo_id NULL)	✅ NO reproducido en tenant_34 (cerrado)
Bug B (rotación <7d → "—")	✅ Validado en tenant_34
Anulación POS	✅ Validado end-to-end (venta → anulada → stock revertido → reporte excluye)
Demo	✅ admin_27 / demo2026
Tenants productivos	tenant_1 + tenant_27
Tenants de pruebas	tenant_31 + tenant_34
DT críticas abiertas	0
DT medias abiertas	0
DT bajas abiertas	~18: C-2 a C-8, unificar-naming, E-5, E-6, F2.6, unificar-productos-populares, unificar-prefijos-int-ext, formato-es-CO, F-BAK (39 archivos .bak)
Siguiente tarea	Fase F (parte 2): DTs BAJAS de Fase C (C-2 a C-8) + docs/ESTRUCTURA_TENANT.md
Fase actual	Fase F (parte 1 cerrada, parte 2 pendiente)
Dockerización	Fase G, ~22-32 h (post Fase F parte 2)
Working tree	limpio (post commit 99bb28f)
▼▼▼ SECCIÓN 12: CÓMO CONTINUAR EN CHAT NUEVO ▼▼▼

📞 Cómo continuar en un chat nuevo
Pegar este archivo como contexto inicial con esta instrucción:

"Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el HANDOFF.md v9.20 con el contexto actual. Por favor actúa como instructor guiando paso a paso, con la metodología del HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/PowerShell Select-String, commit tras cada fix verificado. Al insertar bloques, muéstrame ANTES → DESPUÉS con número de línea exacto. Tú me das LUZ VERDE cuando los cambios estén 100% validados. Yo aplico los cambios en mi editor. Primera tarea: Fase F (parte 2). Arrancar por las DTs BAJAS de Fase C (C-2 a C-8: columnas muertas en DDL, sucursales legacy, seed_demo_history). Empieza con diagnóstico del DDL actual de configuracion_produccion, configuracion_sistema, pagos_individuales, panaderias, sucursales, usuarios en crear_tablas_en_orden()."

▼▼▼ SECCIÓN 13: ROADMAP A PRODUCCIÓN ▼▼▼

1️⃣2️⃣ Roadmap a Producción
Objetivo: lanzar PanaderíaPro a producción en enero 2027.
Modalidad: part-time (~10-15 h/semana).

Estado actual (13 Nov 2026)
Aspecto	% Listo
Funcionalidad (features)	~92%
Producción-ready (infra)	~35% (Fases A-E cerradas, sube de 30%)
Deuda técnica	✅ 0 DTs críticas, 0 medias, ~18 BAJAS
Bloqueantes críticos	4 (bajó de 5)
Estimación total	~30-45 h (4-6 jornadas de 8 h)
Cronograma propuesto
Semana	Foco	Estado
1 (5-11 Nov)	✅ CERRADA: Commit 2 + DTs de Fase D	✅
2 (12-18 Nov)	✅ CERRADA: Fases A + B + C + E + Fase F parte 1	✅
3 (19-25 Nov)	Fase F (parte 2): DTs BAJAS de Fase C + docs/ESTRUCTURA_TENANT.md	🟡 Próxima
4 (26-2 Dic)	Fase G: Dockerfile + docker-compose.yml + .env.example	⏸️
5 (3-9 Dic)	Fase G: WSGI production + SSL + Nginx	⏸️
6 (10-16 Dic)	Fase G: Backup automático + /health + logging	⏸️
7 (17-23 Dic)	Fase G: Deploy a VPS real + hardening	⏸️
8 (24-30 Dic)	Fase G: Smoke test producción + docs	⏸️
31 Dic - 1 Ene	Buffer + lanzamiento	⏸️
Prioridades
P0 (sin esto no hay producción):

✅ Fases A + B + C (auditorías). Cerradas.

✅ Fase E (tenant virgen + Bug A). Cerrada.

🟡 Fase F parte 2 (DTs BAJAS). Pendiente.

☐ Docker + WSGI + SSL.

☐ Backup automático.

☐ /health endpoint.

P1 (post-lanzamiento 1-2 semanas):

CI/CD (GitHub Actions).

Monitoreo avanzado (Sentry, Prometheus).

Rate limiting.

Tests automatizados (pytest).

P2 (deseables):

i18n de diccionarios Python.

API REST.

Dashboard de admin.

Rotación automática de contraseñas.

Criterios de "listo para producción"
☑ Tenants con schema correcto (tenant_{id}). ✅ (11 Nov)

☑ Fases A/B/C completadas. ✅ (12 Nov)

☑ Fase E OK. ✅ (12 Nov)

☐ Fase F parte 2 OK (DTs BAJAS cerradas).

☐ docker-compose up levanta sin errores.

☐ HTTPS funciona.

☐ /health responde 200 OK.

☐ Backup automático corriendo.

☐ Logs a stdout + rotación.

☐ Smoke test de producción OK.

☐ dev_master + 2 tenants productivos.

☐ Documentación de deploy en docs/DEPLOY.md.

☐ Rollback plan documentado.

Decisiones pendientes
Proveedor de VPS (Hetzner, DigitalOcean, AWS Lightsail).

Dominio y subdominios por tenant.

SSL (Let's Encrypt).

Backup (pg_dump diario + retención + copia externa).

tenant_27 (demo): migrar a la nube o demo nueva.

Precio final de licencias.

▼▼▼ RECOMENDACIÓN PARA NO ATRASARTE ▼▼▼

🎯 Recomendación para no atrasarte
Fase F parte 2: priorizá C-2 a C-6 (limpieza del DDL) en un solo commit. C-7 y C-8 son limpieza de datos, se pueden agrupar en otro commit. docs/ESTRUCTURA_TENANT.md puede esperar a que termines las DTs.

Fase G (Docker): empezá por el docker-compose.yml más simple (Flask + Postgres). Después agregá Nginx + SSL. No intentes hacer todo perfecto el día 1.

No acumules .bak: agregá *.bak* a .gitignore antes de empezar Fase G.

Fin del HANDOFF.md — v9.20