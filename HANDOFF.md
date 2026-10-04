# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP)

**Última actualización:** 3 de Octubre, 2026
**Último commit:** b111005 (fix DT-20 Fase C - Tanda 3)
**Sesión 2 Oct:** DT-11, DT-12, DT-13, DT-14, DT-16, DT-26, DT-27, DT-3, DT-4
**Sesión 3 Oct:** DT-1, DT-6, DT-9, DT-20 Fase C (Tanda 1 + Tanda 2 + Tanda 3), DT-30, DT-31

---

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp)
- **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.1.8 — **11/11 módulos completados (100%)** + Demo Fases 1-12 + Endurecimiento de seguridad + **DT-20 al 100%** (modelo + BD) + Código limpio
- **Arquitectura:** Multi-tenant con PostgreSQL (schemas por tenant)
- **Próximo hito:** Fase C.3 (auditoría de columnas huérfanas) + Fase 3 (Docker + nube)

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
- `app.py` (~12.600 líneas, ~528 KB) — aplicación principal
- `models.py` (~3.050 líneas, ~130 KB) — modelos SQLAlchemy
- `reportes.py` (~3.250 líneas, ~160 KB) — generación PDF
- `seed_demo.py` (~450 líneas) — seed del Demo
- `seeds/` — 11 fases del seed
- `middleware_saas.py`, `tenant_decorators.py`, `tenant_context.py` — multi-tenant
- `templates/`, `static/`
- `.env` (protegido en `.gitignore`), `.env.example` (plantilla)
- `HANDOFF.md` — este archivo

---

## 3️⃣ Tenants activos

| ID | Nombre | Subdominio | Plan | Licencia |
|----|--------|-----------|------|----------|
| 1 | Panadería Principal | principal | basico | local |
| 25 | Panadería Test Fase C | panadería_test_fase_ | premium | nube_premium |
| 26 | Test Audit Fase C.2 | test_audit_fase_c2 | premium | nube_premium |
| 27 | **Panadería Demo** | panadería_demo | premium | nube_premium |

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
- **Todos los usuarios del tenant_27:** contraseña **`demo2026`**.
- Se restaura automáticamente en cada `--reset-all`.
- Constante `DEMO_PASSWORD` en `seed_demo.py` (línea 21).

### Creación de usuarios (diseño del negocio)
- **NO se crean usuarios desde el frontend.**
- Los usuarios se crean al **alta del tenant** en `crear_tenant_saas()` (SQL directo con `panaderia_id` explícito).
- **Licencia premium:** 3 usuarios (admin, supervisor, cajero).
- **Licencia básica:** 1 usuario (admin).
- Endpoint `/crear_usuario` fue **eliminado** en DT-20 Fase C Tanda 2 (código huérfano).

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
b111005 fix(DT-20 Fase C - Tanda 3): eliminar default=1 en ConfiguracionPanaderia y Panaderia + arreglar INSERT ORM
82ed869 docs: HANDOFF v7.3 - 6 deudas resueltas (3 Oct), DT-20 Fase C al 93%, reglas 21-22
14de608 fix(DT-20 Fase C - Tanda 2): eliminar endpoint /crear_usuario huérfano + eliminar default=1 en Categoria y Usuario
45d011e fix(DT-20 Fase C - Tanda 1): eliminar default=1 en panaderia_id de 27 modelos seguros - Grupo A
0becbf8 fix(DT-1): eliminar filtro redundante por tenant_id en _obtener_nombre_empresa
9b29c3b docs: HANDOFF v7.2 - DT-6 + DT-9 resueltas, regla 21
a25505a fix(DT-6, DT-9): eliminar default=1 de panaderia_id en PagoIndividual y Proveedor
11662f5 docs: HANDOFF v7.1
71f6ae1 fix(DT-3, DT-4): eliminar import muerto Response y 4 reimports redundantes
8bda650 docs: HANDOFF v7
cafc325 fix(DT-14): leer SECRET_KEY desde .env
301bd65 docs(DT-13): agregar .env.example
ffd8e8f fix(DT-16): no imprimir password de BD en log de login
6e260b1 fix(DT-12): verificar current_user de forma segura
1e4c120 fix(DT-27): reemplazar Query.get() por db.session.get()
a2a2e71 docs: HANDOFF v6
cbcb76b chore: limpiar .gitignore
a522e0c fix(DT-11): eliminar acceso a current_user en event listener

