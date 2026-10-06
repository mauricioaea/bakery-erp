# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP)

**Última actualización:** 5 de Octubre, 2026 (noche)
**Último commit:** fe6fb0d (fix DT-25: refactor del before_request — unificar 2 middlewares duplicados en uno solo)
**Sesión 2 Oct:** DT-11, DT-12, DT-13, DT-14, DT-16, DT-26, DT-27, DT-3, DT-4
**Sesión 3 Oct:** DT-1, DT-6, DT-9, DT-20 Fase C (Tanda 1+2+3), DT-30, DT-31
**Sesión 4 Oct:** DT-10, DT-22, DT-24, DT-17, DT-33, DT-34, DT-32, DT-18
**Sesión 5 Oct (mañana):** Fase C.3 parcial + DT-38 (4/5 lotes) + DT-40 + DT-39 + DT-36
**Sesión 5 Oct (noche):** Borrado tenants 25/26 + DT-35 + DT-5 + DT-5-quater + DT-5-ter + DT-21 + **DT-25 (refactor before_request)** + **DT-29 (resuelta de paso)**

---

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp)
- **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.3.0 — **11/11 módulos completados (100%)** + Demo Fases 1-12 + Endurecimiento de seguridad + **DT-20 al 100%** + **DT-18 reporte tesorería nivel contable** + tenant_1 limpio + **Fase C.3 cerrada** + **DT-38 4/5 lotes** + **DT-40 cerrada** + **DT-39 cerrada** + **DT-36 cerrada (public limpio)** + **DT-25 cerrada (before_request refactorizado)** + **DT-29 cerrada**
- **Arquitectura:** Multi-tenant con PostgreSQL (schemas por tenant)
- **Próximo hito:** DT-28 (doble submit) + DT-37 (i18n) + **DT-CRÉDITOS** (módulo de créditos/fiado)

---

## 2️⃣ Stack tecnológico

### Backend
- Python 3.10+, Flask 3.1.2, SQLAlchemy 2.0
- PostgreSQL 17.10 (puerto 5433)
- Flask-Login, Werkzeug (pbkdf2:sha256, scrypt), ReportLab, Matplotlib
- **BD:** `panaderia_master` — credenciales en `.env`

### Frontend
- HTML5/CSS3, JavaScript vanilla, Bootstrap 5.1.3, Chart.js, Font Awesome 6

### Estructura de archivos
- `app.py` (~12.500 líneas) — aplicación principal
- `models.py` (~3.050 líneas) — modelos SQLAlchemy
- `reportes.py` (~3.400 líneas) — generación PDF
- `seed_demo.py` (~450 líneas) — seed del Demo
- `seeds/` — 11 fases del seed
- `middleware_saas.py`, `tenant_decorators.py`, `tenant_context.py` — multi-tenant
- `security_utils.py` — utilidades de seguridad multi-tenant
- `migrations/sql/` — scripts SQL versionados
- `templates/`, `static/`
- `.env` (protegido), `.env.example` (plantilla)
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

**Estado de `tenant_27`:** ✅ Re-seedeado el 5 Oct post-DT-39 (9.968 filas).

### 📌 Arquitectura de `public.*` (post-DT-36)

**`public` tiene SOLO 3 tablas** (todas críticas, todas las demás fueron dropeadas en DT-36):

| Tabla | Rol | Filas |
|---|---|---|
| `public.tenants` | Maestra de tenants (SELECT/UPDATE/DELETE en arranque, alta, borrado) | 2 |
| `public.usuarios` | Fallback de `dev_master` (login) | 3 (`admin`, `dev_master`, `admin_1`, todos `tenant_id=1`) |
| `public.configuracion_panaderia` | Espejo de config por tenant (SELECT/DELETE en alta/baja) | 1 |

**Columnas reales de `public.tenants` (actualizado 5 Oct):**
`id`, `nombre`, `subdominio`, `base_datos`, `fecha_creacion`, `activo`, `plan`, `fecha_vencimiento`, `fecha_expiracion`.
**NO tiene columna `licencia`** (dato que vive en `ConfiguracionSistema` del tenant).

**3 secuencias asociadas:** `tenants_id_seq`, `usuarios_id_seq`, `configuracion_panaderia_id_seq`.

**El resto vive en `tenant_X.*`** (schemas por tenant), creados por `crear_tablas_en_orden(schema_name)`.

---

## 4️⃣ Usuarios del sistema

### Roles
- **super_admin** (dev_master) → gestiona TODOS los tenants
- **admin_cliente** → acceso TOTAL a su tenant
- **supervisor** → producción, recetas, MP, proveedores, reportes
- **cajero** → solo POS y cierre de caja

