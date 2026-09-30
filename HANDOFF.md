# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP)

**Última actualización:** 30 de Septiembre, 2026
**Último commit:** 3fa92ef (Fase 9 - activos fijos)

---

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp)
- **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.0.0 — 10.95/11 módulos completados (~99.5%) + Demo Fases 1-10 (90%)
- **Arquitectura:** Multi-tenant con PostgreSQL (schemas por tenant)
- **Próximo hito:** Demo Fases 8, 11-12 + Bugs + Fase D2 (PDF)

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
- `app.py` (~520 KB) — aplicación principal
- `models.py` (~130 KB) — modelos SQLAlchemy
- `reportes.py` (~147 KB) — generación PDF
- `seed_demo.py` (~15 KB) — seed modular del Demo
- `seeds/` — 9 fases del seed (fase1, 2, 3, 4, 5, 6, 7, 9, 10)
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

**Tenant principal del Demo:** `tenant_27` ("Panadería Demo"), poblado con `seed_demo.py` (Fases 1-7, 9-10 completadas).

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
- `admin_27` (id=1), `super_27` (id=2), `cajero_27` (id=3) — tenant_27 Demo

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
| 3 | Productos Externos | ✅ COMPLETO (falta seed Fase 8) |
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
3fa92ef feat(demo): Fase 9 - activos fijos (12 activos, 23 mantenimientos)
a3ef25e feat(demo): Fase 10 - movimientos financieros (34 pagos, 18 depositos, 4 saldos, 49 gastos)
de29666 docs(HANDOFF): actualizar con Fases 6 v2 + 7 completadas + hallazgos verificacion visual
93bf74c feat(demo): Fase 7 - ventas (90 dias, 3069 ventas, 4677 detalles, 90 jornadas)
252b7a8 feat(demo): Fase 6 v2 - reposicion semanal de MP (12 semanas, 279 ordenes, 2413 filas)
fd862c3 feat(demo): Fase 6 - produccion diaria (90 dias, 71 ordenes, 560 filas)
a43045e docs(HANDOFF): actualizar con 5 fixes críticos del 27 Sep + hallazgos QA

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

## 8️⃣ Demo — Estado de las fases del seed

| # | Fase | Estado | Filas | Commit |
|---|------|--------|-------|--------|
| 1 | Configuración base | ✅ | 9 | fd862c3 |
| 2 | Proveedores | ✅ | 6 | fd862c3 |
| 3 | Materias primas | ✅ | 18 | fd862c3 |
| 4 | Recetas y fórmulas | ✅ | 80 | fd862c3 |
| 5 | Productos | ✅ | 13 | fd862c3 |
| 6 | Producción diaria (v2 con reposición) | ✅ | 2.413 | 252b7a8 |
| 7 | Ventas | ✅ | 7.836 | 93bf74c |
| 8 | Productos externos | ⏳ | — | pendiente |
| 9 | Activos fijos | ✅ | 35 | 3fa92ef |
| 10 | Movimientos financieros | ✅ | 292 | a3ef25e |
| 11 | Cierres diarios (módulo) | ⏳ | — | pendiente |
| 12 | Reset automatizado | ⏳ | — | pendiente |

**Total acumulado:** ~10.702 filas en tenant_27.

### Detalle por fase

**Fase 6 v2 (Producción):**
- Reposición semanal cada 7 días hasta 150% del stock inicial.
- 279 órdenes de producción (90 días).
- 12 reposiciones (~190 filas en historial_inventario).
- 1.665 consumos de MP.
- 279 entradas de producto.

**Fase 7 (Ventas):**
- 3.069 ventas (90 días).
- 4.677 detalles de venta.
- 90 jornadas cerradas.
- $12.608.800 COP en ventas.
- Distribución: 59.3% efectivo / 30.8% transferencia / 9.9% tarjeta.
- Ticket promedio: ~$4.108 COP.

