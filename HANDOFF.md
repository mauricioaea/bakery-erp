# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP)

**Última actualización:** 5 de Octubre, 2026 (mañana)
**Último commit:** cefb33f (fix DT-FaseC.3: alinear ORM y BD - 5 cols ORM + 4 DROP BD + fix seeds + CREATE TABLE)
**Sesión 2 Oct:** DT-11, DT-12, DT-13, DT-14, DT-16, DT-26, DT-27, DT-3, DT-4
**Sesión 3 Oct:** DT-1, DT-6, DT-9, DT-20 Fase C (Tanda 1+2+3), DT-30, DT-31
**Sesión 4 Oct:** DT-10, DT-22, DT-24, DT-17, DT-33, DT-34, DT-32, DT-18
**Sesión 5 Oct:** Fase C.3 parcial (modelos vivos alineados ORM↔BD)

---

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp)
- **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.2.2 — **11/11 módulos completados (100%)** + Demo Fases 1-12 + Endurecimiento de seguridad + **DT-20 al 100%** + **DT-18 reporte tesorería nivel contable** + tenant_1 limpio + **Fase C.3 parcial (modelos vivos alineados)**
- **Arquitectura:** Multi-tenant con PostgreSQL (schemas por tenant)
- **Próximo hito:** Fase C.3 continuación (5 modelos muertos + 30 SIN FILAS) + DT-5 + deudas medias + Docker

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
- `app.py` (~12.600 líneas) — aplicación principal
- `models.py` (~3.050 líneas) — modelos SQLAlchemy
- `reportes.py` (~3.400 líneas) — generación PDF
- `seed_demo.py` (~450 líneas) — seed del Demo
- `seeds/` — 11 fases del seed
- `middleware_saas.py`, `tenant_decorators.py`, `tenant_context.py` — multi-tenant
- `migrations/sql/` — scripts SQL versionados
- `templates/`, `static/`
- `.env` (protegido), `.env.example` (plantilla)
- `HANDOFF.md` — este archivo
- `audit_columns.py`, `audit_columns_classify.py`, `audit_columns_classify_v2.py` — scripts de auditoría Fase C.3 (5 Oct)

---

## 3️⃣ Tenants activos

| ID | Nombre | Subdominio | Plan | Licencia |
|----|--------|-----------|------|----------|
| 1 | Panadería Principal | principal | basico | local |
| 25 | Panadería Test Fase C | panadería_test_fase_ | premium | nube_premium |
| 26 | Test Audit Fase C.2 | test_audit_fase_c2 | premium | nube_premium |
| 27 | **Panadería Demo** | panadería_demo | premium | nube_premium |

**Tenant principal del Demo:** `tenant_27` ("Panadería Demo").

**Estado de `tenant_1`:** ✅ Limpio (18 panaderías huérfanas y 1 usuario duplicado eliminados el 4 Oct).

**Estado de `tenant_27`:** ✅ Re-seedeado el 5 Oct con el schema alineado (10.432 filas, EXIT_CODE=0).

---

## 4️⃣ Usuarios del sistema

### Roles
- **super_admin** (dev_master) → gestiona TODOS los tenants
- **admin_cliente** → acceso TOTAL a su tenant
- **supervisor** → producción, recetas, MP, proveedores, reportes
- **cajero** → solo POS y cierre de caja

### Usuarios actuales
- **Tenant 1:**
  - `dev_master` (id=2, super_admin, panaderia_id=1)
  - `admin` (id=1, administrador, panaderia_id=1)
  - `admin_1` (id=4, admin_cliente, panaderia_id=1)
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
- Endpoint `/crear_usuario` fue **eliminado** en DT-20 Fase C Tanda 2.