### Usuarios actuales
- **Tenant 1:** `dev_master` (super_admin), `admin`, `admin_1` (los 3 en `public.usuarios` con `tenant_id=1`)
- **Tenant 27:** `admin_27`, `super_27`, `cajero_27` (viven en `tenant_27.usuarios`)

**⚠️ Password de `admin` (tenant 1):** perdida. Resetear vía dev_master cuando se necesite (DT-44).

### Contraseña del Demo
- **Todos los usuarios del tenant_27:** contraseña **`demo2026`**.
- Se restaura automáticamente en cada `--reset-all`.
- Constante `DEMO_PASSWORD` en `seed_demo.py` (línea 21).

### Creación de usuarios (diseño del negocio)
- **NO se crean usuarios desde el frontend.**
- Los usuarios se crean al **alta del tenant** en `crear_tenant_saas()`.
- **Licencia premium:** 3 usuarios (admin, supervisor, cajero).
- **Licencia básica:** 1 usuario (admin) — **aunque la generación actual crea los 3 igual.**
- Los usuarios viven en `tenant_X.usuarios`.
- **NO se escriben en `public.usuarios`** salvo los 3 del `tenant_1`.

### Datos de facturación (por tenant, personalizables)
- **Cada tenant** configura sus datos fiscales en `/configuracion/facturacion`.
- Se guardan en `ConfiguracionSistema` (dentro del schema del tenant).
- Datos: `nombre_empresa`, `nit_empresa`, `direccion_empresa`, `ciudad_empresa`, `telefono_empresa`, `regimen_empresa`, `moneda`, `usa_centavos`, `simbolo_moneda`.
- **Estos datos se usan en recibos POS, facturas electrónicas y TODOS los reportes.**
- **Fallback:** si `ConfiguracionSistema` está vacío, se usan datos de `ConfiguracionPanaderia` (legacy).

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
fe6fb0d fix(DT-25): refactor del before_request - unificar 2 middlewares duplicados en uno solo
7adb546 fix(DT-5-ter): DROP columnas legacy fecha/descripcion en tabla gastos (tenant_1 + tenant_27)
da8dbeb fix(DT-36): limpieza de 42 tablas huérfanas en public.* + fix endpoint eliminar_cliente
1e4dbeb docs: HANDOFF v8.1 - DT-39 cerrada (25 columnas SIN FILAS) + reglas 35-36
d6961a2 fix(DT-39): eliminar 25 columnas SIN FILAS en 7 tablas + DROP en tenant_25/26/27
f2c5d03 docs: HANDOFF v8.0 - DT-40 cerrada (columnas legacy ventas) + reglas 33-34
a003172 fix(DT-40): eliminar 6 columnas legacy de ventas del CREATE TABLE + DROP en tenant_25/26/27
bf31e96 docs: HANDOFF v7.9 - DT-38 cerrada (4/5 lotes) + reglas 31-32
480e9e3 fix(DT-38 Lote D): alinear HistorialMantenimiento con BD + arreglar SQL crudo
b656964 fix(DT-38 Lote C): alinear StockProducto con BD
856392e fix(DT-38 Lote B): alinear Gasto con BD
2748a70 fix(DT-38 Lote A): agregar JornadaVentas.total_tarjeta al ORM

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
| 7 | Ventas | ✅ | ~7.029 |
| 8 | Productos externos | ✅ | 12 |
| 9 | Activos fijos | ✅ | 36 |
| 10 | Movimientos financieros | ✅ | 261 |
| 11 | Cierres diarios | ✅ | 90 |
| 12 | Reset automatizado | ✅ | — |

**Total aproximado:** ~9.968 filas en tenant_27 (verificado el 5 Oct post-DT-5-ter).

**Última re-ejecución:** 5 Oct 2026 (post-DT-5-ter) — `EXIT_CODE=0`.

---

## 8️⃣ Configuración crítica

### Variables de entorno (.env)
DATABASE_URL=postgresql://postgres:...@localhost:5433/panaderia_master
DB_PASSWORD=...
FLASK_ENV=development
SECRET_KEY=...

text

- `.env` en `.gitignore`. `.env.example` en el repo.
- `load_dotenv()` al inicio de `app.py` (línea ~1258).
- **SECRET_KEY** se lee del `.env` (DT-14).

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
- **Eliminado:** `/crear_usuario`

### Bug sistémico — panaderia_id default=1 (DT-20)

**✅ RESUELTO AL 100% (3 Oct 2026).** Ningún modelo tiene `default=1` en `panaderia_id`. Si un INSERT olvida pasar `panaderia_id`, falla con `IntegrityError`.

### 🎯 Arquitectura del `before_request` (post-DT-25)

**Un solo `before_request` en `app.py:1736` (`antes_de_cada_peticion`).**

