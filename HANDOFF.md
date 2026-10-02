# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP)

**Última actualización:** 2 de Octubre, 2026
**Último commit:** cbcb76b (chore: limpiar .gitignore)
**Sesión anterior:** a522e0c (fix DT-11: event listener sin current_user)

---

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp)
- **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.1.2 — **11/11 módulos completados (100%)** + Demo Fases 1-12 completadas + Endurecimiento de seguridad
- **Arquitectura:** Multi-tenant con PostgreSQL (schemas por tenant)
- **Próximo hito:** DT-12 (warning `_obtener_nombre_empresa`) + DT-26 (latencia 3s) + DT-20 Fase C

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
cbcb76b chore: limpiar .gitignore - eliminar duplicados, corregir linea rota de secrets.py/migrations, agregar artefactos de pruebas
a522e0c fix(DT-11): eliminar acceso a current_user en event listener de checkout - rompe recursion con load_user y elimina error isce de SQLAlchemy 2.0
12bce7b docs: HANDOFF v5
4a9669b security(B7): validacion global de Origin en before_request (mitigacion CSRF para todos los POST)
11f0689 fix(reset-demo): B4 v2 - persistir estado del ultimo reset en JSON separado + /status lo lee
35fe33c fix(reset-demo): B3 lock atomico con O_CREAT|O_EXCL (elimina race condition) + marcadores EXIT_CODE en seed
344c552 fix(multi-tenant): DT-20 Fase B - agregar panaderia_id explicito a 4 INSERTs criticos
dcad6d6 fix(reportes): DT-2 y DT-2b - eliminar metodos duplicados + corregir indentacion en tabla de tesoreria
9d5c88f security(D1): externalizar password PostgreSQL a variables de entorno
4250ba3 docs: HANDOFF v4 (Fase D2 completada, 11/11 modulos, DT-1 a DT-12)
3cac49e feat(reportes): Fase D2 - export PDF historial de pagos y depositos
239612f docs+fix: HANDOFF v3 (Fases 1-12 + admin panel) + A7

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

**Total aproximado:** ~10.100 filas en tenant_27.

---

## 8️⃣ Fase 12 — Reset automatizado (con mejoras B3, B4 v2)

### Comandos disponibles
- `python seed_demo.py --tenant=27 --status` — ver estado
- `python seed_demo.py --tenant=27 --fase=1,2,3` — fases específicas
- `python seed_demo.py --tenant=27 --fase=all` — todas las fases
- `python seed_demo.py --tenant=27 --reset` — alias de --reset-only
- `python seed_demo.py --tenant=27 --reset-only` — solo borrar
- `python seed_demo.py --tenant=27 --reset-all` — reset + re-seed

### Reset desde frontend
- **Solo `dev_master`** (super_admin).
- Botón "🔄 Resetear Demo (tenant_27)" en `/mi_perfil`.
- Polling cada 10s a `/admin/reset-demo/status`.
- Lock file: `.reset_demo.lock` (con PID). Log: `reset_demo.log`.
- Estado persistente: `reset_demo.last_status.json`.

### B7 — CSRF global
- Validación global de `Origin`/`Referer` en `@app.before_request`.
- Política: rechaza POST/PUT/DELETE/PATCH con `Origin` distinto al `Host`.
- Permite requests sin `Origin` (curl, tests, webhooks) con warning en log.

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

- `.env` está en `.gitignore` (protegido).
- `load_dotenv()` se llama al inicio de `app.py`.

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
- **Fase A (auditoría):** completada.
- **Fase B (fix quirúrgico):** completada — 4 INSERTs corregidos (commit `344c552`).
- **Fase C (eliminar defaults):** pendiente.

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
| DT-12 | `reportes.py:48-68` | `_obtener_nombre_empresa` usa `current_user.is_authenticated` sin verificar `None` → warning en cada request al arranque |
| DT-13 | repo | Falta `.env.example` documentando variables requeridas |
| DT-15 | `.env` | Password PostgreSQL embebida en `DATABASE_URL` |
| DT-16 | `app.py:login` | Log de login imprime `DATABASE_URL` con password visible |
| DT-17 | `reportes.py` | Reporte de tesorería muestra `$0` de ingresos |
| DT-18 | `reportes.py` | Reporte de tesorería no tiene nivel contable profesional |
| DT-19 | global | CSRF fix completo con `flask-wtf` (mitigación actual usa Origin; cobertura 99%) |
| DT-21 | POS | Modal de crear cliente sin botón visible |
| DT-25 | `app.py:1744` | Verificar orden real de ejecución de `before_request` vs `login_required` |
| **DT-26** | **global** | **Latencia ~3s entre módulos tras resolver DT-11. Requiere profiling con timer `@after_request`. Prioridad MEDIA.** |

### 🟢 Bajas