**Fase 9 (Activos fijos):**
- 12 activos (hornos, batidoras, vitrinas, camioneta, etc.).
- 23 mantenimientos (13 preventivos + 10 correctivos).
- Valor total: ~$120M COP.

**Fase 10 (Movimientos financieros):**
- 180 historial_compras.
- 34 pagos_individuales.
- 18 depósitos bancarios.
- 4 saldos de banco.
- 49 gastos.

---

## 9️⃣ Reglas de negocio confirmadas

- **Unidades de costo:** `costo_promedio` en **$/gramo**, `stock_actual` en **gramos**.
- **Fórmula:** `costo_ingrediente = cantidad_gramos × costo_promedio`.
- **Empanadas en Colombia NO llevan IVA** (junto con pan, arepas, buñuelos, almojábanas). `es_pan=True` los marca.
- **Huevos:** por gramos (~50g por unidad), costo desde cubeta.
- **Reposición de MP:** cada 7 días hasta 150% del stock inicial.
- **Estacionalidad de ventas:** lun-vie normal, sábado +20%, domingo -30%.
- **Métodos de pago reales:** 60% efectivo, 30% transferencia, 10% tarjeta.
- **Horarios pico:** 7-9am y 4-6pm.

---

## 🔟 Hallazgos de la verificación visual (30 Sep 2026)

### ✅ Funciona bien
- Login, `/dashboard`, `/produccion_diaria`, `/punto_venta`, `/reportes`.
- `/activos_fijos` → 12 activos visibles.
- `/gestion_financiera` → carga OK.
- `/depositos_bancarios` → muestra los 18 depósitos.
- `/reporte/cierre_caja?fecha=2026-09-20` → genera reporte.
- Los 13 productos con stock, las 18 MP con stock, las 13 recetas visibles.
- `/editar_materia_prima/50` funciona.

### 🐛 Bugs encontrados

**1. 🆕 Botón "Cerrar" en Reportes → Cierre de Caja no funciona**
- **URL afectada:** `/reporte/cierre_caja` **desde el módulo de Reportes Profesionales**.
- **Síntoma:** el reporte abre, pero al hacer clic en "Cerrar" no cierra el modal.
- **Consecuencia:** la página queda bloqueada y hay que editar la barra de navegación para salir.
- **Comparación:** el mismo reporte desde **POS → Cierre de Caja SÍ funciona**.
- **Causa probable:** duplicación de template con `href` incorrecto o JS que no ejecuta.
- **Fix propuesto:** comparar los 2 templates y unificar el botón "Cerrar".

**2. `/api/donaciones/hoy` → 404**
- Ya conocido. Frontend llama, no rompe UI.
- Fix: crear endpoint o eliminar llamada.

**3. `/api/stock_vitrina_actualizado` → 404**
- Nuevo. La vitrina del POS no se actualiza en tiempo real.
- Fix: crear endpoint o eliminar llamada del JS.

**4. `user_loader: This session is provisioning a new connection`**
- Ruido en logs, no rompe nada.
- Fix: investigar session pooling de SQLAlchemy.

**5. `LegacyAPIWarning: Query.get()` (app.py:2196, 2207)**
- Migrar a `db.session.get()`.

---

## 1️⃣1️⃣ Deuda técnica pendiente

### 🟡 Ajuste financiero pendiente (Fase 10)

- **Problema:** los egresos (~$15.5M) > ingresos (~$12.6M).
- **Causa:** las ventas del Demo son bajas.
- **Fix propuesto:** aumentar ventas/día en Fase 7 (de ~34 a ~60/día) o reducir más los gastos.
- **Prioridad:** media (post-Demo).
- **Impacto:** actualmente el Demo muestra pérdidas, poco realista.

### 🚨 CRÍTICO — 22 tablas con columnas extras (Fase C.3)

**Hallazgo Fase C.2:** 79 columnas huérfanas en 23 tablas. Se limpió solo `activos_fijos`. Las 22 restantes siguen con:

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

**Plan Fase C.3:** auditar cada tabla, clasificar y aplicar fix. Tiempo estimado: 4-6 horas.

