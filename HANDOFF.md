# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP)

**Última actualización:** 18 de Octubre, 2026
**Último commit:** `6b6204b` (feat DT-37 F4: migrar tesoreria_unificado a i18n)
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
**Sesión 18 Oct (mañana):** DT-37 F4.7 (`historial_pagos` + `historial_depositos`) + DT-37 F4.8 (`tesoreria_unificado` método principal + 4 helpers + `_generar_reporte_error`) — **10/10 reportes UI migrados**.

---

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp)
- **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.7.0 — **11/11 módulos completados (100%)** + **DT-37 F4 100% en reportes.py** (10 reportes UI + 4 helpers + 1 huérfano pendiente: `libro_diario`). F5 (reportes HTML en `app.py`) pendiente.
- **Arquitectura:** Multi-tenant con PostgreSQL (schemas por tenant)
- **Próximo hito:** DT-37 F5 (i18n de reportes HTML en `app.py`) + Dockerización (Fase 3) + DT-CRÉDITOS.
- **Seguridad:** Producción-ready (CSRF con tokens firmados + Origin/Referer + logging centralizado)
- **Observabilidad:** Producción-ready (logger con rotación de archivos, niveles configurables)
- **i18n:** Operativo para reportes PDF en **es/en/pap** (10 de 10 reportes UI en `reportes.py` migrados).

---

## 2️⃣ Stack tecnológico

### Backend
- Python 3.10+, Flask 3.1.2, SQLAlchemy 2.0
- PostgreSQL 17.10 (puerto 5433)
- Flask-Login, Flask-WTF, Werkzeug (pbkdf2:sha256, scrypt), ReportLab, Matplotlib
- **Flask-Babel 4.0.0** + **Babel 2.18.0** (nuevo, DT-37)
- **Logging:** `logging` + `RotatingFileHandler` (built-in, sin dependencias)
- **BD:** `panaderia_master` — credenciales en `.env`
- **Password postgres (local):** `PanaderiaPro2026!` (⚠️ NO incluir en HANDOFFs públicos)

### Frontend
- HTML5/CSS3, JavaScript vanilla, Bootstrap 5.1.3, Chart.js, Font Awesome 6

### Estructura de archivos
- `app.py` (~12.700 líneas) — aplicación principal
- `models.py` (~3.060 líneas) — modelos SQLAlchemy
- `reportes.py` (~3.600 líneas) — generación PDF
- `seed_demo.py` (~450 líneas) — seed del Demo
- `seeds/` — 11 fases del seed
- `middleware_saas.py`, `tenant_decorators.py`, `tenant_context.py` — multi-tenant
- `security_utils.py` — utilidades de seguridad multi-tenant
- `migrations/sql/` — scripts SQL versionados
- **`babel.cfg`** — config de extracción de strings
- **`locales/`** — catálogos de traducción
  - `locales/messages.pot` — plantilla (**344 msgids**)
  - `locales/es/LC_MESSAGES/messages.{po,mo}` — español (0 traducidos, fallback)
  - `locales/en/LC_MESSAGES/messages.{po,mo}` — inglés (**344 traducidos, 100%**)
  - `locales/pap/LC_MESSAGES/messages.{po,mo}` — papiamentu Curazao (**344 traducidos, 100%**)
- `templates/` (54 templates + `_csrf_head.html` partial + subcarpetas `secciones/`)
- `static/js/` — incluye `csrf-auto-inject.js`
- `logs/` — archivo rotativo `panaderia.log` (ignorado por git)
- `.env` (protegido), `.env.example` (plantilla)
- `requirements.txt` — incluye `Flask-WTF==1.3.0`, `WTForms==3.2.2`, `Flask-Babel==4.0.0`, `Babel==2.18.0`
- `HANDOFF.md` — este archivo

---

## 3️⃣ Tenants activos

| ID | Nombre | Subdominio | Plan | Licencia |
|----|--------|-----------|------|----------|
| 1 | Panadería Principal | principal | basico | local |
| 27 | **Panadería Demo** | panadería_demo | premium | nube_premium |

**Tenant principal del Demo:** `tenant_27` ("Panadería Demo").
**Tenants de producción real:** `tenant_1` (Principal) + `tenant_27` (Demo).
**Estado de `tenant_1`:** ✅ Limpio.
**Estado de `tenant_27`:** ✅ Re-seedeado el 5 Oct (9.968 filas) + ventas acumuladas del smoke test. `idioma = pap` (para pruebas de i18n).

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
- Valores soportados: `es`, `en`, `pap` (Papiamentu Curazao), `pt` (futuro).
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
- **NO se crean usuarios desde el frontend.**
- Se crean al **alta del tenant** en `crear_tenant_saas()`.
- Los usuarios viven en `tenant_X.usuarios`.
- **NO se escriben en `public.usuarios`** salvo los 3 del `tenant_1`.

