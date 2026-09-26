# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP)

**Última actualización:** 26 de Septiembre, 2026  
**Último commit:** 4846513

---

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp)
- **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.0.0 — 10.95/11 módulos completados (~99.5%)
- **Arquitectura:** Multi-tenant con PostgreSQL (schemas por tenant)
- **Próximo hito:** Cerrar Módulo 11 (Fase D2: PDF) + Dockerización

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
- `app.py` (~500 KB) — aplicación principal
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
| 21 | Panadería Demo | panaderia_demo | premium | nube_premium |
| 22 | Test Sincronización | test_sincronizacion | premium | nube_premium |

**Nota:** tenant_23 (Panadería Audit Test) fue creado y eliminado para validar el fix de auditoría. Ya no existe.

---

## 4️⃣ Usuarios del sistema

### Roles
- **super_admin** (dev_master) → gestiona TODOS los tenants, licencias, config global
- **admin_cliente** → acceso TOTAL a su tenant
- **supervisor** → producción, recetas, materias primas, proveedores, reportes
- **cajero** → solo punto de venta y cierre de caja

### Usuarios actuales
- `dev_master` (super_admin, tenant_1)
- `admin_21`, `super_21`, `cajero_21` (tenant_21)
- `admin_22` (tenant_22)

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

```
4846513 fix(multi-tenant): completar CREATE TABLE de depositos_bancarios, pagos_individuales y saldos_banco
ee3bcc9 feat(reportes): historiales de pagos/depositos + bancos dinamicos multi-pais
19e843a feat(reportes): reorganizar dashboard y exponer reportes escondidos + HANDOFF.md
71f5b1d feat(reportes): migrar reportes.html a base.html y corregir sidebar
8be33ad fix(financiera): completar modulo con filtros multi-tenant, fixes de esquemas y mejora UX
5352e61 feat(permisos): /mi_perfil filtra modulos por rol correctamente
14721d2 fix(gitignore): restaurar patron _ARCHIVE_*/ y agregar *.bak_* correctamente
045866e feat(perfil): modulo Mi Perfil completo + fixes multi-tenant
c9bb8b0 fix(licencias): sincronizar public.tenants.plan al cambiar licencia de tenant
ee2da79 feat(activos): rediseñar reporte con paleta corporativa y formato compacto
```

---

## 7️⃣ Módulo 11 — Reportes (estado detallado)

### Fases completadas
- ✅ **Fase A+B:** migración `reportes.html` a `base.html` + sidebar corregido
- ✅ **Fase E:** dashboard reorganizado en 4 secciones + 7 reportes expuestos + rutas placeholder
- ✅ **Fase D1:** historiales de pagos y depósitos con filtros + paginación + multi-país
- 🔧 **Fase D2:** exportación PDF (pendiente)

### Estructura del dashboard `/reportes`

```
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
```

### Fase D2 (pendiente)
**Objetivo:** exportación PDF de los historiales.

**Plan:**
1. Agregar 2 funciones a `reportes.py`:
   - `generar_reporte_historial_pagos(panaderia_id, fecha_inicio, fecha_fin, categoria=None, proveedor_id=None)`
   - `generar_reporte_historial_depositos(panaderia_id, fecha_inicio, fecha_fin, banco=None, estado=None)`
2. Agregar 2 rutas en `app.py`:
   - `GET /exportar_historial_pagos`
   - `GET /exportar_historial_depositos`
3. Agregar botones "Exportar PDF" en:
   - `templates/historial_pagos.html`
   - `templates/historial_depositos.html`
4. Verificar + commit

**Tiempo estimado:** 1.5-2 horas.

---

## 8️⃣ Logros recientes (última sesión)

### Módulo 10 — Gestión Financiera (commit 8be33ad)
- ✅ Filtros multi-tenant en `PagoIndividual`
- ✅ `NotNullViolation` en `saldos_banco` (columna `banco`)
- ✅ `NotNullViolation` en `depositos_bancarios` (columna `banco`)
- ✅ `NotNullViolation` en `pagos_individuales` (columna `concepto`)
- ✅ `UnboundLocalError` en `actualizar_saldo_automatico`
- ✅ Redirect inconsistente (`control_diario` → `gestion_financiera`)
- ✅ `accion_efectivo` movido al form correcto
- ✅ Modal mejorado con dropdown de bancos
- ✅ Pagos limitados a 10 items con "Ver todos"
- ✅ Depósitos limitados a 5 items con "Ver todos"

### Módulo 11 — Reportes
- ✅ **Migración de `reportes.html`** a `base.html` (eliminadas ~300 líneas CSS duplicado)
- ✅ **Sidebar corregido** (link "Reportes" ahora apunta a `/reportes`)
- ✅ **Dashboard reorganizado** en 4 secciones (Movimientos, Contable, Análisis, IA)
- ✅ **7 reportes expuestos** (antes solo accesibles por URL directa)
- ✅ **Historiales completos** (`/historial_pagos` y `/historial_depositos`)
- ✅ **Multi-país:** bancos dinámicos con datalist HTML5

