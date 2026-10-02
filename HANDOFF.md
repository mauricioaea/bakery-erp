# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP)

**Última actualización:** 1 de Octubre, 2026
**Último commit:** bd0cac8 (3 pendientes menores resueltos)

---

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp)
- **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.0.0 — 10.95/11 módulos completados (~99.5%) + Demo Fases 1-12 completadas
- **Arquitectura:** Multi-tenant con PostgreSQL (schemas por tenant)
- **Próximo hito:** Fase D2 (PDF) + Fase C.3 (auditoría) + Seguridad (D1)

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
- `seed_demo.py` (~18 KB) — seed modular del Demo
- `seeds/` — 11 fases del seed (fase1 a fase11)
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

**Tenant principal del Demo:** `tenant_27` ("Panadería Demo").

---

## 4️⃣ Usuarios del sistema

### Roles
- **super_admin** (dev_master) → gestiona TODOS los tenants
- **admin_cliente** → acceso TOTAL a su tenant
- **supervisor** → producción, recetas, MP, proveedores, reportes
- **cajero** → solo POS y cierre de caja

### Usuarios actuales
- `dev_master` (id=2, super_admin, tenant_1)
- `admin_25`, `super_25`, `cajero_25` (tenant_25)
- `admin_26`, `super_26`, `cajero_26` (tenant_26)
- `admin_27` (id=1), `super_27` (id=2), `cajero_27` (id=3) — tenant_27 Demo

### Contraseña del Demo
- **Todos los usuarios del tenant_27** (`admin_27`, `super_27`, `cajero_27`): contraseña **`demo2026`**.
- **Se restaura automáticamente** en cada `--reset-all` (fix A4).
- Constante `DEMO_PASSWORD` en `seed_demo.py` (línea 21).

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

---

## 6️⃣ Últimos commits pusheados
bd0cac8 fix(admin): 3 pendientes menores (A2 codigo salida reset-all, A4 restaurar passwords demo, C1 texto banner)
378f810 fix(admin): 4 fixes criticos del reset (pid_vivo, encoding utf8, rollback loop, sequences usuarios)
b5bb809 feat(admin): panel Super Admin con boton Reset Demo (solo dev_master)
59581f3 feat(admin): endpoints /admin/reset-demo y /admin/reset-demo/status
99aecea feat(demo): banner Demo via after_request (solo tenant_27)
9a2732e refactor(seeds): reemplazar raise por warning en validacion de tenant_27 (fases 6-11)
19c15b1 feat(demo): Fase 12 - reset total + reset-all (37 tablas, sequences, re-seed completo)
0695350 feat(demo): Fase 11 - cierres diarios (90 cierres con tendencia y productos top)
135a5b9 feat(demo): Fase 8 - productos externos (12 productos: bebidas, snacks, pasabocas)
fda25b9 fix(demo): Fase 10 v3 - separar pagos (insumos) de gastos (operativos) + ajustar montos (utilidad +18%)

text

---

## 7️⃣ Demo — Estado de las fases del seed

| # | Fase | Estado | Filas | Commit |
|---|------|--------|-------|--------|
| 1 | Configuración base | ✅ | 9 | fd862c3 |
| 2 | Proveedores | ✅ | 6 | fd862c3 |
| 3 | Materias primas | ✅ | 17 | fd862c3 |
| 4 | Recetas y fórmulas | ✅ | 80 | fd862c3 |
| 5 | Productos | ✅ | 12 | fd862c3 |
| 6 | Producción diaria (v2 con reposición) | ✅ | ~2.300 | 252b7a8 |
| 7 | Ventas | ✅ | ~7.300 | 93bf74c |
| 8 | Productos externos | ✅ | 12 | 135a5b9 |
| 9 | Activos fijos | ✅ | ~38 | 3fa92ef |
| 10 | Movimientos financieros | ✅ | ~265 | fda25b9 |
| 11 | Cierres diarios | ✅ | 90 | 0695350 |
| 12 | Reset automatizado | ✅ | — | 19c15b1 |

**Total aproximado:** ~10.100 filas en tenant_27 (depende del random en cada ejecución).

---

## 8️⃣ Fase 12 — Reset automatizado

### Comandos disponibles

| Comando | Función |
|---------|---------|
| `python seed_demo.py --tenant=27 --status` | Ver estado del seed |
| `python seed_demo.py --tenant=27 --fase=1,2,3` | Ejecutar fases específicas |
| `python seed_demo.py --tenant=27 --fase=all` | Ejecutar todas las fases |
| `python seed_demo.py --tenant=27 --reset` | Alias de `--reset-only` |
| `python seed_demo.py --tenant=27 --reset-only` | Solo borrar datos |
| `python seed_demo.py --tenant=27 --reset-all` | Reset + re-seed completo |

