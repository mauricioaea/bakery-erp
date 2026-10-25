# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP)

**Última actualización:** 24 de Octubre, 2026
**Último commit:** `9e645ba` (feat: agregar toppings a recetas con calculo de costos, descuento de stock, historial de inventario y visualizacion en modal de produccion)
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

---

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp)
- **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.9.1 — **11/11 módulos completados (100%)** + **DT-37 F4 100%** + **DT-37 F5 100%** + **Feature Toppings 100%**.
- **Arquitectura:** Multi-tenant con PostgreSQL (schemas por tenant).
- **Seguridad:** Producción-ready (CSRF con tokens firmados + Origin/Referer + logging centralizado).
- **Observabilidad:** Producción-ready (logger con rotación de archivos, niveles configurables).
- **i18n:** 3 idiomas operativos (es/en/pap) en PDF reportes (100%) y HTML reportes (100%). Diccionarios Python pendientes (DT-nueva-media-baja).

### 📋 Próximos pasos planificados (ver sección 2️⃣6️⃣)

1. **Anulación de recibos POS** (~3-5 h) — Media-alta.
2. **i18n de diccionarios Python** (~2-4 h) — Baja (si es necesario; sino dejar como está).
3. **Auditoría ORM ↔ BD** (verificar con git que no haya discrepancias).
4. **Crear tenant nuevo + smoke test** (verificar que todo funcione).
5. **Pre-Dockerización (Fases A-F)** (~13-15 h) — CRÍTICA.
6. **Dockerización (Fase G)** (~22-32 h).

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
- `app.py` (~12.700 líneas) — aplicación principal
- `models.py` (~3.100 líneas) — modelos SQLAlchemy
- `reportes.py` (~3.600 líneas) — generación PDF
- `seed_demo.py` (~450 líneas) — seed del Demo
- `seeds/` — 11 fases del seed
- `middleware_saas.py`, `tenant_decorators.py`, `tenant_context.py` — multi-tenant
- `security_utils.py` — utilidades de seguridad multi-tenant
- `migrations/sql/` — scripts SQL versionados
  - `2026-10-24_add_receta_toppings.sql` (nuevo)
- **`babel.cfg`** — config extracción strings (`[jinja2: **.html]`)
- **`locales/`** — catálogos de traducción
  - `locales/messages.pot` — plantilla (**~771 msgids**)
  - `locales/es/LC_MESSAGES/messages.{po,mo}` — español (fallback)
  - `locales/en/LC_MESSAGES/messages.{po,mo}` — inglés (**~767 traducidos, 99%**)
  - `locales/pap/LC_MESSAGES/messages.{po,mo}` — papiamentu Curazao (**~766 traducidos, 99%**)
- `templates/` (54 templates + `_csrf_head.html` partial + subcarpeta `secciones/` con 4 parciales)
- `static/js/` — incluye `csrf-auto-inject.js`
- `logs/` — archivo rotativo `panaderia.log` (ignorado por git)
- `.env` (protegido), `.env.example` (plantilla)
- `requirements.txt` — incluye `Flask-WTF==1.3.0`, `WTForms==3.2.2`, `Flask-Babel==4.0.0`, `Babel==2.18.0`
- `HANDOFF.md` — este archivo
- **`_limpiar_fuzzy.py`** — script de utilidad (CRÍTICO en F5)
- **`_ver_untraducciones.py`** — script de utilidad (diagnóstico i18n — tiene bug conocido, ver DT-nueva-baja)

---

## 3️⃣ Tenants activos

| ID | Nombre | Subdominio | Plan | Licencia |
|----|--------|-----------|------|----------|
| 1 | Panadería Principal | principal | basico | local |
| 27 | **Panadería Demo** | panadería_demo | premium | nube_premium |

**Tenant principal del Demo:** `tenant_27` ("Panadería Demo").
**Tenants de producción real:** `tenant_1` (Principal) + `tenant_27` (Demo).
**Estado de `tenant_1`:** ✅ Alineado (tiene `receta_toppings` + `historial_inventario` con 12 columnas + `producto_id` nullable).
**Estado de `tenant_27`:** ✅ Re-seedeado el 5 Oct (9.968 filas) + ventas acumuladas + toppings. `idioma = pap`.

### 📌 Arquitectura de `public.*` (post-DT-36)

**`public` tiene SOLO 3 tablas:**

| Tabla | Rol | Filas |
|---|---|---|
| `public.tenants` | Maestra de tenants | 2 |
| `public.usuarios` | Fallback de `dev_master` (login) | 3 |
| `public.configuracion_panaderia` | Espejo de config por tenant | 1 |

**Columnas reales de `public.tenants`:**
`id`, `nombre`, `subdominio`, `base_datos`, `fecha_creacion`, `activo`, `plan`, `fecha_vencimiento`, `fecha_expiracion`.
**NO tiene columna `licencia`.**

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

### Datos de facturación (por tenant)
- Configurables en `/configuracion/facturacion`.
- Se guardan en `ConfiguracionSistema` (dentro del schema del tenant). Fallback: `ConfiguracionPanaderia`.
- Incluye: tipo_facturacion, nombre_empresa, moneda, usa_centavos, simbolo_moneda, **idioma**.