### Datos de facturación (por tenant, personalizables)
- **Cada tenant** configura sus datos fiscales en `/configuracion/facturacion`.
- Se guardan en `ConfiguracionSistema`:
  - `nombre_empresa`, `nit_empresa`, `direccion_empresa`, `ciudad_empresa`, `telefono_empresa`, `regimen_empresa`
  - `moneda`, `usa_centavos`, `simbolo_moneda`
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
| 11 | Reportes Profesionales | ✅ COMPLETO (DT-18 cerró reporte tesorería) |

---

## 6️⃣ Últimos commits pusheados
cefb33f fix(DT-FaseC.3): alinear ORM y BD - 5 cols ORM + 4 DROP BD + fix seeds + CREATE TABLE
74a76af docs: HANDOFF v7.7 - DT-18 cerrado (reporte tesorería nivel contable), reglas 26-27, DT-35/36/37 documentadas
d8a8afd feat(DT-18): reporte tesoreria nivel contable - 6 secciones (ingresos, metodos pago, consumo interno, gastos, resumen, detalle diario) + firma
e512c12 feat(DT-18): encabezado fiscal del tenant + consecutivo + fecha emision en reporte tesoreria (bloques 1-2)
272f60d fix(DT-32): eliminar columna panaderia_id redundante en Panaderia - DROP COLUMN en 4 schemas + limpiar modelo y INSERT SQL
9d0d026 docs: HANDOFF v7.6 - DT-33 + DT-34 resueltas (tenant_1 limpio), regla 25, DT-32 desbloqueada
a417502 docs: HANDOFF v7.5
08dae2d fix(DT-17): cambiar fuente de ingresos de RegistroDiario a Venta en reporte tesoreria
70e7916 fix(DT-10, DT-22, DT-24): comentarios separadores en exports PDF + confirmacion NIT + mostrar exitoso en mi_perfil
9012851 docs(DT-31): versionar script SQL DROP DEFAULT + HANDOFF v7.4.1
e3dd9d4 docs: HANDOFF v7.4 - DT-20 al 100%
b111005 fix(DT-20 Fase C - Tanda 3): Panaderia + ConfiguracionPanaderia
82ed869 docs: HANDOFF v7.3
14de608 fix(DT-20 Fase C - Tanda 2): Categoria + Usuario + endpoint huérfano
45d011e fix(DT-20 Fase C - Tanda 1): 27 modelos del Grupo A
0becbf8 fix(DT-1): filtro redundante tenant_id
9b29c3b docs: HANDOFF v7.2
a25505a fix(DT-6, DT-9): default=1 en 2 modelos
11662f5 docs: HANDOFF v7.1
71f6ae1 fix(DT-3, DT-4): imports muertos
8bda650 docs: HANDOFF v7
cafc325 fix(DT-14): SECRET_KEY desde .env
301bd65 docs(DT-13): agregar .env.example
ffd8e8f fix(DT-16): password BD oculta en log
6e260b1 fix(DT-12): current_user seguro
1e4c120 fix(DT-27): Query.get() → db.session.get()
a2a2e71 docs: HANDOFF v6
cbcb76b chore: limpiar .gitignore
a522e0c fix(DT-11): event listener sin current_user

---

## 7️⃣ Demo — Estado de las fases del seed

| # | Fase | Estado | Filas |
|---|------|--------|-------|
| 1 | Configuración base | ✅ | 9 |
| 2 | Proveedores | ✅ | 6 |
| 3 | Materias primas | ✅ | 17 |
| 4 | Recetas y fórmulas | ✅ | 12 recetas / 80 ingredientes |
| 5 | Productos | ✅ | 12 |
| 6 | Producción diaria | ✅ | ~2.434 |
| 7 | Ventas | ✅ | ~7.470 |
| 8 | Productos externos | ✅ | 12 |
| 9 | Activos fijos | ✅ | ~34 |
| 10 | Movimientos financieros | ✅ | ~268 |
| 11 | Cierres diarios | ✅ | 90 |
| 12 | Reset automatizado | ✅ | — |

