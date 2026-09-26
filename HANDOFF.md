# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP)

**Última actualización:** 26 de Septiembre, 2026  
**Último commit:** 61799c4 (Fase C.1 completada)

---

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp)
- **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.0.0 — 10.95/11 módulos completados (~99.5%)
- **Arquitectura:** Multi-tenant con PostgreSQL (schemas por tenant)
- **Próximo hito:** Tenant Demo (marketing) + Auditoría de columnas + Dockerización

---

## 2️⃣ Stack tecnológico

### Backend
- Python 3.10+, Flask 3.1.2, SQLAlchemy 2.0
- PostgreSQL 17.10 (puerto 5433)
- Flask-Login, Werkzeug (pbkdf2:sha256, scrypt), ReportLab, Matplotlib
- **BD:** `panaderia_master` — user: `postgres`, password: `PanaderiaPro2026!`

### Frontend
- HTML5/CSS3, JavaScript vanilla, Bootstrap 5.1.3, Chart.js, Font Awesome 6

### Estructura de archivos
- `app.py` (~510 KB) — aplicación principal
- `models.py` (~124 KB) — modelos SQLAlchemy
- `reportes.py` (~147 KB) — generación PDF
- `middleware_saas.py`, `tenant_decorators.py`, `tenant_context.py` — multi-tenant
- `templates/` — templates Jinja2
- `static/` — CSS, JS, IMG
- `HANDOFF.md` — este archivo (contexto maestro)

---

## 3️⃣ Tenants activos

| ID | Nombre | Subdominio | Plan | Licencia |
|----|--------|-----------|------|----------|
| 1 | Panadería Principal | principal | basico | local |
| 25 | Panadería Test Fase C | panadería_test_fase_ | premium | nube_premium |

**Nota histórica:** tenants 21 y 22 fueron eliminados durante Fase C.1 (eran de prueba). tenant_23 también fue eliminado (audit test previo). La secuencia de IDs está en 25; el próximo tenant será 26.

**Tenant pendiente de crear:** `Demo Marketing` (ver sección 15).

---

## 4️⃣ Usuarios del sistema

### Roles
- **super_admin** (dev_master) → gestiona TODOS los tenants, licencias, config global
- **admin_cliente** → acceso TOTAL a su tenant
- **supervisor** → producción, recetas, materias primas, proveedores, reportes
- **cajero** → solo punto de venta y cierre de caja

### Usuarios actuales
- `dev_master` (super_admin, tenant_1)
- `admin_25`, `super_25`, `cajero_25` (tenant_25)

### Licencias
- `local` → permanente, acceso completo (dev_master)
- `nube_basica` → 1 usuario, sin módulos premium
- `nube_premium` → 3 usuarios, acceso completo a todos los módulos

---

## 5️⃣ Estado de los módulos (10.95/11)

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
| 11 | Reportes Profesionales | 🔧 90% (falta Fase D2) |

**Progreso global:** 10.95/11 módulos (~99.5%)

---

## 6️⃣ Últimos commits pusheados
61799c4 fix(faseC1): auditoria de esquemas - alinear crear_tablas_en_orden con modelos ORM
20442a9 docs(HANDOFF): actualizar contexto pre-Fase C con logros recientes
4846513 fix(multi-tenant): completar CREATE TABLE de depositos_bancarios, pagos_individuales y saldos_banco
ee3bcc9 feat(reportes): historiales de pagos/depositos + bancos dinamicos multi-pais
19e843a feat(reportes): reorganizar dashboard y exponer reportes escondidos + HANDOFF.md
71f5b1d feat(reportes): migrar reportes.html a base.html y corregir sidebar
8be33ad fix(financiera): completar modulo con filtros multi-tenant, fixes de esquemas y mejora UX
5352e61 feat(permisos): /mi_perfil filtra modulos por rol correctamente
14721d2 fix(gitignore): restaurar patron ARCHIVE*/ y agregar .bak_ correctamente
045866e feat(perfil): modulo Mi Perfil completo + fixes multi-tenant
c9bb8b0 fix(licencias): sincronizar public.tenants.plan al cambiar licencia de tenant
ee2da79 feat(activos): rediseñar reporte con paleta corporativa y formato compacto