### Reseteo de contraseñas
- **Endpoint:** `POST /resetear_password/<int:usuario_id>` (`app.py:11362`).
- **UI desde dev_master:** `templates/gestion_clientes.html:787`.
- **UI desde admin_cliente:** `templates/gestion_usuarios.html:296`.

### Datos de facturación (por tenant)
- Configurables en `/configuracion/facturacion`.
- Se guardan en `ConfiguracionSistema` (dentro del schema del tenant).
- Fallback: `ConfiguracionPanaderia` (legacy).
- Incluye: tipo_facturacion, nombre_empresa, moneda, usa_centavos, simbolo_moneda, **idioma** (DT-37).

---

## 5️⃣ Estado de los módulos (11/11 = 100%)

| # | Módulo | Estado |
|---|--------|--------|
| 1 | Punto de Venta | ✅ COMPLETO |
| 2 | Producción Diaria | ✅ COMPLETO |
| 3 | Productos Externos | ✅ COMPLETO |
| 4 | Recetas y Fórmulas | ✅ COMPLETO |
| 5 | Materias Primas | ✅ COMPLETO |
| 6 | Proveedores | ✅ COMPLETO |
| 7 | Gestión de Clientes (solo dev_master) | ✅ COMPLETO |
| 8 | Activos Fijos | ✅ COMPLETO |
| 9 | Gestión de Usuarios + Mi Perfil | ✅ COMPLETO |
| 10 | Gestión Financiera | ✅ COMPLETO |
| 11 | Reportes Profesionales | ✅ COMPLETO (i18n PDF: 100% en `reportes.py`; HTML: pendiente F5) |

---

## 6️⃣ Últimos commits pusheados

