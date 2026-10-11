# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP)

**Última actualización:** 11 de Octubre, 2026
**Último commit:** ad2b876 (feat DT-19: proteccion CSRF completa con flask-wtf)
**Sesión 2 Oct:** DT-11, DT-12, DT-13, DT-14, DT-16, DT-26, DT-27, DT-3, DT-4
**Sesión 3 Oct:** DT-1, DT-6, DT-9, DT-20 Fase C (Tanda 1+2+3), DT-30, DT-31
**Sesión 4 Oct:** DT-10, DT-22, DT-24, DT-17, DT-33, DT-34, DT-32, DT-18
**Sesión 5 Oct (mañana):** Fase C.3 parcial + DT-38 (4/5 lotes) + DT-40 + DT-39 + DT-36
**Sesión 5 Oct (noche):** Borrado tenants 25/26 + DT-35 + DT-5 + DT-5-quater + DT-5-ter + DT-21 + DT-25 (refactor before_request) + DT-29
**Sesión 6 Oct (mediodía):** DT-28 + DT-45 + DT-42 + DT-43 + DT-44 (documentada)
**Sesión 7 Oct (noche):** DT-46 + DT-5-bis + DT-5-quinquies + DT-5-quater-bis (reformulada) — **Opción Rápida 100%**
**Sesión 8 Oct (tarde):** DT-19 (CSRF completo con flask-wtf) — **Producción-ready en seguridad**

---

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp)
- **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.4.0 — **11/11 módulos completados (100%)** + Demo Fases 1-12 + Endurecimiento de seguridad + DT-20 100% + DT-18 reporte tesorería nivel contable + tenant_1 limpio + Fase C.3 cerrada + DT-25 cerrada (before_request refactorizado) + DT-29 cerrada + DT-28/DT-45/DT-42/DT-43/DT-44/DT-46 cerradas + DT-5-bis/DT-5-quinquies/DT-5-quater-bis cerradas + **DT-19 cerrada (CSRF completo con flask-wtf)**
- **Arquitectura:** Multi-tenant con PostgreSQL (schemas por tenant)
- **Próximo hito:** Dockerización (Fase 3) + DT-CRÉDITOS (módulo de fiado)
- **Seguridad:** Producción-ready (CSRF con tokens firmados + Origin/Referer como defensa en profundidad)

---

## 2️⃣ Stack tecnológico

### Backend
- Python 3.10+, Flask 3.1.2, SQLAlchemy 2.0
- PostgreSQL 17.10 (puerto 5433)
- Flask-Login, Flask-WTF (nuevo), Werkzeug (pbkdf2:sha256, scrypt), ReportLab, Matplotlib
- **BD:** `panaderia_master` — credenciales en `.env`
- **Password postgres (local):** `PanaderiaPro2026!` (⚠️ NO incluir en HANDOFFs públicos)

### Frontend
- HTML5/CSS3, JavaScript vanilla, Bootstrap 5.1.3, Chart.js, Font Awesome 6

### Estructura de archivos
- `app.py` (~12.450 líneas) — aplicación principal
- `models.py` (~3.060 líneas) — modelos SQLAlchemy
- `reportes.py` (~3.400 líneas) — generación PDF
- `seed_demo.py` (~450 líneas) — seed del Demo
- `seeds/` — 11 fases del seed
- `middleware_saas.py`, `tenant_decorators.py`, `tenant_context.py` — multi-tenant
- `security_utils.py` — utilidades de seguridad multi-tenant
- `migrations/sql/` — scripts SQL versionados
- `templates/` (54 templates + `_csrf_head.html` partial + subcarpetas `secciones/`)
- `static/js/` — incluye `csrf-auto-inject.js` (nuevo)
- `.env` (protegido), `.env.example` (plantilla)
- `requirements.txt` — ahora incluye `Flask-WTF==1.3.0`, `WTForms==3.2.2`
- `HANDOFF.md` — este archivo

