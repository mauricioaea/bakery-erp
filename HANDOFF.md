# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP)

**Última actualización:** 6 de Octubre, 2026 (mediodía)
**Último commit:** f2caa24 (fix DT-42, DT-43: eliminar duplicaciones de código)
**Sesión 2 Oct:** DT-11, DT-12, DT-13, DT-14, DT-16, DT-26, DT-27, DT-3, DT-4
**Sesión 3 Oct:** DT-1, DT-6, DT-9, DT-20 Fase C (Tanda 1+2+3), DT-30, DT-31
**Sesión 4 Oct:** DT-10, DT-22, DT-24, DT-17, DT-33, DT-34, DT-32, DT-18
**Sesión 5 Oct (mañana):** Fase C.3 parcial + DT-38 (4/5 lotes) + DT-40 + DT-39 + DT-36
**Sesión 5 Oct (noche):** Borrado tenants 25/26 + DT-35 + DT-5 + DT-5-quater + DT-5-ter + DT-21 + DT-25 (refactor before_request) + DT-29
**Sesión 6 Oct (mediodía):** DT-28 + DT-45 + DT-42 + DT-43 + DT-44 (documentada)

---

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp)
- **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.3.1 — **11/11 módulos completados (100%)** + Demo Fases 1-12 + Endurecimiento de seguridad + DT-20 100% + DT-18 reporte tesorería nivel contable + tenant_1 limpio + Fase C.3 cerrada + DT-25 cerrada (before_request refactorizado) + DT-29 cerrada + DT-28/DT-45/DT-42/DT-43 cerradas
- **Arquitectura:** Multi-tenant con PostgreSQL (schemas por tenant)
- **Próximo hito:** DT-37 (i18n reportes) + DT-CRÉDITOS (módulo de fiado)

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
- `app.py` (~12.480 líneas) — aplicación principal
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

**Estado de `tenant_1`:** ✅ Limpio. Password de `admin` perdida (DT-44, resoluble vía endpoint).

**Estado de `tenant_27`:** ✅ Re-seedeado el 5 Oct post-DT-5-ter (9.968 filas).

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