| # | Ubicación | Descripción |
|---|-----------|-------------|
| DT-3 | `reportes.py:12` | Import muerto de `Response` |
| DT-4 | `reportes.py` (varios) | Reimport local de modelos |
| DT-10 | `app.py:9022-9495` | Exports PDF no agrupados bajo comentario separador |
| DT-22 | `/configuracion/facturacion` | Permite modificar NIT del tenant sin confirmación |
| DT-23 | `models.py` | Ver DT-20 (Fase C) |
| DT-24 | `mi_perfil.html` | Frontend no muestra el campo `exitoso` del último reset |

### 🚨 Otras deudas
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
17. **🆕 Antes de proponer un fix de concurrencia o de conexión, medir el impacto en el pool de SQLAlchemy.**
18. **🆕 Nunca usar `echo texto >> archivo` en Windows para modificar `.gitignore` u otros archivos de texto (no añade newline si el archivo no termina en newline). Usar Notepad o PowerShell.**

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

✅ D1: Password PostgreSQL a env vars
✅ DT-2 + DT-2b: Métodos duplicados + indentación
✅ DT-20 Fase A + B: Multi-tenant INSERTs
✅ B3: Lock atómico
✅ B4 v2: Estado persistente reset
✅ B7: CSRF global
✅ DT-11: Event listener sin current_user (2 Oct 2026)

⏳ DT-12 (warning _obtener_nombre_empresa)
⏳ DT-26 (latencia ~3s entre módulos)
⏳ DT-20 Fase C (eliminar 32 defaults)
⏳ Fase C.3 (auditoría de columnas, 22 tablas)
⏳ DT-18 (reporte tesorería nivel contable)
⏳ DT-19 (CSRF completo con flask-wtf)
⏳ Fase 4: Dockerización + nube
⏳ Fase 5: API REST
⏳ Fase 6: Chat IA básico
⏳ Fase 7: Junta Directiva IA
⏳ Fase 8: Integraciones estratégicas
1️⃣3️⃣ DT-11 — Resuelto (2 Oct 2026) — Bitácora completa
Causa raíz: El event listener checkout (app.py:1322-1380) accedía a current_user (Flask-Login) para determinar el tenant. current_user es un LocalProxy que dispara load_user al primer acceso. load_user hace db.session.execute() → checkout → event listener → current_user → load_user → ... recursión infinita. SQLAlchemy 2.0 detecta la reentrada y aborta con:

This session is provisioning a new connection; concurrent operations are not permitted (isce)

Solución: Eliminar el acceso a current_user del event listener. Leer el tenant SOLO desde flask.session (que es un dict, no dispara load_user).

Bitácora de intentos fallidos:

Versión	Cambio	Resultado
v1	Reducir queries en load_user (3→1)	❌ No resolvió — era concurrencia, no cantidad
v2	Usar db.engine.connect() en load_user	❌ Peor — agotó el pool (2 conexiones por request × N llamadas)
v3	Cache con flask.g en load_user	❌ No resolvió — el cache no estaba listo cuando el event listener corría
v4	Eliminar current_user del event listener	✅ RESUELTO
Commit: a522e0c

1️⃣4️⃣ Notas estratégicas
Objetivo del ERP
ERP SaaS multi-tenant multi-país con: POS, inventario, producción, recetas, activos fijos, reportes con IA, finanzas, multi-país, base para API REST + IA avanzada.

🎁 Tenant Demo (marketing)
Fases 1-12 completadas (~10.100 filas). Contraseña: demo2026. Reset desde /mi_perfil con dev_master.

Mercado objetivo
3.000-5.000 panaderías en Colombia.

10.000-30.000 en LATAM.

Precio sugerido: $60k-$600k COP/mes.

📞 Cómo continuar en un chat nuevo
Al iniciar un nuevo chat, pegar este archivo como contexto inicial.

Instrucción sugerida para el asistente:

"Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el archivo HANDOFF.md con el contexto maestro del proyecto. Vamos a continuar desde donde lo dejamos. Por favor actúa como instructor guiando paso a paso, con la metodología de trabajo descrita en el HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/findstr, commit tras cada fix verificado. Al insertar bloques, muéstrame ANTES → DESPUÉS con número de línea exacto."

Próxima tarea sugerida: DT-12 (warning _obtener_nombre_empresa en reportes.py:48-68).

✅ Última validación
Último commit: cbcb76b (pusheado a GitHub).

Working tree: clean (excepto .gitignore.bak_before_cleanup — agregar a .gitignore o borrar).

Servidor: detenido.

Sistema: 100% funcional end-to-end.

Módulos: 11/11 completados (100%).

Demo: Fases 1-12 completadas, contraseña demo2026, ~10.100 filas.

Sesión 2 Oct 2026 (mañana): 6 commits (D1, DT-2, DT-20 Fase B, B3, B4 v2, B7).

Sesión 2 Oct 2026 (tarde): 2 commits (DT-11 resuelto, limpieza .gitignore).

Pendientes críticos: DT-12, DT-26 (latencia), DT-20 Fase C, Fase C.3.

Fin del HANDOFF.md — v6