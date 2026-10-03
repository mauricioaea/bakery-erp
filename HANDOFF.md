# 🗂️ CONTEXTO MAESTRO — PanaderíaPro (Bakery ERP)

**Última actualización:** 3 de Octubre, 2026
**Último commit:** a25505a (fix DT-6 + DT-9: default=1 eliminado)
**Sesión 2 Oct:** DT-11, DT-12, DT-13, DT-14, DT-16, DT-26, DT-27, DT-3, DT-4
**Sesión 3 Oct:** DT-6, DT-9

---

## 1️⃣ Información general

- **Nombre:** PanaderíaPro (bakery-erp)
- **Repo:** https://github.com/mauricioaea/bakery-erp
- **Estado:** v1.1.5 — **11/11 módulos completados (100%)** + Demo Fases 1-12 completadas + Endurecimiento de seguridad + Log limpio sin warnings + Código sin imports muertos + 2 deudas críticas de `default=1` resueltas
- **Arquitectura:** Multi-tenant con PostgreSQL (schemas por tenant)
- **Próximo hito:** DT-20 Fase C (eliminar los 30 `default=1` restantes)

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
- `reportes.py` (~3.250 líneas, ~160 KB) — generación PDF
- `seed_demo.py` (~450 líneas, ~18 KB) — seed modular del Demo
- `seeds/` — 11 fases del seed (fase1 a fase11)
- `middleware_saas.py`, `tenant_decorators.py`, `tenant_context.py` — multi-tenant
- `templates/`, `static/`
- `.env` — variables de entorno (credenciales BD, SECRET_KEY)
- `.env.example` — plantilla documentada
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
a25505a fix(DT-6, DT-9): eliminar default=1 de panaderia_id en PagoIndividual y Proveedor
11662f5 docs: HANDOFF v7.1 - DT-3 + DT-4 resueltas, regla 20 (findstr /c:), balance del día 9 deudas
71f6ae1 fix(DT-3, DT-4): eliminar import muerto Response y 4 reimports redundantes de func en reportes.py
8bda650 docs: HANDOFF v7 - 7 deudas resueltas (DT-11 a DT-27), estimaciones Fases 3-8, reglas 17-19
cafc325 fix(DT-14): leer SECRET_KEY desde .env en lugar de hardcodearla
301bd65 docs(DT-13): agregar .env.example con variables requeridas documentadas
ffd8e8f fix(DT-16): no imprimir password de BD en log de login - sanitizar URI
6e260b1 fix(DT-12): verificar current_user de forma segura en _obtener_nombre_empresa
1e4c120 fix(DT-27): reemplazar Query.get() por db.session.get() en login
a2a2e71 docs: HANDOFF v6 - DT-11 resuelto
cbcb76b chore: limpiar .gitignore
a522e0c fix(DT-11): eliminar acceso a current_user en event listener de checkout

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

**Total aproximado:** ~10.100 filas en tenant_27.

---

## 8️⃣ Configuración crítica

### Variables de entorno (.env)
DATABASE_URL=postgresql://postgres:...@localhost:5433/panaderia_master
DB_PASSWORD=...
FLASK_ENV=development
SECRET_KEY=...

text

- `.env` está en `.gitignore` (protegido).
- `.env.example` está en el repo (documenta las variables).
- `load_dotenv()` se llama al inicio de `app.py` (línea ~1258).
- `app.py` y `seed_demo.py` usan `os.getenv()` para credenciales.
- **SECRET_KEY** se lee del `.env` (fix DT-14).
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

- **~30 modelos** todavía tienen `panaderia_id = db.Column(..., default=1)`.
- **Fase A (auditoría):** completada.
- **Fase B (fix quirúrgico):** completada — 4 INSERTs corregidos (commit `344c552`).
- **Fixes puntuales:** DT-6 (`PagoIndividual`) y DT-9 (`Proveedor`) — commit `a25505a`.
- **Fase C (eliminar ~30 defaults restantes):** pendiente.

---

## 9️⃣ Deuda técnica acumulada

### ✅ RESUELTAS el 3 de Octubre 2026

| # | Descripción | Commit |
|---|-------------|--------|
| DT-6 | `PagoIndividual.panaderia_id default=1` | `a25505a` |
| DT-9 | `Proveedor.panaderia_id default=1` | `a25505a` |

### ✅ RESUELTAS el 2 de Octubre 2026 (11 deudas)

| # | Descripción | Commit |
|---|-------------|--------|
| DT-3 | Import muerto `Response` en reportes.py | `71f6ae1` |
| DT-4 | 4 reimports redundantes de `func` en reportes.py | `71f6ae1` |
| DT-11 | Event listener `checkout` sin `current_user` (rompe recursión con `load_user`) | `a522e0c` |
| DT-12 | `_obtener_nombre_empresa` verifica `current_user` seguro | `6e260b1` |
| DT-13 | `.env.example` con variables documentadas | `301bd65` |
| DT-14 | `SECRET_KEY` leída del `.env` (no hardcodeada) | `cafc325` |
| DT-16 | Password de BD ya no se imprime en log de login | `ffd8e8f` |
| DT-26 | Latencia ~3s — **resuelta indirectamente por DT-11** | — |
| DT-27 | `Query.get()` reemplazado por `db.session.get()` | `1e4c120` |

