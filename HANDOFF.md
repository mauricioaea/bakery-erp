# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP)

**Última actualización:** 26 de Septiembre, 2026  
**Último commit:** 5bfad7f (Demo Fases 1-5 + Fase C.2 parcial)

---

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp)
- **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.0.0 — 10.95/11 módulos completados (~99.5%)
- **Arquitectura:** Multi-tenant con PostgreSQL (schemas por tenant)
- **Próximo hito:** Tenant Demo (Fases 6-12) + Auditoría completa + Dockerización

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
- `seed_demo.py` (~15 KB) — NUEVO: seed modular del Demo
- `seeds/` — NUEVO: 5 fases del seed
- `middleware_saas.py`, `tenant_decorators.py`, `tenant_context.py` — multi-tenant
- `templates/`, `static/`
- `HANDOFF.md` — este archivo

---

## 3️⃣ Tenants activos

| ID | Nombre | Subdominio | Plan | Licencia |
|----|--------|-----------|------|----------|
| 1 | Panadería Principal | principal | basico | local |
| 25 | Panadería Test Fase C | panadería_test_fase_ | premium | nube_premium |
| 26 | Test Audit Fase C.2 | test_audit_fase_c2 | premium | nube_premium |
| 27 | **Panadería Demo** | panadería_demo | premium | nube_premium |

**Nota histórica:** tenants 21 y 22 fueron eliminados durante Fase C.1 (eran de prueba).

**Tenant principal del Demo:** `tenant_27` ("Panadería Demo"), poblado con `seed_demo.py` (Fases 1-5 completadas).

---

## 4️⃣ Usuarios del sistema

### Roles
- **super_admin** (dev_master) → gestiona TODOS los tenants
- **admin_cliente** → acceso TOTAL a su tenant
- **supervisor** → producción, recetas, MP, proveedores, reportes
- **cajero** → solo POS y cierre de caja

### Usuarios actuales
- `dev_master` (super_admin, tenant_1)
- `admin_25`, `super_25`, `cajero_25` (tenant_25)
- `admin_26`, `super_26`, `cajero_26` (tenant_26)
- `admin_27`, `super_27`, `cajero_27` (tenant_27 — Demo)

### Licencias
- `local` → permanente, acceso completo
- `nube_basica` → 1 usuario, sin módulos premium
- `nube_premium` → 3 usuarios, acceso completo

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
5bfad7f feat(demo): seed_demo.py modular + Fases 1-5 del tenant Demo
5cb2fa6 fix(faseC2): limpiar activos_fijos + documentar 22 tablas pendientes
7fad49b docs(HANDOFF): actualizar a Fase C.1 completada - 8 bugs corregidos + tenant_25 + pendientes C.2
61799c4 fix(faseC1): auditoria de esquemas - alinear crear_tablas_en_orden con modelos ORM
20442a9 docs(HANDOFF): actualizar contexto pre-Fase C con logros recientes
4846513 fix(multi-tenant): completar CREATE TABLE de depositos_bancarios, pagos_individuales y saldos_banco
ee3bcc9 feat(reportes): historiales de pagos/depositos + bancos dinamicos multi-pais
19e843a feat(reportes): reorganizar dashboard y exponer reportes escondidos + HANDOFF.md
71f5b1d feat(reportes): migrar reportes.html a base.html y corregir sidebar
8be33ad fix(financiera): completar modulo con filtros multi-tenant, fixes de esquemas y mejora UX

text

---

## 7️⃣ Módulo 11 — Reportes (estado detallado)

### Fases completadas
- ✅ **Fase A+B:** migración + sidebar
- ✅ **Fase E:** dashboard reorganizado + 7 reportes expuestos
- ✅ **Fase D1:** historiales de pagos y depósitos + multi-país
- 🔧 **Fase D2:** exportación PDF (pendiente)

### Fase D2 (pendiente)
1. Agregar 2 funciones a `reportes.py`:
   - `generar_reporte_historial_pagos(...)`
   - `generar_reporte_historial_depositos(...)`
2. Agregar 2 rutas en `app.py`: `/exportar_historial_pagos`, `/exportar_historial_depositos`
3. Agregar botones "Exportar PDF" en templates.

**Tiempo estimado:** 1.5-2 horas.

---

## 8️⃣ Logros recientes (sesión del 26 Sep 2026)

### 🎯 Fase C.1 — Auditoría de esquemas básica (commit 61799c4)