Flujo:
1. **Rutas públicas** (`static`, `login`, `logout`, `suscripcion_vencida`) → return directo, sin overhead.
2. **CSRF** por Origin/Referer (solo POST/PUT/DELETE/PATCH).
3. **Detección de tenant** (`_detectar_tenant()`): current_user > session > subdominio.
4. **Sin tenant válido** → `session.clear()` + redirect a login (NO fallback a tenant 1).
5. **Setea `g.tenant` (dict) + `g.panaderia_id` (int) + `g.current_tenant` + `g.es_super_admin`**.
6. **`set_tenant_schema()`** una sola vez.
7. **Verificación de suscripción** (`_verificar_suscripcion()`).

**Funciones auxiliares en `app.py`:**
- `_validar_origen_csrf()` — CSRF por Origin.
- `_detectar_tenant()` — detección por ORM (NO psycopg2 raw).
- `_verificar_suscripcion()` — vigencia de suscripción.

**Eliminado:** `TenantContext.initialize_app(app)` (duplicaba el `before_request`).

**Rendimiento:** ~66% menos operaciones BD por request (2 conexiones raw `psycopg2` → 0, 4 queries → 2).

---

## 9️⃣ Deuda técnica acumulada

### ✅ RESUELTAS el 5 de Octubre 2026 (mañana)

| # | Descripción | Commit |
|---|-------------|--------|
| Fase C.3.1-5 | Auditoría columnas huérfanas + alineación ORM↔BD | `cefb33f` |
| DT-38 Lote A | `JornadaVentas.total_tarjeta` agregada al ORM | `2748a70` |
| DT-38 Lote B | `Gasto` alineado con BD | `856392e` |
| DT-38 Lote C | `StockProducto` alineado con BD | `b656964` |
| DT-38 Lote D | `HistorialMantenimiento` alineado con BD | `480e9e3` |
| DT-40 | 6 columnas legacy de `ventas` eliminadas | `a003172` |
| DT-39 | 25 columnas SIN FILAS eliminadas en 7 tablas | `d6961a2` |
| DT-36 | 42 tablas huérfanas en `public.*` dropeadas + fix endpoint `eliminar_cliente` | `da8dbeb` |

### ✅ RESUELTAS el 5 de Octubre 2026 (noche)

| # | Descripción | Método |
|---|-------------|--------|
| **Tenants 25/26** | Borrado vía endpoint (valida DT-36 2ª vez) | UI |
| **DT-35** | `public.configuracion_sistema` + `pagos_individuales` | Resuelta por DT-36 |
| **DT-5** | `Gasto` vs `RegistroFinanciero` | "No aplica" — sin solapamiento |
| **DT-5-quater** | `RegistroFinanciero` vacío en tenant_27 | Funcional (nunca se ejecutó cierre) |
| **DT-5-ter** | DROP columnas legacy `fecha`/`descripcion` en `gastos` | Script SQL `2026-10-05_drop_gastos_legacy.sql` |
| **DT-21** | Modal crear cliente POS | "No aplica" — reformulada a DT-CRÉDITOS |
| **DT-25** | Refactor `before_request` (2 middlewares → 1) | Commit `fe6fb0d` |
| **DT-29** | Fallback silencioso a tenant 1 | Resuelta de paso por DT-25 |

### 🟡 Medias pendientes

| # | Ubicación | Descripción |
|---|-----------|-------------|
| DT-5-bis | `models.py:1055` | ORM `Gasto` huérfano — nunca instanciado, todo es SQL crudo |
| DT-5-quater-bis | `app.py:7360-7363` | `return jsonify` con fallback cosmético al crear `RegistroFinanciero` |
| DT-5-quinquies | `tenant_1.gastos` | Estructura legacy distinta al ORM (8 cols vs 7, `categoria NOT NULL text`) |
| DT-7 | `models.py` | Inconsistencia FK: 2 modelos con FK a `panaderias.id`, 2 no. **Aceptada (4 Oct).** |
| DT-19 | global | CSRF completo con `flask-wtf` |
| DT-28 | `POST /` | Doble submit detectado (cosmético, sin daño real) |
| DT-37 | `reportes.py` | **Soporte multi-idioma (i18n).** Refactor con `Flask-Babel`. |
| DT-42 | `app.py:1912` y `app.py:1928` | `diagnosticar_recetas()` duplicada. Eliminar la 2da (tiene comentario sospechoso `# ✅✅✅ AGREGA...`). |
| DT-43 | `tenant_context.py:12` + `tenant_decorators.py:19` | `es_super_admin()` definida 2 veces. Unificar. |
| DT-44 | tenant_1 | Password de `admin` (tenant 1) perdida. Resetear vía dev_master. |

### 🟢 Bajas pendientes
*(ninguna en este momento)*