```
f2caa24 fix(DT-42, DT-43): eliminar duplicaciones de codigo
a39eecf fix(DT-45): eliminar get_flashed_messages() preventivo en login() que destruia flashes
7cda002 fix(DT-28): prevenir doble submit en login (unificar 2 listeners en 1 + btn.disabled)
daa256e docs: HANDOFF v8.3 - DT-25 cerrada (before_request refactor) + DT-29 resuelta + DT-5/DT-5-ter/DT-5-quater/DT-21/DT-35 cerradas + DT-CREDITOS anotada
fe6fb0d fix(DT-25): refactor del before_request - unificar 2 middlewares duplicados en uno solo
7adb546 fix(DT-5-ter): DROP columnas legacy fecha/descripcion en tabla gastos (tenant_1 + tenant_27)
40e74d8 docs: HANDOFF v8.2 - DT-36 cerrada (public limpio + fix endpoint eliminar_cliente) + reglas 37-40
da8dbeb fix(DT-36): limpieza de 42 tablas huérfanas en public.* + fix endpoint eliminar_cliente
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
| 7 | Ventas | ✅ | ~7.029 |
| 8 | Productos externos | ✅ | 12 |
| 9 | Activos fijos | ✅ | 36 |
| 10 | Movimientos financieros | ✅ | 261 |
| 11 | Cierres diarios | ✅ | 90 |
| 12 | Reset automatizado | ✅ | — |

**Total aproximado:** ~9.968 filas en tenant_27.

---

## 8️⃣ Configuración crítica

### Variables de entorno (.env)
```
DATABASE_URL=postgresql://postgres:...@localhost:5433/panaderia_master
DB_PASSWORD=...
FLASK_ENV=development
SECRET_KEY=...
```

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

**Un solo `before_request` en `app.py:1736` (`antes_de_cada_peticion`).**

Flujo:
1. **Rutas públicas** (`static`, `login`, `logout`, `suscripcion_vencida`) → return directo.
2. **CSRF** por Origin/Referer.
3. **Detección de tenant** (`_detectar_tenant()`): current_user > session > subdominio.
4. **Sin tenant válido** → `session.clear()` + redirect a login (NO fallback a tenant 1).
5. **Setea `g.tenant` + `g.panaderia_id` + `g.current_tenant` + `g.es_super_admin`**.
6. **`set_tenant_schema()`** una sola vez.
7. **Verificación de suscripción**.

**Funciones auxiliares en `app.py`:**
- `_validar_origen_csrf()`
- `_detectar_tenant()`
- `_verificar_suscripcion()`

**Rendimiento:** ~66% menos operaciones BD por request.

### 🎯 Flash messages (post-DT-45)

- El handler `login()` **ya NO** consume `get_flashed_messages()` preventivamente.
- Los flashes del logout ("Has cerrado sesión") **se muestran correctamente**.
- Templates con bloque `.flash-messages`: `login.html`, `dashboard.html`, `gestion_clientes.html`, `gestion_usuarios.html`, etc. (28 templates).

### 🎯 `es_super_admin()` (post-DT-43)

- **Definición canónica única:** `tenant_decorators.py:19`.
- `tenant_context.py` la **importa**: `from tenant_decorators import es_super_admin`.
- `app.py` la **importa dentro del `before_request`**: `from tenant_decorators import es_super_admin`.

---

## 9️⃣ Deuda técnica acumulada

### ✅ RESUELTAS el 6 de Octubre 2026 (mediodía)

| # | Descripción | Commit |
|---|-------------|--------|
| **DT-28** | Doble submit en login (unificar 2 listeners + `btn.disabled`) | `7cda002` |
| **DT-45** | `get_flashed_messages()` preventivo destruía flashes del logout | `a39eecf` |
| **DT-42** | `diagnosticar_recetas()` duplicada en `app.py` | `f2caa24` |
| **DT-43** | `es_super_admin()` duplicada en `tenant_context.py` + `tenant_decorators.py` | `f2caa24` |

### ⏸️ DT-44 — Documentada (acción pendiente del usuario)

**No requiere código.** Password del usuario `admin` (tenant 1) perdida. Endpoint `/resetear_password/<id>` ya existe y funciona. Resetear vía dev_master cuando se necesite (5 min).

### ✅ RESUELTAS el 5 de Octubre 2026 (noche)

| # | Descripción | Commit |
|---|-------------|--------|
| Tenants 25/26 | Borrado vía endpoint (valida DT-36) | UI |
| DT-35 | `public.configuracion_sistema` + `pagos_individuales` | Resuelta por DT-36 |
| DT-5 | `Gasto` vs `RegistroFinanciero` | "No aplica" |
| DT-5-quater | `RegistroFinanciero` vacío | Funcional |
| DT-5-ter | DROP columnas legacy `fecha`/`descripcion` en `gastos` | `7adb546` |
| DT-21 | Modal crear cliente POS | Reformulada → DT-CRÉDITOS |
| **DT-25** | **Refactor del `before_request`** | **`fe6fb0d`** |
| **DT-29** | **Fallback silencioso a tenant 1** | **Resuelta por DT-25** |

### ✅ RESUELTAS el 5 de Octubre 2026 (mañana)

Fase C.3, DT-38 (4/5 lotes), DT-40, DT-39, DT-36.

### 🟡 Medias pendientes

| # | Ubicación | Descripción |
|---|-----------|-------------|
| DT-5-bis | `models.py:1055` | ORM `Gasto` huérfano |
| DT-5-quater-bis | `app.py:7360-7363` | `return jsonify` con fallback cosmético |
| DT-5-quinquies | `tenant_1.gastos` | Estructura legacy distinta al ORM |
| DT-7 | `models.py` | Inconsistencia FK (**Aceptada**) |
| DT-19 | global | CSRF completo con `flask-wtf` |
| DT-37 | `reportes.py` | **i18n reportes** (Flask-Babel). ~8-15 h. |
| DT-46 | `app.py:1859` | `before_request` importa `es_super_admin` dentro de la función. Mover al top del archivo. Baja prioridad. |

### 🟢 Bajas pendientes
*(ninguna en este momento)*

### 🚨 Features pendientes

- **DT-CRÉDITOS:** Módulo completo de créditos/fiado. **Detalle en sección 1️⃣9️⃣.**

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
28. **Al auditar columnas (Fase C.3), usar `COUNT(DISTINCT col)` en lugar de `COUNT(col)` para evitar falsos positivos.**
29. **Al agregar una segunda FK a una tabla, SQLAlchemy requiere `foreign_keys=[...]` explícito.**
30. **Al alinear `CREATE TABLE` con el ORM, actualizar también los seeds.**
31. **Al arrancar la app, se ejecuta una migración automática que agrega columnas del ORM que falten en la BD. Verificar siempre con `information_schema.columns`.**
32. **Al alinear ORM↔BD, revisar TODOS los usos del modelo en templates HTML, JavaScript y CSS.**
33. **Al hacer `DROP COLUMN`, verificar SIEMPRE primero con `information_schema.columns` en QUÉ schemas existe. Ejecutar el DROP por transacción individual.**
34. **Al hacer cambios destructivos en BD, tomar un backup FRESCO con `pg_dump -F c` inmediatamente antes.**
35. **Al quitar columnas del `CREATE TABLE`, verificar SIEMPRE si la columna eliminada era la ÚLTIMA del bloque. Si lo era, hay que quitar la coma de la línea precedente.**
36. **Antes de hacer commit de un `CREATE TABLE` modificado, revisar el `git diff` línea por línea.**
37. **Antes de hacer DROP masivos, verificar SIEMPRE las FKs internas con `information_schema.table_constraints`.**
38. **Al dropear una tabla referenciada por otra que se CONSERVA, primero soltar la FK explícitamente.**
39. **Un endpoint de borrado de tenant debe limpiar TODAS las tablas `public.*` que puedan tener datos del tenant.**
40. **Al verificar `COUNT(*)` de tablas, NO confiar en `pg_stat_user_tables.n_live_tup`. Usar siempre `COUNT(*)` real.**
41. **Cuando `powershell -Command "Get-Content ... | Select-Object ..."` corte la salida en un emoji UTF-8, usar `findstr /n /r /c:"^" archivo.py > _dump.txt` y luego `Select-Object` sobre ese archivo.**
42. **Antes de refactorizar un `before_request` o middleware global, mapear TODOS los escritores/lectores de `g.*`.**
43. **En Windows CMD, para `git commit -m "mensaje multilínea"`: crear un archivo `_commit_msg.txt` y usar `git commit --amend -F _commit_msg.txt`.**
44. **Antes de duplicar código defensivamente, verificar si el framework (Flask/Bootstrap/etc.) ya maneja el caso nativamente. Ejemplo: HTML5 `required` ya bloquea envíos con campos vacíos.**

### Comandos útiles

**Encoding:** `chcp 65001`

**psql:**
```
psql -U postgres -p 5433 -h localhost -d panaderia_master
```

**Ver estructura:**
```
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "\d tenant_27.nombre_tabla"
```

**Seed Demo:**
```
python seed_demo.py --tenant=27 --reset-all
```

**Compilar / Servidor:**
```
python -m py_compile app.py
python app.py
```

**Búsquedas:**
```
findstr /n /c:"patrón exacto" archivo.py
findstr /s /n /c:"patrón" *.py
findstr /s /n /c:"patrón" templates\*.html
```

**Extraer líneas (PowerShell):**
```
powershell -Command "Get-Content models.py | Select-Object -Skip 246 -First 20"
```

**Backup de BD:**
```
pg_dump -U postgres -p 5433 -h localhost -d panaderia_master -F c -f backup_pre_XXX.backup
```

**Commit multilínea (Windows CMD):**
```
# Crear _commit_msg.txt con el mensaje completo
git commit --amend -F _commit_msg.txt
del _commit_msg.txt
```

---

## 1️⃣1️⃣ Fase C.3 — Auditoría de columnas huérfanas (cerrada)

Auditoría del 5 Oct, alineación ORM↔BD:
- **Fase C.3 parcial:** modelos vivos (`cefb33f`).
- **DT-38:** 4 lotes de modelos muertos.
- **DT-39:** 25 columnas SIN FILAS.
- **DT-40:** 6 columnas legacy en `ventas`.
- **DT-36:** 42 tablas huérfanas en `public`.
- **DT-5-ter:** columnas legacy en `gastos`.

---

## 1️⃣2️⃣ DT-25 — Bitácora detallada (5 Oct 2026)

**Contexto:** 2 `before_request` registrados (uno en `tenant_context.py`, otro en `app.py`) → trabajo duplicado, 2 conexiones `psycopg2` raw por request, `set_tenant_schema()` 2 veces, mock inútil, fallback a tenant 1.

**Solución:**
- Eliminado `TenantContext.initialize_app(app)`.
- Nuevo `before_request` único (128 líneas) con funciones auxiliares `_validar_origen_csrf()`, `_detectar_tenant()` (usa ORM), `_verificar_suscripcion()`.
- Rutas públicas sin overhead.
- Sin fallback a tenant 1 (DT-29).

**Validación end-to-end:**
- Login admin_27, dev_master, admin_28 (tenant nuevo).
- Ciclo completo: crear tenant → login → navegar → borrar → verificar BD.
- 200 OK en todas las rutas críticas.

**Commit:** `fe6fb0d`.

---

## 1️⃣3️⃣ DT-28 / DT-45 — Bitácora (6 Oct 2026)

### DT-28 — Doble submit en login
**Bug:** 2 listeners `submit` separados. Loading se agregaba antes de validar → botón quedaba atascado si validación fallaba. Y el botón nunca se deshabilitaba → doble click generaba 2 POSTs.

**Fix:** Unificar los 2 listeners en 1. Orden: validar → si OK → `btn.disabled = true` + `.loading`.

**Commit:** `7cda002`.

### DT-45 — Flash messages destruidos
**Bug:** El handler `login()` ejecutaba `get_flashed_messages()` preventivamente (líneas 1953-1955) al inicio, **consumiendo** los flashes pendientes antes del render. Efecto: "Has cerrado sesión" nunca se mostraba.

**Fix:** Eliminar esas 3 líneas + reordenar el docstring de `login()` al inicio de la función.

**Commit:** `a39eecf`.

---

## 1️⃣4️⃣ DT-42 / DT-43 — Bitácora (6 Oct 2026)

### DT-42 — `diagnosticar_recetas()` duplicada
**Bug:** Definida 2 veces en `app.py` (líneas 1912 y 1928). Ambas idénticas. La 2da rodeada de comentarios `# ✅✅✅ AGREGA...` / `# ✅✅✅ FIN DE...`.

