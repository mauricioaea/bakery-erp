# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP)

**Última actualización:** 2 de Octubre, 2026
**Último commit:** 4a9669b (B7 — validación global de Origin / mitigación CSRF)

---

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp)
- **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.1.1 — **11/11 módulos completados (100%)** + Demo Fases 1-12 completadas + Endurecimiento de seguridad
- **Arquitectura:** Multi-tenant con PostgreSQL (schemas por tenant)
- **Próximo hito:** DT-11 + DT-12 (warnings SQLAlchemy) + Fase C.3 (auditoría de columnas)

---

## 2️⃣ Stack tecnológico

### Backend
- Python 3.10+, Flask 3.1.2, SQLAlchemy 2.0
- PostgreSQL 17.10 (puerto 5433)
- Flask-Login, Werkzeug (pbkdf2:sha256, scrypt), ReportLab, Matplotlib
- **BD:** `panaderia_master` — credenciales en `.env` (no hardcodeadas)

### Frontend
- HTML5/CSS3, JavaScript vanilla, Bootstrap 5.1.3, Chart.js, Font Awesome 6

### Estructura de archivos
- `app.py` (~12.700 líneas, ~530 KB) — aplicación principal
- `models.py` (~3.100 líneas, ~130 KB) — modelos SQLAlchemy
- `reportes.py` (~3.254 líneas, ~160 KB) — generación PDF
- `seed_demo.py` (~450 líneas, ~18 KB) — seed modular del Demo
- `seeds/` — 11 fases del seed (fase1 a fase11)
- `middleware_saas.py`, `tenant_decorators.py`, `tenant_context.py` — multi-tenant
- `templates/`, `static/`
- `.env` — variables de entorno (credenciales BD, SECRET_KEY)
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
| 11 | Reportes Profesionales | ✅ COMPLETO (Fase D2 cerrada 2 Oct 2026) |

---

## 6️⃣ Últimos commits pusheados
4a9669b security(B7): validacion global de Origin en before_request (mitigacion CSRF para todos los POST)
11f0689 fix(reset-demo): B4 v2 - persistir estado del ultimo reset en JSON separado + /status lo lee
35fe33c fix(reset-demo): B3 lock atomico con O_CREAT|O_EXCL (elimina race condition) + marcadores EXIT_CODE en seed
344c552 fix(multi-tenant): DT-20 Fase B - agregar panaderia_id explicito a 4 INSERTs criticos
dcad6d6 fix(reportes): DT-2 y DT-2b - eliminar metodos duplicados + corregir indentacion en tabla de tesoreria
9d5c88f security(D1): externalizar password PostgreSQL a variables de entorno
4250ba3 docs: HANDOFF v4 (Fase D2 completada, 11/11 modulos, DT-1 a DT-12)
3cac49e feat(reportes): Fase D2 - export PDF historial de pagos y depositos
239612f docs+fix: HANDOFF v3 (Fases 1-12 + admin panel) + A7

text

---

## 7️⃣ Demo — Estado de las fases del seed

| # | Fase | Estado | Filas | Commit |
|---|------|--------|-------|--------|
| 1 | Configuración base | ✅ | 9 | fd862c3 |
| 2 | Proveedores | ✅ | 6 | fd862c3 |
| 3 | Materias primas | ✅ | 17 | fd862c3 |
| 4 | Recetas y fórmulas | ✅ | 12 recetas / 80 ingredientes | fd862c3 |
| 5 | Productos | ✅ | 12 | fd862c3 |
| 6 | Producción diaria (v2 con reposición) | ✅ | ~2.300 | 252b7a8 |
| 7 | Ventas | ✅ | ~7.300 | 93bf74c |
| 8 | Productos externos | ✅ | 12 | 135a5b9 |
| 9 | Activos fijos | ✅ | ~38 | 3fa92ef |
| 10 | Movimientos financieros | ✅ | ~265 | fda25b9 |
| 11 | Cierres diarios | ✅ | 90 | 0695350 |
| 12 | Reset automatizado | ✅ | — | 19c15b1 |

**Total aproximado:** ~10.100 filas en tenant_27 (depende del random en cada ejecución).

**Conteos verificados con psql (2 Oct 2026):**
- `materias_primas`: 17
- `productos`: 12
- `recetas`: 12
- `proveedor`: 6

---

## 8️⃣ Fase 12 — Reset automatizado (con mejoras B3, B4 v2)

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
- `GET /admin/reset-demo/status` — verifica si hay reset en curso y su resultado.
- Lock file: `.reset_demo.lock` (con PID).
- Log: `reset_demo.log`.
- **Estado persistente:** `reset_demo.last_status.json` (JSON con `{exitoso, errores, tenant_id, timestamp}`).

### B3 — Lock atómico (fix 2 Oct 2026)

- Creación del lock con `os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)`.
- Elimina race condition entre "verificar" y "crear".
- Flag `lock_creado` para cleanup selectivo.

### B4 v2 — Estado persistente (fix 2 Oct 2026)

- `seed_demo.py` escribe `reset_demo.last_status.json` al terminar.
- `/status` lee el JSON cuando no hay lock.
- Responde con `exitoso: true/false`, `timestamp`, `errores`.