### 🚨 Otras deudas
- **DT-CRÉDITOS:** Módulo completo de créditos/fiado para POS. **Detalle en sección 1️⃣9️⃣.**

---

## 🔟 Metodología de trabajo

### Reglas de oro
1. **Un paso a la vez** con confirmación antes de continuar.
2. **Diagnóstico ANTES de modificar.**
3. **Soluciones de raíz** (no parches).
4. **TODO debe funcionar para futuros tenants.**
5. **Verificación con psql/findstr** antes de avanzar.
6. **Commit después de cada fix verificado.**
7. **Backup antes de cada cambio grande.**
8. **Siempre verificar `git status` antes de commitear.**
9. **Push después del commit.**
10. **Detener servidor antes de reiniciar.**
11. **Insertar bloques: mostrar ANTES → DESPUÉS con número de línea exacto.**
12. **Verificar ubicación y compilar tras cada inserción.**
13. **Al detectar deuda técnica: anotarla (no tocarla), priorizarla, decidir después.**
14. **Al insertar código a nivel de módulo: ubicarlo junto a sus hermanos temáticos.**
15. **Al pedir un test, incluir TODAS las verificaciones previas necesarias.**
16. **Cuando el punto de inserción esté justo debajo de un decorador, incluir el decorador en el ANTES → DESPUÉS.**
17. **Antes de proponer un fix de concurrencia, medir impacto en el pool de SQLAlchemy.**
18. **Nunca usar `echo texto >> archivo` en Windows para modificar archivos de texto.**
19. **Nunca acceder a `current_user` desde event listeners de SQLAlchemy.**
20. **En Windows, usar `findstr /c:"patrón"` para búsquedas literales.**
21. **Antes de aplicar un fix según el HANDOFF, verificar el estado actual del archivo.**
22. **Al eliminar código huérfano, verificar PRIMERO que no haya referencias activas (incluye templates HTML y JS).**
23. **Al auditar modelos con `default=N`: verificar TODOS los INSERTs (ORM + SQL directo).**
24. **Al eliminar una columna de un modelo, verificar SIEMPRE primero: (a) si hay lecturas en el código, (b) si hay datos inconsistentes en la BD, (c) si hay usuarios/registros que apunten a valores huérfanos.**
25. **Al hacer DELETE masivos en la BD, verificar SIEMPRE: (a) backup previo, (b) que no haya FKs apuntando a los registros, (c) que no sean tenants reales en `public.tenants`.**
26. **Al modificar un método de `reportes.py` que genera PDF, verificar SIEMPRE el orden de las secciones y que todas las variables estén definidas ANTES de usarse.**
27. **Nunca asumir que el esquema de la BD coincide con el modelo ORM. Verificar con `information_schema.columns` ANTES de usar un ORM en un contexto nuevo.**
28. **Al auditar columnas (Fase C.3), usar `COUNT(DISTINCT col)` en lugar de `COUNT(col)` para evitar falsos positivos por valores DEFAULT 0/constantes.**
29. **Al agregar una segunda FK a una tabla, SQLAlchemy requiere `foreign_keys=[...]` explícito en los `relationship` para evitar `AmbiguousForeignKeysError`.**
30. **Al alinear `CREATE TABLE` con el ORM, actualizar también los seeds que hagan INSERT directo sobre las columnas afectadas.**
31. **Al arrancar la app, se ejecuta una migración automática que agrega columnas del ORM que falten en la BD. Nunca asumir que el `CREATE TABLE` en `app.py` refleja el estado real de la BD. Verificar siempre con `information_schema.columns`.**
32. **Al alinear ORM↔BD, revisar TODOS los usos del modelo en templates HTML, JavaScript y CSS, además del código Python.**
33. **Al hacer `DROP COLUMN`, verificar SIEMPRE primero con `information_schema.columns` en QUÉ schemas existe la columna. No asumir que existe en todos. Ejecutar el DROP por transacción individual.**
34. **Al hacer cambios destructivos en BD, tomar un backup FRESCO con `pg_dump -F c` inmediatamente antes. Verificar que el archivo `.backup` pese > 0 bytes.**
35. **Al quitar columnas del `CREATE TABLE`, verificar SIEMPRE si la columna eliminada era la ÚLTIMA del bloque. Si lo era, hay que quitar la coma de la línea precedente. Verificar el bloque completo con `powershell` después de editar.**
36. **Antes de hacer commit de un `CREATE TABLE` modificado, revisar el `git diff` línea por línea para confirmar que las columnas eliminadas son exactamente las previstas.**
37. **Antes de hacer DROP masivos, verificar SIEMPRE las FKs internas con `information_schema.table_constraints` para respetar el orden de dependencias. Las tablas padre se dropean al final; las hojas primero.**
38. **Al dropear una tabla referenciada por otra que se CONSERVA, primero soltar la FK explícitamente (`ALTER TABLE ... DROP CONSTRAINT ...` + `DROP COLUMN`) antes del DROP de la tabla destino.**
39. **Un endpoint de borrado de tenant debe limpiar TODAS las tablas `public.*` que puedan tener datos del tenant. Hoy son: `tenants`, `usuarios` (por `tenant_id`), `configuracion_panaderia` (por `tenant_id`/`panaderia_id`). Verificar tras cada cambio en `public` si el endpoint sigue completo.**
40. **Al verificar `COUNT(*)` de tablas, NO confiar en `pg_stat_user_tables.n_live_tup` (está desfasado). Usar siempre `COUNT(*)` real.**
41. **Cuando `powershell -Command "Get-Content ... | Select-Object ..."` corte la salida en un emoji UTF-8 (✅, 🔴, etc.), usar `findstr /n /r /c:"^" archivo.py > _dump.txt` y luego `Select-Object` sobre ese archivo. Evita el truncado por mojibake.**
42. **Antes de refactorizar un `before_request` o middleware global, mapear TODOS los escritores/lectores de `g.*` (`g.tenant`, `g.panaderia_id`, etc.) con `findstr` para no romper contratos implícitos.**
43. **En Windows CMD, para `git commit -m "mensaje multilínea"`: crear un archivo `_commit_msg.txt` y usar `git commit --amend -F _commit_msg.txt`. CMD no interpreta bien las comillas multilínea.**