**Fix:** Eliminar la 1ra (huérfana) + los comentarios ruidosos.

### DT-43 — `es_super_admin()` duplicada
**Bug:** Definida 2 veces (`tenant_context.py:12`, `tenant_decorators.py:19`). Idénticas.

**Fix:** Mantener la canónica en `tenant_decorators.py`. `tenant_context.py` la importa (`from tenant_decorators import es_super_admin`).

**Verificación:** sin import circular (ya importaba `TenantSecurityException` de ahí). Smoke test: login admin_27 (False) + dev_master (True).

**Commit:** `f2caa24`.

---

## 1️⃣5️⃣ DT-44 — Documentación (6 Oct 2026)

**Password del usuario `admin` (tenant 1) perdida.**

**Estado:** ⏸️ Pendiente de acción puntual (no requiere código).

**Endpoint ya existe:** `POST /resetear_password/<int:usuario_id>` (`app.py:11362`).
**UI:** `templates/gestion_clientes.html:787` (dev_master) + `templates/gestion_usuarios.html:296` (admin_cliente).

**Acción:** resetear vía dev_master cuando se necesite (5 min).

---

## 1️⃣6️⃣ DT-CRÉDITOS — Módulo de créditos/fiado (PENDIENTE — feature)

**Origen:** detectado durante DT-21 (5 Oct 2026). El POS tiene 3 modos:
1. Venta POS.
2. Venta electrónica (factura DIAN).
3. **Falta:** vender a crédito (fiado).

