# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP)

**Última actualización:** 5 de Octubre, 2026 (noche)
**Último commit:** da8dbeb (fix DT-36: limpieza de 42 tablas huérfanas en public.* + fix endpoint eliminar_cliente)
**Sesión 2 Oct:** DT-11, DT-12, DT-13, DT-14, DT-16, DT-26, DT-27, DT-3, DT-4
**Sesión 3 Oct:** DT-1, DT-6, DT-9, DT-20 Fase C (Tanda 1+2+3), DT-30, DT-31
**Sesión 4 Oct:** DT-10, DT-22, DT-24, DT-17, DT-33, DT-34, DT-32, DT-18
**Sesión 5 Oct:** Fase C.3 parcial + DT-38 (4/5 lotes) + **DT-40** + **DT-39** + **DT-36** (todas cerradas)

---

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp)
- **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.2.2 — **11/11 módulos completados (100%)** + Demo Fases 1-12 + Endurecimiento de seguridad + **DT-20 al 100%** + **DT-18 reporte tesorería nivel contable** + tenant_1 limpio + **Fase C.3 parcial** + **DT-38 4/5 lotes** + **DT-40 cerrada** + **DT-39 cerrada** + **DT-36 cerrada (public limpio)**
- **Arquitectura:** Multi-tenant con PostgreSQL (schemas por tenant)
- **Próximo hito:** deudas medias (DT-5, DT-37, DT-19, DT-21, DT-25, DT-28, DT-29) + Docker + nube

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
- `app.py` (~12.620 líneas) — aplicación principal
- `models.py` (~3.050 líneas) — modelos SQLAlchemy
- `reportes.py` (~3.400 líneas) — generación PDF
- `seed_demo.py` (~450 líneas) — seed del Demo
- `seeds/` — 11 fases del seed
- `middleware_saas.py`, `tenant_decorators.py`, `tenant_context.py` — multi-tenant
- `migrations/sql/` — scripts SQL versionados
- `templates/`, `static/`
- `.env` (protegido), `.env.example` (plantilla)
- `HANDOFF.md` — este archivo

---

## 3️⃣ Tenants activos

| ID | Nombre | Subdominio | Plan | Licencia |
|----|--------|-----------|------|----------|
| 1 | Panadería Principal | principal | basico | local |
| 25 | Panadería Test Fase C | panadería_test_fase_ | premium | nube_premium |
| 26 | Test Audit Fase C.2 | test_audit_fase_c2 | premium | nube_premium |
| 27 | **Panadería Demo** | panadería_demo | premium | nube_premium |

**Tenant principal del Demo:** `tenant_27` ("Panadería Demo").

**Tenants de producción real:** `tenant_1` (Principal) + `tenant_27` (Demo).

**Tenants de prueba:** `tenant_25`, `tenant_26` (pendientes de borrado en una próxima sesión).

**Estado de `tenant_1`:** ✅ Limpio.

**Estado de `tenant_27`:** ✅ Re-seedeado el 5 Oct post-DT-39 (9.781 filas, EXIT_CODE=0).

### 📌 Arquitectura de `public.*` (post-DT-36)

**`public` tiene SOLO 3 tablas** (todas críticas, todas las demás fueron dropeadas en DT-36):

| Tabla | Rol | Filas |
|---|---|---|
| `public.tenants` | Maestra de tenants (SELECT/UPDATE/DELETE en arranque, alta, borrado) | 4 |
| `public.usuarios` | Fallback de `dev_master` (login) | 3 (`admin`, `dev_master`, `admin_1`, todos `tenant_id=1`) |
| `public.configuracion_panaderia` | Espejo de config por tenant (SELECT/DELETE en alta/baja) | 1 |

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
- **Tenant 1:** `dev_master` (super_admin), `admin`, `admin_1`
- **Tenant 25:** `admin_25`, `super_25`, `cajero_25`
- **Tenant 26:** `admin_26`, `super_26`, `cajero_26`
- **Tenant 27:** `admin_27`, `super_27`, `cajero_27`

### Contraseña del Demo
- **Todos los usuarios del tenant_27:** contraseña **`demo2026`**.
- Se restaura automáticamente en cada `--reset-all`.
- Constante `DEMO_PASSWORD` en `seed_demo.py` (línea 21).