### Auditoría de tenants (commit 4846513)
- ✅ Completados 3 CREATE TABLE críticos:
  - `depositos_bancarios` (11 → 17 columnas)
  - `pagos_individuales` (9 → 14 columnas)
  - `saldos_banco` (5 → 6 columnas, `banco` nullable)
- ✅ Verificado con `tenant_23`: todos los flujos funcionan sin errores
- ✅ Futuros tenants nacen con tablas completas

---

## 9️⃣ Deuda técnica pendiente (Fase C)

### 🚨 CRÍTICO — Auditoría de esquemas completa

**Hallazgo:** al crear `tenant_23`, el log mostró:
```
✅ 47 columnas sincronizadas en tenant_23
```

**Eso significa que hay MÁS tablas** con `CREATE TABLE` incompletos (solo arreglamos 3).

**Acción pendiente:** auditar las 36 tablas restantes.

### ⚠️ Warnings recurrentes en el log

1. ⚠️ `user_loader: This session is provisioning a new connection` (aparece en CADA request)
2. ⚠️ `LegacyAPIWarning: Query.get()` en `app.py:2155` y `2166`
3. ⚠️ `Error obteniendo nombre de empresa: 'NoneType' object has no attribute 'is_authenticated'` (al arrancar)
4. ⚠️ Error calculando días: `datetime - date`
5. ⚠️ `/api/donaciones/hoy` 404
6. ⚠️ Reporte PDF: página 2 vacía (bug @media print, cosmético)

### 🧹 Limpieza pendiente

- 🔧 Migrar `dashboard.html` a `base.html` (es autónomo)
- 🔧 Migrar `ventas_avanzado.html` a `base.html`
- 🔧 Migrar `control_diario.html` a `base.html` O deprecarlo
- 🔧 Migrar `reporte_activos.html`, `reporte_inventario_externo.html`, `reporte_ventas_externas.html`, `reporte_produccion.html`
- 🔧 Deprecar `/control_diario` (código muerto)
- 🔧 Agregar a `.gitignore` el archivo `HANDOFF.md` (opcional)
- 🔧 Mejora UX: selector de fechas en `/reportes` más claro (contexto + botón "Actualizar período")

---

## 🔟 Roadmap completo

```
✅ Fase 1: Módulos 1-10 (COMPLETADO)
🔧 Fase 2: Módulo 11 Reportes (90% completado)
        ├── ✅ Fase A+B: migración + sidebar (commit 71f5b1d)
        ├── ✅ Fase E: dashboard reorganizado (commit 19e843a)
        ├── ✅ Fase D1: historiales + multi-país (commit ee3bcc9)
        └── ⏳ Fase D2: exportación PDF (PENDIENTE)
⏳ Fase 3: Deuda técnica (warnings + auditoría completa + migración templates)
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
        ├── Chat informativo en dashboard
        └── Integración con LLM
⏳ Fase 7: Junta Directiva IA (Nivel 2-3)
        ├── Sistema multi-agente (CFO, CMO, COO, CEO)
        ├── Base de conocimiento experto
        ├── Motor de simulación
        └── Plan Elite premium
⏳ Fase 8: Integraciones estratégicas
        ├── DAPTA (leads WhatsApp)
        ├── Pasarelas de pago (Stripe, MercadoPago)
        ├── WhatsApp Business API
        └── Facturación electrónica multi-país
```

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

### Comandos útiles

**Ver líneas específicas:**
```cmd
findstr /N "^" app.py | findstr /R "^1234: ^1235:"
```

**Buscar texto:**
```cmd
findstr /N /C:"texto" app.py
```

**Ver estructura de tabla:**
```cmd
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "\d tenant_21.tabla"
```

**Compilar:**
```cmd
python -m py_compile app.py
```

**Arrancar servidor:**
```cmd
python app.py
```

**Activar venv:**
```cmd
venv\Scripts\activate
```

### Ritual de inicio de sesión
1. Activar venv: `venv\Scripts\activate`
2. Verificar estado de git: `git status`
3. Arrancar servidor: `python app.py`
4. Continuar con el plan de la fase actual.

---

## 1️⃣2️⃣ Configuración crítica del código

### Event listener (app.py ~línea 1300)
- Configura `search_path` en cada checkout del pool SQLAlchemy.
- Prioridad: `g.search_path_override` > tenant del usuario > session.

### Multi-tenant
- Decorador `@tenant_required` configura el schema.
- SQL directo calificado: `UPDATE tenant_X.tabla`.
- Cada query filtra por `panaderia_id`.

### Context processor (`inject_user_permissions`)
Inyecta en todos los templates:
- `usuario_puede`, `usuario_tiene_acceso`
- `modulos_permitidos`, `modulos_con_acceso_completo`
- `MODULOS_SISTEMA`, `config`, `dias_restantes`