```text
6b6204b feat(DT-37 F4): migrar tesoreria_unificado a i18n (es/en/pap)
89c2568 feat(DT-37 F4): migrar historial_pagos + historial_depositos a i18n (es/en/pap)
b7d76b9 feat(DT-37 F4): migrar generar_reporte_ia_predictivo a i18n (es/en/pap)
c368ccb docs: HANDOFF v8.10 - DT-37 F4 partes 1-5 completadas (5/13 reportes) + fix critico de emoji en f-strings
186d78b fix(DT-37 F4): reparar f-strings con emoji en estado_resultados (rama sin datos)
8430027 feat(DT-37 F4): migrar generar_reporte_analisis_inventarios a i18n (es/en/pap)
4cbc257 feat(DT-37 F4): migrar generar_reporte_analisis_gastos a i18n (es/en/pap)
9ddc83f feat(DT-37 F4): migrar generar_reporte_conciliacion_bancaria a i18n (es/en/pap)
8c53f4a feat(DT-37 F4): migrar generar_reporte_flujo_caja a i18n (es/en/pap)
41dc685 feat(DT-37 F4): migrar generar_reporte_estado_resultados a i18n (es/en/pap)
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
⚠️ Importante: SECRET_KEY es crítica para:

Sesiones de Flask.

Firma de tokens CSRF (flask-wtf).

Firma de cookies seguras.

Rutas críticas
/reportes, /historial_pagos, /historial_depositos

/generar_reporte_tesoreria_unificado (✅ i18n es/en/pap)

/generar_reporte_estado_resultados (✅ i18n es/en/pap)

/generar_reporte_flujo_caja (✅ i18n es/en/pap — huérfano, sin UI)

/generar_reporte_conciliacion_bancaria (✅ i18n es/en/pap)

/generar_reporte_analisis_gastos (✅ i18n es/en/pap)

/generar_reporte_tendencia_ventas (✅ i18n es/en/pap)

/generar_reporte_ia_predictivo (✅ i18n es/en/pap)

/generar_reporte_analisis_inventarios (✅ i18n es/en/pap)

/reporte_produccion_diaria, /reporte_inventario_externo, /reporte_ventas_externas, /reporte/cierre_caja, /reporte/ventas, /reporte/productos_populares, /reporte/analisis_predictivo, /reporte/ventas_avanzado, /reporte_activos (⚠️ HTML, pendiente DT-37 F5).

🎯 Arquitectura del before_request (post-DT-25 + DT-37)
Un solo before_request en app.py:1892 (antes_de_cada_peticion).

Flujo:

Rutas públicas (static, login, logout, suscripcion_vencida) → return directo.

CSRF por Origin/Referer (capa adicional a CSRFProtect).

Detección de tenant (_detectar_tenant()): current_user > session > subdominio.

Sin tenant válido → session.clear() + redirect a login (NO fallback a tenant 1).

Setea g.tenant + g.panaderia_id + g.current_tenant + g.es_super_admin.

set_tenant_schema() una sola vez.

DT-37: Carga g.idioma_tenant desde ConfiguracionSistema.idioma (fallback 'es').

Verificación de suscripción.

Funciones auxiliares en app.py:

_validar_origen_csrf() (L1751)

_detectar_tenant()

_verificar_suscripcion()

inject_csrf_token() (L1842)

inject_user_permissions() (L1572)

Rendimiento: ~66% menos operaciones BD por request.

🎯 CSRF con flask-wtf (post-DT-19)
Arquitectura de protección CSRF:

CSRFProtect(app) inicializado en app.py:1253.

Context processor inject_csrf_token() (app.py:1842).

Partial templates/_csrf_head.html con meta tag + script. Incluido en 53 templates vía {% include %}.

Script static/js/csrf-auto-inject.js que:

Auto-inyecta <input name="csrf_token"> en formularios POST.

Envuelve window.fetch para agregar X-CSRFToken en AJAX POST.

login.html tiene el token manual (funciona sin JS).
Defensa en profundidad: _validar_origen_csrf() (Origin/Referer) sigue activo.

🎯 Logging centralizado (post-DT-47)
Arquitectura de logging:

Imports en app.py:4-5: import logging + from logging.handlers import RotatingFileHandler

Configuración en app.py:1263-1290:

logger = logging.getLogger('panaderia')

Nivel auto: DEBUG en development, INFO en prod.

Handler 1: consola (StreamHandler).

Handler 2: archivo rotativo logs/panaderia.log (5 MB × 5 backups).

Formato de logs: [2026-10-12 10:20:42] INFO [panaderia] ✅ Venta registrada - ID: 2779

Cero print() activos. Los 6 restantes son comentados o dentro de strings.

.gitignore: logs/ y *.log ya están excluidos.

🎯 i18n con Flask-Babel (post-DT-37 F3 + F4)
Arquitectura de i18n:

Inicialización en app.py:~1256:

python
from flask_babel import Babel

def _get_locale():
    return getattr(g, 'idioma_tenant', None) or 'es'

babel = Babel(
    app,
    locale_selector=_get_locale,
    default_translation_directories=os.path.join(app.root_path, 'locales')
)
⚠️ Lección clave: app.config['BABEL_TRANSLATION_DIRECTORIES'] aplicado después de Babel(app) es demasiado tarde → Babel ya leyó el default (translations/). Pasar default_translation_directories al constructor.

_get_locale() resuelve el locale por request, leyendo g.idioma_tenant (cargado en el before_request).

Pipeline i18n (comandos):

cmd
# 1. Marcar strings en código con _()
# 2. Extraer strings (SOLO archivos específicos, NO '.'):
pybabel extract -F babel.cfg -o locales/messages.pot app.py models.py reportes.py

# 3. Actualizar catálogos existentes (después de agregar nuevos strings):
pybabel update -i locales/messages.pot -d locales

# 4. Traducir los msgstr en cada .po (es/, en/, pap/)
# 5. Compilar .po -> .mo:
pybabel compile -d locales --statistics
Idiomas soportados: es (base/fallback), en, pap (Papiamentu Curazao).

Cómo funciona el fallback:

es.po tiene 0 traducciones → Babel devuelve el msgid original (que ya está en español).

en.po y pap.po tienen 344 traducciones cada uno.

Días en Papiamentu Curazao:

ES	PAP Curazao
Lunes	djaluna
Martes	djamars
Miércoles	djárason
Jueves	djaweps
Viernes	djabièrnè
Sábado	djasabra
Domingo	djadumingu
9️⃣ Deuda técnica acumulada
✅ RESUELTAS el 18 de Octubre 2026 — DT-37 F4.6 + F4.7 + F4.8
#	Descripción	Commit
DT-37 F4.6	Migrar ia_predictivo (método + 3 helpers)	b7d76b9
DT-37 F4.7	Migrar historial_pagos + historial_depositos	89c2568
DT-37 F4.8	Migrar tesoreria_unificado (método + 4 helpers) + _generar_reporte_error	6b6204b
✅ RESUELTAS el 16 de Octubre 2026 — DT-37 F4 (parte 1-5 + fix)
#	Descripción	Commit
DT-37 F4.1	Migrar estado_resultados	41dc685 + 186d78b
DT-37 F4.2	Migrar flujo_caja	8c53f4a
DT-37 F4.3	Migrar conciliacion_bancaria	9ddc83f
DT-37 F4.4	Migrar analisis_gastos	4cbc257
DT-37 F4.5	Migrar analisis_inventarios	8430027
✅ RESUELTAS el 15 de Octubre 2026 — DT-37 (parcial)
#	Descripción	Commit
DT-37 F0	Campo idioma en ConfiguracionSistema + migración BD + UI	85f8cf5
DT-37 F1	Instalación Flask-Babel + Babel	fbea5d8
DT-37 F2	Babel(app) + _get_locale() + hook en before_request	fbea5d8
DT-37 F3	Reporte piloto (tendencia_ventas) migrado a i18n	9490e97 + 5860fdf
DT-37 Papiamento	Catálogo pap completo (53 traducciones)	93a1e82
🟡 Medias pendientes
#	Ubicación	Descripción
DT-37 F5	app.py + templates/	i18n de reportes HTML: /reporte_produccion_diaria, /reporte_inventario_externo, /reporte_ventas_externas, /reporte/cierre_caja, /reporte/ventas, /reporte/productos_populares, /reporte/analisis_predictivo, /reporte/ventas_avanzado, /reporte_activos. Estimación: ~4-6 h.
DT-37 F4.9	reportes.py:500	libro_diario: método huérfano (sin UI). Baja prioridad. ~30 min.
DT-NUEVA-1	migrations/sql/	Sincronizar CREATE TABLE con idioma para tenants nuevos (obligatorio antes del próximo tenant).
DT-nueva	reportes.py	Error 'ingreso' en generar_reporte_ia_predictivo (L1936). El PDF muestra "Las recomendaciones no están disponibles temporalmente por error técnico". El except ya está i18n-ready.
DT-nueva	app.py:9066	Endpoint /generar_reporte_flujo_caja huérfano: existe pero ningún template lo invoca. Además tiene bug: generador.generar_reporte_flujo_caja(fecha_inicio, fecha_fin) le falta panaderia_id (L9092).
🚨 DT-nueva-CRÍTICA	reportes.py (ReportLab)	Emojis 🔴 🟢 🟡 ⚪ 📦 📊 🚨 💡 📋 ✅ rotos en PDFs: la fuente Helvetica default de ReportLab no tiene glyphs de emoji → salen como n. Deuda cosmética global.
DT-nueva	analisis_gastos (matplotlib)	Overlap de labels en pie chart cuando hay categorías con valores pequeños. Deuda cosmética.
🟢 Bajas pendientes
#	Descripción
DT-nueva	tenant_1.configuracion_sistema tiene 6 filas con panaderia_id = 1, 5, 22, 24, 27, 28 (posible data legacy).
DT-nueva	Imports redundantes de os en app.py (líneas 1225, 10519, 11009, 11958, 12323, 12429).
DT-nueva	Fluho Neto en lugar de Flusho Neto en PAP (ajuste menor de traducción).
🚨 Features pendientes
DT-CRÉDITOS: Módulo completo de créditos/fiado. Detalle en sección 2️⃣0️⃣.

Dockerización (Fase 3): ~22-32 h.

🔟 Metodología de trabajo
Reglas de oro
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

Al insertar código a nivel de módulo: ubicarlo junto a sus hermanos temáticos.

Al pedir un test, incluir TODAS las verificaciones previas necesarias.

Cuando el punto de inserción esté justo debajo de un decorador, incluir el decorador en el ANTES → DESPUÉS.

Antes de proponer un fix de concurrencia, medir impacto en el pool de SQLAlchemy.

Nunca usar echo texto >> archivo en Windows para modificar archivos de texto.

Nunca acceder a current_user desde event listeners de SQLAlchemy.

En Windows, usar findstr /c:"patrón" para búsquedas literales.

Antes de aplicar un fix según el HANDOFF, verificar el estado actual del archivo.

Al eliminar código huérfano, verificar PRIMERO que no haya referencias activas (incluye templates HTML y JS).

Al auditar modelos con default=N: verificar TODOS los INSERTs (ORM + SQL directo).

Al eliminar una columna de un modelo, verificar SIEMPRE primero: (a) si hay lecturas en el código, (b) si hay datos inconsistentes en la BD, (c) si hay usuarios/registros que apunten a valores huérfanos.

Al hacer DELETE masivos en la BD, verificar SIEMPRE: (a) backup previo, (b) que no haya FKs apuntando a los registros, (c) que no sean tenants reales en public.tenants.

Al modificar un método de reportes.py que genera PDF, verificar SIEMPRE el orden de las secciones y que todas las variables estén definidas ANTES de usarse.

Nunca asumir que el esquema de la BD coincide con el modelo ORM. Verificar con information_schema.columns ANTES de usar un ORM en un contexto nuevo.

Al auditar columnas (Fase C.3), usar COUNT(DISTINCT col) en lugar de COUNT(col) para evitar falsos positivos.

Al agregar una segunda FK a una tabla, SQLAlchemy requiere foreign_keys=[...] explícito.

Al alinear CREATE TABLE con el ORM, actualizar también los seeds.

Al arrancar la app, se ejecuta una migración automática que agrega columnas del ORM que falten en la BD. Verificar siempre con information_schema.columns.

Al alinear ORM↔BD, revisar TODOS los usos del modelo en templates HTML, JavaScript y CSS.

Al hacer DROP COLUMN, verificar SIEMPRE primero con information_schema.columns en QUÉ schemas existe. Ejecutar el DROP por transacción individual.

Al hacer cambios destructivos en BD, tomar un backup FRESCO con pg_dump -F c inmediatamente antes.

Al quitar columnas del CREATE TABLE, verificar SIEMPRE si la columna eliminada era la ÚLTIMA del bloque. Si lo era, hay que quitar la coma de la línea precedente.

Antes de hacer commit de un CREATE TABLE modificado, revisar el git diff línea por línea.

Antes de hacer DROP masivos, verificar SIEMPRE las FKs internas con information_schema.table_constraints.

Al dropear una tabla referenciada por otra que se CONSERVA, primero soltar la FK explícitamente.

Un endpoint de borrado de tenant debe limpiar TODAS las tablas public.* que puedan tener datos del tenant.

Al verificar COUNT(*) de tablas, NO confiar en pg_stat_user_tables.n_live_tup. Usar siempre COUNT(*) real.

Cuando powershell -Command "Get-Content ... | Select-Object ..." corte la salida en un emoji UTF-8, usar findstr /n /r /c:"^" archivo.py > _dump.txt y luego Select-Object sobre ese archivo.

Antes de refactorizar un before_request o middleware global, mapear TODOS los escritores/lectores de g.*.

En Windows CMD, para git commit -m "mensaje multilínea": crear un archivo _commit_msg.txt y usar git commit -F _commit_msg.txt.

Antes de duplicar código defensivamente, verificar si el framework (Flask/Bootstrap/etc.) ya maneja el caso nativamente.

Nunca confiar en el output de CMD para diagnosticar código con emojis o caracteres no-ASCII: el mojibake (UTF-8 → Latin-1) puede simular errores de sintaxis que no existen. Verificar SIEMPRE con el editor o con Get-Content de PowerShell.

Antes de proponer un "fix urgente" basado en sospechas, confirmar el bug con evidencia directa (imagen del editor, cat -A, hexdump).

Al aplicar cambios en cadena (Tanda 1, Tanda 2, ...), usar los TEXTOS (comentarios, prints, strings únicos) como referencia de ubicación, no los números de línea.

En PowerShell, Select-String con regex :7[3-9][0-9][0-9]: NO matchea porque el output de findstr /n ya tiene los dos puntos. Usar '^7[3-9][0-9][0-9]:' en su lugar.

Para eliminar un bloque for que contiene solo un print, eliminar el for completo.

Nunca pasar scripts PowerShell multilínea desde CMD. Usar Python (script .py creado en editor) o crear el .ps1 manualmente.

Para migrar CSRF (o cualquier cambio transversal) en apps con muchos templates: usar "1 partial + 1 script JS" en lugar de editar 30+ formularios manualmente.

login.html (crítico) SIEMPRE debe tener el token CSRF manual en el <form>, NO depender de JS.

Los templates que extienden base.html heredan automáticamente los {% include %} del padre.

Al inicializar CSRFProtect(app) en Flask, verificar SIEMPRE la ubicación: debe ir DESPUÉS de app.secret_key.

Antes de migrar print() a logger, verificar si hay print() a nivel de módulo ANTES de la definición del logger.

En RotatingFileHandler, siempre configurar encoding='utf-8'.

Al configurar un logger en Flask debug mode, evitar handlers duplicados. Flask debug ejecuta el módulo dos veces (por el reloader).

findstr /c:"texto con tilde" puede fallar por encoding. Usar fragmentos sin tildes o PowerShell con Get-Content -Encoding UTF8.

Antes de reemplazar masivamente print() por logger.*() con un script, hacer dry-run con muestras de cada categoría.

Los scripts de diagnóstico y reemplazo deben crear su propio backup con timestamp.

En Flask-Babel 4.0, default_translation_directories DEBE pasarse al constructor Babel(app, ...).

pybabel extract con . escanea TODO el proyecto (incluido venv/). Usar lista explícita: app.py models.py reportes.py.

Jinja2 3.x eliminó jinja2.ext.autoescape y jinja2.ext.with_. NO declararlas en babel.cfg.

Los archivos .mo deben commitearse al repo — no se generan automáticamente en runtime.

Verificar el locale NO es suficiente con get_locale(). Hay que verificar que gettext() efectivamente traduzca.

Antes de agregar un idioma nuevo, verificar el código ISO 639-2/3. Papiamentu = pap.

Días en Papiamentu Curazao llevan prefijo dja-.

Los scripts de diagnóstico temporales se crean en archivo .py (no con python -c "...").

🚨 pybabel NO extrae _() dentro de f-strings. Solución: extraer los _() a variables ANTES de la f-string.

🚨 pybabel NO extrae _() después de emoji dentro de f-string. Solución: usar concatenación "emoji " + _('texto') en lugar de f"emoji {_('texto')}".

pybabel update marca como #, fuzzy msgids que heredan traducción de otros strings similares. Verificar SIEMPRE y corregir.

Los msgids largos se dividen en multi-línea en el .po (76 chars). Los scripts de reemplazo deben manejar esto con fragmentos clave.

Los strings con %(...)s llevan #, python-format. Al eliminar fuzzy, preservar python-format.

Los scripts de reemplazo de .po deben aceptar --apply (dry-run por defecto).

Los scripts de corrección de fuzzy deben usar regex flexible que capture #, fuzzy con o sin , python-format.

Los scripts de reemplazo en reportes.py deben crear backup con timestamp.

Al commitear, SIEMPRE usar git add <archivo> explícito. Evitar git add ..

Verificar git status DESPUÉS de cada git add y antes de commitear.

Antes de generar un PDF i18n con emojis, verificar que NO haya f"emoji {_('texto')}".

Los msgids de más de 76 caracteres se parten en multi-línea. Los scripts de traducción (FASE 3) deben manejar esto buscando un "fragmento clave" (ej. **Tendencia muy positiva**) dentro del bloque msgid "" ..., en lugar de buscar el string completo.

El except que captura str(e) también se migra. Patrón: _('Error: %(err)s') % {'err': str(e)} (o %(msg)s).

Los arrays de strings en matplotlib (ej. metricas = ['A', 'B']) se migran elemento por elemento: metricas = [_('A'), _('B')].

Al auditar reportes para i18n, confirmar en la UI qué botón corresponde a qué método. Un reporte puede llamarse distinto en la UI que en el código. No asumir por el nombre.

No todos los botones de la UI usan reportes.py. Algunos usan rutas en app.py que renderizan HTML/JS (ej. /reporte/cierre_caja, /reporte/productos_populares). Antes de migrar, confirmar en la UI qué botón corresponde a qué método/ruta. Los reportes HTML son un ticket aparte (DT-37 F5).

_generar_reporte_error no es un reporte de usuario, es un fallback interno. Se genera automáticamente cuando hay un error (licencia, permisos, etc.). Se migra igual para consistencia.

libro_diario y flujo_caja son reportes huérfanos (sin UI). Migrar flujo_caja fue por consistencia. libro_diario queda pendiente como baja prioridad.

Un % literal en un msgstr puede romper la compilación de Babel si el msgid no lo tiene o si el msgid tiene #, python-format. La solución es evitar el % en el texto (ej. cambiar "Menos del 50%" por "Menos de la mitad") en lugar de escapar con %%. Escapar con %% solo funciona si el msgid también lo tiene.

Comandos útiles
Encoding: chcp 65001

psql: psql -U postgres -p 5433 -h localhost -d panaderia_master

Ver estructura: psql -U postgres -p 5433 -h localhost -d panaderia_master -c "\d tenant_27.nombre_tabla"

Seed Demo: python seed_demo.py --tenant=27 --reset-all

Compilar / Servidor: python -m py_compile app.py / python app.py

Búsquedas: findstr /n /c:"patrón exacto" archivo.py

Extraer líneas (PowerShell): powershell -Command "Get-Content models.py | Select-Object -Skip 246 -First 20"

Backup de BD: pg_dump -U postgres -p 5433 -h localhost -d panaderia_master -F c -f backup_pre_XXX.backup

Commit multilínea (Windows CMD): crear _commit_msg.txt, luego git commit -F _commit_msg.txt, luego del _commit_msg.txt

Pipeline i18n (DT-37):

cmd
pybabel extract -F babel.cfg -o locales/messages.pot app.py models.py reportes.py
pybabel update -i locales/messages.pot -d locales
pybabel compile -d locales --statistics
findstr /n /c:"#, fuzzy" locales\en\LC_MESSAGES\messages.po
findstr /n /c:"#, fuzzy" locales\pap\LC_MESSAGES\messages.po
powershell -Command "Select-String -Path reportes.py -Pattern 'f\".*\{_'"
1️⃣1️⃣ Fase C.3 — Auditoría de columnas huérfanas (cerrada)
Auditoría del 5 Oct, alineación ORM↔BD:

Fase C.3 parcial: modelos vivos (cefb33f).

DT-38: 4 lotes de modelos muertos.

DT-39: 25 columnas SIN FILAS.

DT-40: 6 columnas legacy en ventas.

DT-36: 42 tablas huérfanas en public.

DT-5-ter: columnas legacy en gastos.

DT-5-quinquies: alineación estructural tenant_1.gastos con tenant_27.gastos (7 Oct).

1️⃣2️⃣ DT-25 — Bitácora detallada (5 Oct 2026)
Contexto: 2 before_request registrados → trabajo duplicado, 2 conexiones psycopg2 raw por request, set_tenant_schema() 2 veces, mock inútil, fallback a tenant 1.
Solución: Eliminado TenantContext.initialize_app(app). Nuevo before_request único (128 líneas) con funciones auxiliares. Rutas públicas sin overhead. Sin fallback a tenant 1 (DT-29).
Commit: fe6fb0d.

1️⃣3️⃣ DT-28 / DT-45 — Bitácora (6 Oct 2026)
DT-28 — Doble submit en login
Fix: Unificar los 2 listeners en 1. Orden: validar → si OK → btn.disabled = true + .loading.
Commit: 7cda002.

DT-45 — Flash messages destruidos
Fix: Eliminar get_flashed_messages() preventivo en login() + reordenar docstring.
Commit: a39eecf.

1️⃣4️⃣ DT-42 / DT-43 — Bitácora (6 Oct 2026)
DT-42 — diagnosticar_recetas() duplicada
Fix: Eliminar la 1ra (huérfana).

DT-43 — es_super_admin() duplicada
Fix: Mantener la canónica en tenant_decorators.py.
Commit: f2caa24.

1️⃣5️⃣ DT-46 — Bitácora (7 Oct 2026)
Fix: Mover import de es_super_admin al top de app.py. Eliminar imports locales redundantes.
Commit: 34aad22.

1️⃣6️⃣ DT-5-bis + DT-5-quinquies — Bitácora (7 Oct 2026)
DT-5-bis — ORM Gasto documentado
Fix: 9 líneas de comentario antes de class Gasto.

DT-5-quinquies — tenant_1.gastos alineada
Fix: DROP + CREATE con la estructura de tenant_27.gastos.
Archivo: migrations/sql/2026-10-07_align_tenant_1_gastos.sql.
Commit: ff1d704.

1️⃣7️⃣ DT-5-quater-bis (reformulada) — Bitácora (7 Oct 2026)
Fix (4 tandas): Eliminación progresiva de prints + bloque de debug + comentario triplicado.
Resultado: 35 prints eliminados, 50 líneas netas menos.
Falso positivo detectado: Bug estructural en except → artefacto de mojibake. El código siempre estuvo sano.
Commit: 93ea142.

1️⃣8️⃣ DT-19 — CSRF completo con flask-wtf (8 Oct 2026)
Enfoque: Plan C híbrido (manual en login, auto-inyección JS para el resto).
Fases: Backups → Instalar flask-wtf → CSRFProtect → Context processor → Script + partial → 53 templates → AJAX wrapper → login manual → Smoke test → Commit.
Smoke test validado: login, formularios, AJAX POST, todas las rutas críticas.
Commit: ad2b876.

1️⃣9️⃣ DT-47 — Logging centralizado (12 Oct 2026)
Enfoque: Script Python de diagnóstico + script de reemplazo + edición manual de 4 casos especiales.
Fases: Backup → Diagnóstico (350 prints) → Configurar logger → Dry-run del reemplazo → Aplicar (355 reemplazos) → Migrar 4 prints con comentario inline → Smoke test → Commit.
Resultado: 355 print() → logger.info/debug/warning/error. Cero prints activos. Logger con rotación de archivo (5 MB × 5). Smoke test OK.
Commit: 92f2d0d.

2️⃣0️⃣ DT-37 — i18n reportes (COMPLETADA EN reportes.py)
Alcance: reportes.py (~3.600 líneas) genera PDFs con texto hardcodeado en español. Objetivo: multi-idioma con Flask-Babel.
Estado: F0-F4 completadas para reportes.py. 10/10 reportes UI migrados. 1 huérfano pendiente (libro_diario). F5 (reportes HTML en app.py) pendiente.

Resumen de migraciones
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
_generar_reporte_error (helper)	6b6204b	18 Oct
Total: 344 msgids (100% traducidos en EN y PAP).

F5 — Pendiente (Reportes HTML en app.py)
Los siguientes reportes se generan como HTML/JS (no en reportes.py) y necesitan i18n con Flask-Babel en templates:

/reporte_produccion_diaria

/reporte_inventario_externo

/reporte_ventas_externas

/reporte/cierre_caja

/reporte/ventas

/reporte/productos_populares

/reporte/analisis_predictivo

/reporte/ventas_avanzado

/reporte/activos

Estimación: ~4-6 h.

2️⃣1️⃣ DT-CRÉDITOS — Módulo de créditos/fiado (PENDIENTE — feature)
Origen: detectado durante DT-21 (5 Oct 2026). El POS tiene 3 modos:

Venta POS.

Venta electrónica.

Falta: vender a crédito (fiado).

Alcance MVP
Tablas nuevas: creditos, credito_detalle, abonos.

POS: botón "Fiar" + modal simple de cliente.

Endpoints: /fiar_venta + /registrar_abono.

Sección nueva: "Créditos" con estado de cuenta + CxC.

Decisiones de negocio pendientes (cuestionario previo)
¿Inventario al fiar o al cobrar?

¿Cupo por cliente?

¿IVA al fiar o al cobrar?

¿Intereses por mora?

¿Cómo manejar cliente que no paga?

Estimación
MVP: 6-8 h (1-2 sesiones).

Completo: 15-25 h (3-4 sesiones).

Reutilizable
✅ Tabla clientes.

✅ POST /registrar_venta (con flag es_credito=true).

✅ Estructura del carrito.

NO reutilizable
❌ Modal clienteModal (11 campos fiscales).

❌ /api/guardar-cliente.

❌ procesarVentaElectronica().

Prioridad: Media-alta, después de Dockerización.

2️⃣2️⃣ Notas estratégicas
Objetivo del ERP
ERP SaaS multi-tenant multi-país con: POS, inventario, producción, recetas, activos fijos, reportes con IA, finanzas, i18n multi-idioma (es/en/pap), multi-país, base para API REST + IA avanzada, módulo de créditos.

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

Estimación de tiempos (18 Oct 2026)
Bloque	Estimación
DT-37 F5 (reportes HTML)	~4-6 h
DT-37 F4.9 (libro_diario huérfano)	~30 min
Auditoría f-strings emoji	✅ CERRADA (0 casos)
Dockerización (Fase 3)	~22-32 h
DT-CRÉDITOS (MVP)	~6-8 h
DT-CRÉDITOS (completo)	~15-25 h
Fase 4 (seguridad adicional)	~14-20 h
Fase 5 (monetización)	~26-36 h
Fases 6-8 (IA + integraciones)	~50-85 h
🐳 Preparación para Dockerización
El sistema está listo para Docker gracias a las DT cerradas:

✅ CSRF con SECRET_KEY (portable entre entornos).

✅ Logs a archivo + consola (compatible con docker logs).

✅ Logs con rotación (evita llenar disco).

✅ Sin dependencias de red específicas.

✅ requirements.txt actualizado.

✅ i18n con locales/ (portable, los .mo van en el repo).

Próximo paso natural: crear Dockerfile + docker-compose.yml con PostgreSQL.

📞 Cómo continuar en un chat nuevo
Al iniciar un nuevo chat, pegar este archivo como contexto inicial.

Instrucción sugerida:

"Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el archivo HANDOFF.md v9.0 con el contexto maestro. Vamos a continuar desde donde lo dejamos. Por favor actúa como instructor guiando paso a paso, con la metodología de trabajo descrita en el HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/findstr, commit tras cada fix verificado. Al insertar bloques, muéstrame ANTES → DESPUÉS con número de línea exacto. Tú me das LUZ VERDE cuando los cambios estén 100% validados. Yo aplico los cambios en mi editor."

Próxima tarea sugerida:

OPCIÓN A (recomendada): Arrancar DT-37 F5 (i18n de reportes HTML en app.py). ~4-6 h. Cierra el módulo de reportes 100%.

OPCIÓN B: Dockerización (Fase 3). Sesión dedicada. ~22-32 h.

OPCIÓN C: DT-CRÉDITOS. Sesión dedicada con cuestionario previo.

✅ Última validación
Último commit: 6b6204b (tesoreria_unificado, pusheado).

Última sesión: 18 Oct 2026 (mañana) — DT-37 F4 completada para reportes.py.

Working tree: clean (solo _ver_untraducciones.py untracked, script temporal).

Servidor: detenido.

Sistema: 100% funcional end-to-end.

Módulos: 11/11 completados.

Demo: ~9.972 filas. idioma = pap en tenant_27.

Seguridad: Producción-ready (CSRF con tokens firmados).

Observabilidad: Producción-ready (logger con rotación).

i18n: 3 idiomas (es/en/pap), 10/10 reportes UI en reportes.py migrados (+ 1 huérfano pendiente: libro_diario).

DT-37: 🟡 F0-F3 ✅ | F4 reportes.py 100% ✅ | F5 (reportes HTML) PENDIENTE.

DT-19, DT-25, DT-28, DT-29, DT-42, DT-43, DT-45, DT-46, DT-47, DT-5-bis, DT-5-quinquies, DT-5-quater-bis: ✅ Resueltas.

Pendientes: DT-37 F5, DT-37 F4.9 (libro_diario), Dockerización (Fase 3), DT-CRÉDITOS.

Fin del HANDOFF.md — v9.0