text

---

## 7️⃣ Módulo 11 — Reportes (estado detallado)

### Fases completadas
- ✅ **Fase A+B:** migración `reportes.html` a `base.html` + sidebar corregido
- ✅ **Fase E:** dashboard reorganizado en 4 secciones + 7 reportes expuestos + rutas placeholder
- ✅ **Fase D1:** historiales de pagos y depósitos con filtros + paginación + multi-país
- 🔧 **Fase D2:** exportación PDF (pendiente)

### Estructura del dashboard `/reportes`
📊 Sistema de Reportes Profesionales

📋 MOVIMIENTOS
├── Historial de Pagos (con filtros, paginación)
├── Historial de Depósitos (con filtros, paginación)
├── Historial de Ventas (/reporte/ventas)
└── Cierre de Caja (/reporte/cierre_caja)

🧮 CONTABLE
├── Estado de Resultados (PDF)
├── Conciliación Bancaria (modal + PDF)
├── Reporte Unificado de Tesorería (PDF)
└── Análisis de Gastos (PDF)

📈 ANÁLISIS Y OPERACIONES
├── Productos Populares
├── Producción Diaria
├── Inventario Externo
├── Ventas Externas (PREMIUM)
└── Activos Fijos

🤖 GERENCIAL CON IA
├── Reporte Avanzado Ventas + IA (PREMIUM)
├── Análisis Predictivo
├── Tendencia de Ventas (PDF)
├── Recomendaciones IA (PDF)
└── Análisis de Inventarios (PDF)

text

### Fase D2 (pendiente)
**Objetivo:** exportación PDF de los historiales.

**Plan:**
1. Agregar 2 funciones a `reportes.py`:
   - `generar_reporte_historial_pagos(...)`
   - `generar_reporte_historial_depositos(...)`
2. Agregar 2 rutas en `app.py`:
   - `GET /exportar_historial_pagos`
   - `GET /exportar_historial_depositos`
3. Agregar botones "Exportar PDF" en:
   - `templates/historial_pagos.html`
   - `templates/historial_depositos.html`
4. Verificar + commit

**Tiempo estimado:** 1.5-2 horas.

---

## 8️⃣ Logros recientes (Fase C.1 — 26 Sep 2026)

### 🎯 Bugs corregidos en `crear_tablas_en_orden`

- ✅ **7 CREATE TABLE renombrados** para alinear con el modelo ORM:
  - `sucursal` → `sucursales`
  - `detalles_compra` → `detalle_compras`
  - `historial_precios_receta` → `historial_precios_recetas`
  - `detalles_venta` → `detalle_venta`
  - `jornada_ventas` → `jornadas_ventas`
  - `registro_financiero` → `registros_financieros`
  - `permisos_usuarios` → `permisos_usuario`

- ✅ **CREATE TABLE `facturas` agregado** (faltaba en `crear_tablas_en_orden`, aunque el modelo ORM lo definía).

- ✅ **CREATE INDEX corregido:** `idx_detalles_venta_venta` → `idx_detalle_venta_venta` (apuntaba a tabla mal nombrada).

### 🎯 Bugs corregidos en `crear_tenant_saas`

- ✅ **Transacción atómica:** quitado `commit()` prematuro después de `CREATE SCHEMA`. Ahora si algo falla, todo se revierte (evita tenants fantasma).

- ✅ **Cálculo de `plan`** en `public.tenants` ahora usa `tipo_licencia` (no `max_usuarios`):
  - `premium` si `nube_premium` o `premium`
  - `basico` en otro caso

### 🎯 Bugs corregidos en decoradores

- ✅ **`permisos_requeridos`** ahora exceptúa a `super_admin` (consistente con `modulo_requerido`). Esto arregló el botón "cambiar licencia" que no funcionaba.

### 🎯 Bugs corregidos en `models.py`