- ✅ 7 `CREATE TABLE` renombrados en `crear_tablas_en_orden` (sucursales, detalle_compras, detalle_venta, jornadas_ventas, permisos_usuario, registros_financieros, historial_precios_recetas).
- ✅ `CREATE TABLE facturas` agregado.
- ✅ `CREATE INDEX idx_detalles_venta_venta` corregido.
- ✅ Transacción atómica en `crear_tenant_saas` (evita tenants fantasma).
- ✅ `plan` en `public.tenants` calculado desde `tipo_licencia`.
- ✅ `permisos_requeridos` exceptúa `super_admin` (arregla "cambiar licencia").
- ✅ `Factura`: quitados defaults hardcodeados.
- ✅ Limpieza `tenant_1` (44 → 40 tablas).
- ✅ `tenant_25` creado con 40 tablas correctas.

### 🎯 Fase C.2 — Auditoría de columnas (parcial, commit 5cb2fa6)

- ✅ Script `audit_columns.py` creado (comparación ORM vs BD).
- ✅ **Hallazgo:** NO faltan columnas del ORM. Al contrario: **sobran 79 columnas huérfanas** en 23 tablas.
- ✅ **Fix aplicado:** `CREATE TABLE activos_fijos` limpiado (6 columnas huérfanas eliminadas + 6 columnas del ORM agregadas).
- ✅ Verificación 1:1 con `tenant_1.activos_fijos` (18 columnas).

### 🎯 Tenant Demo (Fases 1-5, commit 5bfad7f)

- ✅ **`seed_demo.py` modular y reutilizable** creado.
- ✅ **5 archivos de fase** en `seeds/`:
  - Fase 1: Configuración base (9 filas)
  - Fase 2: Proveedores (6 filas)
  - Fase 3: Materias primas (17 filas)
  - Fase 4: Recetas (12 recetas + 68 ingredientes = 80 filas)
  - Fase 5: Productos (12 filas)
- ✅ **Total: 124 filas** insertadas en `tenant_27`.
- ✅ **Costos exactos a Excel real:** Pan de Yema = $7.906 vs Excel $7.905.

### 🎯 Reglas de negocio confirmadas

- **Unidades de costo:** `costo_promedio` en **$/gramo**, `stock_actual` en **gramos**.
- **Fórmula del sistema:** `costo_ingrediente = cantidad_gramos × costo_promedio` (sin división).
- **Empanadas en Colombia NO llevan IVA** (junto con pan, arepas, buñuelos, almojábanas). El campo `es_pan=True` los marca correctamente. **No es bug que "emPANada" contenga "pan".**

---

## 9️⃣ Deuda técnica pendiente

### 🚨 CRÍTICO — 22 tablas con columnas extras (Fase C.3)

**Hallazgo Fase C.2:** `audit_columns.py` identificó 79 columnas huérfanas en 23 tablas. Se limpió solo `activos_fijos`. Las 22 restantes siguen con:

| Tabla | Extras |
|-------|--------|
| `configuracion_produccion` | 7 |
| `registros_financieros` | 7 |
| `ventas` | 7 |
| `registros_diarios` | 6 |
| `historial_inventario` | 5 |
| `jornadas_ventas` | 5 |
| `compras` | 4 |
| `configuracion_sistema` | 4 |
| `depositos_bancarios` | 4 |
| `gastos` | 4 |
| `ordenes_produccion` | 3 |
| `control_vida_util` | 2 |
| `detalle_compras` | 2 |
| `historial_mantenimientos` | 2 |
| `historial_rotacion_producto` | 2 |
| `logs_sistema` | 2 |
| `stock_productos` | 2 |
| `categorias` | 1 |
| `detalle_venta` | 1 |
| `pagos_individuales` | 1 |
| `productos_externos` | 1 |
| `sucursales` | 1 |

**Total:** 73 columnas.

**Plan Fase C.3:**
1. Por cada tabla: buscar las columnas extras en código (`app.py`, `models.py`, `reportes.py`, templates).
2. Clasificar:
   - **A)** Columna usada → agregar al ORM.
   - **B)** Columna no usada → eliminar del `CREATE TABLE`.
   - **C)** Columna con conflicto método/property → renombrar.
3. Aplicar fixes + verificar con `audit_columns.py`.
4. Recrear tenant de prueba.
5. Commit.

**Tiempo estimado:** 4-6 horas.

### 🚨 CRÍTICO — `public` tiene el schema duplicado

`public` tiene ~45 tablas, de las cuales 40 son copia del schema del tenant. Residuo de la migración SQLite → PostgreSQL. **Riesgo:** si un tenant no tiene `search_path` configurado, SQLAlchemy usa `public` por defecto.

### 🚨 Encoding en CMD

Los caracteres con tilde (`Nariño`, `Panadería`) se ven mal en `psql` dentro de CMD. **Solución:** `chcp 65001` + `SET client_encoding TO 'UTF8';` antes de cada consulta.