### Creación de usuarios (diseño del negocio)
- **NO se crean usuarios desde el frontend.**
- Los usuarios se crean al **alta del tenant** en `crear_tenant_saas()`.
- **Licencia premium:** 3 usuarios (admin, supervisor, cajero).
- **Licencia básica:** 1 usuario (admin).
- Los usuarios viven en `tenant_X.usuarios`.
- **NO se escriben en `public.usuarios`** salvo los 3 del `tenant_1` (que son el fallback para `dev_master`).

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
da8dbeb fix(DT-36): limpieza de 42 tablas huérfanas en public.* + fix endpoint eliminar_cliente (DELETE public.usuarios por tenant_id)
1e4dbeb docs: HANDOFF v8.1 - DT-39 cerrada (25 columnas SIN FILAS) + reglas 35-36
d6961a2 fix(DT-39): eliminar 25 columnas SIN FILAS en 7 tablas + DROP en tenant_25/26/27
f2c5d03 docs: HANDOFF v8.0 - DT-40 cerrada (columnas legacy ventas) + reglas 33-34
a003172 fix(DT-40): eliminar 6 columnas legacy de ventas del CREATE TABLE + DROP en tenant_25/26/27
bf31e96 docs: HANDOFF v7.9 - DT-38 cerrada (4/5 lotes) + reglas 31-32
480e9e3 fix(DT-38 Lote D): alinear HistorialMantenimiento con BD + arreglar SQL crudo
b656964 fix(DT-38 Lote C): alinear StockProducto con BD
856392e fix(DT-38 Lote B): alinear Gasto con BD
2748a70 fix(DT-38 Lote A): agregar JornadaVentas.total_tarjeta al ORM
e2029a4 docs: HANDOFF v7.8 - Fase C.3 parcial
cefb33f fix(DT-FaseC.3): alinear ORM y BD
74a76af docs: HANDOFF v7.7 - DT-18 cerrado
d8a8afd feat(DT-18): reporte tesoreria nivel contable
e512c12 feat(DT-18): encabezado fiscal + consecutivo
272f60d fix(DT-32): eliminar columna panaderia_id redundante en Panaderia
9d0d026 docs: HANDOFF v7.6 - DT-33 + DT-34
a417502 docs: HANDOFF v7.5
08dae2d fix(DT-17): fuente de ingresos en reporte tesoreria
70e7916 fix(DT-10, DT-22, DT-24)
9012851 docs(DT-31): versionar script SQL
e3dd9d4 docs: HANDOFF v7.4 - DT-20 al 100%
b111005 fix(DT-20 Fase C - Tanda 3)
82ed869 docs: HANDOFF v7.3
14de608 fix(DT-20 Fase C - Tanda 2)
45d011e fix(DT-20 Fase C - Tanda 1)
0becbf8 fix(DT-1)
9b29c3b docs: HANDOFF v7.2
a25505a fix(DT-6, DT-9)
11662f5 docs: HANDOFF v7.1
71f6ae1 fix(DT-3, DT-4)
8bda650 docs: HANDOFF v7
cafc325 fix(DT-14)
301bd65 docs(DT-13)
ffd8e8f fix(DT-16)
6e260b1 fix(DT-12)
1e4c120 fix(DT-27)
a2a2e71 docs: HANDOFF v6
cbcb76b chore: limpiar .gitignore
a522e0c fix(DT-11)

---

## 7️⃣ Demo — Estado de las fases del seed

| # | Fase | Estado | Filas |
|---|------|--------|-------|
| 1 | Configuración base | ✅ | 9 |
| 2 | Proveedores | ✅ | 6 |
| 3 | Materias primas | ✅ | 17 |
| 4 | Recetas y fórmulas | ✅ | 12 recetas / 80 ingredientes |
| 5 | Productos | ✅ | 12 |
| 6 | Producción diaria | ✅ | ~2.168 |
| 7 | Ventas | ✅ | ~7.084 |
| 8 | Productos externos | ✅ | 12 |
| 9 | Activos fijos | ✅ | ~39 |
| 10 | Movimientos financieros | ✅ | ~264 |
| 11 | Cierres diarios | ✅ | 90 |
| 12 | Reset automatizado | ✅ | — |