- ✅ **`Factura`**: quitados defaults hardcodeados (`'Semillas Panadería'`, `'1085297960'`, `'Carrera 18 #9-45, Pasto'`, `'+57 3189098818'`). Ahora se llenan al emitir.

### 🎯 Limpieza de BD

- ✅ **`tenant_1`:** eliminadas 4 tablas basura:
  - `configuracion_panaderia_backup2`
  - `configuracion_panaderia_backup_20260916`
  - `configuracion_panaderia_backup_contaminacion`
  - `producto_externo` (singular, huérfana)
  - **tenant_1 quedó en 40 tablas.**

- ✅ **`tenant_21` y `tenant_22`** eliminados (eran de prueba).

### 🎯 Verificación exitosa

- ✅ **`tenant_25` ("Panadería Test Fase C") creado** con:
  - 40 tablas correctas (1:1 con tenant_1)
  - Licencia `nube_premium`, `plan=premium`
  - 3 usuarios (`admin_25`, `super_25`, `cajero_25`)
  - Sin tenants fantasma

### 🎯 Commit

- ✅ Commit `61799c4` pusheado a GitHub.
- ✅ Backup BD: `backup_pre_faseC_20260926.dump` (547 KB).

---

## 9️⃣ Deuda técnica pendiente (Fase C.2 / C.3)

### 🚨 CRÍTICO — Auditoría de columnas

**Hallazgo Fase C.1:** al crear `tenant_25`, el log mostró:
✅ 68 columnas sincronizadas en tenant_25

text

**Eso significa que los 40 `CREATE TABLE` de `crear_tablas_en_orden` siguen incompletos.** La función `_sincronizar_columnas_tenant` los parchea automáticamente, pero es deuda técnica.

**Acción pendiente:** auditar los 40 `CREATE TABLE` contra el modelo ORM completo y agregar las 68 columnas faltantes. Así los tenants nacerán completos sin parches.

### 🚨 CRÍTICO — `public` tiene el schema duplicado

**Hallazgo Fase C.1:** `public` tiene ~45 tablas, de las cuales 40 son copia del schema del tenant (`usuarios`, `ventas`, `productos`, etc.). Residuo de la migración SQLite → PostgreSQL.

**Acción pendiente:** decidir si se eliminan o se documentan como fallback. Riesgo: si un tenant no tiene `search_path` configurado, SQLAlchemy usa `public` por defecto → **puede leer/escribir en `public` sin darse cuenta**.

### 🚨 CRÍTICO — Encoding roto en nombres

**Hallazgo Fase C.1:** los nombres de tenants se ven como `PanaderÝa Principal`, `panaderÝa_test_fase_`. Es un problema de encoding (`client_encoding` de psql vs `UTF8` del servidor). Cosmético pero confuso.

**Acción pendiente:** revisar `client_encoding` en el cliente psql y/o el servidor PostgreSQL.

### 🚨 Subdominio mal formado

**Hallazgo Fase C.1:** al crear tenant_25, el subdominio quedó como `panadería_test_fase_` (con `_` final). El código trunca a 20 caracteres y deja el `_`.

**Acción pendiente:** mejorar la generación del subdominio (quitar `_` final, limitar mejor).

### ⚠️ Warnings recurrentes en el log

1. ⚠️ `user_loader: This session is provisioning a new connection` (aparece en CADA request)
2. ⚠️ `LegacyAPIWarning: Query.get()` en `app.py:2194` y `2205`
3. ⚠️ `Error obteniendo nombre de empresa: 'NoneType' object has no attribute 'is_authenticated'` (al arrancar)
4. ⚠️ Error calculando días: `datetime - date`
5. ⚠️ `/api/donaciones/hoy` 404
6. ⚠️ Reporte PDF: página 2 vacía (bug @media print, cosmético)

### 🧹 Tablas backup en `public`

- 🔧 `public.tenants_backup_20260916`
- 🔧 `public.tenants_backup_tenant20`
- 🔧 `public.configuracion_panaderia_backup_20260916`
- 🔧 `public.alembic_version` (¿se usa Alembic?)