### Comandos útiles

**Encoding:** `chcp 65001`

**psql:**
psql -U postgres -p 5433 -h localhost -d panaderia_master

text
Dentro: `SET client_encoding TO 'UTF8';` Salir: `\q`

**Ver estructura:**
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "\d tenant_27.nombre_tabla"

text

**Seed Demo:**
python seed_demo.py --tenant=27 --reset-all

text

**Compilar / Servidor:**
python -m py_compile app.py
python app.py

text

**Búsquedas:**
findstr /n /c:"patrón exacto" archivo.py
findstr /s /n /c:"patrón" *.py
findstr /s /n /c:"patrón" templates*.html

text

**Extraer líneas (PowerShell):**
powershell -Command "Get-Content models.py | Select-Object -Skip 246 -First 20"

text

**Backup de BD:**
pg_dump -U postgres -p 5433 -h localhost -d panaderia_master -F c -f backup_pre_XXX.backup

text

**Commit multilínea (Windows CMD):**
Crear _commit_msg.txt con el mensaje completo
git commit --amend -F _commit_msg.txt
del _commit_msg.txt

text

---

## 1️⃣1️⃣ Fase C.3 — Auditoría de columnas huérfanas (cerrada)

### Contexto
El 5 de Oct, se detectó que la BD (tenant_27) y el ORM estaban desalineados por desincronización acumulada entre:
1. `CREATE TABLE` de `app.py`.
2. `models.py` (ORM).
3. Seeds (SQL crudo con nombres viejos).
4. Migración automática del ORM.

### Lo que se hizo
- **Fase C.3 parcial:** alineación de modelos vivos (`cefb33f`).
- **DT-38:** 4 lotes de modelos muertos (`2748a70`, `856392e`, `b656964`, `480e9e3`).
- **DT-39:** 25 columnas SIN FILAS en 7 tablas (`d6961a2`).
- **DT-40:** 6 columnas legacy en `ventas` (`a003172`).
- **DT-36:** 42 tablas huérfanas en `public` + fix endpoint (`da8dbeb`).
- **DT-5-ter:** columnas legacy `fecha`/`descripcion` en `gastos` (noche 5 Oct).

**Resultado:** la BD está ahora alineada con el ORM. `public` tiene solo 3 tablas críticas. Los tenants nuevos nacen limpios.

---

## 1️⃣2️⃣ DT-11 — Resuelto (2 Oct 2026) — Bitácora

**Causa raíz:** El event listener `checkout` accedía a `current_user` → recursión infinita con `load_user`.

**Solución:** Eliminar `current_user` del event listener. Leer solo de `flask.session`.

**Commit:** `a522e0c`

---

## 1️⃣3️⃣ DT-20 — Bug sistémico del default=1 — Resuelto (3 Oct 2026)

**Problema:** 32 modelos tenían `panaderia_id = db.Column(..., default=1)`.

**Solución:** 4 fases + DT-31 (`ALTER TABLE DROP DEFAULT` en 7 columnas).

**Resultado:** 31 modelos sin `default=1`. Fail-fast con `IntegrityError`.

---

## 1️⃣4️⃣ DT-18 — Reporte de tesorería nivel contable — Resuelto (4 Oct 2026)