### 🟡 Warnings recurrentes

1. `user_loader: This session is provisioning a new connection` (cada request)
2. `LegacyAPIWarning: Query.get()` (app.py:2194, 2205)
3. `Error obteniendo nombre de empresa: 'NoneType'` (al arrancar)
4. `/api/donaciones/hoy` 404
5. Reporte PDF: página 2 vacía (cosmético)

### 🧹 Limpieza pendiente

- Migrar templates autónomos a `base.html`
- Deprecar `/control_diario`
- Tablas backup en `public`: `tenants_backup_20260916`, `tenants_backup_tenant20`, `configuracion_panaderia_backup_20260916`

---

## 🔟 Roadmap completo
✅ Fase 1: Módulos 1-10
🔧 Fase 2: Módulo 11 Reportes (90%)
└── ⏳ Fase D2: exportación PDF
✅ Fase C.1: Auditoría de esquemas básica (61799c4)
🔧 Fase C.2: Auditoría de columnas (parcial, 5cb2fa6)
└── ⏳ Fase C.3: 22 tablas restantes (73 columnas)
🔧 Fase Demo: Tenant Demo (Fases 1-5 completadas, 5bfad7f)
├── ✅ Fase 1: Configuración base
├── ✅ Fase 2: Proveedores
├── ✅ Fase 3: Materias primas
├── ✅ Fase 4: Recetas
├── ✅ Fase 5: Productos
├── ⏳ Fase 6: Producción diaria (30-90 días)
├── ⏳ Fase 7: Ventas (3 meses)
├── ⏳ Fase 8: Productos externos
├── ⏳ Fase 9: Activos fijos
├── ⏳ Fase 10: Movimientos financieros
├── ⏳ Fase 11: Cierres diarios
└── ⏳ Fase 12: Reset automatizado
⏳ Fase 4: Dockerización + nube
⏳ Fase 5: API REST
⏳ Fase 6: Chat IA básico
⏳ Fase 7: Junta Directiva IA
⏳ Fase 8: Integraciones estratégicas

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