### 🧹 Limpieza de templates

- 🔧 Migrar `dashboard.html` a `base.html`
- 🔧 Migrar `ventas_avanzado.html` a `base.html`
- 🔧 Migrar `control_diario.html` a `base.html` O deprecarlo
- 🔧 Migrar `reporte_activos.html`, `reporte_inventario_externo.html`, `reporte_ventas_externas.html`, `reporte_produccion.html`
- 🔧 Deprecar `/control_diario` (código muerto)
- 🔧 Mejora UX: selector de fechas en `/reportes`

### 🧹 Arquitectura a revisar

- 🔧 `public.usuarios` con usuarios de tenant_1 (3 filas). Revisar si es la arquitectura correcta.

---

## 🔟 Roadmap completo
✅ Fase 1: Módulos 1-10 (COMPLETADO)
🔧 Fase 2: Módulo 11 Reportes (90% completado)
├── ✅ Fase A+B: migración + sidebar (71f5b1d)
├── ✅ Fase E: dashboard reorganizado (19e843a)
├── ✅ Fase D1: historiales + multi-país (ee3bcc9)
└── ⏳ Fase D2: exportación PDF (PENDIENTE)
✅ Fase C.1: Auditoría de esquemas básica (61799c4)
├── ✅ 7 CREATE TABLE renombrados
├── ✅ CREATE TABLE facturas agregado
├── ✅ Fix CREATE INDEX
├── ✅ Transacción atómica en crear_tenant_saas
├── ✅ Fix plan desde tipo_licencia
├── ✅ Fix permisos_requeridos (super_admin)
└── ✅ tenant_25 creado con 40 tablas correctas
⏳ Fase C.2: Auditoría de columnas (68 pendientes)
⏳ Fase C.3: Warnings + limpieza de public + encoding
⏳ Fase C.4: Migración de templates autónomos
⏳ Fase Demo: Tenant Demo para marketing
⏳ Fase 4: Dockerización + nube
├── Dockerfile + docker-compose
├── Nginx + subdominios dinámicos
├── Deploy VPS
└── SSL/HTTPS + Backups automáticos
⏳ Fase 5: API REST
├── Endpoints públicos (v1)
├── Autenticación por API Key
├── Swagger/OpenAPI
└── Integración con DAPTA, Shopify, etc.
⏳ Fase 6: Chat IA básico (Nivel 1)
⏳ Fase 7: Junta Directiva IA (multi-agente)
⏳ Fase 8: Integraciones estratégicas
├── DAPTA (leads WhatsApp)
├── Pasarelas de pago (Stripe, MercadoPago)
├── WhatsApp Business API
└── Facturación electrónica multi-país (DIAN)

text

---

## 1️⃣1️⃣ Metodología de trabajo

### Reglas de oro
1. **Un paso a la vez** con confirmación antes de continuar.
2. **Diagnóstico ANTES de modificar.**
3. **Soluciones de raíz** (no parches).
4. **TODO debe funcionar para futuros tenants.**
5. **Verificación con psql/findstr** antes de avanzar.
6. **Commit después de cada fix verificado.**
7. **Backup antes de cada cambio grande** (`app.py.bak_XXX`).
8. **Siempre verificar `git status` antes de commitear.**
9. **Push después del commit** (commit local ≠ GitHub).

### Comandos útiles