---

## 3️⃣ Tenants activos

| ID | Nombre | Subdominio | Plan | Licencia |
|----|--------|-----------|------|----------|
| 1 | Panadería Principal | principal | basico | local |
| 27 | **Panadería Demo** | panadería_demo | premium | nube_premium |

**Tenant principal del Demo:** `tenant_27` ("Panadería Demo").

**Tenants de producción real:** `tenant_1` (Principal) + `tenant_27` (Demo).

**Estado de `tenant_1`:** ✅ Limpio. Password de `admin` perdida (DT-44, resoluble vía endpoint).

**Estado de `tenant_27`:** ✅ Re-seedeado el 5 Oct post-DT-5-ter (9.968 filas) + 2 ventas nuevas agregadas el 8 Oct (IDs 2777, 2778) durante smoke test DT-19.

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

---

## 4️⃣ Usuarios del sistema

### Roles
- **super_admin** (dev_master) → gestiona TODOS los tenants
- **admin_cliente** → acceso TOTAL a su tenant
- **supervisor** → producción, recetas, MP, proveedores, reportes
- **cajero** → solo POS y cierre de caja

### Usuarios actuales
- **Tenant 1:** `dev_master` (super_admin), `admin` (password perdida, DT-44), `admin_1`
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
| 11 | Reportes Profesionales | ✅ COMPLETO |

---

## 6️⃣ Últimos commits pusheados
ad2b876 feat(DT-19): proteccion CSRF completa con flask-wtf
09b67e8 docs: HANDOFF v8.5 - DT-46/DT-5-bis/DT-5-quinquies/DT-5-quater-bis cerradas (Opcion Rapida 100%)
93ea142 fix(DT-5-quater-bis): limpiar debug verboso en reporte_cierre_caja
ff1d704 fix(DT-5-bis, DT-5-quinquies): documentar ORM Gasto + alinear tenant_1.gastos
34aad22 fix(DT-46): mover import de es_super_admin al top de app.py
f2caa24 fix(DT-42, DT-43): eliminar duplicaciones de codigo
a39eecf fix(DT-45): eliminar get_flashed_messages() preventivo en login() que destruia flashes
7cda002 fix(DT-28): prevenir doble submit en login (unificar 2 listeners en 1 + btn.disabled)
daa256e docs: HANDOFF v8.3 - DT-25 cerrada (before_request refactor) + DT-29 resuelta + DT-5/DT-5-ter/DT-5-quater/DT-21/DT-35 cerradas + DT-CREDITOS anotada
fe6fb0d fix(DT-25): refactor del before_request - unificar 2 middlewares duplicados en uno solo

text

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
| 7 | Ventas | ✅ | ~7.029 (+2 del smoke test DT-19 = 7.031) |
| 8 | Productos externos | ✅ | 12 |
| 9 | Activos fijos | ✅ | 36 |
| 10 | Movimientos financieros | ✅ | 261 |
| 11 | Cierres diarios | ✅ | 90 |
| 12 | Reset automatizado | ✅ | — |

**Total aproximado:** ~9.970 filas en tenant_27.

---

## 8️⃣ Configuración crítica

### Variables de entorno (.env)
DATABASE_URL=postgresql://postgres:...@localhost:5433/panaderia_master
DB_PASSWORD=...
FLASK_ENV=development
SECRET_KEY=...

text

**⚠️ Importante:** `SECRET_KEY` es **crítica** para:
- Sesiones de Flask.
- Firma de tokens CSRF (`flask-wtf`).
- Firma de cookies seguras.

Debe ser **larga, aleatoria y secreta** en producción. `flask-wtf` la usa automáticamente.