**Encoding en CMD (obligatorio para psql):**
```cmd
chcp 65001
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "SET client_encoding TO 'UTF8'; ..."
Ver estructura de tabla:

cmd
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "SET client_encoding TO 'UTF8'; \d tenant_1.tabla"
Seed Demo (tenant_27):

cmd
python seed_demo.py --list                    # Lista fases
python seed_demo.py --tenant=27 --status      # Estado actual
python seed_demo.py --tenant=27 --fase=1,2,3  # Ejecutar fases
python seed_demo.py --tenant=27 --fase=all    # Todas
python seed_demo.py --tenant=27 --reset       # Resetear
Compilar / Servidor:

cmd
python -m py_compile app.py
python app.py
Activar venv:

cmd
venv\Scripts\activate
Ritual de inicio de sesión
Activar venv: venv\Scripts\activate

Verificar git: git status

Arrancar servidor: python app.py

Continuar con el plan de la fase actual.

1️⃣2️⃣ Configuración crítica del código
Event listener (app.py ~1300)
Configura search_path en cada checkout del pool SQLAlchemy.

Multi-tenant
Decorador @tenant_required configura el schema.

SQL directo calificado: UPDATE tenant_X.tabla.

Cada query filtra por panaderia_id.

Context processor
Inyecta en templates: usuario_puede, usuario_tiene_acceso, modulos_permitidos, config, dias_restantes.

Rutas críticas
/reportes, /historial_pagos, /historial_depositos

/gestion_financiera, /mi_perfil, /cambiar_licencia/<id>

Bancos dinámicos multi-país
Backend extrae bancos usados por tenant.

Frontend: <input list> + <datalist>.

Fallback: 12 bancos genéricos.

_sincronizar_columnas_tenant (app.py:12034)
Compara columnas del ORM con la BD.

Agrega las faltantes con ALTER TABLE ADD COLUMN IF NOT EXISTS.

Limitación: no actualiza constraints ni elimina extras.

crear_tablas_en_orden (app.py:8-900)
Crea los 40 CREATE TABLE en orden.

Deuda técnica: activos_fijos limpiado, 22 tablas con 73 columnas extras.

crear_tenant_saas (app.py:938-1180)
Crea schema + tablas + datos base + usuarios.

Transacción atómica.

Decoradores críticos
@modulo_requerido(modulo) — exceptúa super_admin.

@permisos_requeridos(modulo, accion) — exceptúa super_admin.

@licencia_premium_requerida().

Reglas de cálculo de recetas
**costo_promedio = 
/
g
r
a
m
o
∗
∗
(
n
o
/gramo∗∗(no/kg ni $/unidad).

stock_actual = gramos (no kg ni unidades).

Fórmula: costo_ingrediente = cantidad_gramos × costo_promedio.

CIF = 45% del costo de MP.

Margen deseado: variable (default 30-45%).

1️⃣3️⃣ Pendientes críticos antes de Dockerización
🚨 PRIORIDAD ALTA
Fase C.3: auditar 22 tablas (73 columnas extras).

Limpiar public: decidir sobre 40 tablas duplicadas.

Resolver warnings del log.

🟡 PRIORIDAD MEDIA
Fase D2 del Módulo 11: exportación PDF.

Migrar templates a base.html.

Completar Fases 6-12 del Demo.

🟢 PRIORIDAD BAJA
Mejoras UX.

Reporte PDF: página 2 vacía.

1️⃣4️⃣ Próxima sesión — Prioridad sugerida
🎯 Plan recomendado
BLOQUE 1 — Prueba manual de Producción Diaria (15-20 min)

Login como admin_demo en tenant_27.

Crear 1-2 órdenes de producción manualmente.

Verificar descuento de MP y suma de stock.

Documentar bugs si aparecen.

BLOQUE 2 — Fase 6: Producción diaria automatizada (45-60 min)

Script seeds/fase6_produccion.py.

Generar órdenes de producción de 30-90 días.

Descontar MP, sumar stock.

Verificar coherencia.

BLOQUE 3 — Fase 7: Ventas (3 meses) (1-1.5h)

Script seeds/fase7_ventas.py.

Generar 3.600 ventas distribuidas en 90 días.

Consumir stock de productos.

Actualizar jornadas_ventas y cierres_diarios.

BLOQUE 4 — Fases 8-12 del Demo (1-2h)

Productos externos, activos fijos, movimientos financieros.

Reset automatizado.

Alternativa: Fase D2 (PDF) primero.

1️⃣5️⃣ Notas estratégicas del proyecto
Objetivo del ERP
ERP SaaS para panaderías multi-tenant multi-país con: POS, inventario, producción, recetas, activos fijos, reportes con IA, finanzas, multi-país, base para API REST + IA avanzada.

Diferenciadores técnicos
Multi-tenant real (schemas PostgreSQL).

Multi-país (configuración dinámica).

IA-ready.

Bancos dinámicos.

🎁 Tenant Demo (marketing)
Objetivo: tenant público con datos precargados y realistas.

Estado actual: Fases 1-5 completadas (124 filas). Fases 6-12 pendientes.

Características planeadas:

Subdominio sugerido: demo.panaderiapro.com.

Datos: 6 proveedores, 17 MP, 12 recetas, 12 productos.

Ventas de 3 meses (Fase 7).

Reset automatizado cada X días (Fase 12).

Regla de negocio importante (Colombia):

Productos SIN IVA: pan, empanadas, arepas, buñuelos, almojábanas. Marcados con es_pan=True.

Productos CON IVA: bebidas, snacks, productos externos.

No es bug que "emPANada" contenga "pan". Es intencional.

Roadmap a futuro
Chat IA básico (Nivel 1)

Junta Directiva IA (multi-agente: CFO, CMO, COO, CEO)

API REST para integraciones (DAPTA, Shopify, MercadoPago)

Dockerización + Deploy en VPS

Mercado objetivo
3.000-5.000 panaderías en Colombia

10.000-30.000 en LATAM

Precio sugerido: $60k-$600k COP/mes

📞 Cómo continuar en un chat nuevo
Al iniciar un nuevo chat, pegar este archivo como contexto inicial.
Instrucción sugerida para el asistente:

"Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el archivo HANDOFF.md con el contexto maestro del proyecto. Vamos a continuar desde donde lo dejamos. Por favor actúa como instructor guiando paso a paso, con la metodología de trabajo descrita en el HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/findstr, commit tras cada fix verificado."

Próxima tarea sugerida
Prueba manual de Producción Diaria + Fase 6 (Producción automatizada) (ver sección 14).

✅ Última validación
Último commit: 5bfad7f (pusheado a GitHub)

Working tree: clean

Servidor: corriendo en http://localhost:5000

Próximo hito: Fases 6-12 del Demo

Estado del proyecto: Estable, multi-tenant funcional, Demo parcialmente poblado, listo para completar Fases 6-12.

Fin del HANDOFF.md

text

---

## 🎯 Instrucciones para aplicar el HANDOFF

**Mauricio:**

1. **Backup del actual:**

```cmd
copy HANDOFF.md HANDOFF.md.bak_20260926_epic