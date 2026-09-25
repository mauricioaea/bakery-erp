🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP)
1️⃣ Información general
Nombre: PanaderíaPro (bakery-erp)

Repo: https://github.com/mauricioaea/bakery-erp

Estado: v1.0.0 — 10.5/11 módulos completados (~95%)

Arquitectura: Multi-tenant con PostgreSQL (schemas por tenant)

2️⃣ Stack tecnológico
Backend:

Python 3.10+, Flask 3.1.2, SQLAlchemy 2.0

PostgreSQL 17.10 (puerto 5433)

Flask-Login, Werkzeug, ReportLab, Matplotlib

BD: panaderia_master — user: postgres, password: PanaderiaPro2026!

Frontend:

HTML5/CSS3, JavaScript vanilla, Bootstrap 5.1.3, Chart.js, Font Awesome 6

Estructura de archivos:

app.py (~500 KB) — app principal

models.py (~124 KB) — modelos SQLAlchemy

reportes.py (~147 KB) — generación PDF

middleware_saas.py, tenant_decorators.py, tenant_context.py — multi-tenant

templates/ — templates Jinja2

static/ — CSS, JS, IMG

3️⃣ Tenants activos
ID	Nombre	Subdominio	Plan	Licencia
1	Panadería Principal	principal	basico	local
21	Panadería Demo	panaderia_demo	premium	nube_premium
22	Test Sincronización	test_sincronizacion	premium	nube_premium
4️⃣ Usuarios del sistema
Roles:

super_admin (dev_master) → gestiona TODOS los tenants, licencias, config global

admin_cliente → acceso TOTAL a su tenant

supervisor → producción, recetas, materias primas, proveedores, reportes

cajero → solo punto de venta y cierre de caja

Usuarios actuales:

dev_master (super_admin, tenant_1)

admin_21, super_21, cajero_21 (tenant_21)

admin_22 (tenant_22)

Licencias:

local → permanente, acceso completo (dev_master)

nube_basica → 1 usuario, sin módulos premium

nube_premium → 3 usuarios, acceso completo a todos los módulos

5️⃣ Módulos completados (10.5/11)
#	Módulo	Estado
1	Punto de Venta	✅
2	Producción Diaria	✅
3	Productos Externos	✅
4	Recetas y Fórmulas	✅
5	Materias Primas	✅
6	Proveedores	✅
7	Gestión de Clientes (solo dev_master)	✅
8	Activos Fijos	✅
9	Gestión de Usuarios + Mi Perfil	✅
10	Gestión Financiera	✅
11	Reportes Profesionales	🔧 60%
6️⃣ Últimos commits pusheados
text
71f5b1d feat(reportes): migrar reportes.html a base.html y corregir sidebar
8be33ad fix(financiera): completar modulo con filtros multi-tenant, fixes de esquemas y mejora UX
5352e61 feat(permisos): /mi_perfil filtra modulos por rol correctamente
14721d2 fix(gitignore): restaurar patron _ARCHIVE_*/ y agregar *.bak_* correctamente
045866e feat(perfil): modulo Mi Perfil completo + fixes multi-tenant
c9bb8b0 fix(licencias): sincronizar public.tenants.plan al cambiar licencia de tenant
7️⃣ Módulo 11 — Reportes (estado detallado)
Fases:

✅ Fase A+B: migración reportes.html a base.html + sidebar corregido

🔧 Fase D: Historial de Pagos + Historial de Depósitos (pendiente)

🔧 Fase E: Exponer 7 reportes escondidos + reorganizar dashboard (en curso)

Dashboard de reportes — estructura objetivo:

text
📊 Sistema de Reportes Profesionales

📋 MOVIMIENTOS
├── Historial de Pagos (Fase D)
├── Historial de Depósitos (Fase D)
├── Historial de Ventas (/reporte/ventas)
└── Cierre de Caja (/reporte/cierre_caja)

🧮 CONTABLE
├── Estado de Resultados (PDF)
├── Conciliación Bancaria (modal)
├── Reporte Unificado de Tesorería (PDF)
└── Análisis de Gastos (PDF)

📈 ANÁLISIS Y OPERACIONES
├── Productos Populares (/reporte/productos_populares)
├── Producción Diaria (/reporte_produccion_diaria)
├── Inventario Externo (/reporte_inventario_externo)
├── Ventas Externas (/reporte_ventas_externas)
└── Activos Fijos (/reporte_activos)

🤖 GERENCIAL CON IA
├── Reporte Avanzado Ventas + IA (/reporte/ventas_avanzado)
├── Análisis Predictivo (/reporte/analisis_predictivo)
├── Tendencia de Ventas (PDF)
├── Recomendaciones IA (PDF)
└── Análisis de Inventarios (PDF)
8️⃣ Bugs de raíz resueltos recientemente
Módulo 10 (Finanzas):

✅ Filtros multi-tenant en PagoIndividual

✅ NotNullViolation en saldos_banco (columna banco missing)

✅ NotNullViolation en depositos_bancarios (columna banco missing)

✅ NotNullViolation en pagos_individuales (columna concepto missing)

✅ UnboundLocalError en actualizar_saldo_automatico

✅ Redirect inconsistente (control_diario vs gestion_financiera)

✅ accion_efectivo huérfano (movido al form de cierre)

Módulo 9 (Usuarios):

✅ Sincronización public.tenants.plan al cambiar licencia