### 🚨 CRÍTICO — `public` tiene el schema duplicado

`public` tiene ~45 tablas, de las cuales 40 son copia del schema del tenant. Residuo de la migración SQLite → PostgreSQL.

**Plan:** decidir si se eliminan o se documentan. **Fase C.3.**

### 🧹 Limpieza de templates

- Migrar `dashboard.html`, `ventas_avanzado.html`, `control_diario.html`, etc. a `base.html`.
- Deprecar `/control_diario` (código muerto).

---

## 1️⃣2️⃣ Roadmap completo
✅ Fase 1: Módulos 1-10
🔧 Fase 2: Módulo 11 Reportes (90%)
└── ⏳ Fase D2: exportación PDF (1.5-2h)

✅ Fase C.1: Auditoría de esquemas básica
✅ Fase C.2: Auditoría de columnas (parcial)
└── ⏳ Fase C.3: 22 tablas restantes (4-6h)

✅ Fase Demo: Tenant Demo
├── ✅ Fase 1: Configuración base
├── ✅ Fase 2: Proveedores
├── ✅ Fase 3: Materias primas
├── ✅ Fase 4: Recetas
├── ✅ Fase 5: Productos
├── ✅ Fase 6: Producción diaria (v2 con reposición)
├── ✅ Fase 7: Ventas
├── ⏳ Fase 8: Productos externos (~1h)
├── ✅ Fase 9: Activos fijos
├── ✅ Fase 10: Movimientos financieros
├── ⏳ Fase 11: Cierres diarios (~1h)
└── ⏳ Fase 12: Reset automatizado (~1h)

⏳ Bugs: 404s + botón "Cerrar" (~1h)
⏳ Ajuste financiero Fase 10 (~30 min)
⏳ Fase 4: Dockerización + nube
⏳ Fase 5: API REST
⏳ Fase 6: Chat IA básico
⏳ Fase 7: Junta Directiva IA
⏳ Fase 8: Integraciones estratégicas

text

---

## 1️⃣3️⃣ Metodología de trabajo

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

### Comandos útiles