### B7 — CSRF global (fix 2 Oct 2026)

- Validación global de `Origin`/`Referer` en `@app.before_request`.
- Política: rechaza POST/PUT/DELETE/PATCH con `Origin` distinto al `Host`.
- Permite requests sin `Origin` (curl, tests, webhooks) con warning en log.
- Cubre TODOS los endpoints POST del sistema (todos los tenants actuales y futuros).

### Tablas del reset (39)

Permisos, hijos, cabeceras, productos, recetas, proveedores, clientes, configuración, categorías, seed.

### Sequences excluidas del reset

- `usuarios_id_seq` (los usuarios no se borran).
- `panaderias_id_seq` (la panadería no se borra).

---

## 9️⃣ Configuración crítica

### Variables de entorno (.env)
DATABASE_URL=postgresql://postgres:...@localhost:5433/panaderia_master
DB_PASSWORD=...
FLASK_ENV=development
SECRET_KEY=...

text

- `.env` está en `.gitignore` (protegido).
- `load_dotenv()` se llama al inicio de `app.py`.
- `app.py` y `seed_demo.py` usan `os.getenv()` para credenciales.
- Fallback en `seed_demo.py` (`'PanaderiaPro2026!'`) por compatibilidad con dev.

### Rutas críticas

- `/reportes`, `/historial_pagos`, `/historial_depositos`
- `/exportar_historial_pagos`, `/exportar_historial_depositos`
- `/gestion_financiera`, `/mi_perfil`, `/cambiar_licencia/<id>`
- `/punto_venta`, `/registrar_venta`, `/recibo-pos/<id>`
- `/materias_primas`, `/editar_materia_prima/<id>`
- `/produccion_diaria`, `/reporte/cierre_caja`
- `/reporte/ventas_avanzado`, `/activos_fijos`
- `/depositos_bancarios`
- `/admin/reset-demo`, `/admin/reset-demo/status` (super_admin)

### Bug sistémico — panaderia_id default=1 (DT-20)

- **~32 modelos** tienen `panaderia_id = db.Column(..., default=1)`.
- Algunos INSERTs olvidan pasar `panaderia_id` → cae en `tenant_1` silenciosamente.
- **Fase A (auditoría):** completada — se identificaron 4 INSERTs críticos.
- **Fase B (fix quirúrgico):** completada — 4 INSERTs corregidos (commit `344c552`).
- **Fase C (eliminar defaults):** pendiente — sesión dedicada.

### Bug sistémico — productos.id ≠ productos.producto_id

- `productos.id` = PK.
- `producto_id` = FK en otras tablas.

---

## 🔟 Deuda técnica acumulada

### 🔴 Críticos

| # | Ubicación | Descripción |
|---|-----------|-------------|
| DT-2 | `reportes.py:2578 y 2733` | `_agregar_resumen_ejecutivo_tesoreria` y `_generar_reporte_error` duplicados |
| DT-6 | `models.py:2124` | `PagoIndividual.panaderia_id default=1` |
| DT-9 | `models.py:523` | `Proveedor.panaderia_id default=1` |
| DT-14 | `.env` | `SECRET_KEY` débil (`panaderiapro2026`) |
| DT-20 | `models.py` (32 modelos) | Bug sistémico `panaderia_id default=1` (Fase C pendiente) |

### 🟡 Medias

| # | Ubicación | Descripción |
|---|-----------|-------------|
| DT-1 | `reportes.py:48-68` | `_obtener_nombre_empresa` doble filtro tenant_id/panaderia_id |
| DT-5 | `models.py:1055 vs 2441` | `Gasto` vs `RegistroFinanciero` posible solapamiento |
| DT-7 | `models.py:2075 vs 2124` | Inconsistencia `nullable` entre modelos hermanos |
| DT-11 | `user_loader` | Warning `This session is provisioning a new connection` en cada request |
| DT-13 | repo | Falta `.env.example` documentando variables requeridas |
| DT-15 | `.env` | Password PostgreSQL embebida en `DATABASE_URL` (inevitable con ese formato) |
| DT-16 | `app.py:login` | Log de login imprime `DATABASE_URL` con password visible |
| DT-17 | `reportes.py` | Reporte de tesorería muestra `$0` de ingresos porque busca en tabla incorrecta/vacía |
| DT-18 | `reportes.py` | Reporte de tesorería no tiene nivel contable profesional (NIT, consecutivo, discriminación) |
| DT-19 | global | CSRF fix completo con `flask-wtf` (mitigación actual usa Origin; cobertura 99%) |
| DT-21 | POS | Modal de crear cliente sin botón visible; solo se abre durante el flujo de venta |
| DT-25 | `app.py:1744` | Verificar orden real de ejecución de `before_request` vs `login_required` |

### 🟢 Bajas