**Ver líneas específicas:**
```cmd
findstr /N "^" app.py | findstr /R "^1234: ^1235:"
Buscar texto:

cmd
findstr /N /C:"texto" app.py
Ver estructura de tabla:

cmd
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "\d tenant_1.tabla"
Compilar:

cmd
python -m py_compile app.py
Arrancar servidor:

cmd
python app.py
Activar venv:

cmd
venv\Scripts\activate
Ritual de inicio de sesión
Activar venv: venv\Scripts\activate

Verificar estado de git: git status

Arrancar servidor: python app.py

Continuar con el plan de la fase actual.

1️⃣2️⃣ Configuración crítica del código
Event listener (app.py ~línea 1300)
Configura search_path en cada checkout del pool SQLAlchemy.

Prioridad: g.search_path_override > tenant del usuario > session.

Multi-tenant
Decorador @tenant_required configura el schema.

SQL directo calificado: UPDATE tenant_X.tabla.

Cada query filtra por panaderia_id.

Context processor (inject_user_permissions)
Inyecta en todos los templates:

usuario_puede, usuario_tiene_acceso

modulos_permitidos, modulos_con_acceso_completo

MODULOS_SISTEMA, config, dias_restantes

Rutas críticas
/reportes — dashboard de reportes

/historial_pagos — historial con filtros y paginación

/historial_depositos — historial con filtros y paginación

/gestion_financiera — módulo financiero completo

/mi_perfil — perfil del usuario (todos los roles)

/cambiar_licencia/<id> — super_admin cambia licencia de tenant

Bancos dinámicos multi-país
Backend: en /gestion_financiera, se extraen bancos usados por el tenant.

Frontend: <input list> + <datalist> en el modal de nuevo depósito.

Fallback: 12 bancos genéricos si el tenant no tiene ninguno.

_sincronizar_columnas_tenant
Compara columnas del ORM con las de la BD.

Agrega las faltantes con ALTER TABLE ADD COLUMN IF NOT EXISTS.

Se ejecuta al arrancar el servidor para cada tenant.

Limitación: no actualiza constraints (NOT NULL).

Deuda técnica: parchea las 68 columnas que crear_tablas_en_orden no crea.

crear_tablas_en_orden (app.py:8-900 aprox)
Crea los 40 CREATE TABLE en orden de dependencias.

Renombrado en Fase C.1 para alinear con ORM.

Deuda técnica: 68 columnas faltantes.

crear_tenant_saas (app.py:938-1180 aprox)
Crea schema + tablas + datos base + usuarios.

Transacción atómica desde Fase C.1.

Decoradores críticos
@login_required — Flask-Login.

@modulo_requerido(modulo) — verifica acceso al módulo, exceptúa super_admin.

@permisos_requeridos(modulo, accion) — verifica permiso específico, exceptúa super_admin (arreglado en Fase C.1).

@licencia_premium_requerida() — verifica licencia premium.

1️⃣3️⃣ Pendientes críticos antes de Dockerización
🚨 PRIORIDAD ALTA
Auditoría de columnas: completar los 40 CREATE TABLE de crear_tablas_en_orden (68 columnas faltantes).

Limpiar public: decidir sobre las 40 tablas duplicadas.

Revisar encoding de nombres de tenants.

Resolver warnings del log.

🟡 PRIORIDAD MEDIA
Fase D2 del Módulo 11: exportación PDF.

Migrar templates autónomos a base.html.

Deprecar /control_diario.

Crear tenant Demo (marketing).

🟢 PRIORIDAD BAJA
Mejoras UX.

Reporte PDF: página 2 vacía.

/api/donaciones/hoy 404.

1️⃣4️⃣ Próxima sesión — Prioridad sugerida
🎯 Plan recomendado (3 bloques)
BLOQUE 1 — Tenant Demo (marketing) (1-2h)

Diseñar datos demo realistas.

Crear script seed_demo.py.

Crear tenant + ejecutar seed.

Verificar en UI.

Commit + push.

BLOQUE 2 — Auditoría de columnas (2-3h)

Script de comparación ORM vs BD.

Aplicar fixes a crear_tablas_en_orden.

Recrear tenant + verificar.

Commit + push.

BLOQUE 3 — Fase D2 (PDF de historiales) (1.5-2h)

2 funciones en reportes.py.

2 rutas en app.py.

2 botones en templates.

Commit + push.

Alternativa: Fase C.3 (warnings + limpieza) primero.

1️⃣5️⃣ Notas estratégicas del proyecto
Objetivo del ERP
ERP SaaS para panaderías multi-tenant multi-país con:

Punto de venta, inventario, producción, recetas, activos fijos

Reportes con IA (predictivos ya implementados)

Finanzas completas

Multi-país (bancos, moneda, fechas)

Base para API REST + IA avanzada

Diferenciadores técnicos
Multi-tenant real con schemas PostgreSQL.

Multi-país (configuración dinámica).

IA-ready (reportes predictivos + tendencias).

Bancos dinámicos (funciona en cualquier país).

🎁 Tenant Demo (marketing)
Objetivo: tenant público con datos precargados y realistas para que clientes potenciales experimenten el ERP en vivo.

Características:

Productos típicos de panadería (pan, pasteles, bebidas, etc.).

Ventas de 3-6 meses de historial (para que los reportes IA tengan datos).

Usuarios por rol: admin, supervisor, cajero.

Reset automático cada X días (automatización futura).

Subdominio sugerido: demo.panaderiapro.com.

Enlace desde landing page: "Probar sin registro".

Estado: pendiente de crear.

Roadmap a futuro
Chat IA básico (Nivel 1)

Junta Directiva IA (multi-agente: CFO, CMO, COO, CEO)

API REST para integraciones (DAPTA, Shopify, MercadoPago)

Dockerización + Deploy en VPS

Mercado objetivo
3.000-5.000 panaderías en Colombia

10.000-30.000 en LATAM

Precio sugerido: $60k-$600k COP/mes según plan

📞 Cómo continuar en un chat nuevo
Al iniciar un nuevo chat, pegar este archivo como contexto inicial.
Instrucción sugerida para el asistente:

"Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el archivo HANDOFF.md con el contexto maestro del proyecto. Vamos a continuar desde donde lo dejamos. Por favor actúa como instructor guiando paso a paso, con la metodología de trabajo descrita en el HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/findstr, commit tras cada fix verificado."

Próxima tarea sugerida
Tenant Demo (marketing) → Auditoría de columnas → Fase D2 (PDF) (ver sección 14).

✅ Última validación
Último commit: 61799c4 (pusheado a GitHub)

Working tree: clean

Servidor: corriendo en http://localhost:5000

Próximo hito: Tenant Demo + Auditoría de columnas

Estado del proyecto: Estable, multi-tenant funcional, listo para crear tenant Demo y completar auditoría de esquemas.

Fin del HANDOFF.md

text

---

## 🎯 Cómo aplicar este HANDOFF

**Opción A — Reemplazar completo (recomendado):**

1. **Backup del HANDOFF actual:**

```cmd
copy HANDOFF.md HANDOFF.md.bak_20260926
Abrir HANDOFF.md en tu editor.