text

---

## 7️⃣ Demo — Estado de las fases del seed

| # | Fase | Estado | Filas |
|---|------|--------|-------|
| 1 | Configuración base | ✅ | 9 |
| 2 | Proveedores | ✅ | 6 |
| 3 | Materias primas | ✅ | 17 |
| 4 | Recetas y fórmulas | ✅ | 12 recetas / 80 ingredientes |
| 5 | Productos | ✅ | 12 |
| 6 | Producción diaria | ✅ | ~2.300 |
| 7 | Ventas | ✅ | ~7.300 |
| 8 | Productos externos | ✅ | 12 |
| 9 | Activos fijos | ✅ | ~38 |
| 10 | Movimientos financieros | ✅ | ~265 |
| 11 | Cierres diarios | ✅ | 90 |
| 12 | Reset automatizado | ✅ | — |

**Total aproximado:** ~10.100 filas en tenant_27.

---

## 8️⃣ Configuración crítica

### Variables de entorno (.env)
DATABASE_URL=postgresql://postgres:...@localhost:5433/panaderia_master
DB_PASSWORD=...
FLASK_ENV=development
SECRET_KEY=...

text

- `.env` en `.gitignore`. `.env.example` en el repo.
- `load_dotenv()` al inicio de `app.py`.
- **SECRET_KEY** se lee del `.env` (DT-14).

### Rutas críticas

- `/reportes`, `/historial_pagos`, `/historial_depositos`
- `/gestion_financiera`, `/mi_perfil`, `/cambiar_licencia/<id>`
- `/punto_venta`, `/registrar_venta`, `/recibo-pos/<id>`
- `/materias_primas`, `/editar_materia_prima/<id>`
- `/produccion_diaria`, `/reporte/cierre_caja`
- `/reporte/ventas_avanzado`, `/activos_fijos`
- `/depositos_bancarios`
- `/admin/reset-demo`, `/admin/reset-demo/status`
- `/crear_cliente`, `/editar_cliente_super`, `/renovar_suscripcion_super`, `/eliminar_cliente`
- **Eliminado:** `/crear_usuario`

### Bug sistémico — panaderia_id default=1 (DT-20)

**✅ RESUELTO AL 100% (3 Oct 2026).**

- **Fase A (auditoría):** completada.
- **Fase B (fix quirúrgico):** completada — 4 INSERTs críticos (`344c552`).
- **Fase C - Tanda 1:** 27 modelos del Grupo A (`45d011e`).
- **Fase C - Tanda 2:** Categoria y Usuario + endpoint huérfano eliminado (`14de608`).
- **Fase C - Tanda 3:** Panaderia y ConfiguracionPanaderia + INSERT ORM de `app.py:1719` (`b111005`).

**Resultado:** ningún modelo tiene `default=1` en `panaderia_id`. Si un INSERT olvida pasar `panaderia_id`, **falla con `IntegrityError`** (fail-fast).

---

## 9️⃣ Deuda técnica acumulada

### ✅ RESUELTAS el 3 de Octubre 2026 (9 deudas)

| # | Descripción | Commit |
|---|-------------|--------|
| DT-1 | Filtro redundante por tenant_id en `_obtener_nombre_empresa` | `0becbf8` |
| DT-6 | `PagoIndividual.panaderia_id default=1` | `a25505a` |
| DT-9 | `Proveedor.panaderia_id default=1` | `a25505a` |
| DT-20 Fase C Tanda 1 | 27 modelos del Grupo A sin default | `45d011e` |
| DT-20 Fase C Tanda 2 | Categoria + Usuario sin default + 2 INSERTs + endpoint huérfano | `14de608` |
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
| DT-7 | `models.py:2075 vs 2124` | Inconsistencia `nullable` entre modelos hermanos |

| DT-17 | `reportes.py` | Reporte tesorería muestra `$0` de ingresos |
| DT-18 | `reportes.py` | Reporte tesorería nivel contable profesional |
| DT-19 | global | CSRF completo con `flask-wtf` |
| DT-21 | POS | Modal de crear cliente sin botón visible |
| DT-25 | `app.py:1744` | Orden real de `before_request` vs `login_required` |
| DT-28 | `POST /` | Doble submit detectado |
| DT-29 | `app.py` (before_request fallback) | Tenant por defecto "Panadería Principal" en usuarios anónimos |


