# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP) — v9.10

**Última actualización:** 5 de Noviembre, 2026 (tarde)
**Último commit:** `6e7dbbf` (fix: CRÍTICA-4 colisión IDs + rotación <7d + IA KeyError)
**HANDOFF anterior:** `HANDOFF_v9.5.md` (histórico congelado, ver raíz del proyecto)
**Bitácoras históricas:** `bitacora/2026-10-sesiones.md`, `bitacora/2026-11-sesiones.md`
**Tenants de prueba:** `bitacora/tenants_prueba.md` (incluye `tenant_31`)

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
- **Estado:** v1.9.3 — **11/11 módulos completos (100%)** + i18n PDF/HTML 100% + Features Toppings, Anulación POS y Baja de Inventario 100%.
- **Arquitectura:** Multi-tenant con PostgreSQL (un schema por tenant).
- **Seguridad:** Producción-ready (CSRF con tokens firmados + Origin/Referer). ✅ CRÍTICA-1 resuelta. ⚠️ DT CRÍTICA-2 abierta (`base_datos` huérfano).
- **Observabilidad:** logger con rotación. ⚠️ DT-nueva-MEDIA-logging-ruido abierta.
- **i18n:** es/en/pap operativos. Diccionarios Python pendientes (deuda baja).

### 📋 Próximos pasos

1. **Fase D — Pre-Dockerización:** resolver CRÍTICA-2, logging ruidoso, 3 DTs nuevas financieras (desconciliación + ANULADO + whitelist), BAJA (endpoint huérfano), MEDIA-BAJA (cierre jornada) (~8-10 h). **Siguiente tarea: Commit 2 (rediseño "menos es más" + recomendaciones dinámicas en `productos_populares.html`).**
2. **Fase E — Prueba de "tenant virgen"** (~2 h), post-Fase D. Verificar Bug A (posible caché en `producto_externo_id`).
3. **Fase G — Dockerización** (~22-32 h).
4. (Opcional/baja) **i18n de diccionarios Python** (~2-4 h).

### 📌 Estructura del HANDOFF (v9.6+)

- `HANDOFF.md` — **contexto actual** (se reescribe por sesión, ~400 líneas).
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
- `app.py` (~13.300 líneas), `models.py` (~3.250), `reportes.py` (~3.600), `seed_demo.py` + `seeds/`.
- Multi-tenant: `middleware_saas.py`, `tenant_decorators.py`, `tenant_context.py`, `security_utils.py`.
- `migrations/sql/` — scripts SQL versionados (toppings, anulación ventas, total_anulaciones, idioma, `bajas_inventario`).
- `babel.cfg` (`[jinja2: **.html]`), `locales/{es,en,pap}/LC_MESSAGES/messages.{po,mo}` (los `.mo` se commitean).
- `templates/` (~56 + `_csrf_head.html` + `secciones/` con 4 parciales), `static/js/csrf-auto-inject.js`, `logs/` (ignorado por git).
- `.env` (protegido), `.env.example`, `requirements.txt`.
- Utilidades: `_limpiar_fuzzy.py` (CRÍTICO), `_ver_untraducciones.py` (bug conocido), `_audit_schema.py`, `_test_jinja.py` (usar solo nombre de archivo, no ruta), `_test_mo.py`, `_test_descuento.py`.

---

## 3️⃣ Tenants

| ID | Nombre | Subdominio | Plan | Licencia | Estado | Notas |
|----|--------|-----------|------|----------|--------|-------|
| 1 | Panadería Principal | principal | basico | local | Producción | Plantilla multi-tenant. `base_datos=panaderia_principal.db` (legacy). |
| 27 | **Panadería Demo** | panadería_demo | premium | nube_premium | Producción | Demo comercial, `demo2026`. `base_datos=tenant_panadería_demo` (≠ schema `tenant_27`). |
| 31 | **Diagnóstico Productos Populares** | diagnóstico_producto | basico | nube_basica | **Pruebas** | **Tenant de pruebas** (diagnóstico 5 Nov). Usuario `admin_31`. Sin acceso a reportes premium. Detalle en `bitacora/tenants_prueba.md`. |