### Rutas críticas
- `/reportes` — dashboard de reportes
- `/historial_pagos` — historial con filtros y paginación
- `/historial_depositos` — historial con filtros y paginación
- `/gestion_financiera` — módulo financiero completo
- `/mi_perfil` — perfil del usuario (todos los roles)

### Bancos dinámicos multi-país
- **Backend:** en `/gestion_financiera`, se extraen bancos usados por el tenant.
- **Frontend:** `<input list>` + `<datalist>` en el modal de nuevo depósito.
- **Fallback:** 12 bancos genéricos si el tenant no tiene ninguno.

### `_sincronizar_columnas_tenant`
- Compara columnas del ORM con las de la BD.
- Agrega las faltantes con `ALTER TABLE ADD COLUMN IF NOT EXISTS`.
- Se ejecuta al arrancar el servidor para cada tenant.
- **Limitación:** no actualiza constraints (NOT NULL).

---

## 1️⃣3️⃣ Pendientes críticos antes de Dockerización

### 🚨 PRIORIDAD ALTA

1. **Auditoría de esquemas completa:**
   - Comparar CREATE TABLE vs modelo ORM para las 39 tablas.
   - Arreglar las que tengan discrepancias.
   - **Motivo:** evita que futuros tenants tengan bugs tipo NotNullViolation.

2. **Resolver warnings en el log:**
   - `user_loader` provisionando nueva conexión (aparece en cada request).
   - `Query.get()` legacy de SQLAlchemy 2.0.
   - `Error obteniendo nombre de empresa` al arrancar.

### 🟡 PRIORIDAD MEDIA

3. **Fase D2 del Módulo 11:** exportación PDF de historiales.
4. **Migrar templates autónomos** a `base.html`.
5. **Deprecar `/control_diario`** (código muerto).

### 🟢 PRIORIDAD BAJA

6. Mejoras UX (selector de fechas, etc.).
7. Reporte PDF: página 2 vacía (bug cosmético).
8. `/api/donaciones/hoy` 404.

---

## 1️⃣4️⃣ Próxima sesión — Prioridad sugerida

### 🎯 Recomendación: **Fase C (Deuda técnica) primero**

**Razones:**
1. Los warnings ensucian el log y dificultan debug.
2. La auditoría de esquemas evita bugs futuros.
3. Limpiar antes de dockerizar es más fácil.

**Plan de Fase C:**
1. **Auditoría de esquemas completa** (2-3h)
   - Script que compare ORM vs BD de las 39 tablas.
   - Arreglar discrepancias en `CREATE TABLE`.
   - Verificar con tenant nuevo.

2. **Resolver warnings** (1-2h)
   - Migrar `Query.get()` → `db.session.get()`.
   - Arreglar `user_loader`.
   - Arreglar "Error obteniendo nombre de empresa".

3. **Migrar templates autónomos** (2-3h)
   - `dashboard.html`, `ventas_avanzado.html`, `control_diario.html`, etc.

**Alternativa:** Fase D2 (PDF) primero (1.5-2h).

---

## 1️⃣5️⃣ Notas estratégicas del proyecto

### Objetivo del ERP
ERP SaaS para panaderías multi-tenant multi-país con:
- Punto de venta, inventario, producción, recetas, activos fijos
- Reportes con IA (predictivos ya implementados)
- Finanzas completas
- Multi-país (bancos, moneda, fechas)
- Base para API REST + IA avanzada

### Diferenciadores técnicos
- **Multi-tenant real** con schemas PostgreSQL.
- **Multi-país** (configuración dinámica).
- **IA-ready** (reportes predictivos + tendencias).
- **Bancos dinámicos** (funciona en cualquier país).

### Roadmap a futuro
- Chat IA básico (Nivel 1)
- Junta Directiva IA (multi-agente: CFO, CMO, COO, CEO)
- API REST para integraciones (DAPTA, Shopify, MercadoPago)
- Dockerización + Deploy en VPS

### Mercado objetivo
- 3.000-5.000 panaderías en Colombia
- 10.000-30.000 en LATAM
- Precio sugerido: $60k-$600k COP/mes según plan

---

## 📞 Cómo continuar en un chat nuevo

### Al iniciar un nuevo chat, pegar este archivo como contexto inicial.

**Instrucción sugerida para el asistente:**

> "Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el archivo HANDOFF.md con el contexto maestro del proyecto. Vamos a continuar desde donde lo dejamos. Por favor actúa como instructor guiando paso a paso, con la metodología de trabajo descrita en el HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/findstr, commit tras cada fix verificado."

### Próxima tarea sugerida
**Fase C — Auditoría de esquemas + resolver warnings** (ver sección 14).

---

## ✅ Última validación

- Último commit: `4846513`
- Working tree: clean
- Servidor: corriendo en `http://localhost:5000`
- Próximo hito: Fase D2 (PDF) o Fase C (auditoría)

**Estado del proyecto:** Estable, funcional, listo para cierre del Módulo 11 y Dockerización.

---

**Fin del HANDOFF.md**