### Alcance MVP
- **Tablas nuevas:** `creditos`, `credito_detalle`, `abonos`.
- **POS:** botón "Fiar" + modal simple de cliente (5 campos: nombre, tipo doc, documento, ciudad, teléfono).
- **Endpoints:** `/fiar_venta` + `/registrar_abono`.
- **Sección nueva:** "Créditos" con estado de cuenta + CxC.

### Decisiones de negocio pendientes (cuestionario previo)
- ¿Inventario al fiar o al cobrar?
- ¿Cupo por cliente?
- ¿IVA al fiar o al cobrar?
- ¿Intereses por mora?
- ¿Cómo manejar cliente que no paga?

### Estimación
- **MVP:** 6-8 h (1-2 sesiones).
- **Completo:** 15-25 h (3-4 sesiones).

### Reutilizable
- ✅ Tabla `clientes`.
- ✅ `POST /registrar_venta` (con flag `es_credito=true`).
- ✅ Estructura del carrito.

### NO reutilizable
- ❌ Modal `clienteModal` (11 campos fiscales).
- ❌ `/api/guardar-cliente`.
- ❌ `procesarVentaElectronica()`.

**Prioridad:** Media-alta, después de cerrar DT-37.

---

## 1️⃣7️⃣ DT-37 — i18n reportes (PENDIENTE)