- **Producción real:** `tenant_1` + `tenant_27` (Demo, ~9.972 filas, `idioma = pap`).
- **Pruebas:** `tenant_31` (básico, ~10 filas). Conservado para futuras pruebas de tenants nuevos/básicos.
- `public` tiene SOLO 3 tablas: `tenants` (sin columna `licencia`), `usuarios` (fallback `dev_master`), `configuracion_panaderia`.
- `idioma` vive en `tenant_X.configuracion_sistema` (`VARCHAR(5) NOT NULL DEFAULT 'es'`; valores `es`, `en`, `pap`, `pt` futuro).
- `tenant_1.configuracion_sistema` tiene 6 filas con `panaderia_id` = 1, 5, 22, 24, 27, 28 (posible data legacy, no bloquea).

---

## 4️⃣ Usuarios

- **Roles:** `super_admin` (dev_master, todos los tenants), `admin_cliente` (total en su tenant), `supervisor` (producción, recetas, MP, proveedores, reportes), `cajero` (POS y cierre).
- **Usuarios:** tenant 1 → `dev_master`, `admin`, `admin_1`. Tenant 27 → `admin_27`, `super_27`, `cajero_27`. Tenant 31 → `admin_31`, `super_31`, `cajero_31`.
- **Demo:** todos los usuarios del tenant_27 usan **`demo2026`**. `admin_27` tiene nombre `Administrador Panadería Demo` (sin espacio final).
- **Tenant de pruebas:** `admin_31` (pass en `bitacora/tenants_prueba.md`, rotada 5 Nov).
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
| 11 | Reportes Profesionales | ✅ (i18n PDF y HTML 100% + donaciones separadas + rotación <7d) |

**Features recientes (detalle en bitácoras)**
- Toppings: `9e645ba` — tabla `receta_toppings`, costos por gramos/lote, descuento de stock, `/api/calcular_ingredientes`.
- Anulación POS: `4ecfde9` — soft-delete `Venta.estado`, `/ventas_del_dia`, `POST /anular_venta/<id>`, blindaje de 11 consultas.
- Baja de Inventario: `ba48503` + `52696be` — `bajas_inventario` (motivo `VENCIMIENTO`/`ROTURA`), `/baja_inventario`, `/api/productos_vitrina`, `POST /registrar_baja`, costo desde receta; integrado en Estado de Resultados, Análisis de Gastos y Cierre de Caja.
- **Fix CRÍTICA-1 (1 Nov):** `5d289fd` — depósitos CONCILIADOS inmutables (backend 403 + frontend solo-lectura).
- **Fix MEDIA-ALTA (3 Nov):** `8304a16` — auditoría completa de donaciones/anuladas en cadena financiera (15 fixes) + fix `fecha_fin` a medianoche.
- **Fix MEDIA-BAJA (4 Nov):** `607ac75` — Ventas del Día distingue donaciones (badge, tooltip, guard de rol).
- **Fix CRÍTICA-4 + Bug B + IA (5 Nov):** `6e7dbbf` — colisión IDs int/ext en Productos Populares + rotación <7d → "—" + KeyError en `_generar_recomendaciones_ia`.

---

## 6️⃣ Últimos commits