Seleccionar todo (Ctrl+A) → Borrar (Delete).

Pegar el contenido nuevo que te di arriba.

Guardar (Ctrl+S).

Opción B — Parchear secciones: más tedioso. No lo recomiendo.

🛑 Antes de aplicar
Mauricio, antes de pegar el nuevo HANDOFF:

Revisa mi propuesta. Si algo no te gusta (redacción, secciones, orden), dime y lo ajusto.

Verifica que el HANDOFF actual esté en git status como clean:

cmd
git status
Debe estar limpio (el push anterior lo dejó clean).

Copia el backup antes de reemplazar:

cmd
copy HANDOFF.md HANDOFF.md.bak_20260926
🎯 Después de aplicar el nuevo HANDOFF
1. Verifica el diff:

cmd
git diff HANDOFF.md --stat
2. Commit:

cmd
git add HANDOFF.md
git commit -m "docs(HANDOFF): actualizar a Fase C.1 completada - 8 bugs corregidos + tenant_25 + pendientes C.2"
3. Push:

cmd
git push origin main
📋 Estado del plan
Bloque	Tarea	Estado
1	HANDOFF - Leer actual	✅
1	HANDOFF - Reescribir	🟡 Revisar propuesta
1	HANDOFF - Backup + reemplazar	⏳
1	HANDOFF - Commit + push	⏳
2	Demo - Diseñar + seed	⏳
3	Auditoría - Columnas	⏳