**Total aproximado:** ~10.432 filas en tenant_27 (verificado el 5 Oct).

**Última re-ejecución:** 5 Oct 2026 (post-alineación de schema) — `EXIT_CODE=0`.

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
- `/crear_cliente`, `/editar_cliente_super`, `/renovar_suscripcion_super`, `/eliminar_cliente`
- `/configuracion/facturacion` (datos fiscales del tenant)
- **Eliminado:** `/crear_usuario`

### Bug sistémico — panaderia_id default=1 (DT-20)

**✅ RESUELTO AL 100% (3 Oct 2026).**

- **Fase A (auditoría):** completada.
- **Fase B (fix quirúrgico):** completada — 4 INSERTs críticos (`344c552`).
- **Fase C - Tanda 1:** 27 modelos del Grupo A (`45d011e`).
- **Fase C - Tanda 2:** Categoria y Usuario + endpoint huérfano eliminado (`14de608`).
- **Fase C - Tanda 3:** Panaderia y ConfiguracionPanaderia + INSERT ORM de `app.py:1719` (`b111005`).
- **DT-31:** `ALTER TABLE DROP DEFAULT` en 7 columnas de 4 schemas (3 Oct).
- **Script SQL versionado:** `migrations/sql/2026-10-03_drop_default_tenant_id.sql`.

**Resultado:** ningún modelo tiene `default=1` en `panaderia_id`. Si un INSERT olvida pasar `panaderia_id`, **falla con `IntegrityError`** (fail-fast).

---

## 9️⃣ Deuda técnica acumulada

### ✅ RESUELTAS el 5 de Octubre 2026 (Fase C.3 parcial — modelos vivos)

| # | Descripción | Commit |
|---|-------------|--------|
| Fase C.3.1 | Auditoría completa: 68 columnas huérfanas identificadas en 21 tablas | (scripts) |
| Fase C.3.2 | Clasificación por datos reales: 14 REAL + 24 CONSTANTES + 5 MUERTAS + 25 SIN FILAS | (scripts) |
| Fase C.3.3 | Alineación ORM↔BD en modelos vivos: 5 columnas ORM + 4 DROP BD + 2 CREATE TABLE + 2 seeds | `cefb33f` |
| Fase C.3.4 | Fix `AmbiguousForeignKeysError` en `OrdenProduccion.usuario` | `cefb33f` |
| Fase C.3.5 | Fix seeds `fase8_externos.py` y `fase10_financieros.py` | `cefb33f` |

### ✅ RESUELTAS el 4 de Octubre 2026 (8 deudas)

| # | Descripción | Commit |
|---|-------------|--------|
| DT-10 | Comentarios separadores en exports PDF | `70e7916` |
| DT-22 | Confirmación al cambiar NIT | `70e7916` |
| DT-24 | Mostrar campo `exitoso` en `mi_perfil.html` | `70e7916` |
| DT-17 | Fuente de ingresos: `RegistroDiario` → `Venta` | `08dae2d` |
| DT-33 | Limpieza de 18 panaderías huérfanas en `tenant_1` | (BD) |
| DT-34 | Eliminación de usuario `admin` duplicado (id=3) en `tenant_1` | (BD) |
| DT-32 | Eliminar columna `panaderia_id` redundante en `Panaderia` | `272f60d` |
| DT-18 | Reporte tesorería nivel contable (6 secciones + encabezado fiscal) | `d8a8afd` |

### ✅ RESUELTAS el 3 de Octubre 2026 (9 deudas)