### ✅ RESUELTAS anteriormente

- D1, DT-2, DT-2b, DT-20 Fase A, DT-20 Fase B, B3, B4 v2, B7.

### 🔴 Críticas pendientes

| # | Ubicación | Descripción |
|---|-----------|-------------|
| DT-20 | `models.py` (~30 modelos) | Bug sistémico `panaderia_id default=1` (Fase C pendiente) |

### 🟡 Medias pendientes

| # | Ubicación | Descripción |
|---|-----------|-------------|
| DT-1 | `reportes.py:48-68` | `_obtener_nombre_empresa` doble filtro tenant_id/panaderia_id |
| DT-5 | `models.py:1055 vs 2441` | `Gasto` vs `RegistroFinanciero` posible solapamiento |
| DT-7 | `models.py:2075 vs 2124` | Inconsistencia `nullable` entre modelos hermanos |
| DT-15 | `.env` | Password PostgreSQL embebida en `DATABASE_URL` |
| DT-17 | `reportes.py` | Reporte de tesorería muestra `$0` de ingresos |
| DT-18 | `reportes.py` | Reporte de tesorería no tiene nivel contable profesional |
| DT-19 | global | CSRF fix completo con `flask-wtf` (mitigación actual usa Origin; cobertura 99%) |
| DT-21 | POS | Modal de crear cliente sin botón visible |
| DT-25 | `app.py:1744` | Verificar orden real de ejecución de `before_request` vs `login_required` |
| DT-28 | `POST /` | Doble submit detectado (mitigado, no crítico) |

### 🟢 Bajas pendientes

| # | Ubicación | Descripción |
|---|-----------|-------------|
| DT-10 | `app.py:9022-9495` | Exports PDF no agrupados bajo comentario separador |
| DT-22 | `/configuracion/facturacion` | Permite modificar NIT del tenant sin confirmación |
| DT-23 | `models.py` | Ver DT-20 (Fase C) |
| DT-24 | `mi_perfil.html` | Frontend no muestra el campo `exitoso` del último reset |

### 🚨 Otras deudas
- **22 tablas con columnas huérfanas (79 columnas).** Fase C.3 planificada.
- **`public` con 40 tablas duplicadas.** Residuo de migración SQLite → PostgreSQL.

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
15. **Al pedir un test, incluir TODAS las verificaciones previas necesarias en el mismo mensaje.**
16. **Cuando el punto de inserción esté justo debajo de un decorador, incluir el decorador en el ANTES → DESPUÉS.**
17. **Antes de proponer un fix de concurrencia, medir impacto en el pool de SQLAlchemy.**
18. **Nunca usar `echo texto >> archivo` en Windows para modificar archivos de texto. Usar Notepad o PowerShell.**
19. **Nunca acceder a `current_user` desde event listeners de SQLAlchemy (`checkout`, `connect`). Causa recursión con `load_user`. Usar `flask.session` o `flask.g`.**
20. **En Windows, `findstr "patrón"` sin `/c:` hace búsqueda con wildcards y a veces no encuentra coincidencias literales. Usar siempre `findstr /c:"patrón"` para búsquedas literales.**
21. **Antes de aplicar un fix según el HANDOFF, verificar el estado actual del archivo. El HANDOFF puede estar desactualizado — el código es la fuente de verdad.**

### Comandos útiles