**Total aproximado:** ~9.781 filas en tenant_27 (verificado el 5 Oct post-DT-39).

**Última re-ejecución:** 5 Oct 2026 (post-DT-39) — `EXIT_CODE=0`.

---

## 8️⃣ Configuración crítica

### Variables de entorno (.env)
DATABASE_URL=postgresql://postgres:...@localhost:5433/panaderia_master
DB_PASSWORD=...
FLASK_ENV=development
SECRET_KEY=...

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

---

## 9️⃣ Deuda técnica acumulada

### ✅ RESUELTAS el 5 de Octubre 2026

| # | Descripción | Commit |
|---|-------------|--------|
| Fase C.3.1-5 | Auditoría columnas huérfanas + alineación ORM↔BD en modelos vivos | `cefb33f` |
| DT-38 Lote A | `JornadaVentas.total_tarjeta` agregada al ORM | `2748a70` |
| DT-38 Lote B | `Gasto` alineado con BD | `856392e` |
| DT-38 Lote C | `StockProducto` alineado con BD | `b656964` |
| DT-38 Lote D | `HistorialMantenimiento` alineado con BD | `480e9e3` |
| **DT-40** | **6 columnas legacy de `ventas` eliminadas del CREATE TABLE + DROP en tenant_25/26/27** | **`a003172`** |
| **DT-39** | **25 columnas SIN FILAS eliminadas en 7 tablas + DROP en tenant_25/26/27** | **`d6961a2`** |
| **DT-36** | **42 tablas huérfanas en `public.*` dropeadas + fix endpoint `eliminar_cliente` (DELETE `public.usuarios` por `tenant_id`)** | **`da8dbeb`** |

### ⚠️ DT-38 — Cerrada con 4 de 5 lotes

- **Lote A** (`JornadaVentas`): ✅
- **Lote B** (`Gasto`): ✅
- **Lote C** (`StockProducto`): ✅
- **Lote D** (`HistorialMantenimiento`): ✅
- **Lote E** (`HistorialInventario`): ⏸️ **Diferido.** El endpoint `producir_receta` está huérfano en el frontend. La tabla se usa solo por el seed (Fase 6) por SQL crudo.

### ✅ RESUELTAS en sesiones anteriores (2-4 Oct)

DT-1, DT-3, DT-4, DT-6, DT-9, DT-10, DT-11, DT-12, DT-13, DT-14, DT-15 (aceptada), DT-16, DT-17, DT-18, DT-20 (100%), DT-22, DT-24, DT-26, DT-27, DT-30, DT-31, DT-32, DT-33, DT-34. D1, DT-2, DT-2b, B3, B4 v2, B7.

### 🔴 Críticas pendientes
**Ninguna.** ✅

### 🟡 Medias pendientes

| # | Ubicación | Descripción |
|---|-----------|-------------|
| DT-5 | `models.py:1055 vs 2441` | `Gasto` vs `RegistroFinanciero` posible solapamiento |
| DT-7 | `models.py` | Inconsistencia FK: 2 modelos con FK a `panaderias.id`, 2 no. **Aceptada (4 Oct).** |
| DT-19 | global | CSRF completo con `flask-wtf` |
| DT-21 | POS | Modal de crear cliente sin botón visible |
| DT-25 | `app.py:1744` | Orden real de `before_request` vs `login_required` |
| DT-28 | `POST /` | Doble submit detectado |
| DT-29 | `app.py` (before_request fallback) | Tenant por defecto "Panadería Principal" en usuarios anónimos |
| DT-35 | `public.configuracion_sistema` + `public.pagos_individuales` | **Ya no aplica** tras DT-36 (tablas dropeadas). Verificar en HANDOFF v8.3. |
| DT-37 | `reportes.py` | **Soporte multi-idioma (i18n).** Refactor con `Flask-Babel`. |

### 🟢 Bajas pendientes
*(ninguna en este momento)*

### 🚨 Otras deudas
- **Tenants 25 y 26:** pendientes de borrado (usar el endpoint `/eliminar_cliente` con el fix de DT-36). Prioridad baja.

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

### Comandos útiles

**Encoding:** `chcp 65001`

**psql:**
```cmd
psql -U postgres -p 5433 -h localhost -d panaderia_master
```
Dentro: `SET client_encoding TO 'UTF8';` Salir: `\q`