| # | Descripción | Commit |
|---|-------------|--------|
| DT-1 | Filtro redundante por tenant_id en `_obtener_nombre_empresa` | `0becbf8` |
| DT-6 | `PagoIndividual.panaderia_id default=1` | `a25505a` |
| DT-9 | `Proveedor.panaderia_id default=1` | `a25505a` |
| DT-20 Fase C Tanda 1 | 27 modelos del Grupo A sin default | `45d011e` |
| DT-20 Fase C Tanda 2 | Categoria + Usuario sin default + endpoint huérfano | `14de608` |
| DT-20 Fase C Tanda 3 | Panaderia + ConfiguracionPanaderia + INSERT ORM | `b111005` |
| DT-30 | Endpoint `/crear_usuario` huérfano eliminado | `14de608` |
| DT-31 | `DEFAULT 1` en PostgreSQL eliminado (7 ALTER TABLE) | (BD) |
| DT-15 | Password PostgreSQL en `DATABASE_URL` — **Aceptada** | — |

### ✅ RESUELTAS el 2 de Octubre 2026 (11 deudas)

| # | Descripción | Commit |
|---|-------------|--------|
| DT-3 | Import muerto `Response` | `71f6ae1` |
| DT-4 | 4 reimports redundantes de `func` | `71f6ae1` |
| DT-11 | Event listener `checkout` sin `current_user` | `a522e0c` |
| DT-12 | `_obtener_nombre_empresa` seguro | `6e260b1` |
| DT-13 | `.env.example` | `301bd65` |
| DT-14 | `SECRET_KEY` desde `.env` | `cafc325` |
| DT-16 | Password BD oculta en log | `ffd8e8f` |
| DT-26 | Latencia (resuelta por DT-11) | — |
| DT-27 | `Query.get()` → `db.session.get()` | `1e4c120` |

### ✅ RESUELTAS anteriormente
- D1, DT-2, DT-2b, DT-20 Fase A, DT-20 Fase B, B3, B4 v2, B7.

### 🔴 Críticas pendientes
**Ninguna.** DT-20 al 100%. ✅

### 🟡 Medias pendientes

| # | Ubicación | Descripción |
|---|-----------|-------------|
| DT-5 | `models.py:1055 vs 2441` | `Gasto` vs `RegistroFinanciero` posible solapamiento |
| DT-7 | `models.py` (PagoIndividual, SaldoBanco vs DepositoBancario, RegistroFinanciero) | Inconsistencia FK: 2 modelos tienen FK a `panaderias.id`, 2 no. **Aceptada (4 Oct):** no hay bug funcional. |
| DT-19 | global | CSRF completo con `flask-wtf` |
| DT-21 | POS | Modal de crear cliente sin botón visible |
| DT-25 | `app.py:1744` | Orden real de `before_request` vs `login_required` |
| DT-28 | `POST /` | Doble submit detectado |
| DT-29 | `app.py` (before_request fallback) | Tenant por defecto "Panadería Principal" en usuarios anónimos |
| DT-35 | `public.configuracion_sistema` + `public.pagos_individuales` | **Sincronizar columnas** de tablas de `public` con el modelo. Aplicado parcialmente el 4 Oct. Ver DT-36. |
| DT-36 | `public.*` | **Auditoría completa de `public.*` vs `tenant_*`.** Muchas tablas de `public` están desactualizadas. |
| DT-37 | `reportes.py` | **Soporte multi-idioma (i18n).** Refactor con `Flask-Babel`. |

### 🟢 Nuevas deudas surgidas de la Fase C.3 (5 Oct)