✅ load_user incompleto (agregados nombre_completo, email, telefono)

✅ login incompleto (mismo fix)

✅ Generadores de contraseñas con caracteres ambiguos (I, l, 1, O, 0)

✅ modulos_con_acceso_completo() filtra por rol

Módulo 11 (Reportes):

✅ reportes.html migrado a base.html (eliminadas 300 líneas CSS duplicado)

9️⃣ Deuda técnica pendiente (Fase C)
Warnings recurrentes en el log:

⚠️ user_loader: This session is provisioning a new connection (aparece en CADA request)

⚠️ LegacyAPIWarning: Query.get() en app.py:2155 y 2166

⚠️ Error obteniendo nombre de empresa: 'NoneType' object has no attribute 'is_authenticated' (al arrancar)

⚠️ Error calculando días: datetime - date

⚠️ /api/donaciones/hoy 404

⚠️ Reporte PDF: página 2 vacía (bug @media print, cosmético)

Limpieza pendiente:

🔧 Migrar dashboard.html a base.html (es autónomo)

🔧 Migrar control_diario.html a base.html O deprecarlo (es legacy)

🔧 Migrar ventas_avanzado.html a base.html

🔧 Migrar reporte_activos.html, reporte_inventario_externo.html, reporte_ventas_externas.html, reporte_produccion.html

🔧 Auditoría de esquemas: comparar modelos ORM vs BD reales (evitar más bugs tipo NotNullViolation)

🔧 Deprecar /control_diario (código muerto)

🔟 Roadmap completo
text
✅ Fase 1: Módulos 1-10 (COMPLETADO)
🔧 Fase 2: Módulo 11 Reportes (60% completado)
        ├── ✅ Fase A+B: migración + sidebar
        ├── 🔧 Fase E: reorganizar dashboard (EN CURSO)
        └── ⏳ Fase D: historiales (PENDIENTE)
⏳ Fase 3: Deuda técnica (warnings + auditoría + migración templates)
⏳ Fase 4: Dockerización + nube
        ├── Dockerfile + docker-compose
        ├── Nginx + subdominios dinámicos
        ├── Deploy VPS
        └── SSL/HTTPS + Backups
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
1️⃣1️⃣ Metodología de trabajo
Un paso a la vez con confirmación

Diagnóstico ANTES de modificar

Soluciones de raíz (no parches)

TODO debe funcionar para futuros tenants

Verificación con psql/findstr antes de avanzar

Commit después de cada fix verificado

Backup antes de cada cambio grande

Comandos útiles:

Ver líneas: findstr /N "^" archivo.py | findstr /R "^123: ^124:"

Buscar texto: findstr /N /C:"texto" archivo.py

Ver estructura BD: psql -U postgres -p 5433 -h localhost -d panaderia_master -c "\d tenant_21.tabla"

Compilar: python -m py_compile app.py

Servidor: python app.py

1️⃣2️⃣ Configuración crítica del código
Event listener (app.py ~1300):

Configura search_path en cada checkout del pool SQLAlchemy

Prioridad: g.search_path_override > tenant del usuario > session

Multi-tenant:

Decorador @tenant_required configura el schema

SQL directo calificado: UPDATE tenant_X.tabla

Cada query filtra por panaderia_id

Context processor (inject_user_permissions):

Inyecta: usuario_puede, usuario_tiene_acceso, modulos_permitidos, modulos_con_acceso_completo, MODULOS_SISTEMA, config, dias_restantes

Nuevas rutas placeholder (Módulo 11 Fase E):

/historial_pagos → flash "en desarrollo" + redirect a /reportes

/historial_depositos → mismo


Fase E COMPLETADA! — Excelente trabajo
Mauricio, la migración quedó perfecta. Del screenshot se ve:

✅ Verificación visual
✅ Sidebar con "Reportes" en el menú.

✅ Header con título y botones.

✅ Selector de fechas con atajos.

✅ Sección "Movimientos" con 4 cards (Historial Pagos, Historial Depósitos, Ventas, Cierre).

✅ Sección "Contable" con 4 cards.

✅ Sección "Análisis y Operaciones" con 5 cards.

✅ Sección "Gerencial con IA" con 5 cards.

✅ Badges "NUEVO" en los reportes recién expuestos.

✅ Badge "PREMIUM" en los que requieren licencia premium.

✅ Flash message mostrando "Modulo de Historial de Depositos en desarrollo".

✅ Verificación funcional
✅ Historial de Pagos → flash + redirect

✅ Historial de Depósitos → flash + redirect

✅ Productos Populares → funciona

✅ Producción Diaria → funciona

✅ Activos Fijos → funciona

Todo está OK. 🎯

✅ Módulo 9  COMPLETO
✅ Módulo 10 COMPLETO (commit 8be33ad)
🔧 Módulo 11 — Reportes (Fases A+B+E completadas, falta commit)
        ├── ✅ Fase A+B: migración reportes.html + sidebar
        ├── ✅ Fase E: dashboard reorganizado + 7 reportes expuestos
        │             + rutas placeholder para historiales
        ├── 🔧 COMMIT PENDIENTE (Fase E)                  ← ACÁ RETOMAMOS
        ├── ⏳ Fase D: historiales reales (próxima sesión)
        └── ⏳ Commit + Push
⏳ Fase C — Warnings + Auditoría
⏳ Fase D — Dockerización