```text
6e7dbbf fix(reportes): CRÍTICA-4 colisión IDs int/ext + rotación <7d a '—' + IA KeyError
f694ae5 docs: HANDOFF v9.9 + bitácora sesión 4 Nov (MEDIA-BAJA + regla doble servidor)
607ac75 feat(ventas-del-dia): distinguir donaciones con badge, tooltip y guard de rol
8304a16 fix(reportes): auditoría completa de donaciones/anuladas en cadena financiera
0da8b5b docs: reemplazar PENDIENTE_HASH por 5d289fd (hash real del commit CRITICA-1)
5d289fd fix(CRITICA-1): bloquear edición de depósitos CONCILIADOS (auditoría contable)
6173cfe fix: current_user detached — db.session.merge() en load_user (CRÍTICA-3 resuelta)
7️⃣ Deuda técnica PENDIENTE
✅ Cerradas en sesión 5 Nov (commit 6e7dbbf)
Prioridad	DT	Descripción
✅ CRÍTICA-4	Colisión IDs int/ext en reporte_productos_populares	
✅ Bug B	Rotación <7 días → — (días reales del tenant)	
✅ DT-BAJA-mensajes-IA	KeyError en _generar_recomendaciones_ia	
🚨 Pendientes (orden de prioridad)
Prioridad	DT	Descripción corta
🚨 CRÍTICA	DT-nueva-CRÍTICA-2	base_datos = tenant_{subdominio} vs schema real tenant_{id} (reproducida en vivo en tenant_31). Fix al final de Fase D, con pg_dump previo.
🟡 MEDIA	DT-nueva-MEDIA-logging-ruido	Logging ruidoso en producción (20-30 líneas INFO por request).
🟡 MEDIA	DT-nueva-MEDIA (desconciliación)	No existe endpoint para desconciliar depósitos (CONCILIADO inmutable tras CRÍTICA-1).
🟡 MEDIA	DT-nueva-MEDIA (estado ANULADO sin flujo)	Modal permite setear estado='ANULADO' sin endpoint dedicado ni auditoría.
🟡 MEDIA	DT-nueva-MEDIA (whitelist estado backend)	editar_deposito_bancario() acepta cualquier string en data['estado'].
🟡 MEDIA	Commit 2 (rediseño)	"Menos es más" en productos_populares.html + recomendaciones dinámicas. Próxima tarea.
🟢 BAJA	DT-nueva-BAJA (endpoint huérfano)	/reporte/ventas define def reporte_ventas() (app.py:8248) pero su template es ventas_periodo.html. Opcional: renombrar en Fase D.
🟡 MEDIA-BAJA	DT-nueva-MEDIA-BAJA (cierre jornada)	models.py:2166 (cierre de jornada): query a Venta sin filtro panaderia_id, estado, es_donacion. Verificar sin auditoría.
📋 Otras medias / bajas (heredadas, detalle en HANDOFF_v9.5.md sec. 9)
Medias: DT-37 F5-pulido · DT-37 F4.9 (libro_diario huérfano) · DT-NUEVA-1 (CREATE TABLE con idioma) · error 'ingreso' en generar_reporte_ia_predictivo (✅ cerrada 5 Nov) · endpoint huérfano /generar_reporte_flujo_caja · overlap de labels en pie chart · i18n de diccionarios Python · mapeo Jinja2 de badges dinámicos · bug de _ver_untraducciones.py.

Cosmética crítica: emojis rotos en PDFs de ReportLab (Helvetica sin glyphs).

Bajas: filas legacy en tenant_1.configuracion_sistema · imports redundantes de os en app.py · "Fluho Neto" → "Flusho Neto" (PAP) · cierre_diario.html y ruta /cierre_diario huérfanos · renombrar "Historial de Ventas" en reportes.html:229 · datos demo hardcodeados en ventas_periodo.html · traducciones PAP heredadas · tenant_1.historial_inventario sin FK en orden_produccion_id.

🔍 Hallazgos 5 Nov (diagnóstico con tenant_31)
CRÍTICA-2 reproducida en vivo: tenant_31.base_datos = tenant_diagnóstico_producto vs schema real tenant_31. tenant_27 ya mostraba la inconsistencia (tenant_panadería_demo vs tenant_27), pero era data legacy. tenant_31 la reproduce en runtime limpio. Evidencia empírica para el fix final de Fase D.

Bug A (nota, no es CRÍTICA): En el primer día de vida del tenant, detalle_venta.producto_externo_id quedó NULL en 2 ventas con externos. Tras reiniciar servidor, las filas se "corrigieron". No reproducible. Hipótesis: caché/ORM en primer arranque. Verificar en Fase E.

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

Verificación con psql/findstr antes de avanzar. Commit después de cada fix verificado.

Backup (pg_dump) antes de cada cambio grande.

git status antes de commitear; git add <archivo> explícito; push tras el commit.

Detener el servidor antes de reiniciar. Verificar con tasklist | findstr python. netstat -ano | findstr :5000 → 1 sola línea LISTENING (nueva regla 5 Nov, refuerza regla 4 Nov de doble servidor).

Antes de testear templates, modo incógnito + servidor reiniciado (nueva regla 5 Nov, por caché del navegador).

Insertar bloques mostrando ANTES → DESPUÉS con número de línea exacto; compilar tras cada inserción (python -m py_compile app.py).

Deuda técnica detectada: anotarla (no tocarla), priorizar, decidir después.

Windows: findstr /c:"patrón" para búsquedas literales (con tildes/emoji puede fallar → usar powershell -Command "Select-String -Path ..." o script Python). Preferir scripts Python al copy-paste del chat (mojibake).

git commit -F _commit_msg.txt (UTF-8) para mensajes con tildes/emojis (nueva regla 5 Nov).

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

Todo cambio de schema se prueba con un tenant nuevo (básico y premium, 16 puntos). tenant_31 sirve como tenant de pruebas básico.

search_path DEBE estar seteado antes de consultar modelos fuera de request.

producto_id puede ser NULL en historial_inventario. _descontar_ingredientes() DEBE registrar en HistorialInventario.

FKs ambiguas en SQLAlchemy: declarar foreign_keys='Tabla.columna' en el relationship.

load_user() debe devolver un objeto ATTACHED (db.session.merge(user)).

Antes de cambiar un patrón global, auditar con grep quién lo toca y correr un test de regresión.

Colisión de IDs int/ext: cuando dos tablas (productos, productos_externos) tienen su propio id autoincremental, los id colisionan (ej. Pan Prueba id=1 y Agua id=1). Usar prefijos (int_, ext_) al armar claves de diccionarios. Regla nueva 5 Nov.

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

Rotación <7 días: si el tenant tiene menos de 7 días de vida, rotacion_promedio = None (template muestra —). Criterio: dias_reales_tenant desde la primera venta del tenant. Regla nueva 5 Nov.

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
9️⃣ Plan pre-Dockerización (Fases A-G)
Objetivo: que models.py ↔ app.py ↔ BD estén sincronizados y que un tenant nuevo nazca 100% funcional. Prioridad CRÍTICA: no dockerizar sin completar A-F.

Fase	Alcance	Estimación
A — Auditoría de modelos	Mapear modelos, detectar huérfanos, FKs mal definidas, documentar estructura canónica	~2 h
B — Auditoría de app.py	Queries a tablas/columnas inexistentes, crear_tenant_saas() crea todo y en orden correcto	~2 h
C — Auditoría de BD	information_schema en tenant_1 vs tenant_27, modelos vs BD real, tablas huérfanas	~2 h
D — Sincronización + DT abiertas	Script SQL para alinear tenants, crear_tenant_saas(), models.py, migraciones; resolver las DT de la sección 7 (CRÍTICA-2 al final)	~8-10 h
E — Tenant virgen	Crear tenant desde cero, comparar columnas, flujo login → POS → venta → cierre → reporte, borrar el tenant. Verificar Bug A (caché producto_externo_id).	~2 h
F — Documentación y limpieza	docs/ESTRUCTURA_TENANT.md, eliminar código huérfano, actualizar HANDOFF	~2 h
G — Dockerización	requirements.txt completo, .mo commiteados, .env.example con todas las variables, Dockerfile + docker-compose.yml con PostgreSQL	~22-32 h
Riesgos: tablas creadas "al vuelo" en app.py sin estar en models.py; tenants antiguos con estructura distinta a un tenant nuevo; código huérfano; dependencias ocultas entre tablas; el renombre de schemas (CRÍTICA-2) es transversal y de alto riesgo.

Listo para Docker: ✅ CSRF con SECRET_KEY portable · ✅ logs a archivo + consola con rotación · ✅ sin dependencias de red específicas · ✅ i18n portable (.mo en el repo) · ✅ crear_tenant_saas() sin errores de FK · ✅ CRÍTICA-1 resuelta · ✅ cadena financiera auditada (donaciones/anuladas) · ✅ Ventas del Día con guard de rol para donaciones · ✅ CRÍTICA-4 resuelta · ✅ Bug B (rotación) resuelto · ✅ IA KeyError resuelto · 🟡 Fases A-F pendientes · 🟡 Dockerfile/compose por crear.

🔟 Notas estratégicas
Objetivo: ERP SaaS multi-tenant multi-país: POS, inventario, producción, recetas (toppings), activos fijos, reportes con IA, finanzas, i18n (es/en/pap), anulación de ventas, bajas de inventario, donaciones con auditoría; base para API REST + IA avanzada.

Mercado: 3.000-5.000 panaderías en Colombia · 10.000-30.000 en LATAM · Curazao-Antillas Holandesas (Papiamentu). Precio $60k-$600k COP/mes.

Licencias: Premium 3 usuarios · Básica 1 usuario.

Demo: fases 1-12 completas (~9.972 filas), contraseña demo2026, idioma = pap.

1️⃣1️⃣ Estado actual (resumen ejecutivo)
Aspecto	Estado
Último commit	6e7dbbf en origin/main (pusheado)
Módulos	11/11 completos (100%)
Fix 5 Nov	✅ CRÍTICA-4 + Bug B + IA KeyError aplicados. Commit 6e7dbbf.
Fix 4 Nov	✅ MEDIA-BAJA (Ventas del Día donación) aplicada + guard de rol. Commit 607ac75.
Fix 3 Nov	✅ MEDIA-ALTA aplicada (15 fixes en cadena financiera) + fix fecha_fin. Commit 8304a16.
Fix 1 Nov (noche)	✅ CRÍTICA-1 aplicada, smoke test 7/7, pusheada
Fix 1 Nov (mañana)	✅ CRÍTICA-3 aplicada (6173cfe), test 6/6
Tests de regresión	✅ CRÍTICA-4: Top 10 con Agua + Pan Prueba separados · ✅ Bug B: rotación — en <7d, real en tenant_27 · ✅ IA: "Producto estrella: Pan de Yema" en PDF tenant_27
Demo	✅ admin_27 / demo2026
Tenants productivos	tenant_1 + tenant_27
Tenants de pruebas	tenant_31 (básico, diagnóstico 5 Nov)
DT críticas abiertas	1: CRÍTICA-2 (base_datos huérfano)
DT medias abiertas	4: logging ruidoso, desconciliación/ANULADO/whitelist, rediseño (Commit 2)
DT medias-bajas abiertas	1: cierre de jornada sin filtros
DT bajas abiertas	1: endpoint huérfano
Siguiente tarea	Commit 2 (rediseño "menos es más" + recomendaciones dinámicas en productos_populares.html) (~4-6 h)
Fase actual	Fase D (pre-Dockerización), ~8-10 h restantes
Dockerización	Fase G, ~22-32 h (post Fase D)
Working tree	nothing to commit, working tree clean
📞 Cómo continuar en un chat nuevo
Pegar este archivo como contexto inicial con esta instrucción:

"Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el HANDOFF.md v9.10 con el contexto actual (el histórico está en HANDOFF_v9.5.md, bitácoras en bitacora/, tenants de prueba en bitacora/tenants_prueba.md). Por favor actúa como instructor guiando paso a paso, con la metodología del HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/PowerShell Select-String, commit tras cada fix verificado. Al insertar bloques, muéstrame ANTES → DESPUÉS con número de línea exacto. Tú me das LUZ VERDE cuando los cambios estén 100% validados. Yo aplico los cambios en mi editor. Primera tarea: Commit 2 (rediseño "menos es más" + recomendaciones dinámicas en productos_populares.html). Empieza con diagnóstico del template actual y la lógica de recomendaciones."

Orden sugerido del resto de Fase D: Commit 2 (rediseño) → MEDIA (logging ruidoso) → MEDIA (desconciliación + ANULADO + whitelist, un solo commit) → BAJA (endpoint huérfano) → MEDIA-BAJA (cierre jornada) → CRÍTICA-2 (al final, con backup completo).

---

## 1️⃣2️⃣ Roadmap a Producción (Nota personal de Mauricio)

> **Objetivo:** lanzar PanaderíaPro a producción en **enero 2027** (inicio de mes).
> **Modalidad:** trabajo solo, part-time (~10-15 h/semana).
> **Ventana:** 8 semanas (5 Nov 2026 → 1 Ene 2027), ~80-120 h disponibles.

### Estado actual (5 Nov 2026)

| Aspecto | % Listo |
|---|---|
| **Funcionalidad (features)** | ~90% |
| **Producción-ready (infra)** | ~20% |
| **Deuda técnica (Fase D)** | 15-22 h restantes |
| **Bloqueantes críticos** | 8 |
| **Estimación total** | 54-74 h (7-9 jornadas de 8 h) |

### Cronograma propuesto (8 semanas part-time)

| Semana | Foco | Estimación | Entregable |
|---|---|---|---|
| **1 (5-11 Nov)** | Cerrar Fase D: Commit 2 (rediseño) + logging ruidoso | ~6-8 h | `productos_populares.html` rediseñado, logging limpio |
| **2 (12-18 Nov)** | Cerrar Fase D: desconciliación + ANULADO + whitelist + endpoint huérfano + cierre jornada | ~6-8 h | Commits independientes, DTs cerradas |
| **3 (19-25 Nov)** | **CRÍTICA-2** (renombrar schemas) con `pg_dump` previo | ~6-8 h | Schemas alineados (`tenant_{id}` en todo el código) |
| **4 (26-2 Dic)** | **Fase E**: tenant virgen + verificar Bug A (caché `producto_externo_id`) | ~4-6 h | Tenant de prueba creado desde cero, smoke test OK |
| **5 (3-9 Dic)** | **Docker**: `Dockerfile` + `docker-compose.yml` + `.env.example` completo | ~8-12 h | Stack dockerizado local (Flask + PostgreSQL + Nginx) |
| **6 (10-16 Dic)** | **WSGI production** (`gunicorn`/`waitress`) + SSL + Nginx reverse proxy | ~6-8 h | Deploy reproducible en VPS local |
| **7 (17-23 Dic)** | **Backup automático** + logging a stdout + `/health` + monitoreo básico | ~6-8 h | Observabilidad mínima operativa |
| **8 (24-30 Dic)** | **Deploy a VPS real** + hardening + documentación + smoke test producción | ~8-10 h | Producción lista (o casi) |
| **31 Dic - 1 Ene** | **Buffer** (imprevistos) + capacitación usuarios | ~4-6 h | Lanzamiento |

**Total estimado:** ~50-66 h + buffer. **Realista con tu plan.**

### Prioridades (si algo se atrasa)

**P0 (sin esto no hay producción):**
1. CRÍTICA-2 (schemas alineados).
2. Docker + WSGI + SSL.
3. Backup automático.
4. `/health` endpoint.
5. Variables de entorno producción.

**P1 (importante pero puede esperar 1-2 semanas post-lanzamiento):**
- CI/CD (GitHub Actions).
- Monitoreo avanzado (Sentry, Prometheus).
- Rate limiting.
- Tests automatizados (pytest).

**P2 (deseables, post-lanzamiento):**
- i18n de diccionarios Python.
- API REST.
- Dashboard de admin.
- Rotación automática de contraseñas.

### Riesgos identificados

1. **CRÍTICA-2 es transversal:** renombrar schemas de `tenant_1` + `tenant_27` + `tenant_31` puede romper si no hay `pg_dump` previo. **Hacer al final de Fase D, con backup completo.**
2. **`tenant_27` (demo) tiene `base_datos` inconsistente:** CRÍTICA-2 lo resuelve, pero hay que decidir si se migra o se borra antes del lanzamiento.
3. **Bug A (caché `producto_externo_id`):** verificar en Fase E. Si se reproduce, escalar a CRÍTICA-5.
4. **Sin tests automatizados:** la validación es manual (screenshots + PDFs). Post-lanzamiento, agregar `pytest` con 20-30 tests de humo.
5. **Lógica `<7 días` en reportes:** cada tenant nuevo va a ver `—` en rotación hasta los 7 días. **Documentar en onboarding.**

### Decisiones pendientes (para antes del deploy)

- **Proveedor de VPS:** Hetzner (€5/mes) vs DigitalOcean ($6/mes) vs AWS Lightsail ($5/mes). **Recomendación:** Hetzner CX22 (mejor relación precio/rendimiento en Europa) o DigitalOcean (más amigable, más datacenters).
- **Dominio:** ¿ya tenés? (ej. `panaderiapro.com`). ¿Usarás subdominios por tenant (`cliente1.panaderiapro.com`)?
- **SSL:** Let's Encrypt (gratis, auto-renovable).
- **Backup:** `pg_dump` diario + retención 7 días + copia semanal a almacenamiento externo (S3, Backblaze).
- **`tenant_27` (demo):** ¿se migra a la nube o se crea una demo nueva con datos reales?
- **Precio final de licencias:** Premium $X COP/mes, Básica $Y COP/mes.

### Criterios de "listo para producción"

- [ ] Los 3 tenants (1, 27, 31) tienen schema correcto (`tenant_{id}`).
- [ ] `docker-compose up` levanta el stack local sin errores.
- [ ] HTTPS funciona con certificado válido.
- [ ] `/health` responde 200 OK.
- [ ] Backup automático corriendo (verificar restaurando 1 backup).
- [ ] Logs van a stdout + rotación.
- [ ] Smoke test de producción: login → POS → venta → cierre → reporte → PDF.
- [ ] `dev_master` + 2 tenants productivos creados.
- [ ] Documentación de deploy en `docs/DEPLOY.md`.
- [ ] Rollback plan documentado.

### Notas personales

- **No dockerizar hasta completar Fases A-F.** (Regla del HANDOFF v9.10.)
- **CRÍTICA-2 al final, con backup.** No antes.
- **Cada semana, actualizar este roadmap** con lo hecho + lo pendiente.
- **Si algo se atrasa, priorizar P0 sobre P1 y P2.**
- **El lanzamiento es "soft launch"** (2-3 clientes beta) antes de marketing masivo.

---

**Fin del HANDOFF.md — v9.10**