**Contexto:** el reporte original tenía 3 secciones y sin datos fiscales.

**Solución:** 6 secciones profesionales + encabezado fiscal + consecutivo + firma.

**Commits:** `e512c12` + `d8a8afd`.

---

## 1️⃣5️⃣ DT-38 — Bitácora detallada (5 Oct 2026)

**Contexto:** 5 modelos "muertos". 4/5 lotes ejecutados.

- **Lote A** — JornadaVentas: `+total_tarjeta` ✅
- **Lote B** — Gasto: `fecha→fecha_gasto, descripcion→concepto, +observaciones, +usuario_id` ✅
- **Lote C** — StockProducto: `receta_id→producto_id, +stock_maximo` ✅
- **Lote D** — HistorialMantenimiento: `activo_id→activo_fijo_id, realizado_por→tecnico` ✅
- **Lote E** — HistorialInventario: ⏸️ Diferido.

---

## 1️⃣6️⃣ DT-40 — Bitácora detallada (5 Oct 2026)

**Contexto:** 6 columnas legacy en `ventas` (`total_venta`, `total_donacion`, `impuesto`, `descuento`, `consecutivo`, `observaciones`).

**Diagnóstico:** todas con valores 0 o NULL. Cero referencias en código.

**Ejecución:**
- Paso 1: `CREATE TABLE` en `app.py:445` limpiado ✅
- Paso 2: 18 `ALTER TABLE DROP COLUMN` en tenant_25/26/27 ✅
- Paso 3: `migrations/sql/2026-10-05_drop_ventas_legacy.sql` ✅
- Paso 4: smoke test OK ✅
- Paso 5: re-seed OK ✅
- Paso 6: commit `a003172` ✅

---

## 1️⃣7️⃣ DT-39 — Bitácora detallada (5 Oct 2026)

**Contexto:** 25 columnas huérfanas SIN FILAS en 7 tablas vacías.

**Ejecución — 7 sub-lotes:**
- 39-A: `logs_sistema` (2 cols)
- 39-B: `control_vida_util` (2 cols) — coma colgante corregida
- 39-C: `historial_rotacion_producto` (2 cols)
- 39-D: `detalle_compras` (2 cols)
- 39-E: `compras` (4 cols)
- 39-F: `registros_diarios` (6 cols)
- 39-G: `registros_financieros` (7 cols)
- `migrations/sql/2026-10-05_drop_columnas_sin_filas.sql` ✅
- Re-seed + smoke test + commit `d6961a2` ✅

**Lección (regla 35):** quitar la coma de la línea precedente al eliminar la última columna.

---

## 1️⃣8️⃣ DT-36 — Bitácora detallada (5 Oct 2026)

**Contexto:** A lo largo del desarrollo se crearon 50+ tenants de prueba. Al borrarlos, el endpoint `/eliminar_cliente` solo hacía `DROP SCHEMA` + `DELETE` en 3 tablas de `public`, dejando restos acumulados en 42 tablas más.

### Diagnóstico
- **45 tablas en `public`:** 3 críticas + 30 vacías + 6 con datos huérfanos + 3 backups + 3 residuos.
- **110 filas huérfanas** en `productos` (37), `categorias` (24), `permisos_usuario` (21), `jornadas_ventas` (18), `panaderias` (9), `proveedor` (1).
- **El código usa SOLO** `public.tenants`, `public.usuarios`, `public.configuracion_panaderia`.

### Ejecución
- **Fase A — Backup:** `backup_pre_dt36.backup` (909 KB) ✅
- **Fase B — Limpieza de `public`:** DROP de 42 tablas ✅
- **Fase C — Fix del endpoint `/eliminar_cliente`:** Añadido paso 5: `DELETE FROM public.usuarios WHERE tenant_id = :id` ✅
- **Fase D — Auditoría del alta:** confirmado que `crear_tenant_saas` es limpio ✅
- **Fase E — Verificación end-to-end:** Ciclo completo tenant_28 → verificar → borrar → verificar ✅
- **Fase F — Commit:** `da8dbeb` ✅

**Validaciones posteriores:**
- 5 Oct noche, borrado de tenants 25 y 26 vía UI: ✅
- 5 Oct noche, borrado del tenant 28 (creado durante DT-25): ✅ 5 acciones completas del endpoint.

---

## 1️⃣9️⃣ DT-25 — Bitácora detallada (5 Oct 2026, noche)

**Contexto original (HANDOFF v8.2):** "Orden real de `before_request` vs `login_required`".

### Diagnóstico
- **Había 2 `before_request` registrados:**
  1. `tenant_context.py:46` (`set_tenant_context`) — registrado en `app.py:1209` (`TenantContext.initialize_app`), corre PRIMERO.
  2. `app.py:1736` (`antes_de_cada_peticion`) — corre SEGUNDO.
