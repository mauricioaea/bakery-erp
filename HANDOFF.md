# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP) — v9.9

**Última actualización:** 4 de Noviembre, 2026 (noche)
**Último commit:** `607ac75` (feat: Ventas del Día distingue donaciones + guard de rol)
**HANDOFF anterior:** `HANDOFF_v9.5.md` (histórico congelado, ver raíz del proyecto)
**Bitácoras históricas:** `bitacora/2026-10-sesiones.md`, `bitacora/2026-11-sesiones.md`
**Sesión 4 Nov:** Fix MEDIA-BAJA (Ventas del Día no distingue donaciones). Badge + tooltip + guard de rol. Commit `607ac75`.
**Sesión 3 Nov:** Fix MEDIA-ALTA (donaciones en "Ingresos") + auditoría completa de cadena financiera (15 fixes) + fix `fecha_fin` a medianoche. Commit `8304a16`.
**Sesión 1 Nov (noche):** Fix CRÍTICA-1 (depósitos CONCILIADOS editables) — backend 403 + frontend solo-lectura + smoke test 7/7. Commit `5d289fd`.
**Sesión 1 Nov (mañana):** Fix de raíz `current_user` detached (`db.session.merge()` en `load_user`) + test de regresión 6/6 + commit `6173cfe`.
**Sesión 31 Oct:** Feature Baja de Inventario + fix FK diferida en `crear_tenant_saas()` + smoke test tenants nuevos (commits `ba48503` + `52696be`).

> Este archivo es **contexto actual** (liviano). Detalle de sesiones, tablas de DT resueltas y registros de features: `bitacora/`. Todo lo anterior al 1 Nov, completo: `HANDOFF_v9.5.md`.

---

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp) — **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.9.3 — **11/11 módulos completos (100%)** + i18n PDF/HTML 100% + Features Toppings, Anulación POS y Baja de Inventario 100%.
- **Arquitectura:** Multi-tenant con PostgreSQL (un schema por tenant).
- **Seguridad:** Producción-ready (CSRF con tokens firmados + Origin/Referer). ✅ CRÍTICA-1 resuelta (depósitos conciliados inmutables). ⚠️ DT CRÍTICA-2 abierta (`base_datos` huérfano).
- **Observabilidad:** logger con rotación. ⚠️ DT-nueva-MEDIA-logging-ruido abierta.
- **i18n:** es/en/pap operativos. Diccionarios Python pendientes (deuda baja).

### 📋 Próximos pasos

1. **Fase D — Pre-Dockerización:** resolver CRÍTICA-2, MEDIA (productos populares vacío), logging ruidoso, 3 DTs nuevas financieras (desconciliación + ANULADO + whitelist), BAJA (mensajes IA), BAJA (endpoint huérfano) + MEDIA-BAJA (cierre jornada) (~8-10 h). **Siguiente tarea: MEDIA (Productos Populares vacío en tenant nuevo).**
2. **Fase E — Prueba de "tenant virgen"** (~2 h), post-Fase D.
3. **Fase G — Dockerización** (~22-32 h).
4. (Opcional/baja) **i18n de diccionarios Python** (~2-4 h).

### 📌 Estructura del HANDOFF (v9.6+)

- `HANDOFF.md` — **contexto actual** (se reescribe por sesión, ~400 líneas).
- `HANDOFF_v9.5.md` — **histórico congelado** (consulta para Dockerización o dudas históricas).
- `bitacora/2026-10-sesiones.md` — bitácora octubre (append-only).
- `bitacora/2026-11-sesiones.md` — bitácora noviembre (append-only).

**Regla:** cada sesión agrega su bitácora al final de `bitacora/YYYY-MM-sesiones.md` y actualiza `HANDOFF.md` (solo el estado, no el histórico).

---

## 2️⃣ Stack y estructura

- **Backend:** Python 3.10+, Flask 3.1.2, SQLAlchemy 2.0, PostgreSQL 17.10 (puerto **5433**), Flask-Login, Flask-WTF, Werkzeug, ReportLab, Matplotlib, **Flask-Babel 4.0.0** + **Babel 2.18.0**, logging con `RotatingFileHandler`.
- **BD:** `panaderia_master` — credenciales en `.env` (la contraseña local de postgres está en `HANDOFF_v9.5.md`; ⚠️ no copiarla a documentos públicos).
- **Frontend:** HTML5/CSS3, JS vanilla, Bootstrap 5.1.3, Chart.js, Font Awesome 6.