### Rutas críticas
- `/reportes`, `/historial_pagos`, `/historial_depositos`
- `/gestion_financiera`, `/mi_perfil`, `/cambiar_licencia/<id>`
- `/punto_venta`, `/registrar_venta`, `/recibo-pos/<id>`
- `/materias_primas`, `/editar_materia_prima/<id>`
- `/produccion_diaria`, `/reporte/cierre_caja`
- `/reporte/ventas_avanzado`, `/activos_fijos`
- `/depositos_bancarios`, `/depositos_bancarios/crear`
- `/admin/reset-demo`, `/admin/reset-demo/status`
- `/crear_cliente`, `/editar_cliente_super`, `/renovar_suscripcion_super`, `/eliminar_cliente/<id>`, `/gestion_clientes`
- `/configuracion/facturacion`
- `/resetear_password/<id>` (POST)

### 🎯 Arquitectura del `before_request` (post-DT-25)

**Un solo `before_request` en `app.py:1841` (`antes_de_cada_peticion`).**

Flujo:
1. **Rutas públicas** (`static`, `login`, `logout`, `suscripcion_vencida`) → return directo.
2. **CSRF por Origin/Referer** (capa adicional a CSRFProtect).
3. **Detección de tenant** (`_detectar_tenant()`): current_user > session > subdominio.
4. **Sin tenant válido** → `session.clear()` + redirect a login (NO fallback a tenant 1).
5. **Setea `g.tenant` + `g.panaderia_id` + `g.current_tenant` + `g.es_super_admin`**.
6. **`set_tenant_schema()`** una sola vez.
7. **Verificación de suscripción**.

**Funciones auxiliares en `app.py`:**
- `_validar_origen_csrf()` (L1751)
- `_detectar_tenant()`
- `_verificar_suscripcion()`
- `inject_csrf_token()` (nuevo, L1842) — context processor
- `inject_user_permissions()` (L1572) — context processor preexistente

**Rendimiento:** ~66% menos operaciones BD por request.

### 🎯 CSRF con flask-wtf (post-DT-19)

**Nueva arquitectura de protección CSRF:**

1. **`CSRFProtect(app)`** inicializado en `app.py:1251`.
   - Protege **TODOS** los POST/PUT/DELETE/PATCH por defecto.
   - Usa el header `X-CSRFToken` o el campo `csrf_token` en formularios.
   - Firma tokens con `SECRET_KEY`.

2. **Context processor `inject_csrf_token()`** (`app.py:1842`):
   - Expone `csrf_token()` a **todos** los templates sin importar.