- **El de `app.py` hacía 9+ responsabilidades** en 210 líneas:
  - CSRF por Origin.
  - Query BD para verificar tenant en session.
  - **2 conexiones `psycopg2` raw** por request.
  - `set_tenant_schema()` **2 veces por request**.
  - Llamaba a `obtener_info_usuario()` (mock inútil, retornaba siempre datos del tenant 1).
  - **Fallback silencioso a tenant 1** (DT-29).
- **El de `tenant_context.py` era un no-op** en la práctica (porque el `hasattr(g, 'panaderia_id')` nunca era True al ser el primero).
- **Contrato crítico detectado:** `g.panaderia_id` (int) es fuente de verdad para `security_utils.py`, `tenant_decorators.py` y `tenant_context.py`. `g.tenant` (dict) era la fuente para `app.py`.

### Solución aplicada (commit `fe6fb0d`)
- **Eliminado:** `TenantContext.initialize_app(app)` en `app.py:1209`.
- **Reemplazado:** el `before_request` completo por versión limpia de 128 líneas.
- **Nuevas funciones auxiliares:**
  - `_validar_origen_csrf()`
  - `_detectar_tenant()` (usa ORM, no psycopg2 raw)
  - `_verificar_suscripcion()`
- **Nuevo comportamiento:**
  - Salta rutas públicas (`static`, `login`, `logout`, `suscripcion_vencida`).
  - Sin tenant válido → limpia sesión + redirect a login (**elimina DT-29**).
  - Setea `g.tenant` + `g.panaderia_id` + `g.current_tenant` + `g.es_super_admin`.
  - `set_tenant_schema()` **1 vez**.

### Validación (test end-to-end)
1. **Login** admin_27, dev_master → ✅
2. **Navegación módulos** tenant_27 (POS, Producción, Reportes, Financiera) → ✅
3. **`/static/css/pos-moderno.css`** → ✅ 304
4. **Sin sesión → `/punto_venta`** → ✅ 302 → login (DT-29 resuelta)
5. **Crear tenant_28 "Test DT25"** vía `/gestion_clientes` → ✅
6. **Verificar BD:** `public.tenants`=3, schema `tenant_28` creado, 3 usuarios, `public.usuarios` limpio → ✅
7. **Login admin_28** → ✅ detecta `tenant_28` correctamente
8. **Navegar módulos tenant_28** (vacíos) → ✅
9. **Borrar tenant_28** vía UI → ✅ 5 acciones del endpoint completas
10. **Verificar BD post-borrado:** `public.tenants`=2, schemas=`tenant_1`,`tenant_27`, `public.usuarios`=3 → ✅

### Impacto
- **Eliminadas** 2 conexiones raw `psycopg2` por request.
- **Eliminado** `set_tenant_schema()` duplicado.
- **Eliminado** `obtener_info_usuario()` (mock inútil).
- **Eliminado** fallback silencioso a tenant 1 (**DT-29**).
- **Rendimiento:** ~66% menos operaciones BD por request.

**Diff:** `app.py | 320 +++++---`, `124 insertions(+), 196 deletions(-)`.

---

## 2️⃣0️⃣ DT-CRÉDITOS — Módulo de créditos/fiado (PENDIENTE — feature)

**Origen:** detectado durante DT-21 (5 Oct 2026, noche). El POS actual tiene 3 modos:
1. Venta POS (recibo rápido).
2. Venta electrónica (factura DIAN).
3. **Falta:** vender a crédito (fiado).

### Alcance MVP
- **Tablas nuevas:** `creditos`, `credito_detalle`, `abonos`.
- **POS:** botón "Fiar" + modal simple de cliente (5 campos: nombre, tipo doc, documento, ciudad, teléfono).
- **Endpoints:** `/fiar_venta` + `/registrar_abono`.
- **Sección nueva:** "Créditos" con estado de cuenta + CxC.

### Decisiones de negocio pendientes (cuestionario previo)
- ¿Se descuenta del inventario al fiar o al cobrar?
- ¿Cupo por cliente?
- ¿IVA al fiar o al cobrar?
- ¿Intereses por mora?
- ¿Cómo manejar cliente que no paga?

### Estimación
- **MVP:** 6-8 h (1-2 sesiones).
- **Completo (aging, moras, reportes):** 15-25 h (3-4 sesiones).

### Reutilizable
- ✅ Tabla `clientes` (solo `nombre`/`documento`/`telefono`).
- ✅ `POST /registrar_venta` (con flag `es_credito=true`).
- ✅ Estructura del carrito.