**Ver estructura:**
```cmd
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "\d tenant_27.nombre_tabla"
```

**Seed Demo:**
```cmd
python seed_demo.py --tenant=27 --reset-all
```

**Compilar / Servidor:**
```cmd
python -m py_compile app.py
python app.py
```

**Búsquedas:**
```cmd
findstr /n /c:"patrón exacto" archivo.py
findstr /s /n /c:"patrón" *.py
findstr /s /n /c:"patrón" templates\*.html
```

**Extraer líneas (PowerShell):**
```cmd
powershell -Command "Get-Content models.py | Select-Object -Skip 246 -First 20"
```

**Backup de BD:**
```cmd
pg_dump -U postgres -p 5433 -h localhost -d panaderia_master -F c -f backup_pre_XXX.backup
```

**Auditoría de columnas (Fase C.3):**
```cmd
python audit_columns.py
python audit_columns_classify_v2.py
```

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

**Descubrimiento:** `tenant_1` **NO tenía** las columnas (schema distinto).

---

## 1️⃣7️⃣ DT-39 — Bitácora detallada (5 Oct 2026)

**Contexto:** 25 columnas huérfanas SIN FILAS en 7 tablas vacías.

**Diagnóstico:** cruce ORM↔BD → 25 huérfanas. `findstr` → 0 referencias. 100% ruido.

**Ejecución — 7 sub-lotes:**
- 39-A: `logs_sistema` (2 cols) ✅
- 39-B: `control_vida_util` (2 cols) — ⚠️ coma colgante corregida ✅
- 39-C: `historial_rotacion_producto` (2 cols) ✅
- 39-D: `detalle_compras` (2 cols) ✅
- 39-E: `compras` (4 cols) ✅
- 39-F: `registros_diarios` (6 cols) ✅
- 39-G: `registros_financieros` (7 cols) ✅
- `migrations/sql/2026-10-05_drop_columnas_sin_filas.sql` ✅
- Re-seed + smoke test + commit `d6961a2` ✅

**Descubrimiento:** `tenant_1` **NO tenía** las columnas.

**Lección (regla 35):** quitar la coma de la línea precedente al eliminar la última columna.

---

## 1️⃣8️⃣ DT-36 — Bitácora detallada (5 Oct 2026)

**Contexto:** A lo largo del desarrollo se crearon 50+ tenants de prueba. Al borrarlos, el endpoint `/eliminar_cliente` solo hacía `DROP SCHEMA` + `DELETE` en 3 tablas de `public`, dejando restos acumulados en 42 tablas más.

### Diagnóstico

- **45 tablas en `public`:** 3 críticas + 30 vacías + 6 con datos huérfanos + 3 backups + 3 residuos.
- **110 filas huérfanas** en `productos` (37), `categorias` (24), `permisos_usuario` (21), `jornadas_ventas` (18), `panaderias` (9), `proveedor` (1).
- **44 FKs internas** entre las tablas de `public`.
- **El código usa SOLO** `public.tenants`, `public.usuarios`, `public.configuracion_panaderia`.
- **El alta (`crear_tenant_saas`)** escribe solo en `public.tenants` + `tenant_X.*`. NO toca las 42 dropeadas.
- **El borrado (`/eliminar_cliente`)** limpiaba solo `tenants`, `configuracion_panaderia`, dejando restos en `public.usuarios` (por eso la limpieza era incompleta).

### Ejecución

**Fase A — Backup:** `backup_pre_dt36.backup` (909 KB) ✅

**Fase B — Limpieza de `public`:**
- Soltar FK `usuarios.sucursal_id` → `sucursales.id` ✅
- DROP de 42 tablas (con `IF EXISTS` + `CASCADE`) ✅
- Resultado: `public` con SOLO 3 tablas + 3 secuencias ✅
- Script: `migrations/sql/2026-10-05_limpieza_public.sql` ✅

**Fase C — Fix del endpoint `/eliminar_cliente`:**
- Añadido paso 5: `DELETE FROM public.usuarios WHERE tenant_id = :id` ✅
- Renumerado paso 6 (setval) ✅

**Fase D — Auditoría del alta:** confirmado que `crear_tenant_saas` es limpio ✅