3. **Partial `templates/_csrf_head.html`**:
   ```html
   <meta name="csrf-token" content="{{ csrf_token() }}">
   <script src="{{ url_for('static', filename='js/csrf-auto-inject.js') }}"></script>
Incluido en 53 templates vía {% include '_csrf_head.html' %} antes del </head>.
Los 4 templates que extienden base.html lo heredan.

Script static/js/csrf-auto-inject.js:

Auto-inyecta <input name="csrf_token"> en cada formulario POST.

Envuelve window.fetch para agregar X-CSRFToken a AJAX POST.

login.html tiene el token manual (funciona sin JS).

Defensa en profundidad: _validar_origen_csrf() (Origin/Referer) sigue activo como segunda capa.

Cobertura:

58 templates.

3 AJAX POST externos (pos-moderno.js).

22 AJAX POST inline en templates.

🎯 Flash messages (post-DT-45)
El handler login() ya NO consume get_flashed_messages() preventivamente.

Los flashes del logout ("Has cerrado sesión") se muestran correctamente.

Templates con bloque .flash-messages: login.html, dashboard.html, gestion_clientes.html, gestion_usuarios.html, etc. (28 templates).

🎯 es_super_admin() (post-DT-43 y DT-46)
Definición canónica única: tenant_decorators.py:19.

tenant_context.py la importa: from tenant_decorators import es_super_admin.

app.py la importa a nivel de módulo: from tenant_decorators import tenant_required, with_tenant_context, tenant_query, get_current_tenant_id, es_super_admin (L1175).

Sin imports locales redundantes (DT-46 los eliminó).

🎯 ORM Gasto (post-DT-5-bis)
Definido en models.py:1055 pero NO se usa en código activo.

Documentado con comentario aclaratorio (9 líneas) que explica por qué se mantiene.

NO eliminar sin antes revisar la nota. Referencia canónica para la tabla gastos post-DT-38.

Reevaluar si en el futuro se decide migrar a logging centralizado o reestructurar el modelo financiero.

🎯 reporte_cierre_caja() (post-DT-5-quater-bis)
Ubicada en app.py:7317-7639 (~322 líneas).

Sin prints de debug. 35 print() eliminados.

Sin query duplicada. Solo 1 query filtrada a Venta.

Sin redefinición de panaderia_id. Solo el asignado desde usuario_actual.panaderia_id.

Log silencioso en /reporte/cierre_caja.

🎯 tenant_1.gastos (post-DT-5-quinquies)
Alineada con la estructura canónica de tenant_27.gastos.

categoria: varchar(50) nullable (antes text NOT NULL).

concepto: varchar(100) NOT NULL (antes nullable).

FKs a panaderias(id) y usuarios(id) agregadas.

Migration: migrations/sql/2026-10-07_align_tenant_1_gastos.sql.

9️⃣ Deuda técnica acumulada
✅ RESUELTAS el 8 de Octubre 2026 (tarde) — DT-19
#	Descripción	Commit
DT-19	CSRF completo con flask-wtf (tokens firmados + auto-inyección JS + wrapper fetch)	ad2b876
✅ RESUELTAS el 7 de Octubre 2026 (noche) — Opción Rápida
#	Descripción	Commit
DT-46	Import es_super_admin movido al top de app.py	34aad22
DT-5-bis	ORM Gasto documentado como huérfano intencional	ff1d704
DT-5-quinquies	tenant_1.gastos alineada con tenant_27.gastos (DROP+CREATE)	ff1d704
DT-5-quater-bis (reformulada)	35 prints de debug + query duplicada eliminados de reporte_cierre_caja	93ea142
✅ RESUELTAS el 6 de Octubre 2026 (mediodía)
#	Descripción	Commit
DT-28	Doble submit en login	7cda002
DT-45	Flash messages destruidos por login()	a39eecf
DT-42	diagnosticar_recetas() duplicada	f2caa24
DT-43	es_super_admin() duplicada	f2caa24
⏸️ DT-44 — Documentada (acción pendiente del usuario)
No requiere código. Password del usuario admin (tenant 1) perdida. Endpoint /resetear_password/<id> ya existe y funciona. Resetear vía dev_master cuando se necesite (5 min).

✅ RESUELTAS el 5 de Octubre 2026 (noche)
#	Descripción	Commit
Tenants 25/26	Borrado vía endpoint (valida DT-36)	UI
DT-35	public.configuracion_sistema + pagos_individuales	Resuelta por DT-36
DT-5	Gasto vs RegistroFinanciero	"No aplica"
DT-5-quater	RegistroFinanciero vacío	Funcional
DT-5-ter	DROP columnas legacy fecha/descripcion en gastos	7adb546
DT-21	Modal crear cliente POS	Reformulada → DT-CRÉDITOS
DT-25	Refactor del before_request	fe6fb0d
DT-29	Fallback silencioso a tenant 1	Resuelta por DT-25
✅ RESUELTAS el 5 de Octubre 2026 (mañana)
Fase C.3, DT-38 (4/5 lotes), DT-40, DT-39, DT-36.

🟡 Medias pendientes
#	Ubicación	Descripción
DT-7	models.py	Inconsistencia FK (Aceptada)
DT-37	reportes.py	i18n reportes (Flask-Babel). ~8-15 h.
DT-47 (propuesta)	global	Infraestructura de logging centralizada (import logging + logger). ~2-3 h. Hay ~325 print() restantes en app.py.
🟢 Bajas pendientes
(ninguna en este momento)

🚨 Features pendientes
DT-CRÉDITOS: Módulo completo de créditos/fiado. Detalle en sección 1️⃣9️⃣.

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

Antes de duplicar código defensivamente, verificar si el framework (Flask/Bootstrap/etc.) ya maneja el caso nativamente. Ejemplo: HTML5 required ya bloquea envíos con campos vacíos.

Nunca confiar en el output de CMD para diagnosticar código con emojis o caracteres no-ASCII: el mojibake (UTF-8 → Latin-1) puede simular errores de sintaxis que no existen. Verificar SIEMPRE con el editor o con Get-Content de PowerShell.

Antes de proponer un "fix urgente" basado en sospechas, confirmar el bug con evidencia directa (imagen del editor, cat -A, hexdump). Un falso positivo puede llevar a "arreglar" código que está sano.

Al aplicar cambios en cadena (Tanda 1, Tanda 2, ...), usar los TEXTOS (comentarios, prints, strings únicos) como referencia de ubicación, no los números de línea. Los números se desfasan con cada cambio.

En PowerShell, Select-String con regex :7[3-9][0-9][0-9]: NO matchea porque el output de findstr /n ya tiene los dos puntos. Usar '^7[3-9][0-9][0-9]:' (inicio de línea) en su lugar.

Para eliminar un bloque for que contiene solo un print, eliminar el for completo (no solo el print): Python no permite for sin cuerpo.

Nunca pasar scripts PowerShell multilínea desde CMD. Los here-strings (@'...'@), los %, $, <, > se escapan mal. Usar Python (script .py creado en editor) o crear el .ps1 manualmente y ejecutarlo con powershell -ExecutionPolicy Bypass -File script.ps1.

Para migrar CSRF (o cualquier cambio transversal) en apps con muchos templates: usar "1 partial + 1 script JS" en lugar de editar 30+ formularios manualmente. Mucho más rápido y consistente.

login.html (crítico) SIEMPRE debe tener el token CSRF manual en el <form>, NO depender de JS. Los usuarios podrían tener JS bloqueado.

Los templates que extienden base.html heredan automáticamente los {% include %} del padre. No hay que editarlos si base.html ya tiene el include.

Al inicializar CSRFProtect(app) en Flask, verificar SIEMPRE la ubicación: debe ir DESPUÉS de app.secret_key. Sin SECRET_KEY, los tokens no se pueden firmar.

Comandos útiles
Encoding: chcp 65001

psql:

text
psql -U postgres -p 5433 -h localhost -d panaderia_master
Ver estructura:

text
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "\d tenant_27.nombre_tabla"
Seed Demo:

text
python seed_demo.py --tenant=27 --reset-all
Compilar / Servidor:

text
python -m py_compile app.py
python app.py
Búsquedas:

text
findstr /n /c:"patrón exacto" archivo.py
findstr /s /n /c:"patrón" *.py
findstr /s /n /c:"patrón" templates\*.html
Extraer líneas (PowerShell):

text
powershell -Command "Get-Content models.py | Select-Object -Skip 246 -First 20"
Backup de BD:

text
pg_dump -U postgres -p 5433 -h localhost -d panaderia_master -F c -f backup_pre_XXX.backup
Commit multilínea (Windows CMD):

text
# Crear _commit_msg.txt con el mensaje completo
git commit -F _commit_msg.txt
del _commit_msg.txt
Ver rama con tracking:

text
git branch -vv
Script Python de un solo uso:

Crear _script_temporal.py en el editor.

python _script_temporal.py

del _script_temporal.py al terminar.

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
Contexto: 2 before_request registrados (uno en tenant_context.py, otro en app.py) → trabajo duplicado, 2 conexiones psycopg2 raw por request, set_tenant_schema() 2 veces, mock inútil, fallback a tenant 1.

Solución:

Eliminado TenantContext.initialize_app(app).

Nuevo before_request único (128 líneas) con funciones auxiliares _validar_origen_csrf(), _detectar_tenant() (usa ORM), _verificar_suscripcion().

Rutas públicas sin overhead.

Sin fallback a tenant 1 (DT-29).

Validación end-to-end:

Login admin_27, dev_master, admin_28 (tenant nuevo).

Ciclo completo: crear tenant → login → navegar → borrar → verificar BD.

200 OK en todas las rutas críticas.

Commit: fe6fb0d.

1️⃣3️⃣ DT-28 / DT-45 — Bitácora (6 Oct 2026)
DT-28 — Doble submit en login
Bug: 2 listeners submit separados. Loading se agregaba antes de validar → botón quedaba atascado si validación fallaba. Y el botón nunca se deshabilitaba → doble click generaba 2 POSTs.

Fix: Unificar los 2 listeners en 1. Orden: validar → si OK → btn.disabled = true + .loading.

Commit: 7cda002.

DT-45 — Flash messages destruidos
Bug: El handler login() ejecutaba get_flashed_messages() preventivamente (líneas 1953-1955) al inicio, consumiendo los flashes pendientes antes del render. Efecto: "Has cerrado sesión" nunca se mostraba.

Fix: Eliminar esas 3 líneas + reordenar el docstring de login() al inicio de la función.

Commit: a39eecf.

1️⃣4️⃣ DT-42 / DT-43 — Bitácora (6 Oct 2026)
DT-42 — diagnosticar_recetas() duplicada
Bug: Definida 2 veces en app.py (líneas 1912 y 1928). Ambas idénticas.

Fix: Eliminar la 1ra (huérfana) + los comentarios ruidosos.

DT-43 — es_super_admin() duplicada
Bug: Definida 2 veces (tenant_context.py:12, tenant_decorators.py:19). Idénticas.

Fix: Mantener la canónica en tenant_decorators.py. tenant_context.py la importa.

Commit: f2caa24.

1️⃣5️⃣ DT-44 — Documentación (6 Oct 2026)
Password del usuario admin (tenant 1) perdida.

Estado: ⏸️ Pendiente de acción puntual (no requiere código).

Endpoint ya existe: POST /resetear_password/<int:usuario_id> (app.py:11362).
UI: templates/gestion_clientes.html:787 (dev_master) + templates/gestion_usuarios.html:296 (admin_cliente).

Acción: resetear vía dev_master cuando se necesite (5 min).

1️⃣6️⃣ DT-46 — Bitácora (7 Oct 2026)
Bug: before_request importaba es_super_admin localmente en L1859, cuando ya existía un import a nivel de módulo en L1175. Además, había otro import local redundante de tenant_required en L4440.

Fix:

Agregar es_super_admin al import de tenant_decorators en L1175.

Eliminar import local en L1859.

Eliminar import local en L4440 (bonus).

Verificación: smoke test (dev_master → /gestion_clientes ✅, admin_27 → /gestion_clientes ⛔ 403 ✅).

Commit: 34aad22.

1️⃣7️⃣ DT-5-bis + DT-5-quinquies — Bitácora (7 Oct 2026)
DT-5-bis — ORM Gasto documentado
Diagnóstico: ORM Gasto (models.py:1055) nunca se importa ni se usa en código activo. Templates no acceden a él. reportes.py usa RegistroFinanciero.

Decisión: NO eliminar. Documentar como huérfano intencional.

Fix: 9 líneas de comentario antes de class Gasto.

DT-5-quinquies — tenant_1.gastos alineada
Diagnóstico: tenant_1.gastos tenía estructura legacy:

categoria = text NOT NULL (debe ser varchar(50) nullable).

concepto = nullable (debe ser NOT NULL).

Sin FKs a panaderias(id) ni usuarios(id).

Tabla vacía (0 filas).

Fix: DROP + CREATE con la estructura de tenant_27.gastos.

Archivo: migrations/sql/2026-10-07_align_tenant_1_gastos.sql.

Verificación: \d tenant_1.gastos idéntico a \d tenant_27.gastos. Smoke test OK.

Commit: ff1d704.

1️⃣8️⃣ DT-5-quater-bis (reformulada) — Bitácora (7 Oct 2026)
Descripción original del HANDOFF v8.4: "return jsonify con fallback cosmético (app.py:7360-7363)".

Realidad encontrada: El jsonify original ya no existía. En su lugar había un bloque de debug verboso en reporte_cierre_caja():

Query duplicada a Venta (todas_ventas sin filtro) → performance.

35 prints de debug → log spam.

Comentario triplicado.

Redefinición de panaderia_id.

Fix (4 tandas): Eliminación progresiva de prints + bloque de debug + comentario triplicado.

Resultado: 35 prints eliminados, 50 líneas netas menos, log silencioso.

Falso positivo detectado: Se creyó ver un bug estructural en el except (string sin cerrar). Fue artefacto de mojibake. El código siempre estuvo sano.

Commit: 93ea142.

1️⃣9️⃣ DT-19 — CSRF completo con flask-wtf (8 Oct 2026)
Descripción: Migrar CSRF de solo Origin/Referer a tokens firmados con flask-wtf.

Enfoque: Plan C híbrido.

Manual en login.html (crítico).

Auto-inyección vía JS para el resto.

Fases ejecutadas:

Fase 0 — Backups (app.py.bak_pre_dt19, templates_backup_pre_dt19.zip, requirements.txt.bak_pre_dt19).

Fase 1 — Instalar flask-wtf 1.3.0 + wtforms 3.2.2. Actualizar requirements.txt.

Fase 2 — from flask_wtf.csrf import CSRFProtect (L1184) + csrf = CSRFProtect(app) (L1251).

Fase 3 — Context processor inject_csrf_token() (L1842).

Fase 4 — Script static/js/csrf-auto-inject.js + partial templates/_csrf_head.html.

Fase 5 — Script Python (_fase5_csrf.py) que insertó {% include '_csrf_head.html' %} en 53 templates.

Fase 6 — Actualizar csrf-auto-inject.js para envolver window.fetch (agrega X-CSRFToken en AJAX POST).

Fase 6.5 — Editar login.html manualmente para agregar <input type="hidden" name="csrf_token">.

Fase 7 — Smoke test completo (login, formularios, AJAX POST, todas las rutas críticas). PASÓ.

Fase 8 — Commit ad2b876.

Archivos modificados: 57 (1 app.py, 1 requirements.txt, 53 templates, 2 nuevos).

Smoke test validado:

Login con CSRF: 302 ✅.

Formularios POST tradicionales: 302 ✅.

AJAX POST (/registrar_venta): 2 ventas registradas ✅.

Todas las rutas críticas: 200 OK ✅.

Cero errores 400 ✅.

csrf-auto-inject.js se carga: 200/304 ✅.

Commit: ad2b876.

2️⃣0️⃣ DT-CRÉDITOS — Módulo de créditos/fiado (PENDIENTE — feature)
Origen: detectado durante DT-21 (5 Oct 2026). El POS tiene 3 modos:

Venta POS.

Venta electrónica (factura DIAN).

Falta: vender a crédito (fiado).

Alcance MVP
Tablas nuevas: creditos, credito_detalle, abonos.

POS: botón "Fiar" + modal simple de cliente (5 campos: nombre, tipo doc, documento, ciudad, teléfono).

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

2️⃣1️⃣ DT-37 — i18n reportes (PENDIENTE)
Alcance: reportes.py (~3.400 líneas) genera PDFs con texto hardcodeado en español. Objetivo: multi-idioma con Flask-Babel.

Estimación: ~8-15 h (sesión dedicada).

Prioridad: Media.

Requiere:

Instalar Flask-Babel.

Configurar babel.cfg.

Extraer strings de reportes.py a .po/.mo.

Soporte en config por tenant (idioma).

Probar 11+ reportes.

2️⃣2️⃣ DT-47 — Logging centralizado (PENDIENTE — propuesta)
Origen: aparece tras DT-5-quater-bis. Aún hay ~325 prints en app.py.

Alcance: Reemplazar print() por logger.debug() o app.logger.

Estimación: ~2-3 h.

Prioridad: Media.

Requiere:

import logging al top.

Configurar logger con formato y nivel.

Reemplazo progresivo (o masivo con script Python).

Probar que el log nivel DEBUG no sea verboso en producción.

2️⃣3️⃣ Notas estratégicas
Objetivo del ERP
ERP SaaS multi-tenant multi-país con: POS, inventario, producción, recetas, activos fijos, reportes con IA, finanzas, multi-país, base para API REST + IA avanzada, módulo de créditos.

🎁 Tenant Demo
Fases 1-12 completadas (~9.970 filas). Contraseña: demo2026.

Mercado objetivo
3.000-5.000 panaderías en Colombia.

10.000-30.000 en LATAM.

Precio: $60k-$600k COP/mes.

Modelo de licencias
Premium: 3 usuarios.

Básica: 1 usuario.

Estimación de tiempos (8 Oct 2026)
Bloque	Estimación
DT-47 (logging)	~2-3 h
DT-37 (i18n)	~8-15 h
DT-CRÉDITOS (MVP)	~6-8 h
DT-CRÉDITOS (completo)	~15-25 h
Fase 3 (nube + Docker)	~22-32 h
Fase 4 (seguridad adicional)	~14-20 h
Fase 5 (monetización)	~26-36 h
Fases 6-8 (IA + integraciones)	~50-85 h
📞 Cómo continuar en un chat nuevo
Al iniciar un nuevo chat, pegar este archivo como contexto inicial.

Instrucción sugerida:

"Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el archivo HANDOFF.md v8.6 con el contexto maestro. Vamos a continuar desde donde lo dejamos. Por favor actúa como instructor guiando paso a paso, con la metodología de trabajo descrita en el HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/findstr, commit tras cada fix verificado. Al insertar bloques, muéstrame ANTES → DESPUÉS con número de línea exacto. Tú me das LUZ VERDE cuando los cambios estén 100% validados. Yo aplico los cambios en mi editor."

Próxima tarea sugerida:

Dockerización (Fase 3) — sesión dedicada. ~22-32 h total, pero se puede hacer por fases.

DT-47 (logging centralizado) — ~2-3 h (opcional antes de Docker).

DT-CRÉDITOS — sesión dedicada con cuestionario previo.

DT-37 (i18n) — sesión grande.

✅ Última validación
Último commit: ad2b876 (DT-19, pusheado).

Última sesión: 8 Oct 2026 (tarde) — DT-19 completa.

Working tree: clean.

Servidor: detenido.

Sistema: 100% funcional end-to-end.

Módulos: 11/11 completados.

Demo: ~9.970 filas.

Seguridad: Producción-ready (CSRF con tokens firmados + Origin/Referer).

DT-19: ✅ Resuelta (CSRF completo).

DT-25: ✅ Resuelta.

DT-28: ✅ Resuelta.

DT-29: ✅ Resuelta.

DT-42: ✅ Resuelta.

DT-43: ✅ Resuelta.

DT-44: ⏸️ Documentada (acción pendiente del usuario).

DT-45: ✅ Resuelta.

DT-46: ✅ Resuelta.

DT-5-bis: ✅ Resuelta (documentada).

DT-5-quinquies: ✅ Resuelta (BD alineada).

DT-5-quater-bis: ✅ Resuelta (reformulada).

Pendientes: Dockerización (Fase 3), DT-37, DT-47, DT-CRÉDITOS.

Deudas críticas: ninguna.

Fin del HANDOFF.md — v8.6