### NO reutilizable
- ❌ Modal `clienteModal` (11 campos fiscales — overkill).
- ❌ `/api/guardar-cliente`.
- ❌ `procesarVentaElectronica()`.

### Prioridad
**Media-alta.** Después de cerrar todas las DT pendientes.

---

## 2️⃣1️⃣ Notas estratégicas

### Objetivo del ERP
ERP SaaS multi-tenant multi-país con: POS, inventario, producción, recetas, activos fijos, reportes con IA, finanzas, multi-país, base para API REST + IA avanzada, **módulo de créditos**.

### 🎁 Tenant Demo (marketing)
Fases 1-12 completadas (~9.968 filas). Contraseña: `demo2026`. Reset desde `/mi_perfil` con `dev_master`.

### Mercado objetivo
- 3.000-5.000 panaderías en Colombia.
- 10.000-30.000 en LATAM.
- Precio: $60k-$600k COP/mes.

### Modelo de licencias
- Premium: 3 usuarios (admin, supervisor, cajero).
- Básica: 1 usuario (admin).
- Los usuarios se crean al alta del tenant.

### Personalización por tenant
- Cada tenant configura sus datos fiscales en `/configuracion/facturacion`.
- Se usan en recibos POS, facturas electrónicas y todos los reportes.

### Estimación de tiempos (5 Oct 2026, noche)
| Bloque | Estimación |
|--------|------------|
| DT-28 (doble submit) | ~1 h |
| DT-37 (i18n reportes) | ~8-15 h |
| DT-42, DT-43, DT-44 (nuevas bajas) | ~1-2 h |
| DT-5-bis, DT-5-quater-bis, DT-5-quinquies | ~2-3 h |
| **DT-CRÉDITOS (MVP)** | **~6-8 h** |
| DT-CRÉDITOS (completo) | ~15-25 h |
| Fase 3 (nube + Docker) | ~22-32 h |
| Fase 4 (seguridad avanzada) | ~14-20 h |
| Fase 5 (monetización) | ~26-36 h |
| Fases 6-8 (IA + integraciones) | ~50-85 h |

---

## 📞 Cómo continuar en un chat nuevo

Al iniciar un nuevo chat, pegar este archivo como contexto inicial.

**Instrucción sugerida para el asistente:**

> "Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el archivo HANDOFF.md v8.3 con el contexto maestro del proyecto. Vamos a continuar desde donde lo dejamos. Por favor actúa como instructor guiando paso a paso, con la metodología de trabajo descrita en el HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/findstr, commit tras cada fix verificado. Al insertar bloques, muéstrame ANTES → DESPUÉS con número de línea exacto. **Antes de cualquier cambio, espera mi LUZ VERDE explícita.**"

**Próxima tarea sugerida:**
1. **DT-28** (doble submit en login — 1 h).
2. **DT-42, DT-43, DT-44** (limpiezas rápidas — 1-2 h).
3. **DT-37** (i18n reportes — sesión dedicada).
4. **DT-CRÉDITOS** (módulo completo — sesión dedicada).

---

## ✅ Última validación

- **Último commit:** `fe6fb0d` (DT-25 cerrada, pusheado).
- **Última sesión:** 5 Oct 2026 (noche) — Borrado tenants 25/26 + DT-35 + DT-5 + DT-5-quater + DT-5-ter + DT-21 + DT-25 + DT-29.
- **Working tree:** clean.
- **Servidor:** detenido.
- **Sistema:** 100% funcional end-to-end.
- **Módulos:** 11/11 completados (100%).
- **Demo:** Fases 1-12 completadas, contraseña `demo2026`, ~9.968 filas.
- **Log:** limpio, sin warnings.
- **DT-20:** ✅ 100% RESUELTO.
- **DT-25:** ✅ **RESUELTA** (refactor completo del `before_request`).
- **DT-29:** ✅ **RESUELTA** (de paso por DT-25).
- **DT-35:** ✅ Cerrada (resuelta por DT-36).
- **DT-5:** ✅ Cerrada ("no aplica").
- **DT-5-quater:** ✅ Cerrada (funcional).
- **DT-5-ter:** ✅ Cerrada (DROP columnas legacy `gastos`).
- **DT-21:** ✅ Cerrada (reformulada a DT-CRÉDITOS).
- **`public`: 3 tablas, 3 secuencias** ✅
- **`tenant_1`:** ✅ Limpio.
- **`tenant_27`:** ✅ Re-seedeado (9.968 filas).
- **Deudas críticas pendientes:** ninguna.
- **Pendientes:** DT-28, DT-37 + nuevas bajas (DT-5-bis, DT-5-quater-bis, DT-5-quinquies, DT-42, DT-43, DT-44).
- **Features pendientes:** DT-CRÉDITOS.

---

**Fin del HANDOFF.md — v8.3**