**Alcance:** `reportes.py` (~3.400 líneas) genera PDFs con texto hardcodeado en español. Objetivo: multi-idioma con `Flask-Babel`.

**Estimación:** ~8-15 h (sesión dedicada).

**Prioridad:** Media.

**Requiere:**
- Instalar `Flask-Babel`.
- Configurar `babel.cfg`.
- Extraer strings de `reportes.py` a `.po`/`.mo`.
- Soporte en config por tenant (idioma).
- Probar 11+ reportes.

---

## 1️⃣8️⃣ Notas estratégicas

### Objetivo del ERP
ERP SaaS multi-tenant multi-país con: POS, inventario, producción, recetas, activos fijos, reportes con IA, finanzas, multi-país, base para API REST + IA avanzada, **módulo de créditos**.

### 🎁 Tenant Demo
Fases 1-12 completadas (~9.968 filas). Contraseña: `demo2026`.

### Mercado objetivo
- 3.000-5.000 panaderías en Colombia.
- 10.000-30.000 en LATAM.
- Precio: $60k-$600k COP/mes.

### Modelo de licencias
- Premium: 3 usuarios.
- Básica: 1 usuario.

### Estimación de tiempos (6 Oct 2026)
| Bloque | Estimación |
|--------|------------|
| DT-37 (i18n) | ~8-15 h |
| DT-46 (mover import) | ~5 min |
| DT-5-bis, DT-5-quater-bis, DT-5-quinquies | ~2-3 h |
| DT-19 (CSRF) | ~2-3 h |
| DT-CRÉDITOS (MVP) | ~6-8 h |
| DT-CRÉDITOS (completo) | ~15-25 h |
| Fase 3 (nube + Docker) | ~22-32 h |
| Fase 4 (seguridad) | ~14-20 h |
| Fase 5 (monetización) | ~26-36 h |
| Fases 6-8 (IA + integraciones) | ~50-85 h |

---

## 📞 Cómo continuar en un chat nuevo

Al iniciar un nuevo chat, pegar este archivo como contexto inicial.

**Instrucción sugerida:**

> "Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el archivo HANDOFF.md v8.4 con el contexto maestro. Vamos a continuar desde donde lo dejamos. Por favor actúa como instructor guiando paso a paso, con la metodología de trabajo descrita en el HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/findstr, commit tras cada fix verificado. Al insertar bloques, muéstrame ANTES → DESPUÉS con número de línea exacto. **Tú me das LUZ VERDE cuando los cambios estén 100% validados. Yo aplico los cambios en mi editor.**"

**Próxima tarea sugerida:**
1. **DT-46** (mover import `es_super_admin` al top) — 5 min.
2. **DT-5-bis, DT-5-quater-bis, DT-5-quinquies** — 2-3 h (limpiezas rápidas).
3. **DT-37** (i18n) — sesión dedicada.
4. **DT-CRÉDITOS** — sesión dedicada con cuestionario previo.

---

## ✅ Última validación

- **Último commit:** `f2caa24` (DT-42 + DT-43, pusheado).
- **Última sesión:** 6 Oct 2026 (mediodía) — DT-28, DT-45, DT-42, DT-43, DT-44 (documentada).
- **Working tree:** clean.
- **Servidor:** detenido.
- **Sistema:** 100% funcional end-to-end.
- **Módulos:** 11/11 completados.
- **Demo:** ~9.968 filas.
- **DT-25:** ✅ Resuelta (before_request refactorizado).
- **DT-28:** ✅ Resuelta (doble submit login).
- **DT-29:** ✅ Resuelta (fallback tenant 1).
- **DT-42:** ✅ Resuelta (`diagnosticar_recetas` única).
- **DT-43:** ✅ Resuelta (`es_super_admin` única).
- **DT-44:** ⏸️ Documentada (acción pendiente del usuario).
- **DT-45:** ✅ Resuelta (flash messages).
- **Pendientes:** DT-37, DT-46, DT-5-bis, DT-5-quater-bis, DT-5-quinquies, DT-19, DT-CRÉDITOS.
- **Deudas críticas:** ninguna.

---

**Fin del HANDOFF.md — v8.4**