### 🟢 Bajas pendientes

| # | Ubicación | Descripción |
|---|-----------|-------------|
| DT-10 | `app.py:9022-9495` | Exports PDF no agrupados |
| DT-22 | `/configuracion/facturacion` | Permite modificar NIT sin confirmación |
| DT-24 | `mi_perfil.html` | No muestra `exitoso` del último reset |
| **DT-32** | `models.py:433` + `to_dict()` | `Panaderia.panaderia_id` es redundante con `id`. Nadie lo lee en Python. Candidato a eliminar en migración futura. |

### 🚨 Otras deudas
- **22 tablas con columnas huérfanas (79 columnas).** Fase C.3 planificada.
- **`public` con 40 tablas duplicadas.**

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
22. **Al eliminar código huérfano, verificar PRIMERO que no haya referencias activas con `findstr /s`.**
23. **Al auditar modelos con `default=N`: verificar TODOS los INSERTs (ORM + SQL directo) antes de eliminar el default. Considerar si el modelo tiene INSERTs en `models.py` (métodos `@classmethod`), en `app.py`, en `middleware_saas.py`, en `seeds/`, y en ORM DETACHED.**

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
Ver bloque de líneas (PowerShell):

cmd
powershell -Command "$lines = Get-Content archivo.py; for ($i=INICIO; $i -le FIN; $i++) { Write-Host ($i+1)': ' $lines[$i] }"
1️⃣1️⃣ Roadmap
text
✅ Fase 1: Módulos 1-10
✅ Fase 2: Módulo 11 Reportes (100%)
✅ Fase D2: exportación PDF
✅ Fase Demo: Tenant Demo (Fases 1-12)
✅ Fase Admin: Banner Demo + Panel Super Admin

✅ D1: Password PostgreSQL a env vars
✅ DT-2 + DT-2b: Métodos duplicados + indentación
✅ DT-20 Fase A + B + C: Multi-tenant INSERTs y default=1 (100%)
✅ B3: Lock atómico
✅ B4 v2: Estado persistente reset
✅ B7: CSRF global

--- Sesión 2 Oct 2026 (11 deudas) ---
✅ DT-3 + DT-4: Imports muertos
✅ DT-11: Event listener sin current_user
✅ DT-12: _obtener_nombre_empresa seguro
✅ DT-13: .env.example
✅ DT-14: SECRET_KEY desde .env
✅ DT-16: Password BD oculta en log
✅ DT-26: Latencia resuelta
✅ DT-27: Query.get() → db.session.get()

--- Sesión 3 Oct 2026 (7 deudas) ---
✅ DT-1: Filtro redundante tenant_id
✅ DT-6 + DT-9: default=1 en 2 modelos
✅ DT-20 Fase C Tanda 1: 27 modelos sin default
✅ DT-20 Fase C Tanda 2: Categoria + Usuario + endpoint huérfano
✅ DT-20 Fase C Tanda 3: Panaderia + ConfiguracionPanaderia + INSERT ORM
✅ DT-30: Endpoint /crear_usuario eliminado

⏳ Fase C.3: auditoría de columnas (22 tablas, 79 columnas)
✅ DT-31: DEFAULT 1 en PostgreSQL eliminado (3 Oct)
✅ DT-15: Password PostgreSQL en DATABASE_URL — Aceptada
⏳ DT-29: Tenant por defecto en usuarios anónimos
⏳ DT-5, DT-7, DT-17, DT-18, DT-19, DT-21, DT-25, DT-28: Deudas medias

⏳ Fase 3: Dockerización + subdominios + nube
⏳ Fase 4: HTTPS/SSL + rate limiting + logging + monitoreo + caché
⏳ Fase 5: Pasarela de pagos + portal autogestión + facturación
⏳ Fase 6: Chat IA
⏳ Fase 7: Junta Directiva IA
⏳ Fase 8: Integraciones estratégicas (API REST, webhooks)
1️⃣2️⃣ DT-11 — Resuelto (2 Oct 2026) — Bitácora
Causa raíz: El event listener checkout accedía a current_user (Flask-Login). current_user es un LocalProxy que dispara load_user al primer acceso. load_user hace db.session.execute() → checkout → event listener → current_user → load_user → ... recursión infinita. SQLAlchemy 2.0 aborta con isce.