### Reset desde el frontend

- **Solo `dev_master`** (super_admin).
- Botón "🔄 Resetear Demo (tenant_27)" en `/mi_perfil`.
- Modal de confirmación.
- Polling cada 10s a `/admin/reset-demo/status`.
- Estado se actualiza en vivo.

### Endpoints backend

- `POST /admin/reset-demo` — dispara el reset.
- `GET /admin/reset-demo/status` — verifica si hay reset en curso.
- Lock file: `.reset_demo.lock` (con PID).
- Log: `reset_demo.log`.

### Tablas del reset (39)

Permisos, hijos, cabeceras, productos, recetas, proveedores, clientes, configuración, categorías, seed.

### Sequences excluidas del reset

- `usuarios_id_seq` (los usuarios no se borran).
- `panaderias_id_seq` (la panadería no se borra).

### Contraseñas restauradas

- Constante `DEMO_PASSWORD = 'demo2026'` en `seed_demo.py`.
- Se aplica a `admin_27`, `super_27`, `cajero_27`.
- Solo para `tenant_id == 27`.

---

## 9️⃣ Fixes críticos del reset (resueltos)

| # | Fix | Problema | Solución |
|---|-----|----------|----------|
| B1 | `os.kill(pid, 0)` mataba el proceso en Windows | Función `_pid_vivo()` usando `tasklist` |
| B2 | Falta `PYTHONIOENCODING=utf-8` | Variables de entorno + `encoding='utf-8'` en log |
| A1 | Rollback deshacía borrados previos | Eliminado `conn.rollback()` del loop DELETE |
| A3 | Sequences de usuarios se reseteaban | Excluidas `usuarios_id_seq`, `panaderias_id_seq` |
| A2 | `cmd_run_fases` no devolvía error | Ahora retorna `True`/`False` |
| A4 | Contraseñas no se restauraban | Restaurar a `demo2026` en cada reset |
| A7 | Faltaban tablas en reset | Agregadas `permisos_usuario`, `configuracion_panaderia` |

---

## 🔟 Banner Demo

**Implementación:** vía `@app.after_request` en `app.py`.
**Ubicación:** franja amarilla arriba de todo, solo para `tenant_27`.
**Texto:** "Este es un Demo de PanaderíaPro. Los cambios son temporales y pueden borrarse en cualquier momento."

---

## 1️⃣1️⃣ Módulo 11 — Reportes (estado detallado)

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

**Reportes que YA tienen export PDF:**
- `analisis_predictivo.html`
- `productos_populares.html`
- `ventas_avanzado.html`
- `ventas_periodo.html`

**Tiempo estimado:** 1.5-2 horas.

---

## 1️⃣2️⃣ Pendientes clasificados

### 🔴 CRÍTICOS (seguridad)
- **D1 — Password PostgreSQL en texto plano.** En `seed_demo.py` y `HANDOFF.md`. Rotar y pasar a variables de entorno.

### 🟡 IMPORTANTES (funcionalidad)
- **B3 — Race condition del lock.** Crear lock ANTES con `os.open(..., O_CREAT | O_EXCL)`.
- **B4 — `/status` no informa si falló.** Leer `reset_demo.log` y reportar éxito/fallo.
- **B7 — CSRF.** Verificar si el POST `/admin/reset-demo` tiene token CSRF.

### 🟢 MENORES (cosmético)
- **A8 — Discrepancias de conteo.** El HANDOFF dice "18 MP" pero son 17. El HANDOFF dice "13 productos" pero son 12. Actualizar.
- **B5 — PID reutilizado.** Bajo riesgo. Documentar.
- **B6 — Reset con usuarios conectados.** Durante 5 min el Demo se ve a medias. Aceptable.
- **C2 — `after_request` traga excepciones.** Útil pero oculta fallos.

### 🚨 DEUDA TÉCNICA (Fase C.3)
- **22 tablas con columnas huérfanas (79 columnas).** Fase C.3 planificada.
- **`public` con 40 tablas duplicadas.** Residuo de migración SQLite → PostgreSQL.

### 🟡 WARNINGS RECURRENTES
- `user_loader: This session is provisioning a new connection` → investigar session pooling.
- `LegacyAPIWarning: Query.get()` (app.py:2196, 2207) → migrar a `db.session.get()`.
- `Error obteniendo nombre de empresa: 'NoneType'` (al arrancar) → investigar.

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