**Encoding en CMD:**
```cmd
chcp 65001
Modo interactivo psql:

cmd
psql -U postgres -p 5433 -h localhost -d panaderia_master
Dentro: SET client_encoding TO 'UTF8';
Salir: \q
Ver estructura de una tabla:

cmd
psql -U postgres -p 5433 -h localhost -d panaderia_master -c "\d tenant_27.nombre_tabla"
Seed Demo:

cmd
python seed_demo.py --list
python seed_demo.py --tenant=27 --status
python seed_demo.py --tenant=27 --fase=all
python seed_demo.py --tenant=27 --reset-all
Compilar / Servidor:

cmd
python -m py_compile app.py
python app.py
Generar SECRET_KEY nueva:

cmd
python -c "import secrets; print(secrets.token_hex(32))"
Búsquedas literales con findstr:

cmd
findstr /n /c:"patrón exacto" archivo.py
1️⃣1️⃣ Roadmap
text
✅ Fase 1: Módulos 1-10
✅ Fase 2: Módulo 11 Reportes (100%)
✅ Fase D2: exportación PDF
✅ Fase Demo: Tenant Demo (Fases 1-12)
✅ Fase Admin: Banner Demo + Panel Super Admin

✅ D1: Password PostgreSQL a env vars
✅ DT-2 + DT-2b: Métodos duplicados + indentación
✅ DT-20 Fase A + B: Multi-tenant INSERTs
✅ B3: Lock atómico
✅ B4 v2: Estado persistente reset
✅ B7: CSRF global

--- Sesión 2 Oct 2026 ---
✅ DT-3 + DT-4: Imports muertos y redundantes
✅ DT-11: Event listener sin current_user
✅ DT-12: _obtener_nombre_empresa seguro
✅ DT-13: .env.example
✅ DT-14: SECRET_KEY desde .env
✅ DT-16: Password BD oculta en log
✅ DT-26: Latencia resuelta indirectamente
✅ DT-27: Query.get() → db.session.get()

--- Sesión 3 Oct 2026 ---
✅ DT-6: PagoIndividual.panaderia_id default=1 eliminado
✅ DT-9: Proveedor.panaderia_id default=1 eliminado

⏳ DT-20 Fase C: eliminar ~30 defaults restantes (CRÍTICO)
⏳ Fase C.3: auditoría de columnas (22 tablas)
⏳ DT-17, DT-18: Reportes tesorería nivel contable
⏳ DT-19: CSRF completo con flask-wtf
⏳ DT-1, DT-5, DT-7, DT-21, DT-25, DT-28: Deudas medias varias
⏳ DT-10, DT-22, DT-24: Deudas bajas

⏳ Fase 3: Dockerización + subdominios + nube
⏳ Fase 4: HTTPS/SSL + rate limiting + logging + monitoreo + caché
⏳ Fase 5: Pasarela de pagos + portal autogestión + facturación
⏳ Fase 6: Chat IA
⏳ Fase 7: Junta Directiva IA
⏳ Fase 8: Integraciones estratégicas (API REST, webhooks)
1️⃣2️⃣ DT-11 — Resuelto (2 Oct 2026) — Bitácora
Causa raíz: El event listener checkout (app.py:1322-1380) accedía a current_user (Flask-Login) para determinar el tenant. current_user es un LocalProxy que dispara load_user al primer acceso. load_user hace db.session.execute() → checkout → event listener → current_user → load_user → ... recursión infinita. SQLAlchemy 2.0 detecta la reentrada y aborta con isce.

Solución: Eliminar el acceso a current_user del event listener. Leer el tenant SOLO desde flask.session.

Bitácora de intentos fallidos:

Versión	Cambio	Resultado
v1	Reducir queries en load_user (3→1)	❌ No resolvió — era concurrencia, no cantidad
v2	Usar db.engine.connect() en load_user	❌ Peor — agotó el pool
v3	Cache con flask.g en load_user	❌ No resolvió — el cache no estaba listo a tiempo
v4	Eliminar current_user del event listener	✅ RESUELTO
Efecto colateral positivo: DT-26 (latencia ~3s) se resolvió indirectamente. La latencia era causada por los reintentos fallidos de load_user.

Commit: a522e0c

1️⃣3️⃣ Notas estratégicas
Objetivo del ERP
ERP SaaS multi-tenant multi-país con: POS, inventario, producción, recetas, activos fijos, reportes con IA, finanzas, multi-país, base para API REST + IA avanzada.

🎁 Tenant Demo (marketing)
Fases 1-12 completadas (~10.100 filas). Contraseña: demo2026. Reset desde /mi_perfil con dev_master.

Mercado objetivo
3.000-5.000 panaderías en Colombia.

10.000-30.000 en LATAM.

Precio sugerido: $60k-$600k COP/mes.

Estimación de tiempos (3 Oct 2026)
Bloque	Estimación
DT-20 Fase C	3-4 h
Fase C.3	4-6 h
Fase 3 (nube + Docker)	~22-32 h
Fase 4 (seguridad)	~14-20 h
Fase 5 (monetización)	~26-36 h
Fases 6-8 (IA + integraciones)	~50-85 h
TOTAL hasta Fase 8	~120-180 h
📞 Cómo continuar en un chat nuevo
Al iniciar un nuevo chat, pegar este archivo como contexto inicial.

Instrucción sugerida para el asistente:

"Soy Mauricio, desarrollador de PanaderíaPro (Bakery ERP). Adjunto el archivo HANDOFF.md v7.2 con el contexto maestro del proyecto. Vamos a continuar desde donde lo dejamos. Por favor actúa como instructor guiando paso a paso, con la metodología de trabajo descrita en el HANDOFF: un paso a la vez, diagnóstico antes de modificar, soluciones de raíz, verificación con psql/findstr, commit tras cada fix verificado. Al insertar bloques, muéstrame ANTES → DESPUÉS con número de línea exacto."

Próxima tarea sugerida: DT-20 Fase C (eliminar los ~30 default=1 restantes en models.py).

✅ Última validación
Último commit: a25505a (pusheado a GitHub).

Última sesión: 3 Oct 2026 — DT-6 + DT-9 resueltos.

Working tree: clean.

Servidor: detenido.

Sistema: 100% funcional end-to-end.

Módulos: 11/11 completados (100%).

Demo: Fases 1-12 completadas, contraseña demo2026.

Log: limpio, sin warnings (11 deudas resueltas en 2 días).

PDF generation: probado.

Pendientes críticos: DT-20 Fase C, Fase C.3.

Fin del HANDOFF.md — v7.2