**Archivos clave**
- `app.py` (~13.300 líneas), `models.py` (~3.250), `reportes.py` (~3.600), `seed_demo.py` + `seeds/`.
- Multi-tenant: `middleware_saas.py`, `tenant_decorators.py`, `tenant_context.py`, `security_utils.py`.
- `migrations/sql/` — scripts SQL versionados (toppings, anulación ventas, total_anulaciones, idioma, `bajas_inventario`).
- `babel.cfg` (`[jinja2: **.html]`), `locales/{es,en,pap}/LC_MESSAGES/messages.{po,mo}` (los `.mo` se commitean).
- `templates/` (~56 + `_csrf_head.html` + `secciones/` con 4 parciales), `static/js/csrf-auto-inject.js`, `logs/` (ignorado por git).
- `.env` (protegido), `.env.example`, `requirements.txt`.
- Utilidades: `_limpiar_fuzzy.py` (CRÍTICO), `_ver_untraducciones.py` (bug conocido), `_audit_schema.py`, `_test_jinja.py` (usar solo nombre de archivo, no ruta), `_test_mo.py`, `_test_descuento.py`.

---

## 3️⃣ Tenants

| ID | Nombre | Subdominio | Plan | Licencia |
|----|--------|-----------|------|----------|
| 1 | Panadería Principal | principal | basico | local |
| 27 | **Panadería Demo** | panadería_demo | premium | nube_premium |

- **Producción real:** `tenant_1` + `tenant_27` (Demo, ~9.972 filas, `idioma = pap`).
- **Smoke test 31 Oct:** `tenant_29` (básico) + `tenant_30` (premium) — 16 puntos OK. ⚠️ Confirmar si se borraron o se conservan.
- ⚠️ Confirmar que `tenant_1` y `tenant_27` tengan la tabla `bajas_inventario` (aplicar migración si falta).
- `public` tiene SOLO 3 tablas: `tenants` (sin columna `licencia`), `usuarios` (fallback `dev_master`), `configuracion_panaderia`.
- `idioma` vive en `tenant_X.configuracion_sistema` (`VARCHAR(5) NOT NULL DEFAULT 'es'`; valores `es`, `en`, `pap`, `pt` futuro).
- `tenant_1.configuracion_sistema` tiene 6 filas con `panaderia_id` = 1, 5, 22, 24, 27, 28 (posible data legacy, no bloquea).

---

## 4️⃣ Usuarios

- **Roles:** `super_admin` (dev_master, todos los tenants), `admin_cliente` (total en su tenant), `supervisor` (producción, recetas, MP, proveedores, reportes), `cajero` (POS y cierre).
- **Usuarios:** tenant 1 → `dev_master`, `admin`, `admin_1`. Tenant 27 → `admin_27`, `super_27`, `cajero_27`.
- **Demo:** todos los usuarios del tenant_27 usan **`demo2026`**. `admin_27` tiene nombre `Administrador Panadería Demo` (sin espacio final).
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
| 10 | Gestión Financiera | ✅ (CRÍTICA-1 resuelta) |
| 11 | Reportes Profesionales | ✅ (i18n PDF y HTML 100% + donaciones separadas) |

**Features recientes (detalle en bitácoras)**
- Toppings: `9e645ba` — tabla `receta_toppings`, costos por gramos/lote, descuento de stock, `/api/calcular_ingredientes`.
- Anulación POS: `4ecfde9` — soft-delete `Venta.estado`, `/ventas_del_dia`, `POST /anular_venta/<id>`, blindaje de 11 consultas.
- Baja de Inventario: `ba48503` + `52696be` — `bajas_inventario` (motivo `VENCIMIENTO`/`ROTURA`), `/baja_inventario`, `/api/productos_vitrina`, `POST /registrar_baja`, costo desde receta; integrado en Estado de Resultados, Análisis de Gastos y Cierre de Caja.
- **Fix CRÍTICA-1 (1 Nov noche):** `5d289fd` — depósitos CONCILIADOS inmutables (backend 403 + frontend solo-lectura).
- **Fix MEDIA-ALTA (3 Nov):** `8304a16` — auditoría completa de donaciones/anuladas en cadena financiera (15 fixes) + fix `fecha_fin` a medianoche + columnas "Donaciones" en 2 templates.
- **Feature MEDIA-BAJA (4 Nov):** `607ac75` — Ventas del Día distingue donaciones (badge azul, tooltip, total tachado si anulada) + guard de rol en `anular_venta` (solo admin).