**Modo interactivo psql (recomendado):**
```cmd
psql -U postgres -p 5433 -h localhost -d panaderia_master
Dentro: SET client_encoding TO 'UTF8';
Salir: \q

Seed Demo:

cmd
python seed_demo.py --list                    # Lista fases
python seed_demo.py --tenant=27 --status      # Estado
python seed_demo.py --tenant=27 --fase=1,2,3  # Ejecutar fases
python seed_demo.py --tenant=27 --fase=all    # Todas
python seed_demo.py --tenant=27 --reset       # Reset
python seed_demo.py --tenant=27 --fase=6 --dry-run  # Simular
Compilar / Servidor:

cmd
python -m py_compile app.py
python app.py
1️⃣4️⃣ Configuración crítica del código
Multi-tenant
Decorador @tenant_required configura el schema.

SQL directo calificado: UPDATE tenant_X.tabla.

Cada query filtra por panaderia_id.

Rutas críticas
/reportes, /historial_pagos, /historial_depositos

/gestion_financiera, /mi_perfil, /cambiar_licencia/<id>

/punto_venta, /registrar_venta, /recibo-pos/<id>

/materias_primas, /editar_materia_prima/<id>

/produccion_diaria, /reporte/cierre_caja

/reporte/ventas_avanzado, /activos_fijos

/depositos_bancarios

Bug sistémico — panaderia_id default=1
Múltiples modelos tienen panaderia_id default=1. Si el código NO pasa panaderia_id explícitamente en un INSERT, toma 1.

Regla: SIEMPRE pasar panaderia_id=panaderia_id en cada INSERT.

Bug sistémico — productos.id ≠ productos.producto_id
La tabla productos usa id como PK. Otras tablas usan producto_id como FK.

Regla: al consultar productos, usar SELECT id. Al consultar detalle_venta, stock_productos, historial_inventario, usar producto_id.

Workaround — SQLAlchemy no persiste cambios
En editar_materia_prima, el += de SQLAlchemy no se persistía al commit.

Workaround: usar UPDATE SQL directo.

1️⃣5️⃣ Pendientes críticos antes de Dockerización
🚨 PRIORIDAD ALTA
Fase 8: Productos externos.

Fase 11: Cierres diarios (módulo).

Fase 12: Reset automatizado.

Bug botón "Cerrar": Reportes → Cierre de Caja.

Ajuste financiero Fase 10: egresos > ingresos.

Bugs 404: /api/donaciones/hoy, /api/stock_vitrina_actualizado.

Fase D2: Exportación PDF.

Fase C.3: Auditoría de 22 tablas.

Resolver warnings: user_loader, LegacyAPIWarning.

🟡 PRIORIDAD MEDIA
Migrar templates a base.html.

Fase C.4: mejoras post-Demo (adicionales en recetas, historial producción).

🟢 PRIORIDAD BAJA
Mejoras UX.

Reporte PDF: página 2 vacía.

1️⃣6️⃣ Próxima sesión — Prioridad sugerida
Plan acordado (30 Sep 2026):

✅ Actualizar HANDOFF + commit ← AHORA

⏳ Fase 8 (Productos externos) — ~1 h

⏳ Fase 11 (Cierres diarios) — ~1 h

⏳ Fase 12 (Reset automatizado) — ~1 h

⏳ Bug botón "Cerrar" — ~30 min

⏳ Ajuste financiero Fase 10 — ~30 min

⏳ Bugs 404 — ~30 min

⏳ Fase D2 (Export PDF) — ~1.5 h

⏳ Fase C.3 (Auditoría) — ~4-6 h

1️⃣7️⃣ Notas estratégicas del proyecto
Objetivo del ERP
ERP SaaS para panaderías multi-tenant multi-país con: POS, inventario, producción, recetas, activos fijos, reportes con IA, finanzas, multi-país, base para API REST + IA avanzada.

Diferenciadores técnicos
Multi-tenant real (schemas PostgreSQL).

Multi-país (configuración dinámica).

IA-ready.

Bancos dinámicos.

🎁 Tenant Demo (marketing)
Objetivo: tenant público con datos precargados y realistas.

Estado actual: Fases 1-7, 9-10 completadas (~10.702 filas).

Características planeadas:

Subdominio sugerido: demo.panaderiapro.com.

Datos: 7 proveedores, 18 MP, 13 recetas, 13 productos.

279 órdenes de producción (90 días).

3.069 ventas (90 días).

12 activos fijos + 23 mantenimientos.

Reset automatizado cada X días (Fase 12).

Roadmap a futuro
Chat IA básico (Nivel 1).

Junta Directiva IA (multi-agente).

API REST para integraciones (DAPTA, Shopify, MercadoPago).

Dockerización + Deploy en VPS.

Mercado objetivo
3.000-5.000 panaderías en Colombia.

10.000-30.000 en LATAM.

Precio sugerido: $60k-$600k COP/mes.

📞 Cómo continuar en un chat nuevo
Al iniciar un nuevo chat, pegar este archivo como contexto inicial.

Instrucción sugerida para el asistente:

"Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el archivo HANDOFF.md con el contexto maestro del proyecto. Vamos a continuar desde donde lo dejamos. Por favor actúa como instructor guiando paso a paso, con la metodología de trabajo descrita en el HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/findstr, commit tras cada fix verificado."

Próxima tarea sugerida: Fase 8 (Productos externos) o bug del botón "Cerrar".

✅ Última validación
Último commit: 3fa92ef (pusheado a GitHub).

Working tree: clean.

Servidor: detenido.

Sistema: 100% funcional end-to-end.

Estado del proyecto: Estable, multi-tenant funcional, Demo Fases 1-7, 9-10 completadas.

Pendientes críticos: Fase 8, Fase 11, Fase 12, bug botón "Cerrar", ajuste financiero.

Fin del HANDOFF.md