---

## 5️⃣ Estado de los módulos (11/11 = 100%)

| # | Módulo | Estado |
|---|--------|--------|
| 1 | Punto de Venta | ✅ COMPLETO (⚠️ ver Feature Anulación Recibos) |
| 2 | Producción Diaria | ✅ COMPLETO (con toppings) |
| 3 | Productos Externos | ✅ COMPLETO |
| 4 | Recetas y Fórmulas | ✅ COMPLETO (**con toppings**) |
| 5 | Materias Primas | ✅ COMPLETO |
| 6 | Proveedores | ✅ COMPLETO |
| 7 | Gestión de Clientes (solo dev_master) | ✅ COMPLETO |
| 8 | Activos Fijos | ✅ COMPLETO |
| 9 | Gestión de Usuarios + Mi Perfil | ✅ COMPLETO |
| 10 | Gestión Financiera | ✅ COMPLETO |
| 11 | Reportes Profesionales | ✅ COMPLETO (i18n PDF: 100%; HTML: 100%) |

---

## 6️⃣ Últimos commits pusheados

```text
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
7️⃣ Demo — Estado de las fases del seed
#	Fase	Estado	Filas
1	Configuración base	✅	9
2	Proveedores	✅	6
3	Materias primas	✅	17
4	Recetas y fórmulas	✅	12 recetas / 80 ingredientes
5	Productos	✅	12
6	Producción diaria	✅	~2.416
7	Ventas	✅	~7.033 (+4 del smoke test)
8	Productos externos	✅	12
9	Activos fijos	✅	36
10	Movimientos financieros	✅	261
11	Cierres diarios	✅	90
12	Reset automatizado	✅	—
Total aproximado: ~9.972 filas en tenant_27.

8️⃣ Configuración crítica
Variables de entorno (.env)
text
DATABASE_URL=postgresql://postgres:...@localhost:5433/panaderia_master
DB_PASSWORD=...
FLASK_ENV=development
SECRET_KEY=...
⚠️ SECRET_KEY es crítica para: sesiones Flask, firma de tokens CSRF, firma de cookies seguras.

Rutas críticas
F4 (reportes.py — PDFs): todas ✅ i18n es/en/pap.

F5 (templates HTML): todas ✅ i18n es/en/pap (14 archivos migrados).

Feature Toppings (NUEVO):

/crear_receta — formulario con toppings.

/editar_receta/<id> — edición con toppings.

/detalle_receta/<id> — sección "Toppings".

/produccion_diaria — modal "Ordenar" con toppings.

/api/calcular_ingredientes/<id> — API con toppings.

9️⃣ Deuda técnica acumulada
✅ RESUELTAS el 24 Octubre 2026 (noche) — Feature Toppings
#	Descripción	Commit
Feature	Nueva tabla receta_toppings + CHECK constraint	9e645ba
Feature	Cálculo de costos con toppings (gramos por lote)	9e645ba
Feature	Descuento de stock (ingredientes + toppings)	9e645ba
Feature	Historial de inventario (con toppings)	9e645ba
Feature	Formulario de toppings en crear/editar receta	9e645ba
Feature	Sección "Toppings" en detalle de receta	9e645ba
Feature	Modal de producción con toppings (en gramos)	9e645ba
Feature	Endpoint /api/calcular_ingredientes con toppings	9e645ba
Bug	Panaderia(panaderia_id=...) — argumento inválido	9e645ba
Bug	producto_id NOT NULL en historial_inventario	9e645ba
Bug	search_path no seteado en _descontar_ingredientes()	9e645ba
Bug	Modelo HistorialInventario desalineado con BD	9e645ba
Bug	JS roto en crear_receta.html (âO DEL FORMULARIO)	9e645ba
Bug	JS roto en produccion_diaria.html (âPIDAS)	9e645ba
Migración	SQL para tenants existentes (tenant_1, tenant_27)	9e645ba
✅ RESUELTAS el 24 Octubre 2026 (tarde) — DT-37 F5 (parte 2 y final)
#	Descripción	Commit
DT-37 F5.7	Migrar ventas_periodo.html + fix multi-tenant	0af8fcf
DT-37 F5.8	Migrar analisis_predictivo.html + fix CSS @media print + badge traducción	d0fd6bb
DT-37 F5.9	Migrar reporte_produccion.html	b660db7
DT-37 F5.10	Migrar secciones/analisis_productos.html + fix traducciones heredadas	7582770
DT-37 F5.11	Migrar secciones/recomendaciones.html	84b9080
DT-37 F5.12	Migrar secciones/resumen_ventas.html	ec2687e
DT-37 F5.13	Migrar secciones/analisis_ia.html	61edb44
DT-37 F5.14	Migrar ventas_avanzado.html (padre) — F5 COMPLETADO	c54d9eb
✅ RESUELTAS el 23 Octubre 2026 — DT-37 F5 (parte 1)
#	Descripción	Commit
DT-37 F5.1	Migrar reportes.html (menú principal)	a0de295
DT-37 F5.2	Migrar cierre_caja.html	a0de295
DT-37 F5.3	Migrar productos_populares.html	a796290
DT-37 F5.4	Migrar reporte_activos.html	0ebb3de
DT-37 F5.5	Migrar reporte_inventario_externo.html + fix export PDF	2f9a5fe
DT-37 F5.6	Migrar reporte_ventas_externas.html + fix export PDF	3ea5612
DT-babel-fix	babel.cfg corregido a [jinja2: **.html]	a0de295
DT-app-import	from flask_babel import Babel, gettext as _ en app.py:1264	2f9a5fe
✅ RESUELTAS el 18 Octubre 2026 — DT-37 F4.6 + F4.7 + F4.8
#	Descripción	Commit
DT-37 F4.6	ia_predictivo (método + 3 helpers)	b7d76b9
DT-37 F4.7	historial_pagos + historial_depositos	89c2568
DT-37 F4.8	tesoreria_unificado (método + 4 helpers) + _generar_reporte_error	6b6204b
✅ RESUELTAS el 16 Octubre 2026 — DT-37 F4 (parte 1-5 + fix)
#	Descripción	Commit
DT-37 F4.1	estado_resultados	41dc685 + 186d78b
DT-37 F4.2	flujo_caja	8c53f4a
DT-37 F4.3	conciliacion_bancaria	9ddc83f
DT-37 F4.4	analisis_gastos	4cbc257
DT-37 F4.5	analisis_inventarios	8430027
✅ RESUELTAS el 15 Octubre 2026 — DT-37 (parcial)
#	Descripción	Commit
DT-37 F0	Campo idioma en ConfiguracionSistema + migración BD + UI	85f8cf5
DT-37 F1	Instalación Flask-Babel + Babel	fbea5d8
DT-37 F2	Babel(app) + _get_locale() + hook en before_request	fbea5d8
DT-37 F3	Reporte piloto (tendencia_ventas) migrado a i18n	9490e97 + 5860fdf
DT-37 Papiamento	Catálogo pap completo (53 traducciones)	93a1e82
🟡 Medias pendientes
#	Ubicación	Descripción
DT-37 F5-pulido	app.py / reportes.py	Gráficos de matplotlib (en reporte_activos.html y otros) tienen títulos en español hardcodeados en Python. Requiere i18n en funciones que generan imágenes. Estimación: ~1 h por reporte.
DT-37 F4.9	reportes.py:500	libro_diario: método huérfano (sin UI). Baja prioridad. ~30 min.
DT-NUEVA-1	migrations/sql/	Sincronizar CREATE TABLE con idioma para tenants nuevos (obligatorio antes del próximo tenant).
DT-nueva	reportes.py	Error 'ingreso' en generar_reporte_ia_predictivo (L1936). El PDF muestra "Las recomendaciones no están disponibles temporalmente por error técnico". El except ya está i18n-ready.
DT-nueva	app.py:9066	Endpoint /generar_reporte_flujo_caja huérfano: existe pero ningún template lo invoca. Además tiene bug: generador.generar_reporte_flujo_caja(fecha_inicio, fecha_fin) le falta panaderia_id (L9092).
DT-nueva	analisis_gastos (matplotlib)	Overlap de labels en pie chart con categorías con valores pequeños. Cosmética.
DT-nueva-media-baja	app.py	i18n de diccionarios Python que alimentan reportes HTML: analisis_tendencias.mensaje, analisis_tendencias.recomendaciones, predicciones_ml.mensaje, predicciones_ml.mensaje_tendencia, recomendaciones_personalizadas.mensaje, recomendacion.titulo, recomendacion.mensaje, recomendacion.accion, recomendacion.prioridad, producto.nivel_riesgo, prediccion.confianza. Los textos siguen en español en reportes PAP/EN porque vienen de Python hardcodeado. NO es F5, es deuda de app.py. NO urgente, NO rompe nada.
DT-nueva-baja	templates/	Mapeo Jinja2 de badges dinámicos (prioridad/nivel_riesgo/confianza) en analisis_predictivo.html, analisis_ia.html, ventas_avanzado.html. Ej: {{ {'ALTO': _('Alto'), 'MEDIO': _('Medio'), 'BAJO': _('Bajo')}[valor] }}.
DT-nueva-baja	_ver_untraducciones.py	Bug: reporta 13 strings en EN cuando hay 44, y 0 en PAP cuando hay 53. Reescribir o reemplazar por findstr /c:"msgstr \"\"". Baja prioridad.
🚨 DT-nueva-CRÍTICA
Ubicación	Descripción
reportes.py (ReportLab)	Emojis 🔴 🟢 🟡 ⚪ 📦 📊 🚨 💡 📋 ✅ rotos en PDFs: la fuente Helvetica default de ReportLab no tiene glyphs → salen como n. Cosmética global.
🟢 Bajas pendientes
#	Descripción
DT-nueva	tenant_1.configuracion_sistema tiene 6 filas con panaderia_id = 1, 5, 22, 24, 27, 28 (posible data legacy).
DT-nueva	Imports redundantes de os en app.py (líneas 1225, 10519, 11009, 11958, 12323, 12429).
DT-nueva	Fluho Neto en lugar de Flusho Neto en PAP (ajuste menor de traducción).
DT-nueva	cierre_diario.html es huérfano. La ruta /cierre_diario (app.py:7165) existe pero NO está enlazada desde el frontend. El cierre real se hace desde el POS. Acción futura (decidir): eliminar templates/cierre_diario.html + la ruta /cierre_diario de app.py, o dejarla como utilidad oculta. NO migrar a i18n (no se usa).
DT-nueva	reportes.html:229 tiene el botón para ventas_periodo.html con el nombre "Historial de Ventas". Evaluar renombrar a "Ventas por Período".
DT-nueva-cosmética	ventas_periodo.html tiene datos demo hardcodeados en tabla Distribución por Categoría (40/35/15/10) y gráficos. Deberían venir de Python.
DT-nueva-traducción	al → Real en PAP (heredado). Mejor te o hasta.
DT-nueva-traducción	Medio → Average/Promedio (heredado). Mejor Medium/Medio. Similar para Bajo → LOW/ABOU (heredado).
DT-nueva	tenant_1 (plantilla de referencia) tiene una estructura de historial_inventario ligeramente diferente a tenant_27 (no tiene FK en orden_produccion_id). Evaluar alinear en la Fase A-F de pre-Dockerización.
🔟 Metodología de trabajo
Reglas de oro (heredadas de v9.2)
Un paso a la vez con confirmación antes de continuar.

Diagnóstico ANTES de modificar.

Soluciones de raíz (no parches).

TODO debe funcionar para futuros tenants.

Verificación con psql/findstr antes de avanzar.

Commit después de cada fix verificado.

Backup antes de cada cambio grande.

Siempre verificar git status antes de commitear.

Push después del commit.

Detener servidor antes de reiniciar.

Insertar bloques: mostrar ANTES → DESPUÉS con número de línea exacto.

Verificar ubicación y compilar tras cada inserción.

Al detectar deuda técnica: anotarla (no tocarla), priorizarla, decidir después.

En Windows, usar findstr /c:"patrón" para búsquedas literales.

findstr /c:"texto con tilde" puede fallar por encoding → usar fragmentos sin tildes o Get-Content -Encoding UTF8.

Al commitear, SIEMPRE usar git add <archivo> explícito.

En Flask-Babel 4.0: default_translation_directories DEBE pasarse al constructor Babel(app, ...).

pybabel extract con . escanea TODO (incl. venv/). Usar lista explícita.

Los .mo DEBEN commitearse al repo.

🚨 pybabel NO extrae _() dentro de f-strings. Extraer a variables.

🚨 pybabel NO extrae _() después de emoji dentro de f-string. Usar concatenación.

pybabel update marca #, fuzzy. SIEMPRE correr _limpiar_fuzzy.py después.

El % NUNCA va dentro de _(). Siempre afuera.

babel.cfg: el pattern Jinja2 debe ser [jinja2: **.html], NO **/templates/**.html.

Proteger <style> y <script> ANTES de reemplazos masivos en templates. Usar placeholders.

Reemplazos SOLO entre etiquetas HTML (>Texto<). Nunca palabras sueltas.

Orden de reemplazos: primero los textos que contienen otros textos.

Emojis en HTML: incluirlos en el reemplazo (>📦 Texto<). Si se corrompen, eliminarlos.

Verificar el .mo directamente con gettext.GNUTranslations cuando el HTML no se traduce.

Reiniciar servidor + modo incógnito después de pybabel compile.

Migrar también los PDFs de exportación (/exportar_X en app.py).

Preferir scripts Python sobre copy-paste del chat (mojibake).

N/A, Ninguno, siglas universales también migrar con _().

config.nombre_panaderia ya está disponible globalmente en templates (vía inject_user_permissions()).

reporte_produccion.html es el reporte (/reporte_produccion_diaria). produccion_diaria.html (58 KB) es el dashboard del módulo (no es reporte HTML, no es F5).

cierre_diario.html es huérfano (nadie lo enlaza desde frontend).

🚨 NUEVAS Reglas de oro (Aprendidas en Feature Toppings, 24 Oct 2026)
Modelo ORM ↔ Tabla BD DEBEN estar alineados. Al agregar una columna a un modelo, verificar con information_schema.columns que la tabla real la tiene. Los CREATE TABLE manuales en app.py pueden quedar desalineados.

producto_id puede ser NULL en historial_inventario (para movimientos que no son de producto terminado). Si la tabla lo requiere NOT NULL, usar ALTER TABLE ... DROP NOT NULL.

search_path DEBE estar seteado antes de hacer MateriaPrima.query.get() en contextos fuera de request (scripts, tareas). Verificar con SHOW search_path.

Al agregar una FK a un CREATE TABLE manual, verificar el orden de creación de tablas. Si la tabla referenciada se crea después, dejar la columna sin FK (validar en aplicación) o mover el CREATE TABLE.

_descontar_ingredientes() DEBE registrar en HistorialInventario (no solo restar del stock). Sin historial no hay trazabilidad.

Al procesar toppings, usar factor_escala = cantidad_producir / unidades_obtenidas para escalar correctamente si se produce más de un lote.

Los toppings se manejan SIEMPRE en gramos, independientemente de la unidad de medida de la materia prima. Convertir stock a gramos en el endpoint API.

Verificar los Print de JavaScript en templates — el mojibake puede romper el JS y hacer que aparezca como texto plano en la UI.

tenant_1 (plantilla) y tenant_27 (demo) DEBEN tener la misma estructura. Al agregar columnas/tablas, aplicar la migración a ambos.

Comandos útiles (ACTUALIZADOS)
cmd
# Pipeline i18n
pybabel extract -F babel.cfg -o locales/messages.pot app.py models.py reportes.py templates
pybabel update -i locales/messages.pot -d locales
python _limpiar_fuzzy.py
pybabel compile -d locales --statistics

# Verificar estructura de una tabla
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_schema = 'tenant_27' AND table_name = 'historial_inventario' ORDER BY ordinal_position;"

# Verificar constraints de una tabla
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = 'tenant_27.receta_toppings'::regclass;"

# Verificar historial de movimientos
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "SELECT h.id, mp.nombre, h.cantidad_utilizada, h.orden_produccion_id FROM tenant_27.historial_inventario h JOIN tenant_27.materias_primas mp ON mp.id = h.materia_prima_id WHERE h.orden_produccion_id = 301 ORDER BY h.id;"

# Scripts de diagnóstico (crear _test_XXX.py)
python _test_jinja.py <template.html>
python _test_mo.py
python _test_descuento.py

# Comandos heredados
chcp 65001
psql -U postgres -p 5433 -h localhost -d panaderia_master
python -m py_compile app.py
python app.py
findstr /n /c:"patrón exacto" archivo.py
pg_dump -U postgres -p 5433 -h localhost -d panaderia_master -F c -f backup_pre_XXX.backup
git commit -F _commit_msg.txt && del _commit_msg.txt
Scripts de utilidad que DEBEN existir en el proyecto
_limpiar_fuzzy.py — elimina líneas #, fuzzy de los .po. CRÍTICO.

_ver_untraducciones.py — muestra msgids con msgstr "" en en.po (tiene bug conocido).

_test_jinja.py — valida sintaxis Jinja2 de un template dentro del contexto Flask.

1️⃣1️⃣ Fase C.3 — Auditoría de columnas huérfanas (cerrada)
Auditoría del 5 Oct, alineación ORM↔BD:

Fase C.3 parcial: modelos vivos (cefb33f).

DT-38: 4 lotes de modelos muertos.

DT-39: 25 columnas SIN FILAS.

DT-40: 6 columnas legacy en ventas.

DT-36: 42 tablas huérfanas en public.

DT-5-ter: columnas legacy en gastos.

DT-5-quinquies: alineación estructural tenant_1.gastos con tenant_27.gastos.

1️⃣2️⃣ a 1️⃣9️⃣ Bitácoras anteriores
(Se mantienen las bitácoras de sesiones previas: DT-25, DT-28/45, DT-42/43, DT-46, DT-5-bis/quinquies, DT-5-quater-bis, DT-19, DT-47. Consultar HANDOFF v9.1 si se necesita detalle.)

2️⃣0️⃣ DT-37 — i18n reportes
Estado: ✅ F0-F5 COMPLETADAS AL 100%.

Resumen F4 (PDFs) — 10 reportes + 1 helper
Reporte	Commit	Fecha
tendencia_ventas (piloto)	9490e97	15 Oct
estado_resultados	41dc685 + 186d78b	16 Oct
flujo_caja (huérfano)	8c53f4a	16 Oct
conciliacion_bancaria	9ddc83f	16 Oct
analisis_gastos	4cbc257	16 Oct
analisis_inventarios	8430027	16 Oct
ia_predictivo	b7d76b9	16 Oct
historial_pagos	89c2568	18 Oct
historial_depositos	89c2568	18 Oct
tesoreria_unificado	6b6204b	18 Oct
_generar_reporte_error	6b6204b	18 Oct
Total F4: 344 msgids (100% traducidos en EN y PAP).

Resumen F5 (HTMLs) — 14 archivos
Template	Commit	Fecha
reportes.html	a0de295	20 Oct
cierre_caja.html	a0de295	20 Oct
productos_populares.html	a796290	21 Oct
reporte_activos.html	0ebb3de	21 Oct
reporte_inventario_externo.html	2f9a5fe	22 Oct
reporte_ventas_externas.html	3ea5612	23 Oct
ventas_periodo.html	0af8fcf	23 Oct
analisis_predictivo.html	d0fd6bb	23 Oct
reporte_produccion.html	b660db7	23 Oct
secciones/analisis_productos.html	7582770	24 Oct
secciones/recomendaciones.html	84b9080	24 Oct
secciones/resumen_ventas.html	ec2687e	24 Oct
secciones/analisis_ia.html	61edb44	24 Oct
ventas_avanzado.html (padre)	c54d9eb	24 Oct
Total F5: ~770 msgids en el .pot, ~767 traducidos en EN (99%), ~766 traducidos en PAP (99%).

2️⃣1️⃣ Feature: Toppings en recetas (COMPLETADA 24 Oct 2026)
Alcance
Tabla nueva receta_toppings (con CHECK constraint chk_topping_tipo).

Modelo RecetaTopping en models.py.

Cálculo de costos: gramos por lote × $/gramo (NO por unidad).

Descuento de stock: ingredientes base + toppings.

Historial de inventario: registra ingredientes base + toppings.

Formulario de toppings en crear_receta.html y editar_receta.html.

Sección "Toppings" en detalle_receta.html.

Modal de producción en produccion_diaria.html (con toppings en gramos).

Endpoint API /api/calcular_ingredientes (con toppings).

Migración SQL para tenants existentes (migrations/sql/2026-10-24_add_receta_toppings.sql).

Decisiones de diseño
Toppings = gramos por lote (no por unidad). El usuario ingresa "450g de bocadillo para todo el lote".

NO afectan el peso total de la masa ni las unidades obtenidas.

NO afectan el precio de venta al público (solo el costo real).

Multi-tenant: cada topping tiene panaderia_id.

Fixes preexistentes incluidos
Panaderia(panaderia_id=...) — argumento inválido (columna eliminada en DT-32).

producto_id NOT NULL en historial_inventario → ahora nullable.

search_path no seteado en _descontar_ingredientes().

Modelo HistorialInventario desalineado con la BD (faltaban producto_id, cantidad_anterior, cantidad_nueva, usuario_id, observaciones).

JS roto en crear_receta.html (âO DEL FORMULARIO).

JS roto en produccion_diaria.html (âPIDAS).

Commit
9e645ba

2️⃣2️⃣ 🆕 Feature pendiente: Anulación de recibos POS
Origen: Detectado en sesión 24 Oct 2026.

Problema: Actualmente NO se pueden eliminar recibos POS del sistema. Si una compra queda mal registrada (por error del cajero, doble venta, venta cancelada, cliente que se arrepiente), NO hay forma de revertir la operación.

Necesidad: Implementar un mecanismo para eliminar un recibo POS que:

Revierta las cantidades facturadas al stock en vitrina.

Revierta los movimientos financieros asociados.

Registre el motivo de la eliminación (auditoría).

Mantenga trazabilidad (quién, cuándo, por qué).

No elimine físicamente el registro (soft delete o estado ANULADA).

Acción previa (al implementar): Solicitar al usuario (Mauricio) ampliar la información sobre:

¿Qué permisos debe tener el usuario para anular recibos (solo admin, admin + supervisor)?

¿Debe quedar registro de la venta anulada para reportes (con signo negativo)?

¿Aplica a ventas electrónicas también o solo a POS?

¿Hay un límite de tiempo para anular (ej. solo del día en curso)?

¿Cómo se refleja en el cierre de caja ya realizado?

Prioridad: Media-alta (afecta operación diaria del POS).
Estimación: ~3-5 h (requiere sesión dedicada con cuestionario previo).
Ubicación esperada: models.py (Venta con estado), app.py (endpoint /anular_venta), templates/punto_venta.html (botón "Anular"), reportes.py (reflejar anuladas).

2️⃣3️⃣ 🆕 Plan de trabajo: Análisis pre-Dockerización (SINCRONIZACIÓN MODELOS/APP/BD)
Origen: Detectado en sesión 24 Oct 2026 (feedback del usuario antes de Dockerizar).

Contexto: Antes de dockerizar el sistema, es CRÍTICO asegurar que:

models.py ↔ app.py ↔ Base de datos están sincronizados.

Todos los futuros tenants nazcan completos y actualizados (sin discrepancias).

Crear tablas en orden correcto para que app.py funcione desde el primer arranque.

No haya tablas/columnas huérfanas en ningún schema.

tenant_27 (Demo para marketing) y tenant_1 (Plantilla de referencia) estén sincronizados estructuralmente.

Objetivo final: Dejar el código y la BD limpios, sin discrepancias, listos para dockerizar con la garantía de que un tenant nuevo nace 100% funcional y estructuralmente correcto.

Plan de trabajo propuesto (7 fases A-G)
Fase A — Auditoría de modelos (models.py) (~2 h)

□ Mapear TODOS los modelos definidos en models.py (clases, tablas, columnas, relaciones, FKs).
□ Detectar modelos huérfanos (definidos pero sin uso en app.py ni en templates).
□ Detectar columnas huérfanas (definidas en modelo pero nunca leídas/escritas).
□ Detectar FKs mal definidas o ausentes.
□ Documentar la estructura "canónica" de un tenant completo.
Fase B — Auditoría de app.py (~2 h)

□ Mapear TODAS las queries SQLAlchemy a modelos.
□ Detectar queries a tablas/columnas que NO existen en models.py (bug oculto).
□ Detectar funciones de creación de tenant (crear_tenant_saas()) — verificar que creen TODAS las tablas necesarias.
□ Detectar rutas/endpoints que usen modelos no sincronizados.
□ Verificar el orden de CREATE TABLE en crear_tenant_saas() (FKs antes que tablas dependientes).
Fase C — Auditoría de BD (information_schema) (~2 h)

□ Ejecutar information_schema.columns en tenant_1 y tenant_27 para mapear columnas reales.
□ Comparar columnas de tenant_1 vs tenant_27 → detectar diferencias estructurales.
□ Comparar models.py vs BD real → detectar discrepancias.
□ Detectar tablas huérfanas en public.*.
□ Detectar tablas huérfanas en tenant_1 y tenant_27.
□ Documentar la estructura "real" de la BD.
Fase D — Sincronización (~3-4 h)

□ Crear script SQL de migración para alinear tenant_1 ↔ tenant_27.
□ Actualizar crear_tenant_saas() para que TODAS las tablas/columnas se creen en orden correcto.
□ Actualizar models.py para eliminar huérfanos y agregar lo que falte.
□ Actualizar migrations/sql/ con la migración de sincronización (especialmente CREATE TABLE ... idioma).
□ Ejecutar migración en tenant_1 y tenant_27.
□ Verificar con information_schema.columns que ambos están sincronizados.
Fase E — Prueba de "tenant virgen" (~2 h)

□ Crear tenant de prueba (ej. tenant_test) desde cero con crear_tenant_saas().
□ Verificar que TODAS las tablas del modelo estén creadas.
□ Verificar que information_schema.columns del tenant nuevo coincida con tenant_1 y tenant_27.
□ Probar el flujo completo: login → dashboard → POS → venta → cierre → reporte.
□ Si algo falla → corregir y repetir hasta que un tenant nuevo nazca 100% funcional.
□ Borrar tenant_test (limpieza).
Fase F — Documentación y limpieza (~2 h)

□ Documentar la estructura canónica del tenant (tablas, columnas, FKs, orden de creación).
□ Eliminar código huérfano (modelos sin uso, columnas sin referencias, endpoints muertos).
□ Actualizar HANDOFF con la estructura canónica.
□ Crear docs/ESTRUCTURA_TENANT.md con el mapa completo.
Fase G — Preparación para Dockerización

□ Verificar que requirements.txt esté completo y versionado.
□ Verificar que los .mo estén commiteados.
□ Verificar que .env.example tenga TODAS las variables necesarias.
□ Confirmar que crear_tenant_saas() funciona en un entorno limpio.
□ Crear Dockerfile + docker-compose.yml (Fase 3).
Estimación de tiempos
Fase	Estimación
A — Auditoría de modelos	~2 h
B — Auditoría de app.py	~2 h
C — Auditoría de BD	~2 h
D — Sincronización	~3-4 h
E — Prueba de "tenant virgen"	~2 h
F — Documentación y limpieza	~2 h
Total pre-Dockerización	~13-15 h (2-3 sesiones)
G — Dockerización (Fase 3)	~22-32 h
Prioridad
CRÍTICA — no dockerizar sin completar A-F. Es la base de todo el SaaS multi-tenant.

Riesgos identificados
Puede haber tablas/columnas en app.py que se crean "al vuelo" sin estar en models.py.

Puede haber tenants antiguos (1 y 27) con estructura diferente a un tenant nuevo.

Puede haber código huérfano de features abandonadas (limpiar).

Puede haber dependencias ocultas entre tablas (verificar FKs).

Recomendación de arranque
Empezar por Fase C (auditoría de BD), porque da una foto concreta del estado actual y permite planificar el resto con datos reales.

2️⃣4️⃣ Notas estratégicas
Objetivo del ERP
ERP SaaS multi-tenant multi-país con: POS, inventario, producción, recetas (con toppings), activos fijos, reportes con IA, finanzas, i18n multi-idioma (es/en/pap), multi-país, base para API REST + IA avanzada, módulo de anulación de ventas.

🎁 Tenant Demo
Fases 1-12 completadas (~9.972 filas). Contraseña: demo2026. idioma = pap.

Mercado objetivo
3.000-5.000 panaderías en Colombia.

10.000-30.000 en LATAM.

Clientes internacionales: Curazao-Antillas Holandesas (Papiamentu).

Precio: $60k-$600k COP/mes.

Modelo de licencias
Premium: 3 usuarios.

Básica: 1 usuario.

Estimación de tiempos (24 Oct 2026)
Bloque	Estimación
DT-37 F5	✅ COMPLETADO (100%)
Feature Toppings	✅ COMPLETADO (24 Oct 2026)
Feature Anulación POS	~3-5 h (próxima sesión)
i18n diccionarios Python	~2-4 h (baja prioridad)
Auditoría ORM ↔ BD	~1-2 h
Tenant test + smoke test	~1-2 h
Pre-Dockerización (Fases A-F)	~13-15 h
Dockerización (Fase 3)	~22-32 h
DT-37 F5-pulido (gráficos matplotlib)	~1 h por reporte
DT-37 F4.9 (libro_diario huérfano)	~30 min
2️⃣5️⃣ 🐳 Preparación para Dockerización
El sistema está listo para Docker una vez completadas las fases A-F de pre-Dockerización:

✅ CSRF con SECRET_KEY (portable entre entornos).

✅ Logs a archivo + consola (compatible con docker logs).

✅ Logs con rotación (evita llenar disco).

✅ Sin dependencias de red específicas.

✅ requirements.txt actualizado.

✅ i18n con locales/ (portable, los .mo van en el repo).

✅ Feature Toppings completa.

🟡 Pre-Dockerización pendiente (fases A-F).

🟡 Fase G: Dockerfile + docker-compose.yml (a crear).

2️⃣6️⃣ 🆕 PLAN DE TRABAJO — Próximas sesiones (orden prioritario)
Orden definido por Mauricio (24 Oct 2026):

Fase 1 — Anulación de recibos POS (~3-5 h)
Prioridad: Media-alta.
Requisito: Cuestionario previo (ver sección 2️⃣2️⃣).
Entregable: Funcionalidad completa de anulación (revertir stock + movimientos + trazabilidad).

Fase 2 — i18n de diccionarios Python (~2-4 h)
Prioridad: Baja (si es necesario; sino dejar como está).
Alcance: Migrar los diccionarios de app.py que alimentan reportes HTML (analisis_tendencias.mensaje, recomendacion.titulo, etc.). Ver DT-nueva-media-baja.
Decisión: Evaluar si vale la pena o se deja como deuda aceptada.

Fase 3 — Auditoría ORM ↔ BD (sincronización) (~1-2 h)
Objetivo: Verificar con git y information_schema que no haya discrepancias entre:

models.py (modelo ORM).

app.py (CREATE TABLE manuales).

BD real (tenant_1 y tenant_27).
Entregable: Reporte de discrepancias + fixes.

Fase 4 — Tenant test + smoke test (~1-2 h)
Objetivo: Crear un tenant nuevo desde cero con crear_tenant_saas() y verificar que TODAS las funcionalidades funcionen.
Entregable: Confirmación de que un tenant nuevo nace 100% funcional.

Fase 5 — Pre-Dockerización (Fases A-F) (~13-15 h)
Prioridad: CRÍTICA (bloqueante para dockerizar).
Alcance: Ver sección 2️⃣3️⃣.

Fase 6 — Dockerización (Fase G) (~22-32 h)
Prioridad: Alta.
Alcance: Crear Dockerfile + docker-compose.yml con PostgreSQL.

📞 Cómo continuar en un chat nuevo
Al iniciar un nuevo chat, pegar este archivo como contexto inicial.

Instrucción sugerida:

"Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el archivo HANDOFF.md v9.3 con el contexto maestro. Vamos a continuar desde donde lo dejamos. Por favor actúa como instructor guiando paso a paso, con la metodología de trabajo descrita en el HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/findstr, commit tras cada fix verificado. Al insertar bloques, muéstrame ANTES → DESPUÉS con número de línea exacto. Tú me das LUZ VERDE cuando los cambios estén 100% validados. Yo aplico los cambios en mi editor."

Próxima tarea (orden definido por Mauricio):

Anulación de recibos POS (~3-5 h) — empezar con cuestionario previo.

i18n de diccionarios Python (~2-4 h) — evaluar si es necesario.

Auditoría ORM ↔ BD (~1-2 h) — verificar sincronización.

Tenant test + smoke test (~1-2 h) — verificar tenant nuevo.

Pre-Dockerización (Fases A-F) (~13-15 h) — CRÍTICA.

Dockerización (Fase G) (~22-32 h).

✅ Última validación
Último commit: 9e645ba (Feature Toppings, pusheado).

Última sesión: 24 Oct 2026 — Feature Toppings COMPLETADA (100%).

Working tree: clean.

Servidor: detenido.

Sistema: 100% funcional end-to-end.

Módulos: 11/11 completados.

Demo: ~9.972 filas. idioma = pap en tenant_27.

Seguridad: Producción-ready (CSRF con tokens firmados).

Observabilidad: Producción-ready (logger con rotación).

i18n: 3 idiomas (es/en/pap). PDF reportes: 100%. HTML reportes: 100%. Diccionarios Python pendientes (DT-nueva-media-baja).

DT-37: ✅ F0-F5 COMPLETADAS (100%).

Feature Toppings: ✅ COMPLETADA (100%).

Resueltas: DT-19, DT-25, DT-28, DT-29, DT-42, DT-43, DT-45, DT-46, DT-47, DT-5-bis, DT-5-quinquies, DT-5-quater-bis, DT-37 F0-F5, Feature Toppings.

Pendientes principales:

Feature Anulación POS: ~3-5 h.

i18n diccionarios Python: ~2-4 h (baja).

Auditoría ORM ↔ BD: ~1-2 h.

Tenant test + smoke test: ~1-2 h.

Pre-Dockerización (Fases A-F): ~13-15 h.

Dockerización (Fase G): ~22-32 h.

Fin del HANDOFF.md — v9.3