| # | Ubicación | Descripción | Prioridad |
|---|-----------|-------------|-----------|
| **DT-38** | `models.py` — `Gasto`, `HistorialInventario`, `HistorialMantenimiento`, `JornadaVentas`, `StockProducto` | **5 modelos huérfanos sin uso por ORM.** Ver análisis Fase C.3. Los datos se acceden por SQL crudo (seeds, reportes). Requiere: (a) decidir si agregar al ORM o eliminar, (b) resolver divergencias de nombres (`Gasto.concepto` vs `Gasto.descripcion`, etc.), (c) actualizar seeds/reportes si renombramos. | Media |
| **DT-39** | `tenant_27.*` — 25 columnas SIN FILAS en tablas vacías | Columnas en `compras`, `detalle_compras`, `control_vida_util`, `historial_rotacion_producto`, `logs_sistema`, `registros_diarios`, `registros_financieros`. **No se pueden clasificar por datos.** Investigar cada una con `findstr` para saber si son features del dominio o ruido. | Media |
| **DT-40** | `models.py:985` — `Venta` — columnas legacy en BD | Las columnas `total_venta`, `total_donacion`, `descuento`, `impuesto`, `consecutivo`, `observaciones` **existen en BD pero NO en ORM**. Tienen valores `0` o NULL (defaults). Quedan pendientes para eliminar del `CREATE TABLE` y la BD en una próxima tanda. | Baja |

### 🟢 Bajas pendientes
*(ninguna en este momento)*

### 🚨 Otras deudas
- **`public` con 40 tablas duplicadas.** Cubierto por DT-36.

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
22. **Al eliminar código huérfano, verificar PRIMERO que no haya referencias activas.**
23. **Al auditar modelos con `default=N`: verificar TODOS los INSERTs (ORM + SQL directo).**
24. **Al eliminar una columna de un modelo, verificar SIEMPRE primero: (a) si hay lecturas en el código, (b) si hay datos inconsistentes en la BD, (c) si hay usuarios/registros que apunten a valores huérfanos.**
25. **Al hacer DELETE masivos en la BD, verificar SIEMPRE: (a) backup previo, (b) que no haya FKs apuntando a los registros, (c) que no sean tenants reales en `public.tenants`.**
26. **Al modificar un método de `reportes.py` que genera PDF, verificar SIEMPRE el orden de las secciones y que todas las variables estén definidas ANTES de usarse. El código puede compilar (py_compile) pero fallar en runtime (UnboundLocalError).**
27. **Nunca asumir que el esquema de la BD coincide con el modelo ORM. Verificar con `information_schema.columns` ANTES de usar un ORM en un contexto nuevo. Las tablas de `public` suelen estar desactualizadas.**
28. **Al auditar columnas (Fase C.3), usar `COUNT(DISTINCT col)` en lugar de `COUNT(col)` para evitar falsos positivos por valores DEFAULT 0/constantes.**
29. **Al agregar una segunda FK a una tabla, SQLAlchemy requiere `foreign_keys=[...]` explícito en los `relationship` para evitar `AmbiguousForeignKeysError`.**
30. **Al alinear `CREATE TABLE` con el ORM, actualizar también los seeds que hagan INSERT directo sobre las columnas afectadas.**

### Comandos útiles