---

## 6️⃣ Últimos commits

```text
607ac75 feat(ventas-del-dia): distinguir donaciones con badge, tooltip y guard de rol
8304a16 fix(reportes): auditoría completa de donaciones/anuladas en cadena financiera
0da8b5b docs: reemplazar PENDIENTE_HASH por 5d289fd (hash real del commit CRITICA-1)
5d289fd fix(CRITICA-1): bloquear edición de depósitos CONCILIADOS (auditoría contable)
45e4655 docs: HANDOFF v9.6 liviano + bitacora mensual (oct/nov) + HANDOFF_v9.5 historico congelado
6173cfe fix: current_user detached — db.session.merge() en load_user (CRÍTICA-3 resuelta)
52696be cierre Feature Baja de Inventario + fix FK diferida fk_historial_inventario_orden_produccion
ba48503 feat(baja-inventario): schema BD + modelo ORM + migracion base
4ecfde9 feat(anulacion-pos): UI frontend, modal y blindaje de reportes financieros
1513c9a fix(anulacion-pos): cierre diario y vista excluyen ventas anuladas
7️⃣ Deuda técnica PENDIENTE
Tablas de DT resueltas (incluidas CRÍTICA-3 6173cfe, CRÍTICA-1 5d289fd, MEDIA-ALTA 8304a16, MEDIA-fecha_fin 8304a16, MEDIA-BAJA-ventas-donacion 607ac75): ver bitacora/.

Prioridad	DT	Descripción corta
🚨 CRÍTICA	DT-nueva-CRÍTICA-2	base_datos = tenant_{subdominio} vs schema real tenant_{id}
🟡 MEDIA	DT-nueva-MEDIA (productos populares)	Reporte "Productos Populares" vacío en tenant nuevo (SIGUIENTE TAREA)
🟡 MEDIA	DT-nueva-MEDIA-logging-ruido	Logging ruidoso en producción (20-30 líneas INFO por request de POS)
🟡 MEDIA	DT-nueva-MEDIA (desconciliación)	No existe endpoint para desconciliar depósitos (CONCILIADO es inmutable tras CRÍTICA-1)
🟡 MEDIA	DT-nueva-MEDIA (estado ANULADO sin flujo)	Modal permite setear estado='ANULADO' sin endpoint dedicado ni auditoría
🟡 MEDIA	DT-nueva-MEDIA (whitelist estado backend)	editar_deposito_bancario() acepta cualquier string en data['estado']
🟢 BAJA	DT-nueva-BAJA (mensajes IA)	Mensaje "datos insuficientes" en reportes IA
🟢 BAJA	DT-nueva-BAJA (endpoint huérfano)	Endpoint /reporte/ventas define def reporte_ventas() (app.py:8248) pero su template es ventas_periodo.html. NO existe def reporte_ventas_periodo. Opcional: renombrar en Fase D.
🟡 MEDIA-BAJA	DT-nueva-MEDIA-BAJA (cierre jornada)	models.py:2166 (cierre de jornada): query a Venta sin filtro panaderia_id, estado, es_donacion. Verificar si debe filtrar donaciones (jornada puede incluirlas por diseño). NO tocar sin auditoría de flujo de JornadaVentas.
🚨 CRÍTICA-2 — base_datos huérfano
Bug: crear_tenant_saas() genera base_datos = f"tenant_{subdominio}" pero el schema real es tenant_{id}.
Impacto: inconsistencia de diseño; en la nube, subdominio DNS y schema no coinciden.
Fix: unificar a tenant_{subdominio} en TODO el código (requiere migración de schemas existentes). Hacerla AL FINAL de Fase D, con pg_dump previo.
Ubicación: app.py (líneas ~988, 1899, 1935 + set_tenant_schema() + event listeners).

🟡 MEDIA — "Productos Populares" vacío en tenant nuevo
Bug: carga pero no muestra productos pese a haber ventas.
Fix: revisar query; verificar JOIN con detalle_venta y filtros por panaderia_id.
Ubicación: app.py (reporte_productos_populares) + reportes.py.

🟡 MEDIA — Logging ruidoso (DT-nueva-MEDIA-logging-ruido)
Bug: /punto_venta, /buscar_producto, /produccion_diaria, /recetas, /baja_inventario emiten 20-30 líneas logger.info por request. Con 500+ tenants → ~20M líneas/día.
Impacto: I/O innecesario, rotación rápida, ruido que entierra errores reales.
Fix: ① logger.info → logger.debug en logs de loop; ② INFO solo para eventos únicos; ③ nivel default WARNING en producción.
Ubicación: app.py (endpoints citados), logger_config.py. Estimación: ~1-2 h.

🟡 MEDIA — Desconciliación de depósitos
Contexto: CRÍTICA-1 hizo CONCILIADO inmutable. No hay flujo para desconciliar.
Fix: POST /depositos_bancarios/desconciliar/<id> con auditoría. Solo roles autorizados. Estimación: ~1 h.

🟡 MEDIA — Estado ANULADO sin flujo
Bug: el modal de edición permite setear estado='ANULADO' directamente (gestion_financiera.html:690-694), sin endpoint dedicado ni auditoría.
Fix: endpoint dedicado POST /depositos_bancarios/anular/<id> con auditoría. Estimación: ~45-60 min.

🟡 MEDIA — Whitelist estado backend
Bug: editar_deposito_bancario() acepta data['estado'] sin validar.
Fix: if data.get('estado') not in {...}: return 400. Estimación: 10 min (mismo commit que ANULADO).

🟢 BAJA — "Datos insuficientes" en reportes IA
Bug: con pocos datos (1 día) los PDFs salen sin información. Fix: mensaje explícito. Estimación: ~30 min.
Ubicación: reportes.py (generar_reporte_ia_predictivo, etc.).

Notas al pie (1 Nov + 3 Nov + 4 Nov)
DT-nueva-nota (1 Nov): resetear_password usa method='pbkdf2:sha256'; set_password usa scrypt por default. Ambos seguros. Cosmético.

DT-nueva-nota (1 Nov): app.py:13197 (/api/productos_vitrina) usa Receta.query.get(...) (legacy SQLAlchemy 1.x). Migrar a db.session.get(Receta, ...) en Fase D.

DT-nueva-nota (1 Nov, regla #10): findstr falla con tildes/emoji/UTF-8 multibyte. Usar powershell -Command "Select-String -Path ...".

DT-nueva-nota (3 Nov): Venta.fecha_hora <= fecha_fin truncaba a medianoche. Fix aplicado en reporte_productos_populares con fecha_fin_inclusive. Auditar futuras queries.

DT-nueva-nota (4 Nov): _test_jinja.py recibe solo el nombre del archivo, no la ruta completa. Ej: python _test_jinja.py ventas_del_dia.html (NO templates/ventas_del_dia.html).

Nota informativa (4 Nov, sin acción): el template recibo_pos.html no distingue donaciones visualmente (dice "RECIBO POS" + "Método: Efectivo" + "TOTAL: $0" sin indicar que fue una donación). Bajo impacto, no afecta lógica ni reportes. Si en el futuro se quiere mejorar, agregar texto "DONACIÓN" en el header si venta.es_donacion. NO es DT pendiente, solo nota.

Otras medias / bajas (heredadas, detalle en HANDOFF_v9.5.md sec. 9)
Medias: DT-37 F5-pulido · DT-37 F4.9 (libro_diario huérfano) · DT-NUEVA-1 (CREATE TABLE con idioma) · error 'ingreso' en generar_reporte_ia_predictivo · endpoint huérfano /generar_reporte_flujo_caja · overlap de labels en pie chart · i18n de diccionarios Python · mapeo Jinja2 de badges dinámicos · bug de _ver_untraducciones.py.

Cosmética crítica: emojis rotos en PDFs de ReportLab (Helvetica sin glyphs).

Bajas: filas legacy en tenant_1.configuracion_sistema · imports redundantes de os en app.py · "Fluho Neto" → "Flusho Neto" (PAP) · cierre_diario.html y ruta /cierre_diario huérfanos · renombrar "Historial de Ventas" en reportes.html:229 · datos demo hardcodeados en ventas_periodo.html · traducciones PAP heredadas · tenant_1.historial_inventario sin FK en orden_produccion_id.

8️⃣ Metodología de trabajo
Reglas de oro
Un paso a la vez con confirmación antes de continuar.

Diagnóstico ANTES de modificar. Soluciones de raíz, no parches.

TODO debe funcionar para futuros tenants.

Verificación con psql/findstr antes de avanzar. Commit después de cada fix verificado.

Backup (pg_dump) antes de cada cambio grande.

git status antes de commitear; git add <archivo> explícito; push tras el commit.

Detener el servidor antes de reiniciar. Verificar que no queden procesos python app.py corriendo con tasklist | findstr python (Windows). Causa raíz (4 Nov): 2 servidores simultáneos causaron cache confuso del navegador y diagnóstico erróneo.

Insertar bloques mostrando ANTES → DESPUÉS con número de línea exacto; compilar tras cada inserción (python -m py_compile app.py).

Deuda técnica detectada: anotarla (no tocarla), priorizar, decidir después.

Windows: findstr /c:"patrón" para búsquedas literales (con tildes/emoji puede fallar → usar powershell -Command "Select-String -Path ..."). Preferir scripts Python al copy-paste del chat (mojibake).

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

tenant_1 (plantilla) y tenant_27 (demo) DEBEN tener la misma estructura; toda migración se aplica a ambos.

FK diferida: si una tabla referencia a otra creada DESPUÉS en crear_tenant_saas(), NO poner la FK en el CREATE TABLE; agregarla al final con ALTER TABLE ... ADD CONSTRAINT ... FOREIGN KEY.

Todo cambio de schema se prueba con un tenant nuevo (básico y premium, 16 puntos) y se borra después.

search_path DEBE estar seteado antes de consultar modelos fuera de request.

producto_id puede ser NULL en historial_inventario. _descontar_ingredientes() DEBE registrar en HistorialInventario.

FKs ambiguas en SQLAlchemy: declarar foreign_keys='Tabla.columna' en el relationship.

load_user() debe devolver un objeto ATTACHED (db.session.merge(user)).

Antes de cambiar un patrón global, auditar con grep quién lo toca y correr un test de regresión.

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

Comandos útiles
cmd
chcp 65001
psql -U postgres -p 5433 -h localhost -d panaderia_master
python -m py_compile app.py
python app.py
findstr /n /c:"patrón exacto" archivo.py
powershell -Command "Select-String -Path archivo.py -Pattern 'patrón con tildes'"
git commit -F _commit_msg.txt && del _commit_msg.txt
pg_dump -U postgres -p 5433 -h localhost -d panaderia_master -F c -f backup_pre_XXX.backup

:: Verificar procesos Python corriendo (regla nueva 4 Nov)
tasklist | findstr python

:: Pipeline i18n
pybabel extract -F babel.cfg -o locales/messages.pot app.py models.py reportes.py templates
pybabel update -i locales/messages.pot -d locales
python _limpiar_fuzzy.py
pybabel compile -d locales --statistics

:: Estructura / constraints de una tabla
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_schema = 'tenant_27' AND table_name = 'historial_inventario' ORDER BY ordinal_position;"
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = 'tenant_27.historial_inventario'::regclass;"

:: Diagnóstico
python _audit_schema.py
python _test_jinja.py ventas_del_dia.html   ← SOLO nombre, NO ruta
python _test_mo.py
9️⃣ Plan pre-Dockerización (Fases A-G)
Objetivo: que models.py ↔ app.py ↔ BD estén sincronizados y que un tenant nuevo nazca 100% funcional. Prioridad CRÍTICA: no dockerizar sin completar A-F.

Fase	Alcance	Estimación
A — Auditoría de modelos	Mapear modelos, detectar huérfanos, FKs mal definidas, documentar estructura canónica	~2 h
B — Auditoría de app.py	Queries a tablas/columnas inexistentes, crear_tenant_saas() crea todo y en orden correcto	~2 h
C — Auditoría de BD	information_schema en tenant_1 vs tenant_27, modelos vs BD real, tablas huérfanas	~2 h
D — Sincronización + DT abiertas	Script SQL para alinear tenants, crear_tenant_saas(), models.py, migraciones; resolver las DT de la sección 7 (CRÍTICA-2 al final)	~8-10 h
E — Tenant virgen	Crear tenant desde cero, comparar columnas, flujo login → POS → venta → cierre → reporte, borrar el tenant	~2 h
F — Documentación y limpieza	docs/ESTRUCTURA_TENANT.md, eliminar código huérfano, actualizar HANDOFF	~2 h
G — Dockerización	requirements.txt completo, .mo commiteados, .env.example con todas las variables, Dockerfile + docker-compose.yml con PostgreSQL	~22-32 h
Riesgos: tablas creadas "al vuelo" en app.py sin estar en models.py; tenants antiguos con estructura distinta a un tenant nuevo; código huérfano; dependencias ocultas entre tablas; el renombre de schemas (CRÍTICA-2) es transversal y de alto riesgo.

Listo para Docker: ✅ CSRF con SECRET_KEY portable · ✅ logs a archivo + consola con rotación · ✅ sin dependencias de red específicas · ✅ i18n portable (.mo en el repo) · ✅ crear_tenant_saas() sin errores de FK · ✅ CRÍTICA-1 resuelta · ✅ cadena financiera auditada (donaciones/anuladas) · ✅ Ventas del Día con guard de rol para donaciones · 🟡 Fases A-F pendientes · 🟡 Dockerfile/compose por crear.

🔟 Notas estratégicas
Objetivo: ERP SaaS multi-tenant multi-país: POS, inventario, producción, recetas (toppings), activos fijos, reportes con IA, finanzas, i18n (es/en/pap), anulación de ventas, bajas de inventario, donaciones con auditoría; base para API REST + IA avanzada.

Mercado: 3.000-5.000 panaderías en Colombia · 10.000-30.000 en LATAM · Curazao-Antillas Holandesas (Papiamentu). Precio $60k-$600k COP/mes.

Licencias: Premium 3 usuarios · Básica 1 usuario.

Demo: fases 1-12 completas (~9.972 filas), contraseña demo2026, idioma = pap.

1️⃣1️⃣ Estado actual (resumen ejecutivo)
Aspecto	Estado
Último commit	607ac75 en origin/main (pusheado)
Módulos	11/11 completos (100%)
Fix 4 Nov	✅ MEDIA-BAJA (Ventas del Día donación) aplicada + guard de rol. Commit 607ac75.
Fix 3 Nov	✅ MEDIA-ALTA aplicada (15 fixes en cadena financiera) + fix fecha_fin. Commit 8304a16.
Fix 1 Nov (noche)	✅ CRÍTICA-1 aplicada, smoke test 7/7, pusheada
Fix 1 Nov (mañana)	✅ CRÍTICA-3 aplicada (6173cfe), test 6/6
Tests de regresión	✅ MEDIA-ALTA: 5 reportes validados con PDFs · ✅ MEDIA-BAJA: 3 escenarios validados (donación activa/anulada por cajero/admin)
Demo	✅ admin_27 / demo2026
Tenants productivos	tenant_1 + tenant_27
DT críticas abiertas	1: CRÍTICA-2 (base_datos huérfano)
DT medias abiertas	3: productos populares, logging ruidoso, desconciliación/ANULADO/whitelist
DT medias-bajas abiertas	1: cierre de jornada sin filtros
DT bajas abiertas	2: mensajes IA, endpoint huérfano
Siguiente tarea	MEDIA — Productos Populares vacío en tenant nuevo (~1 h)
Fase actual	Fase D (pre-Dockerización), ~8-10 h restantes
Dockerización	Fase G, ~22-32 h (post Fase D)
Working tree	nothing to commit, working tree clean
📞 Cómo continuar en un chat nuevo
Pegar este archivo como contexto inicial con esta instrucción:

"Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el HANDOFF.md v9.9 con el contexto actual (el histórico está en HANDOFF_v9.5.md y bitacora/). Por favor actúa como instructor guiando paso a paso, con la metodología del HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/PowerShell Select-String, commit tras cada fix verificado. Al insertar bloques, muéstrame ANTES → DESPUÉS con número de línea exacto. Tú me das LUZ VERDE cuando los cambios estén 100% validados. Yo aplico los cambios en mi editor. Primera tarea: MEDIA (Productos Populares vacío en tenant nuevo). Empieza con diagnóstico del endpoint reporte_productos_populares en app.py y del template productos_populares.html, sin modificar nada todavía."

Orden sugerido del resto de Fase D: MEDIA (Productos Populares) → MEDIA (logging ruidoso) → MEDIA (desconciliación + ANULADO + whitelist, en un solo commit) → BAJA (mensajes IA) → BAJA (endpoint huérfano) → MEDIA-BAJA (cierre jornada) → CRÍTICA-2 (al final, con backup completo).

Fin del HANDOFF.md — v9.9