**Fase E — Verificación end-to-end:**
- Arranque limpio ✅
- Smoke test 15+ rutas ✅
- **Ciclo completo:** crear `tenant_28` → verificar en `public.tenants` + `tenant_28` → borrar → verificar que NO queda nada en `public` (5 consultas) ✅
- Los 3 usuarios originales intactos ✅

**Fase F — Commit:** `da8dbeb` ✅

### Lecciones aprendidas (reglas 37-40)
- **Regla 37:** verificar FKs antes de DROP masivo.
- **Regla 38:** soltar FK explícitamente antes de dropear tabla referenciada por otra que se conserva.
- **Regla 39:** el endpoint de borrado debe limpiar TODAS las tablas `public.*` con datos del tenant.
- **Regla 40:** no confiar en `pg_stat_user_tables.n_live_tup` (desfasado).

---

## 1️⃣9️⃣ Notas estratégicas

### Objetivo del ERP
ERP SaaS multi-tenant multi-país con: POS, inventario, producción, recetas, activos fijos, reportes con IA, finanzas, multi-país, base para API REST + IA avanzada.

### 🎁 Tenant Demo (marketing)
Fases 1-12 completadas (~9.781 filas). Contraseña: `demo2026`. Reset desde `/mi_perfil` con `dev_master`.

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
| DT-5 (Gasto vs RegistroFinanciero) | ~1-2 h |
| DT-37 (i18n reportes) | ~8-15 h |
| DT-19, DT-21, DT-25, DT-28, DT-29 | ~6-10 h |
| Borrar tenants 25 y 26 con el endpoint | ~15 min |
| Fase 3 (nube + Docker) | ~22-32 h |
| Fase 4 (seguridad) | ~14-20 h |
| Fase 5 (monetización) | ~26-36 h |
| Fases 6-8 (IA + integraciones) | ~50-85 h |

---

## 📞 Cómo continuar en un chat nuevo

Al iniciar un nuevo chat, pegar este archivo como contexto inicial.

**Instrucción sugerida para el asistente:**

> "Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el archivo HANDOFF.md v8.2 con el contexto maestro del proyecto. Vamos a continuar desde donde lo dejamos. Por favor actúa como instructor guiando paso a paso, con la metodología de trabajo descrita en el HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/findstr, commit tras cada fix verificado. Al insertar bloques, muéstrame ANTES → DESPUÉS con número de línea exacto. **Antes de cualquier cambio, espera mi LUZ VERDE explícita.**"

**Próxima tarea sugerida:** DT-5 (Gasto vs RegistroFinanciero) o borrar tenants 25/26 con el endpoint arreglado.

---

## ✅ Última validación

- **Último commit:** `da8dbeb` (DT-36 cerrada, pusheado).
- **Última sesión:** 5 Oct 2026 — Fase C.3 parcial + DT-38 + DT-40 + DT-39 + DT-36 (todas cerradas).
- **Working tree:** clean.
- **Servidor:** detenido.
- **Sistema:** 100% funcional end-to-end.
- **Módulos:** 11/11 completados (100%).
- **Demo:** Fases 1-12 completadas, contraseña `demo2026`, ~9.781 filas.
- **Log:** limpio, sin warnings.
- **DT-20:** ✅ 100% RESUELTO.
- **DT-17:** ✅ Reporte tesorería funcional.
- **DT-18:** ✅ Reporte tesorería nivel contable.
- **DT-32:** ✅ Columna redundante eliminada.
- **Fase C.3 (modelos vivos):** ✅ Alineada.
- **DT-38 (5 modelos muertos):** ✅ 4/5 lotes. Lote E diferido.
- **DT-40 (columnas legacy ventas):** ✅ **RESUELTA.**
- **DT-39 (25 columnas SIN FILAS):** ✅ **RESUELTA.**
- **DT-36 (public.* limpio + fix endpoint):** ✅ **RESUELTA.**
- **`public`: 3 tablas, 3 secuencias** ✅
- **`tenant_1`:** ✅ Limpio.
- **Deudas críticas pendientes:** ninguna.
- **Pendientes:** DT-5, DT-37, DT-19, DT-21, DT-25, DT-28, DT-29.

---

**Fin del HANDOFF.md — v8.2**