**Encoding:**
```cmd
chcp 65001
psql:

cmd
psql -U postgres -p 5433 -h localhost -d panaderia_master
Dentro: SET client_encoding TO 'UTF8';
Salir: \q

Ver estructura:

cmd
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "\d tenant_27.nombre_tabla"
Seed Demo:

cmd
python seed_demo.py --tenant=27 --reset-all
Compilar / Servidor:

cmd
python -m py_compile app.py
python app.py
Generar SECRET_KEY:

cmd
python -c "import secrets; print(secrets.token_hex(32))"
Búsquedas:

cmd
findstr /n /c:"patrón exacto" archivo.py
findstr /s /n /c:"patrón" *.py
Extraer líneas de un archivo (PowerShell):

cmd
powershell -Command "Get-Content models.py | Select-Object -Skip 246 -First 20"
Backup de BD:

cmd
pg_dump -U postgres -p 5433 -h localhost -d panaderia_master -F c -f backup_pre_XXX.backup
Verificar FK a una tabla:

cmd
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "SELECT tc.table_name, kcu.column_name FROM information_schema.table_constraints AS tc JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'tenant_1' AND ccu.table_name = 'panaderias';"
Comparar columnas de un schema vs otro:

cmd
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "SELECT column_name FROM information_schema.columns WHERE table_schema = 'tenant_27' AND table_name = 'nombre_tabla' ORDER BY ordinal_position;"

psql -U postgres -p 5433 -h localhost -d panaderia_master -c "SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'nombre_tabla' ORDER BY ordinal_position;"
Auditoría de columnas (Fase C.3):

cmd
python audit_columns.py          # Compara ORM vs BD
python audit_columns_classify.py # v1 (con falso positivo)
python audit_columns_classify_v2.py  # v2 (con COUNT DISTINCT, correcto)
1️⃣1️⃣ Fase C.3 — Auditoría de columnas huérfanas (en curso)
Contexto
El 5 de Oct, se detectó que la BD (tenant_27) y el ORM (models.py) están desalineados. Existen columnas en la BD que el ORM no conoce (y viceversa) por desincronización acumulada entre:

CREATE TABLE de app.py (crea la BD de tenants nuevos).

models.py (define el ORM).

Seeds (usan SQL crudo con nombres viejos).

Hallazgos clave
68 columnas huérfanas en 21 tablas de tenant_27.

5 de 9 modelos relevantes están muertos (nadie los usa por ORM): Gasto, HistorialInventario, HistorialMantenimiento, JornadaVentas, StockProducto.

4 modelos están vivos: Categoria, ProductoExterno, OrdenProduccion, DepositoBancario.

5 columnas son MUERTAS (todo NULL): depositos_bancarios.observaciones, gastos.observaciones, historial_mantenimientos.realizado_por, ventas.consecutivo, ventas.observaciones.

Muchas "huérfanas" son duplicados con otro nombre: gastos.concepto vs gastos.descripcion (ORM), depositos_bancarios.tipo vs metodo_deposito, historial_mantenimientos.activo_fijo_id vs activo_id, ordenes_produccion.fecha_orden vs fecha_produccion.

Lo que se hizo (sesión 5 Oct)
Lote 2 (modelos vivos):

Acción	Detalle	Ubicación
ADD al ORM	Categoria.descripcion (Text)	models.py:251
ADD al ORM	DepositoBancario.usuario_id (FK usuarios)	models.py:~2090
ADD al ORM	OrdenProduccion.cantidad_real, fecha_orden, usuario_creacion_id	models.py:~1096
FIX ORM	OrdenProduccion.usuario + usuario_creacion con foreign_keys explícito	models.py:~1115
DROP BD	tenant_27.depositos_bancarios.{tipo, observaciones, fecha_registro}	(SQL)
DROP BD	tenant_27.productos_externos.proveedor	(SQL)
FIX CREATE TABLE	Quitar 4 columnas basura de app.py	app.py:314, 626, 627, 628
FIX seed	seeds/fase8_externos.py — proveedor → proveedor_id + alinear lista proveedores	líneas 37-43, 89, 98, 109
FIX seed	seeds/fase10_financieros.py — quitar tipo del INSERT	líneas 166, 176, 181
Verificaciones:

py_compile app.py + py_compile models.py → OK.

python seed_demo.py --tenant=27 --reset-all → EXIT_CODE=0, 10.432 filas.

Schema verificado: solo usuario_id presente, sin columnas basura.

Smoke test completo: login, dashboard, POS, depósitos, producción, reportes → todos 200 OK.

Commit cefb33f + push a GitHub.

Lo que queda pendiente (DT-38 y DT-39)
DT-38 — 5 modelos muertos:

Gasto, HistorialInventario, HistorialMantenimiento, JornadaVentas, StockProducto.

No se usan por ORM. Los datos se acceden por SQL crudo (seeds, reportes).

Decidir: agregar al ORM (alineando nombres) o eliminar del ORM (y acceder siempre por SQL crudo).

Importante: si agregamos al ORM, hay que renombrar columnas (gastos.concepto → gastos.descripcion) para alinear con el ORM, lo que rompe los seeds → hay que actualizarlos también.

DT-39 — 25 columnas SIN FILAS:

En tablas vacías: compras, detalle_compras, control_vida_util, historial_rotacion_producto, logs_sistema, registros_diarios, registros_financieros.

No se pueden clasificar por datos. Investigar cada una con findstr.

DT-40 — Columnas legacy de ventas:

total_venta, total_donacion, descuento, impuesto, consecutivo, observaciones.

Existen en BD pero no en ORM. Tienen valores 0 o NULL. Eliminar del CREATE TABLE y la BD.

Cómo continuar la Fase C.3
Backup: pg_dump ... -f backup_pre_faseC3_parte2.backup.

Decidir estrategia para los 5 modelos muertos (agregar al ORM vs eliminar).

Revisar las 25 SIN FILAS con findstr en app.py, reportes.py, seeds/*.py.

Aplicar cambios por lotes con LUZ VERDE individual.

Re-ejecutar seed + verificar.

Reglas críticas para esta fase:

Regla 24: antes de DROP COLUMN, verificar lecturas en código + datos + FKs.

Regla 28: usar COUNT(DISTINCT col) para clasificar, no COUNT(col).

Regla 29: toda segunda FK a la misma tabla requiere foreign_keys=[...] en relationship.

Regla 30: al alinear CREATE TABLE, actualizar TODOS los seeds con INSERT directo.

1️⃣2️⃣ DT-11 — Resuelto (2 Oct 2026) — Bitácora
Causa raíz: El event listener checkout accedía a current_user. current_user es un LocalProxy que dispara load_user. load_user hace db.session.execute() → checkout → event listener → current_user → load_user → ... recursión infinita. SQLAlchemy 2.0 aborta con isce.

Solución: Eliminar el acceso a current_user del event listener. Leer el tenant SOLO desde flask.session.

Bitácora:

Versión	Cambio	Resultado
v1	Reducir queries en load_user	❌ No resolvió
v2	db.engine.connect() en load_user	❌ Peor: agotó el pool
v3	Cache con flask.g	❌ No resolvió
v4	Eliminar current_user del event listener	✅ RESUELTO
Commit: a522e0c

1️⃣3️⃣ DT-20 — Bug sistémico del default=1 — Bitácora
Problema: 32 modelos tenían panaderia_id = db.Column(..., default=1). Si un INSERT olvidaba pasar panaderia_id, caía silenciosamente en tenant_1.

Fases:

Fase	Modelos	Commit
A (auditoría)	—	—
B (INSERTs críticos)	4 INSERTs	344c552
C - Tanda 1	27 (Grupo A)	45d011e
C - Tanda 2	2 (Categoria, Usuario)	14de608
C - Tanda 3	2 (Panaderia, ConfiguracionPanaderia)	b111005
DT-31 (ALTER TABLE)	7 columnas PostgreSQL	(BD)
Resultado: 31 modelos sin default=1. Si un INSERT olvida pasar panaderia_id, falla con IntegrityError (fail-fast).

1️⃣4️⃣ DT-18 — Reporte de tesorería nivel contable — Resuelto (4 Oct)
Contexto: el reporte original tenía solo 3 secciones y sin datos fiscales.

Solución: 6 secciones profesionales:

Ingresos Operacionales (ventas del período, cantidad de transacciones).

Ingresos por Método de Pago (efectivo, transferencia, tarjeta con %).

Consumo Interno / Donaciones (por producto, con costo de producción, nota aclaratoria multi-país).

Gastos del Período (por categoría).

Resumen Ejecutivo (ingresos - gastos = utilidad).

Detalle de Ingresos Diarios.

Firma del responsable.

Además:

Encabezado fiscal del tenant (nombre, NIT, régimen, dirección, teléfono) — desde ConfiguracionSistema con fallback a ConfiguracionPanaderia.

Consecutivo con timestamp (TES-YYYYMMDD-HHMM).

Fecha de emisión.

Nota aclaratoria sobre el tratamiento contable de las donaciones (multi-país, sin mencionar DIAN).

Tratamiento contable de donaciones/consumo interno:

NO son ingreso (no entra plata).

Se valúan al costo de producción (no al precio de venta).

Se registran como gasto operativo (implícito en la baja de inventario).

Se muestran por separado para transparencia contable.

Commits: e512c12 (bloques 1-2) + d8a8afd (bloques 3-6).

1️⃣5️⃣ Notas estratégicas
Objetivo del ERP
ERP SaaS multi-tenant multi-país con: POS, inventario, producción, recetas, activos fijos, reportes con IA, finanzas, multi-país, base para API REST + IA avanzada.

🎁 Tenant Demo (marketing)
Fases 1-12 completadas (~10.432 filas). Contraseña: demo2026. Reset desde /mi_perfil con dev_master.

Mercado objetivo
3.000-5.000 panaderías en Colombia.

10.000-30.000 en LATAM.

Precio: $60k-$600k COP/mes.

Modelo de licencias
Premium: 3 usuarios (admin, supervisor, cajero).

Básica: 1 usuario (admin).

Los usuarios se crean al alta del tenant.

Personalización por tenant
Cada tenant configura sus datos fiscales en /configuracion/facturacion.

Se usan en recibos POS, facturas electrónicas y todos los reportes.

Los reportes respetan la moneda, régimen y datos de cada tenant.

Estimación de tiempos (5 Oct 2026, mañana)
Bloque	Estimación
Fase C.3 parte 2 (5 modelos muertos + 25 SIN FILAS)	~4-6 h
DT-5 (Gasto vs RegistroFinanciero)	~1-2 h
DT-36 (auditoría public.* vs tenant_*)	~2-3 h
DT-37 (i18n reportes)	~8-15 h
DT-19, DT-21, DT-25, DT-28, DT-29	~6-10 h
Fase 3 (nube + Docker)	~22-32 h
Fase 4 (seguridad)	~14-20 h
Fase 5 (monetización)	~26-36 h
Fases 6-8 (IA + integraciones)	~50-85 h
📞 Cómo continuar en un chat nuevo
Al iniciar un nuevo chat, pegar este archivo como contexto inicial.

Instrucción sugerida para el asistente:

"Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el archivo HANDOFF.md v7.8 con el contexto maestro del proyecto. Vamos a continuar desde donde lo dejamos. Por favor actúa como instructor guiando paso a paso, con la metodología de trabajo descrita en el HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/findstr, commit tras cada fix verificado. Al insertar bloques, muéstrame ANTES → DESPUÉS con número de línea exacto."

Próxima tarea sugerida: Continuar Fase C.3 parte 2 (DT-38: 5 modelos muertos; DT-39: 25 columnas SIN FILAS).

✅ Última validación
Último commit: cefb33f (pusheado a GitHub).

Última sesión: 5 Oct 2026 — Fase C.3 parcial (modelos vivos alineados).

Working tree: clean.

Servidor: detenido.

Sistema: 100% funcional end-to-end.

Módulos: 11/11 completados (100%).

Demo: Fases 1-12 completadas, contraseña demo2026, ~10.432 filas.

Log: limpio, sin warnings.

DT-20: ✅ 100% RESUELTO.

DT-17: ✅ Reporte tesorería funcional.

DT-18: ✅ Reporte tesorería nivel contable.

DT-32: ✅ Columna redundante eliminada.

Fase C.3 (modelos vivos): ✅ Alineada.

tenant_1: ✅ Limpio.

Deudas críticas pendientes: ninguna.

Pendientes: Fase C.3 parte 2 (DT-38, DT-39, DT-40), DT-36, DT-37, DT-5, DT-19, DT-21, DT-25, DT-28, DT-29.

Fin del HANDOFF.md — v7.8