**Encoding en CMD:**
```cmd
chcp 65001
Modo interactivo psql:

cmd
psql -U postgres -p 5433 -h localhost -d panaderia_master
Dentro: SET client_encoding TO 'UTF8';
Salir: \q

Seed Demo:

cmd
python seed_demo.py --list
python seed_demo.py --tenant=27 --status
python seed_demo.py --tenant=27 --fase=1,2,3
python seed_demo.py --tenant=27 --fase=all
python seed_demo.py --tenant=27 --reset-all
python seed_demo.py --tenant=27 --fase=6 --dry-run
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

/admin/reset-demo, /admin/reset-demo/status (super_admin)

Bug sistémico — panaderia_id default=1
Múltiples modelos tienen panaderia_id default=1. Si no se pasa explícito, toma 1.

Regla: SIEMPRE pasar panaderia_id=panaderia_id en cada INSERT.

Bug sistémico — productos.id ≠ productos.producto_id
productos.id = PK.

producto_id = FK en otras tablas.

Workaround — SQLAlchemy no persiste cambios
En editar_materia_prima, el += no se persiste. Usar UPDATE SQL directo.

Fases del seed — ya no hay hardcode a tenant_27
Las fases 6-11 tienen un print de warning (no raise) si panaderia_id != 27. Permite reutilización.

1️⃣5️⃣ Roadmap completo
text
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
├── ✅ Fase 8: Productos externos
├── ✅ Fase 9: Activos fijos
├── ✅ Fase 10: Movimientos financieros
├── ✅ Fase 11: Cierres diarios
└── ✅ Fase 12: Reset automatizado

✅ Fase Fixes: 5 bugs críticos resueltos (27 Sep 2026)
✅ Fase Admin: Banner Demo + Panel Super Admin + Reset desde frontend
✅ Fase Fixes 2: 4 fixes críticos del reset + 3 pendientes menores
✅ Prueba end-to-end: reset desde frontend en tenant_25 (exitosa)

⏳ Fase D2: Export PDF (~1.5 h)
⏳ Fase C.3: Auditoría de columnas (4-6 h)
⏳ Pendientes críticos: D1 (password), B3, B4, B7
⏳ Warnings SQLAlchemy: user_loader, Query.get()
⏳ Fase 4: Dockerización + nube
⏳ Fase 5: API REST
⏳ Fase 6: Chat IA básico
⏳ Fase 7: Junta Directiva IA
⏳ Fase 8: Integraciones estratégicas
1️⃣6️⃣ Próxima sesión — Prioridad sugerida
Plan acordado (1 Oct 2026):

⏳ Fase D2 (Export PDF) — ~1.5 h

⏳ Fase C.3 (Auditoría de columnas) — ~4-6 h

⏳ D1 (Password PostgreSQL a variables de entorno) — ~30 min

⏳ B3, B4, B7 (Race condition, status, CSRF) — ~1 h

⏳ Warnings SQLAlchemy — ~30 min

⏳ A8 (Actualizar conteos en HANDOFF) — ~5 min

Recomendación para próxima sesión: Empezar con Fase D2 (tangible, cierra el Módulo 11), luego D1 (seguridad, rápido), luego C.3 (larga).

1️⃣7️⃣ Notas estratégicas del proyecto
Objetivo del ERP
ERP SaaS para panaderías multi-tenant multi-país con: POS, inventario, producción, recetas, activos fijos, reportes con IA, finanzas, multi-país, base para API REST + IA avanzada.

🎁 Tenant Demo (marketing)
Objetivo: tenant público con datos precargados y realistas.

Estado: Fases 1-12 completadas (~10.100 filas).

Contraseña: demo2026 para todos los usuarios del Demo.

Reset: automático desde /mi_perfil con dev_master, o manual por CMD.

Subdominio sugerido: demo.panaderiapro.com.

Reset automático programado: PENDIENTE (no implementado). El banner actual dice "los cambios son temporales" (sin prometer 24h).

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

Próxima tarea sugerida: Fase D2 (Export PDF de reportes).

✅ Última validación
Último commit: bd0cac8 (pusheado a GitHub).

Working tree: clean.

Servidor: detenido.

Sistema: 100% funcional end-to-end.

Demo: Fases 1-12 completadas, contraseña demo2026.

Pendientes críticos: D1 (password), Fase C.3 (auditoría).

Fin del HANDOFF.md