| # | Ubicación | Descripción |
|---|-----------|-------------|
| DT-3 | `reportes.py:12` | Import muerto de `Response` |
| DT-4 | `reportes.py` (varios) | Reimport local de modelos |
| DT-10 | `app.py:9022-9495` | Exports PDF no agrupados bajo comentario separador |
| DT-12 | `reportes.py:48-68` | `current_user` puede ser `None` al arrancar |
| DT-22 | `/configuracion/facturacion` | Permite modificar NIT del tenant sin confirmación |
| DT-23 | `models.py` | Ver DT-20 (Fase C) |
| DT-24 | `mi_perfil.html` | Frontend no muestra el campo `exitoso` del último reset |

### 🚨 Otras deudas (HANDOFF v4)

- **22 tablas con columnas huérfanas (79 columnas).** Fase C.3 planificada.
- **`public` con 40 tablas duplicadas.** Residuo de migración SQLite → PostgreSQL.

---

## 1️⃣1️⃣ Metodología de trabajo

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
15. **Al pedir un test, incluir TODAS las verificaciones previas necesarias en el mismo mensaje.**
16. **Cuando el punto de inserción esté justo debajo de un decorador, incluir el decorador en el ANTES → DESPUÉS.**

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
python -m py_compile reportes.py
python -m py_compile seed_demo.py
python app.py
Test CSRF con curl:

cmd
curl -c cookies.txt -X POST http://localhost:5000/ -d "username=admin_27&password=demo2026" -L -o nul
curl -b cookies.txt -X POST http://localhost:5000/admin/reset-demo -H "Origin: https://malicious.example.com" -i
1️⃣2️⃣ Roadmap
text
✅ Fase 1: Módulos 1-10
✅ Fase 2: Módulo 11 Reportes (100%)
✅ Fase D2: exportación PDF (2 Oct 2026)

✅ Fase Demo: Tenant Demo (Fases 1-12)
✅ Fase Admin: Banner Demo + Panel Super Admin + Reset desde frontend

✅ D1: Password PostgreSQL a env vars (2 Oct 2026)
✅ DT-2 + DT-2b: Métodos duplicados + indentación (2 Oct 2026)
✅ DT-20 Fase A + B: Multi-tenant INSERTs (2 Oct 2026)
✅ B3: Lock atómico (2 Oct 2026)
✅ B4 v2: Estado persistente reset (2 Oct 2026)
✅ B7: CSRF global (2 Oct 2026)

⏳ DT-11, DT-12 (warnings SQLAlchemy)
⏳ DT-20 Fase C (eliminar 32 defaults)
⏳ Fase C.3 (auditoría de columnas, 22 tablas)
⏳ DT-18 (reporte tesorería nivel contable)
⏳ DT-19 (CSRF completo con flask-wtf)
⏳ Fase 4: Dockerización + nube
⏳ Fase 5: API REST
⏳ Fase 6: Chat IA básico
⏳ Fase 7: Junta Directiva IA
⏳ Fase 8: Integraciones estratégicas
1️⃣3️⃣ Próxima sesión — Prioridad sugerida
Plan acordado (2 Oct 2026 — post sesión de seguridad):

✅ D1, DT-2, DT-20 Fase B, B3, B4, B7 — COMPLETADAS

⏳ DT-11 (warning user_loader)

⏳ DT-12 (warning current_user is None)

⏳ DT-20 Fase C (eliminar default=1 de 32 modelos)

⏳ Fase C.3 (auditoría columnas)

Recomendación: Empezar con DT-11 y DT-12 (warnings, ~1 h), luego DT-20 Fase C (~3-4 h), finalmente C.3 (~4-6 h).

1️⃣4️⃣ Notas estratégicas
Objetivo del ERP
ERP SaaS multi-tenant multi-país con: POS, inventario, producción, recetas, activos fijos, reportes con IA, finanzas, multi-país, base para API REST + IA avanzada.

🎁 Tenant Demo (marketing)
Fases 1-12 completadas (~10.100 filas).

Contraseña: demo2026.

Reset: automático desde /mi_perfil con dev_master.

Subdominio sugerido: demo.panaderiapro.com.

Mercado objetivo
3.000-5.000 panaderías en Colombia.

10.000-30.000 en LATAM.

Precio sugerido: $60k-$600k COP/mes.

📞 Cómo continuar en un chat nuevo
Al iniciar un nuevo chat, pegar este archivo como contexto inicial.

Instrucción sugerida para el asistente:

"Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el archivo HANDOFF.md con el contexto maestro del proyecto. Vamos a continuar desde donde lo dejamos. Por favor actúa como instructor guiando paso a paso, con la metodología de trabajo descrita en el HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/findstr, commit tras cada fix verificado. Al insertar bloques, muéstrame ANTES → DESPUÉS con número de línea exacto."

Próxima tarea sugerida: DT-11 (warning user_loader).

✅ Última validación
Último commit: 4a9669b (pusheado a GitHub).

Working tree: clean.

Servidor: detenido.

Sistema: 100% funcional end-to-end.

Módulos: 11/11 completados (100%).

Demo: Fases 1-12 completadas, contraseña demo2026, ~10.100 filas.

Sesión 2 Oct 2026: 6 commits (D1, DT-2, DT-20 Fase B, B3, B4 v2, B7).

Pendientes críticos: DT-11, DT-12, DT-20 Fase C, Fase C.3.

Fin del HANDOFF.md — v5

text