Solución: Eliminar el acceso a current_user del event listener. Leer el tenant SOLO desde flask.session.

Bitácora:

Versión	Cambio	Resultado
v1	Reducir queries en load_user	❌ No resolvió
v2	db.engine.connect() en load_user	❌ Peor: agotó el pool
v3	Cache con flask.g	❌ No resolvió
v4	Eliminar current_user del event listener	✅ RESUELTO
Efecto colateral positivo: DT-26 (latencia) se resolvió indirectamente.

Commit: a522e0c

1️⃣3️⃣ DT-20 — Bug sistémico del default=1 — Bitácora
Problema: 32 modelos tenían panaderia_id = db.Column(..., default=1). Si un INSERT olvidaba pasar panaderia_id, caía silenciosamente en tenant_1.

Fases y resultados:

Fase	Modelos	Commit	Notas
A (auditoría)	—	—	Identificados 4 INSERTs críticos
B (fix quirúrgico)	4 INSERTs	344c552	Agregado panaderia_id explícito
C - Tanda 1	27 (Grupo A)	45d011e	Modelos cuyos INSERTs ya pasaban panaderia_id
C - Tanda 2	2 (Categoria, Usuario)	14de608	Arreglados 2 INSERTs + endpoint huérfano eliminado
C - Tanda 3	2 (Panaderia, ConfiguracionPanaderia)	b111005	Arreglado INSERT ORM de app.py:1719
Resultado: 31 modelos sin default=1. Si un INSERT olvida pasar panaderia_id, falla con IntegrityError (fail-fast).

Lecciones aprendidas (regla 23):

Verificar TODOS los INSERTs antes de eliminar un default.

Los ORM DETACHED (que solo leen) cuentan como "OK".

Los INSERTs ORM dentro de models.py (métodos @classmethod) también hay que verificarlos.

1️⃣4️⃣ Notas estratégicas
Objetivo del ERP
ERP SaaS multi-tenant multi-país con: POS, inventario, producción, recetas, activos fijos, reportes con IA, finanzas, multi-país, base para API REST + IA avanzada.

🎁 Tenant Demo (marketing)
Fases 1-12 completadas (~10.100 filas). Contraseña: demo2026. Reset desde /mi_perfil con dev_master.

Mercado objetivo
3.000-5.000 panaderías en Colombia.

10.000-30.000 en LATAM.

Precio: $60k-$600k COP/mes.

Modelo de licencias
Premium: 3 usuarios (admin, supervisor, cajero).

Básica: 1 usuario (admin).

Los usuarios se crean al alta del tenant.

Estimación de tiempos (3 Oct 2026)
Bloque	Estimación
Fase C.3 (auditoría de columnas)	~4-6 h
DT-31 (ALTER TABLE tenant_id)	~1-2 h
Fase 3 (nube + Docker)	~22-32 h
Fase 4 (seguridad)	~14-20 h
Fase 5 (monetización)	~26-36 h
Fases 6-8 (IA + integraciones)	~50-85 h
TOTAL hasta Fase 8	~116-180 h
📞 Cómo continuar en un chat nuevo
Al iniciar un nuevo chat, pegar este archivo como contexto inicial.

Instrucción sugerida para el asistente:

"Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el archivo HANDOFF.md v7.4 con el contexto maestro del proyecto. Vamos a continuar desde donde lo dejamos. Por favor actúa como instructor guiando paso a paso, con la metodología de trabajo descrita en el HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/findstr, commit tras cada fix verificado. Al insertar bloques, muéstrame ANTES → DESPUÉS con número de línea exacto."

Próxima tarea sugerida: Fase C.3 (auditoría de columnas huérfanas en 22 tablas).

✅ Última validación
- **Último commit:** `b111005` (pusheado a GitHub).
- **Última sesión:** 3 Oct 2026 — 9 deudas resueltas.
- **Working tree:** clean.
- **Servidor:** detenido.
- **Sistema:** 100% funcional end-to-end.
- **Módulos:** 11/11 completados (100%).
- **Demo:** Fases 1-12 completadas, contraseña `demo2026`.
- **Log:** limpio, sin warnings.
- **DT-20:** ✅ **100% RESUELTO** (modelo + PostgreSQL).
- **Deudas críticas pendientes:** ninguna.

**Pendientes:** Fase C.3, DT-29, deudas medias varias.

**Fin del HANDOFF.md — v7.4.1**