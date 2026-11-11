# 📓 BITÁCORA — Noviembre 2026 (PanaderíaPro)

> **Append-only.** Cada sesión nueva se agrega al FINAL de este archivo. No se reescribe lo anterior.
> Estado actual del proyecto: `HANDOFF.md`. Octubre: `bitacora/2026-10-sesiones.md`. Histórico completo previo: `HANDOFF_v9.5.md`.

---

## Sesión 1 Nov 2026 (mañana) — Fix de raíz: `current_user` detached (CRÍTICA-3)

**Commit:** `6173cfe` (pusheado a `origin/main`)

### Diagnóstico
- `load_user()` (app.py:1490) construía `Usuario()` manualmente sin `db.session.add()`, dejando `current_user` **detached**.
- Por eso `current_user.set_password()` + `db.session.commit()` en `/mi_perfil` no persistía.
- El parche anterior (SQL directo `UPDATE {schema}.usuarios SET password_hash = ...`) era síntoma, no raíz.

### Auditoría previa al fix
- `grep current_user\.` en app.py → solo `mi_perfil` modifica `current_user` (4 escrituras intencionales).
- Cero `before_request` / `teardown_request` lo modifican → sin riesgo de persistencia accidental al cambiar el patrón.

### Fix aplicado
- `db.session.merge(user)` en los 2 branches de `load_user`: tenant (L~1546) + public fallback (L~1572).
- `mi_perfil` revertido a `current_user.set_password()` + `commit()` (ORM puro, sin SQL directo).

### Test de regresión: 6/6 tests (37/37 verificaciones OK)

| Test | Alcance | Resultado |
|---|---|---|
| 1 | Cambio de contraseña en `/mi_perfil` | 7/7 |
| 2 | Cambio nombre/email/teléfono en `/mi_perfil` (verificado con `octet_length` y `hex` que la `í` está bien en UTF-8: `c3ad`) | 6/6 |
| 3 | No-regresión `/editar_usuario` | 4/4 |
| 4 | No-regresión `/resetear_password` | 7/7 |
| 5 | Smoke test de navegación: dashboard + POS + producción + recetas + reportes + baja_inventario | 7/7 |
| 6 | Restaurar `admin_27` a `demo2026` + limpiar nombre | 6/6 |

### Demo restaurado
`admin_27` / `demo2026`, nombre `Administrador Panadería Demo` (sin espacio final).

### ✅ RESUELTAS el 1 Noviembre 2026 — Fix de raíz `current_user` detached

| # | Descripción | Commit |
|---|-------------|--------|
| Bug CRÍTICA-3 | `load_user()` construía `Usuario()` detached. `db.session.commit()` no persistía cambios en `current_user`. Fix de raíz: `db.session.merge(user)` en los 2 branches de `load_user` (tenant + public). | `6173cfe` |
| Parche revertido | `mi_perfil`: eliminado el `UPDATE {schema}.usuarios SET password_hash = ...` del parche anterior. Vuelve a `current_user.set_password()` + `commit()` (ORM puro). | `6173cfe` |
| Auditoría | Solo `mi_perfil` modifica `current_user` (4 escrituras intencionales). Cero `before_request`/`teardown_request` lo modifican. | `6173cfe` |
| Test de regresión | 6/6 tests (37/37 verificaciones). | `6173cfe` |

### Hallazgos nuevos (anotados, NO tocados)
1. **`DT-nueva-MEDIA-logging-ruido`** — logging ruidoso en POS (20-30 líneas INFO por request). ~1-2 h, Fase D.
2. **Nota:** `resetear_password` (app.py:11981) usa `pbkdf2:sha256` explícito; `set_password` (models.py:48) usa scrypt por default. No unificar sin auditoría.
3. **Nota:** `app.py:13197` (`/api/productos_vitrina`) usa `Receta.query.get(...)` legacy → `LegacyAPIWarning`. Migrar a `db.session.get(Receta, ...)` en Fase D.

### Reestructuración de la documentación
- `HANDOFF.md` pasa a v9.6 (liviano, contexto actual).
- `HANDOFF_v9.5.md` queda como histórico congelado en la raíz.
- Se crea `bitacora/` (append-only por mes). La sesión terminó antes de crear los archivos; se crearon en la sesión siguiente.

### Estado al cierre
- Último commit: `6173cfe`. Próxima tarea: **CRÍTICA-1** (depósitos conciliados editables).

---

## Sesión 1 Nov 2026 (noche) — DT-nueva-CRÍTICA-1: depósitos CONCILIADOS inmutables

**Commit:** `5d289fd` (se asigna al commitear)

### Contexto
CRÍTICA-1 era la siguiente tarea tras el fix de `current_user` detached (`6173cfe`). Bug: el botón "Ver" de un depósito con `estado='CONCILIADO'` abría el **mismo modal editable** que "Editar", y el backend `editar_deposito_bancario()` **no validaba el estado**. Un `POST` directo (curl/Postman) permitía modificar monto/fecha/referencia de un depósito ya conciliado — vulnerabilidad contable.

### Diagnóstico
- **Frontend (`gestion_financiera.html:828`):** el botón "Ver" llamaba `abrirModalDeposito('editar', id)` — mismo flujo que Editar. `abrirModalDeposito()` (L895-927) no distinguía estado.
- **Backend (`app.py:10333-10374`):** `editar_deposito_bancario()` sin guard de estado. Confirmado con `findstr`: 0 referencias a `CONCILIADO` en esa función.
- **Contraste:** `eliminar_deposito_bancario()` (L10410) **sí** validaba (`if deposito.estado != 'REGISTRADO': return 400`). El patrón existía pero no se había aplicado a `editar`.
- **Bug preexistente detectado:** `from datetime import date` local en L10352 (dentro del `if 'fecha_deposito'`, con las líneas que usan `date` fuera del `if`) → `NameError` latente si el POST no traía `fecha_deposito`. Redundante porque `date` ya está importado a nivel módulo en `app.py:1244`.

### Decisión de diseño (regla #9)
**Opción A (estricta, contable):** `CONCILIADO` es **inmutable**. Para desconciliar se requerirá un endpoint dedicado con auditoría (queda como DT-nueva para Fase D). El modal "Ver" se vuelve **solo lectura** y el backend **rechaza con 403**. Aprobado por Mauricio.

### Fix aplicado (de raíz, 3 bloques)

**BLOQUE 1 — `app.py` `editar_deposito_bancario()`:**
- Early-return `403` si `deposito.estado == 'CONCILIADO'` + `logger.warning` con `current_user.username` (trazabilidad de intentos).
- Eliminado `from datetime import date` local (redundante, L10352).
- Reindentadas 5 líneas (`fecha_deposito`, `hoy`, `if fecha_deposito > hoy:`, `return jsonify(...)`) dentro del `if 'fecha_deposito' in data:`.

**BLOQUE 2 — `gestion_financiera.html` `abrirModalDeposito()` + helper:**
- Nueva función `setModalModoLectura(soloLectura)`: deshabilita los 8 campos (`fechaDeposito`, `montoDeposito`, `descripcionDeposito`, `bancoDeposito`, `referenciaDeposito`, `cuentaDeposito`, `metodoDeposito`, `estadoDeposito`) y oculta `btnGuardarDeposito`.
- En `accion === 'editar' || accion === 'ver'`: si `d.estado === 'CONCILIADO'` → `setModalModoLectura(true)` + título "Ver Depósito (Conciliado — solo lectura)".
- En `accion === 'crear'`: `setModalModoLectura(false)` (reset a editable, no-regresión).

**BLOQUE 3 — `gestion_financiera.html` `renderizarDepositos()`:**
- El botón del CONCILIADO pasa `abrirModalDeposito('ver', ...)` (semánticamente correcto) y clase `btn-secondary` (gris = solo lectura). Sin Conciliar/Editar/Eliminar.

### Tests de regresión (7/7)

| Test | Resultado |
|---|---|
| 1 — Fila CONCILIADO solo "Ver" gris | ✅ |
| 2 — Modal "Ver" solo lectura, sin Guardar | ✅ |
| 3 — No-regresión REGISTRADO editable + guarda | ✅ (`POST /editar/20` 200, monto 40→41 persistido) |
| 4 — No-regresión "Nuevo" resetea modo lectura | ✅ (creó #22, borrado después) |
| 5 — Backend 403 (bypass frontend con `fetch` desde Console) | ✅ `ANTES: 5000 CONCILIADO` → `STATUS: 403` → `DESPUÉS: 5000 CONCILIADO` (monto no cambió) |
| 6 — Log del bloqueo | ✅ `logs\panaderia.log:18779: [2026-11-01 23:17:14] WARNING [panaderia] ⛔ Intento de editar depósito CONCILIADO id=21 por usuario=admin_27 — bloqueado.` |
| 7 — Lista y estadísticas sin regresión | ✅ |

### Verificación de comandos pre-smoke
- `findstr` con tildes falló (falso negativo, regla #10) → resuelto con `powershell Select-String` (respeta UTF-8).
- `git diff --stat`: `app.py 25 +/-`, `templates/gestion_financiera.html 29 +/-` (coincide con diseño).
- `py_compile`: silencio.
- Diff HTML revisado línea a línea: 4 hunks exactos, helper bien cerrado (3 llaves OK).

### Limpieza de demo
- Depósito #22 (creado en Test 4, monto=10) → `DELETE` aplicado. Tenant_27 queda: #21 CONCILIADO, #20 REGISTRADO (monto=41 por Test 3, dato legítimo de demo), #19 REGISTRADO.

### ✅ RESUELTAS el 1 Noviembre 2026 (noche) — CRÍTICA-1 depósitos CONCILIADOS

| # | Descripción | Commit |
|---|-------------|--------|
| Bug CRÍTICA-1 | `editar_deposito_bancario()` sin validación de estado → early-return 403 + `logger.warning` con usuario | `5d289fd` |
| Fix preexistente | `from datetime import date` local redundante + mal indentado en `editar_deposito_bancario()` (bug latente `NameError`) | `5d289fd` |
| Feature frontend | `setModalModoLectura()` + botón "Ver" del CONCILIADO como solo-lectura (`btn-secondary`, sin Guardar) | `5d289fd` |
| QA | Smoke test 7/7 (UI + backend 403 + log + no-regresión) | — |

### Hallazgos nuevos (anotados, NO tocados — Fase D)
1. **DT-nueva-MEDIA (desconciliación):** `CONCILIADO` es inmutable por este fix, pero **no existe endpoint para desconciliar**. Si en el futuro se requiere, agregar `POST /depositos_bancarios/desconciliar/<id>` con auditoría (usuario, motivo, fecha). Por ahora: no hay flujo.
2. **DT-nueva-MEDIA (estado `ANULADO` sin flujo):** el modal de edición permite setear `estado='ANULADO'` directamente (select en `gestion_financiera.html:690-694`), sin endpoint dedicado ni auditoría. Revisar si `ANULADO` debe existir en el select o manejarse como `conciliar` (endpoint dedicado). **No afecta CRÍTICA-1** (nuestro guard bloquea CONCILIADO, pero ANULADO sigue siendo editable → se puede "revertir" un ANULADO a REGISTRADO sin control). Anotar para Fase D.
3. **DT-nueva-MEDIA (whitelist `estado` backend):** `editar_deposito_bancario()` acepta `data['estado']` sin validar contra `{'REGISTRADO', 'CONCILIADO', 'ANULADO'}`. Persistiría cualquier string. No explota visualmente pero es un hueco. Anotar para Fase D (mismo commit que el punto 2).

### Estado al cierre
- Último commit: `5d289fd`. Próxima tarea: **DT-nueva-MEDIA-ALTA** (donaciones suman en "Ingresos" del reporte Análisis Productos).

---

## Sesión 3 Nov — Fix MEDIA-ALTA + auditoría de cadena financiera

**Objetivo:** Cerrar DT-nueva-MEDIA-ALTA (donaciones sumaban en "Ingresos" del reporte Análisis Productos).

### Diagnóstico
- Bug detectado en 3 endpoints: `reporte_ventas`, `reporte_productos_populares`, `reporte_ventas_avanzado`.
- Las queries de `DetalleVenta.join(Venta)` NO filtraban `es_donacion == False` ni `estado == 'COMPLETADA'`.
- Auditoría extendida reveló 11 bugs adicionales en cadena financiera (cierre diario, tendencia, proyección, comparativas, alertas, análisis de rotación).

### Fix aplicado (15 bloques)
**app.py:**
- 7714 cierre diario: filtra donaciones de totales
- 7963 comparativa día anterior: agrega `estado`
- 8296 call site `calcular_tendencia_ventas`
- 8298 + 8386 + 8748 reportes de ventas (fix original MEDIA-ALTA)
- 8385 `fecha_fin_inclusive` + 8393, 8432, 8470 (`< fecha_fin_inclusive`)
- 8510 call site `calcular_proyeccion_ventas`
- 8731 call site `calcular_tendencia_ventas`
- 8926 `obtener_ventas_del_dia`: 3 filtros

**models.py:**
- 1725 `calcular_tendencia_ventas`: firma extendida + 3 filtros
- 1799 `calcular_rotacion_automatica`: 3 filtros
- 1877 `calcular_proyeccion_ventas`: firma extendida + 3 filtros
- 2080 `obtener_productos_sin_ventas_recientes`: + 2 filtros

**reportes.py:**
- 1516 `_obtener_datos_tendencia_ventas`: + `es_donacion`

**templates:**
- `ventas_periodo.html`: nueva columna "Donaciones"
- `productos_populares.html`: nueva columna "Donaciones"

### Test (validado con PDFs)
- Inyectadas 1 venta donación ($4,500) + 1 venta normal ($3,000) en tenant_27.
- **Historial de Ventas:** Total $3,000 (no $7,500). ✅
- **Productos Populares:** 2 transacciones donación, 2 productos. Fila "almojábanas 2" con `(3)` en Donaciones, ingresos $3,000. ✅
- **Reporte Avanzado + IA:** TOTAL VENTAS $3,000, DONACIONES 1. ✅
- **Análisis Predictivo:** muestra donaciones correctamente. ✅
- **Tendencia de Ventas:** carga OK. ✅

### DTs nuevas detectadas
- `DT-nueva-BAJA`: endpoint huérfano `reporte_ventas_periodo` vs `reporte_ventas`.
- `DT-nueva-MEDIA-BAJA`: `cerrar_jornada_ventas` (models.py:2166) sin filtros — verificar por diseño.

### DTs cerradas
- ✅ `DT-nueva-MEDIA-ALTA` (donaciones en "Ingresos").
- ✅ `DT-nueva-MEDIA (fecha_fin a medianoche)` — se aplicó `fecha_fin_inclusive` en `reporte_productos_populares`.

### Notas
- Backup: `backup_pre_donaciones_test.backup` (por si acaso).
- 4 archivos de código modificados: `app.py`, `models.py`, `reportes.py`, + 2 templates.
- Commit `8304a16` pusheado a `origin/main`.

---

## Sesión 4 Nov — Fix MEDIA-BAJA (Ventas del Día no distingue donaciones)

**Objetivo:** Cerrar DT-S31-ventas-donacion (una venta con `es_donacion=TRUE` aparecía como "Completada" con Total $0, sin badge distintivo).

### Decisión de diseño — Opción D

En lugar de la opción A del HANDOFF (deshabilitar "Anular" para donaciones), se decidió implementar **Opción D (más profesional):**

- Permitir anular donaciones **solo a `admin_cliente` y `super_admin`** (cajero/supervisor → 403).
- Badge distintivo en columna Estado.
- Aviso en el modal de anulación.
- Motivo `donacion_por_error` en el select.
- Trazabilidad completa (motivo + observación + usuario + fecha).

**Razón:** la opción A dejaba al usuario atrapado si el cajero registraba una donación por error. La opción D permite corregir con salvaguardas.

### Cambios aplicados

**Backend (`app.py:3358`):**
- Guard de rol en `anular_venta(venta_id)`:

```python
if venta.es_donacion:
    rol = (current_user.rol or '').strip().lower()
    if rol not in ('admin_cliente', 'super_admin'):
        return jsonify({'success': False, 'error': 'Solo un administrador...'}), 403
Template (ventas_del_dia.html):

Columna Estado: prioridad ANULADA > es_donacion > COMPLETADA.

Anulada → badge rojo + motivo + observación.

Donación activa → badge azul + tooltip motivo.

Completada → badge verde.

Columna Total: prioridad ANULADA > es_donacion > normal.

Anulada → $0 tachado gris.

Donación → $0 azul info.

Normal → $X normal.

Columna Acciones: botón naranja "Anular donación" si es_donacion, rojo "Anular" si normal, gris "Procesada" si anulada.

Modal: aviso amarillo warning si es_donacion (condicional, vía JS).

Select motivo: agregado donacion_por_error.

JS abrirModalAnulacion: recibe esDonacion como 3er parámetro.

Test validado
Donación activa: badge azul + botón naranja. ✅

Cajero intenta anular: 403 Forbidden + mensaje claro. ✅

Admin anula: 200 OK + stock revertido. ✅

Donación anulada: badge rojo "Anulada" + motivo + total tachado. ✅

Ventas normales (regresión): badge verde "Completada" + botón rojo "Anular". ✅

Bugs colaterales encontrados
Doble servidor: 2 instancias de python app.py causaron cache confuso del navegador y diagnóstico erróneo. Regla nueva HANDOFF: verificar tasklist | findstr python antes de reiniciar.

_test_jinja.py: recibe solo nombre de archivo, no ruta completa (ventas_del_dia.html, no templates/ventas_del_dia.html).

DTs cerradas
✅ DT-S31-ventas-donacion (Ventas del Día no distingue donaciones).

DTs nuevas
Ninguna. La nota sobre el recibo (recibo_pos.html no distingue donaciones) es informativa, sin acción — no se registra como DT.

Commit
607ac75 feat(ventas-del-dia): distinguir donaciones con badge, tooltip y guard de rol.

Sesión 5 Nov — Fix CRÍTICA-4 + Bug B (rotación) + IA KeyError
Commit: 6e7dbbf (pusheado a origin/main)

Contexto
Retomando la DT MEDIA-BAJA del HANDOFF v9.9 ("Productos Populares vacío en tenant nuevo"), el diagnóstico reveló 3 bugs encadenados que ameritaban un commit conjunto. La investigación tomó ~10 h (creación de tenant de prueba, reproducción de bugs, validación con PDFs antes/después).

Tenant de pruebas: tenant_31 (SE CONSERVA)
Creación: 4 Nov 2026, vía frontend con dev_master. Contraseña rotada el 5 Nov, guardada localmente por el desarrollador (no commiteada).

Campo	Valor
id	31
nombre	Diagnóstico Productos Populares
subdominio	diagnóstico_producto
base_datos	tenant_diagnóstico_producto (≠ schema real tenant_31 — evidencia de CRÍTICA-2)
plan	basico (nube_basica)
Usuario admin	admin_31
Contraseña	⚠️ Rotada 2026-11-05. Guardada localmente (no commiteada).
Propósito	Tenant de pruebas para futuras sesiones. Reproduce "tenant nuevo + licencia básica + pocos datos".
Limitación	Licencia básica: sin acceso a /reporte/analisis_predictivo, /reporte/recomendaciones_ia, /reporte/analisis_inventarios. Redirige a dashboard (302).
Datos actuales	8 ventas (1 donación), 1 producto interno (Pan Prueba), 1 producto externo (Agua), 1 receta.
Uso previsto: validar comportamiento de <7 días en reportes (rotación —), restricciones de licencia básica, lógica multi-tenant.

Cómo eliminarlo (cuando ya no se necesite):

sql
DROP SCHEMA tenant_31 CASCADE;
DELETE FROM public.tenants WHERE id = 31;
Diagnóstico
CRÍTICA-4 (nueva): colisión de IDs internos/externos en reporte_productos_populares (app.py:8371). El dict analisis_productos usaba producto.id y producto_externo.id como claves, colisionando cuando ambos tienen id=1 (caso típico en tenant nuevo). Los externos se "fusionaban" con internos del mismo id, mostrando nombre/ingresos del interno.

Bug B (rotación <7d): calcular_rotacion_automatica_por_nombre devolvía total_vendido / 30.0, engañoso con 1 día de datos. Fix: dias_reales_tenant desde primera venta del tenant, None si < 7 días, template muestra —.

DT-BAJA-mensajes-IA: _generar_recomendaciones_ia (reportes.py:1942) usaba x['ingreso'] y producto_top['producto'] sobre dicts sin esas claves. Además, el bloque "Producto estrella" estaba mal indentado dentro del else de variabilidad (solo se ejecutaba con variabilidad baja). Resultado: KeyError intermitente → "error técnico".

Fixes aplicados
Commit 6e7dbbf (3 archivos, 40 insertions, 22 deletions):

app.py:8421, 8425: prefijo int_/ext_ en analisis_productos.

app.py:8464-8468: prefijo int_/ext_ en donaciones_por_producto.

app.py:8470-8480: dias_reales_tenant calculado desde Venta.query...order_by(fecha_hora.asc()).first(). Si < 7 días → rotacion_promedio = None.

templates/productos_populares.html:367, 425, 542, 569, 576: adaptaciones {% if ... is none %}—{% else %}...{% endif %}.

reportes.py:1978-1995: "Producto estrella" movido fuera del else de variabilidad, con claves nombre/ventas.

Tests validados
tenant_31 (período corto):

Top 10: Agua + Pan Prueba separados (fix CRÍTICA-4 ✅).

Rotación: — en Top 10, badge y baja rotación (fix Bug B ✅).

IA: "Se necesitan más datos históricos (mínimo 7 días)" (fix IA no rompe la lógica ✅).

tenant_27 (período largo 2026-07-01 a 2026-11-05):

Productos Populares: sin regresión.

IA: "Producto estrella: Pan de Yema con 1722 unidades vendidas" en PDF (fix IA ✅).

Sin "error técnico" en el PDF.

Bugs / hallazgos laterales
Bug A (descartado como CRÍTICA → nota): En el primer día de vida del tenant, detalle_venta.producto_externo_id quedó NULL en 2 ventas con externos. Tras reiniciar servidor, las filas se "corrigieron". No reproducible. Hipótesis: caché/ORM en primer arranque. Verificar en Fase E (tenant virgen).

CRÍTICA-2 reproducida en vivo: tenant_31.base_datos = tenant_diagnóstico_producto vs schema real tenant_31. tenant_27 ya mostraba la inconsistencia (tenant_panadería_demo vs tenant_27), pero era data legacy. tenant_31 la reproduce en runtime limpio. Evidencia empírica para el fix final de Fase D.

Caché del navegador: screenshots desactualizados confunden diagnóstico. Regla nueva: modo incógnito + reiniciar servidor + netstat (1 línea LISTENING) antes de cada test de template.

Mojibake en commit message: Windows usó cp1252 al escribir git commit -m. Recomendación: usar git commit -F _commit_msg.txt (UTF-8) en próximos commits.

_investigar_ia.py: script de diagnóstico, borrado al cierre (no commiteado).

Estado al cierre
Último commit: 6e7dbbf. Working tree clean.

tenant_31 se conserva vivo como tenant de pruebas (básico).

Próxima tarea: Commit 2 (rediseño "menos es más" + recomendaciones dinámicas en productos_populares.html).

text

---

## 📋 Resumen de acciones

| Archivo | Acción | Notas |
|---|---|---|
| `HANDOFF.md` | **Reemplazar completo** con el v9.10 que te di antes | Ya lo tenés del mensaje anterior |
| `bitacora/2026-11-sesiones.md` | **Reemplazar completo** con el bloque de arriba | Mantiene las 4 sesiones previas + agrega la 5 Nov |
| `bitacora/tenants_prueba.md` | **NO crear** (decisión tuya) | Todo va en la bitácora |

---
---

## Sesión 6 Nov — Commit 2 COMPLETO: rediseño "menos es más" + filtro por producto + i18n

**Commits:** `320881b` (B1+B2+H1+H2.1), `5d8e2b4` (H2.2), `b6a1908` (H2.3+H4), `e3b48e0` (H3), `7ff556f` (i18n)
**Pusheados a `origin/main`.** Working tree clean.

### Contexto

Sesión larga (un solo chat, varios días de trabajo fragmentado en horas). Objetivo: cerrar el Commit 2 pendiente del HANDOFF v9.10 (rediseño "menos es más" + recomendaciones dinámicas en `productos_populares.html`). Se extendió con un filtro `?producto=` en `/reporte/ventas` (necesario para el botón "Ver detalle" del Top 10) y con i18n completo (en + pap).

### Diagnóstico previo

Auditoría exhaustiva (script `_audit_commit2.py`, ya borrado) para verificar si algo ya existía en el código y evitar duplicación:
- `_obtener_datos_productos_populares` (reportes.py:1904) → lógica distinta (para PDF, sin externos, sin donaciones). **No reusar.** DT anotada para Fase F (unificar).
- `calcular_totales` (models.py:2299) → es de `RegistroDiario`, no aplica.
- `analizar_productos_periodo` (models.py:1763) → prefijos `P{id}`/`E{id}` (vs `int_`/`ext_` en `app.py`). Sin filtros de donaciones/anuladas. **No reusar.** DT anotada para Fase F.
- `_generar_recomendaciones_ia` (reportes.py:1942) → acoplada al PDF, riesgo de romper `6e7dbbf`. **No reusar.**
- `_generar_recomendaciones_productos` en `app.py` → **no existía**. Creada nueva.

### Bloque B1 — `_generar_recomendaciones_productos()` en `app.py`

- Nueva función (~65 líneas) insertada entre `reporte_productos_populares` y `@app.route('/reporte/analisis_predictivo')`.
- 5 reglas dinámicas + fallback `<7d` o `<3 productos`:
  1. Top 1 producto (estrella) → % de ingresos y unidades.
  2. Rotación saludable (>10/día) → cuántos productos.
  3. Rotación crítica (<5/día) → qué productos.
  4. Donaciones → # transacciones + valor de mercado.
  5. Cierre (análisis continuo) si ≥3 reglas.
- Devuelve `list[dict]` con `{tipo, icono, titulo, detalle}`. Máximo 6.
- Tests aislados: caso "rico" (3 productos, 30 días) → 5 recomendaciones; caso "fallback" (1 producto, 3 días) → 1 recomendación informativa.

### Bloque B2 — KPIs en `reporte_productos_populares()`

- Calcula `total_unidades`, `total_ingresos` (suma sobre TODOS los productos, no solo top 20).
- Inyecta 4 variables nuevas al `render_template`: `total_unidades`, `total_ingresos`, `dias_reales_tenant`, `recomendaciones`.

### Bloque H1 — Bloque 4 del template (recomendaciones dinámicas)

- Reemplaza el bloque de texto fijo (L593-620 original) por iteración sobre `recomendaciones`.
- Cada recomendación = `alert alert-{tipo}` con `d-flex` + icono + título + detalle.
- Fallback `{% else %}` si `recomendaciones` vacío.
- `_test_jinja.py`: OK.

### Bloque H2.1 — Filtro `?producto=` en `/reporte/ventas`

- **H2.1a:** `producto_filtro = request.args.get('producto')` + filtro en Python sobre `ventas_periodo` + inyección al template.
- **H2.1b:** banner azul "Filtrando por producto: X" + botón "Quitar filtro" en `ventas_periodo.html` (con `no-print`).
- **H2.1c:** filtro también aplicado a `detalles_periodo` y `donaciones_periodo` con `db.or_(DetalleVenta.producto.has(nombre=...), DetalleVenta.producto_externo.has(nombre=...))`. Sin esto, la tabla "Análisis de Productos" mostraba todos los productos aunque el filtro estuviera activo.
- Smoke test 5/5: sin filtro (regresión), con filtro a producto real, con filtro a producto inexistente, "Quitar filtro", regresión de H1.

### Bloque H2.2 — Top 10 único + botón "Ver detalle"

- Eliminadas las 10 cards grandes (duplicadas con la tabla).
- Tabla compacta (que era solo-PDF) promovida a visible en pantalla + PDF.
- Nueva columna "Acciones" con botón 🔍 por fila. Link a `/reporte/ventas?producto=<nombre>&fecha_inicio=<...>&fecha_fin=<...>` (el filtro de H2.1). Con `no-print` para que no aparezca en PDF.
- Badges de ranking: 🥇🥈🥉 para 1-3, número para el resto.
- Tipo completo ("Producción" / "Externo") en lugar de 1 letra.
- Nombre con `title` (tooltip) y truncado a 40 chars.
- **Ahorro: -45 líneas netas.**

### Bloque H2.3 + H4 — Top 5 eliminado + Distribución+Rotación lado a lado

- Eliminado el bloque "Top 5 por Ingresos" (redundante: los ingresos ya están en la columna del Top 10).
- Distribución por Tipo → `col-lg-4` (30%).
- Análisis de Rotación Automática → `col-lg-8` (70%).
- Ambos con `h-100` para igualar alturas.
- **JS del `ingresosChart` eliminado** (huérfano tras quitar el canvas).
- **Bug detectado en el fix:** quedó un `tipoCtx` duplicado + un bloque `type: 'bar'` huérfano. **Corregido:** eliminar el bloque fantasma y dejar solo el `tipoChart` (doughnut).
- **Ahorro: -70 líneas netas** (más JS huérfano eliminado).

### Bloque H3 — 4 KPI cards unificadas

- Eliminada la card grande "Información de Salidas No Comerciales" (redundante).
- 4 mini-cards: **Unidades vendidas** (border-primary) / **Ingresos totales** (border-success) / **Donaciones** (border-warning) / **Productos donados** (border-info).
- Consume `total_unidades` y `total_ingresos` (de B2).
- Banner IA movido a badge compacto debajo de las cards (sin card propia, con `{% if actualizaciones_ml %}`).
- **Ahorro: -15 líneas netas.**

### i18n completo (commit `7ff556f`)

- `pybabel extract -F babel.cfg -o locales/messages.pot app.py models.py reportes.py templates`.
- `pybabel update -i locales/messages.pot -d locales` (propaga a es/en/pap).
- `_limpiar_fuzzy.py` (limpia los `#, fuzzy` que marca el update).
- **13 strings traducidos en `en`** (incluye 4 del Commit 2 + 9 de deuda previa de toppings/bajas).
- **15 strings traducidos en `pap`** (incluye 4 del Commit 2 + 11 de deuda previa).
- `pybabel compile -d locales --statistics`: 0 untranslated reales (los 12-13 del `--statistics` eran headers/obsoletos, verificado con script de diagnóstico).
- **`es` queda al 0% (correcto):** es idioma base, los `msgid` ya están en español.

### Tests finales

- `py_compile app.py`: silencio.
- `_test_jinja.py productos_populares.html` y `ventas_periodo.html`: OK.
- Smoke test visual 6/6 en H2.2 y H3.
- Smoke test i18n: reporte generado en inglés OK (asumido OK en pap).
- `_ver_untraducciones.py`: 0 strings sin traducir en `en.po`.
- Script de diagnóstico de i18n: 0 strings sin traducir en `en.po` y `pap.po` (los 12-13 de `--statistics` eran falso positivo).
- Working tree clean.

### Deuda técnica anotada (NO tocada, para Fase F)

- Unificar `_obtener_datos_productos_populares` (reportes.py) con `reporte_productos_populares` (app.py).
- Unificar `analizar_productos_periodo` (models.py) con el inline de `app.py:8408-8434` (prefijos `P`/`E` vs `int_`/`ext_`, filtros de donaciones).
- **Detalle menor preexistente:** el formato `$20.000.00` (punto como separador de miles + punto decimal) es incorrecto para `es-CO` (debería ser `$20.000,00`). Cosmético, no bloquea.

### Estado al cierre

- **Commit 2 100% cerrado.** 5 commits pusheados (`320881b`, `5d8e2b4`, `b6a1908`, `e3b48e0`, `7ff556f`).
- **Working tree clean.**
- **Cero DT pendiente del Commit 2.**
- **Próxima tarea del HANDOFF:** seguir con Fase D — **MEDIA (logging ruidoso)**, después **MEDIA (desconciliación + ANULADO + whitelist)**, después **BAJA (endpoint huérfano)**, después **MEDIA-BAJA (cierre jornada)**, y **al final CRÍTICA-2** (renombrar schemas).
## Sesión 7 Nov — DT-nueva-MEDIA-logging-ruido (Fases 1 y 1.5)

**Objetivo:** Atacar el ruido en terminal/logs (DT-nueva-MEDIA-logging-ruido).
**Commits:** `51000fc` (F1) + `68f8856` (F1.5). Pusheados a `origin/main`.

### Diagnóstico inicial (evidencia empírica)
- El HANDOFF estimaba "20-30 líneas INFO/request". La realidad medida: **~41 líneas INFO** por request a `/buscar_producto` (con 20 productos).
- El log `panaderia.log` estaba dominado por `INFO` (diagnósticos por producto) y `DEBUG`.
- **Hallazgo colateral (seguridad):** el log imprime el hash de contraseña completo en login (`app.py:2184` y `12351`).
- **Hallazgo colateral (archivos omitidos):** el módulo `utilidades/consultas_filtradas.py` (84 líneas) tenía **10 `print()`** que se ejecutaban en cada request del POS. El inventario previo del HANDOFF solo cubría `app.py`, `models.py` y `reportes.py`.

### Fase 1 — `buscar_producto` (commit `51000fc`)
- **Archivo:** `app.py` (L~2503-2564).
- **Cambio:** 9 `logger.info` → `logger.debug`.
- **Qué se dejó igual:** `logger.error` del `except`, `traceback.print_exc()`, la lógica de negocio, los headers de `logger.debug` preexistentes.
- **Validación:** `py_compile` OK. Diff exacto: 10 inserciones, 10 borrados.
- **Impacto:** ~41 líneas INFO/request → 0 en producción.

### Fase 1.5 — `consultas_filtradas.py` (commit `68f8856`)
- **Archivo:** `utilidades/consultas_filtradas.py`.
- **Cambio:** 
  - Agregado `import logging` + `logger = logging.getLogger('panaderia')`.
  - 7 `print(f"🔍 ...")` de diagnóstico → `logger.debug()`.
  - 3 `print(f"❌ ...")` de error → `logger.error()`.
- **Validación:** `py_compile` OK. `findstr "print("` → 0. Diff exacto: 14 inserciones, 10 borrados. Cero cambios en lógica de negocio.
- **Smoke test 5/5:** POS funcional, cero `print` crudos en terminal (todo con prefijo `[timestamp] DEBUG [panaderia]`), cero `logger.debug` en `logs/panaderia.log`.

### Hallazgos nuevos (anotados, NO tocados)
1. **DT-nueva-MEDIA-2.5 (logging nivel configurable):** En dev (`debug=True`), Flask fuerza el nivel del logger a DEBUG, mostrando todos los `logger.debug` en consola. En producción (`debug=False`) no aparecen. Solución futura: setear nivel de `'panaderia'` explícitamente independiente de Flask, controlado por variable de entorno (`LOG_LEVEL=INFO`).
2. **DT-nueva-MEDIA-2.6 (werkzeug requests HTTP a log):** El logger `werkzeug` (que loguea cada request HTTP: `GET /api/... 200`) está en INFO y ensucia el archivo `panaderia.log`. En producción con 500 tenants esto suma ~80 líneas/minuto. Solución futura: bajar `werkzeug` a WARNING o filtrarlo.
3. **Hash de contraseña en log:** pendiente para **Fase 3** de esta misma DT (seguridad).
4. **Archivo sin newline final:** `utilidades/consultas_filtradas.py` no termina con `\n` (cosmético, Fase F).

### Reglas nuevas aprendidas
1. **Prohibido usar PowerShell para diagnóstico de logs:** Usar `findstr`, `find /c`, `more`, `sort /unique` nativo de CMD (PowerShell es lento y `Get-Content` rompe UTF-8 en la salida).
2. **Validar siempre el formato crudo del log con `more`:** `findstr /c:"[INFO]"` devuelve 0 si el formato no usa corchetes de la forma esperada.
3. **Distinguir `print()` (stdout, siempre visible) de `logger.debug` (respetа nivel).** El síntoma "veo cosas en terminal" no siempre está en el `.log`.
4. **Smoke test obligatorio para fixes de canal de logs** (no solo `py_compile` + `git diff`). Comparar `find logs\panaderia.log /c /v ""` antes y después.
5. **Auditar TODOS los `.py` del repo** para `print()` (no solo los 3 principales). `utilidades/` se nos pasó.

### Estado al cierre
- Último commit: `68f8856`. Working tree clean. Fase 1 y 1.5 cerradas.
- **Próximo paso:** **Fase 2** — bajar a DEBUG el diagnóstico de recetas (`app.py:4908` y similares) + el `[DEBUG] Usuario: ..., Authenticated: True` (app.py:2379).
- **Después:** Fase 3 (hash de contraseña en log).

## Sesión 8 Nov — DT-nueva-MEDIA-logging-ruido (Fase 3: hash de contraseña)

**Objetivo:** Cerrar la DT logging ruidoso resolviendo el último bloque: hash de contraseña expuesto en logs (seguridad).

### Diagnóstico
- **`app.py:2184`:** `logger.info(f"📦 [LOGIN] Hash en BD: {user.password_hash}")` → hash completo (~130 chars) en INFO.
- **`app.py:12351`:** `logger.info(f"✅ [VERIFICACIÓN] Hash en BD post-commit: {stored_hash[:50]}...")` → 50 chars en INFO.
- **`app.py:12356`:** `logger.info(f"✅ [PRUEBA] check_password_hash: {test_verify}")` → resultado True/False.
- **Riesgo:** con 500 tenants × 100 logins/día × 2 líneas = ~100.000 hashes/día en `panaderia.log`. En la nube, logs van a servicios externos (CloudWatch, Datadog).

### Fix aplicado (commit `53fc3f3`)
- 3 `logger.info` → `logger.debug`.
- Hash truncado a 20 chars + `...` (preview, ej: `scrypt:32768:8:1$20f...`).
- 2 comentarios `# ✅ SEGURIDAD:` para documentar la decisión inline.
- **Lo que NO se tocó:** `logger.info` de "USUARIO ENCONTRADO", "Panadería ID", "Login exitoso" (auditoría legítima).

### Smoke test 5/5
- Login `admin_27` / `demo2026` funciona.
- Consola: hash truncado (`scrypt:32768:8:1$20f...`) en `DEBUG`.
- Archivo: **cero `logger.debug` del hash** (respeta INFO).
- Login funcional (`GET /dashboard HTTP/1.1 200`).

### ✅ DT-nueva-MEDIA-logging-ruido — CERRADA AL 100%

4 fases + 1 commit de docs:
- F1 (`51000fc`): `buscar_producto`, ~41 INFO/request → 0.
- F1.5 (`68f8856`): `consultas_filtradas.py`, 10 `print`/request → 0.
- F2 (`620a177`): diagnóstico de recetas, ~15 INFO/request → 0.
- F3 (`53fc3f3`): hash de contraseña, 100k hashes/día → 0.
- Docs (`72bccc4`): HANDOFF v9.12 + bitácora.

**Impacto total:** ~500.000 líneas de log/día en prod (500 tenants × 500 productos) → ~0 líneas operativas. Cero regresiones. Auditoría intacta.

### DTs nuevas anotadas (NO tocadas)
1. **DT-nueva-MEDIA-F2.5:** configurar nivel de logger independiente de Flask `debug=True`. Controlar vía `LOG_LEVEL` en `.env`.
2. **DT-nueva-MEDIA-F2.6:** bajar logger `werkzeug` a WARNING para no ensuciar `panaderia.log` con requests HTTP.
DT F2.5 y F2.6 surgieron del smoke test de F1.5 y F2. Son concerns legítimos, no bugs.

Propuesta de regla nueva (v9.13): "No acumular DT" + "Cero DT en el aire". Va al HANDOFF en próxima sesión.

Prioridad F2.6: 🟡 MEDIA (afecta producción, 115k líneas/día). Resolver antes de CRÍTICA-2.

Prioridad F2.5: 🟢 BAJA (solo afecta dev). Resolver en Fase F o post-Docker.

Próximo paso: push de docs (esta sesión) → reglas nuevas en HANDOFF (próxima sesión) → resolver F2.6 antes de CRÍTICA-2
### Estado al cierre
- Último commit: `53fc3f3`. Working tree clean. 5 commits en `origin/main`.
- **Siguiente tarea del HANDOFF:** MEDIA (desconciliación + ANULADO + whitelist, un solo commit).



## Sesión 8 Nov (tarde) — DT-nueva-MEDIA-F2.6: reformulada a BAJA (falso positivo)

**Objetivo:** Cerrar la DT-nueva-MEDIA-F2.6 (werkzeug requests HTTP a log). Anotada el 8 Nov por extrapolación teórica ("500 tenants × ~80 líneas/minuto = ~115k líneas/día").
**Resultado:** **FALSO POSITIVO.** No aplica al código actual. Reformulada a 🟢 BAJA con sesión objetivo Fase G (Dockerización).

### Diagnóstico previo (CMD nativo, sin tocar código)

**Hallazgo 1 — `basicConfig` no existe en `app.py`:**
```cmd
findstr /n /c:"basicConfig" app.py
(vacío)
El logging no usa basicConfig. Hay config propia.

Hallazgo 2 — getLogger aparece 1 sola vez en app.py:

text
1341: logger = logging.getLogger('panaderia')
No hay logging.getLogger('werkzeug') en el código. Werkzeug hereda del root.

Hallazgo 3 — RotatingFileHandler en línea 1360, atado a 'panaderia':
El bloque 1341-1366 muestra que los 2 handlers (consola + archivo) se agregan al logger 'panaderia', NO al root:

python
logger = logging.getLogger('panaderia')
if not logger.handlers:
    ...
    logger.addHandler(_console_handler)
    logger.addHandler(_file_handler)   # ← solo a 'panaderia'
Hallazgo 4 — Prueba empírica: cero requests HTTP en panaderia.log:

Métrica	Valor
Total líneas del log	24.083
Líneas con werkzeug	0
Líneas con GET /	0
Líneas con POST /	0
Hallazgo 5 — Test Python (estado fresh):

text
root level: 30          ← WARNING
root handlers: []       ← ROOT SIN HANDLERS
werkzeug level: 0       ← NOTSET (hereda → efectivo WARNING)
werkzeug handlers: []   ← sin handlers propios
werkzeug propagate: True
Lectura: werkzeug no tiene handlers propios → propaga al root → root sin handlers → no escribe a ningún lado (en proceso fresh). El file handler está solo en 'panaderia' → panaderia.log nunca recibe werkzeug.

Por qué se veía en Flask dev
Flask con debug=True agrega un handler de consola al logger werkzeug en runtime (dentro de Flask/Werkzeug, no en app.py). Ese handler va a stderr, no al root, y no toca panaderia.log. Los GET /... 200 que se ven en la terminal durante el desarrollo son esperados y útiles. El archivo de log está limpio.

Por qué la DT decía 115k líneas/día
Extrapolación teórica: "500 tenants × ~80 líneas/minuto × 24h = ~115k líneas/día". Pero esa extrapolación asume que werkzeug sí escribe al file handler, lo cual no ocurre con la config actual (handler atado a 'panaderia', no al root).

Riesgo real (futuro, Fase G)
Si el Dockerfile / docker-compose.yml / WSGI (gunicorn/waitress) agrega logging.basicConfig() al root, entonces sí werkzeug empezaría a ensuciar el archivo. Es un riesgo de deploy, no un bug actual.

Acción aplicada
HANDOFF.md — DT F2.6 reformulada:

Título: DT-nueva-MEDIA-F2.6 → DT-nueva-BAJA-F2.6.

Prioridad: 🟡 MEDIA → 🟢 BAJA.

Descripción: "Bajar logger werkzeug a WARNING" → "Falso positivo verificado. Acción real: auditar post-Docker que el deploy NO agregue basicConfig al root; si lo agrega, filtrar werkzeug del root handler o setear WARNING solo en prod."

Sesión objetivo: próxima sesión → Fase G (Dockerización).

Estado: abierta (riesgo post-Docker real).

Código: cero cambios. No se tocó app.py. La config actual es correcta.

DTs nuevas / modificadas
DT-nueva-MEDIA-F2.6 → reformulada a DT-nueva-BAJA-F2.6 (falso positivo, riesgo post-Docker, Fase G).

DT-nueva-MEDIA-F2.5 (logging nivel configurable vía LOG_LEVEL): sin cambios. Sigue 🟡 MEDIA. Es real (hoy debug=True fuerza _log_level a DEBUG en dev; en prod debug=False lo deja en INFO — pero no hay control explícito por env var). Se resuelve en otra sesión.

Reglas aprendidas
"115k líneas/día" era extrapolación, no medición. Regla nueva: toda DT de logging debe basarse en find /c /v "" empírico sobre el log real, no en proyecciones.

Antes de bajar un logger a WARNING, verificar quién tiene el file handler. Si el handler está atado a un logger específico (no al root), los loggers "hermanos" (como werkzeug) no llegan al archivo. No hay nada que filtrar.

Flask dev con debug=True agrega handlers a werkzeug en runtime. Esto es interno de Flask, no está en app.py. No confundir "veo requests en terminal" con "los requests van al log".

Estado al cierre
HANDOFF: F2.6 reformulada. Pendiente commit (docs(handoff): F2.6 reformulada — falso positivo).

Código: working tree clean (cero cambios en .py).

Próxima tarea: MEDIA (desconciliación + ANULADO + whitelist en depósitos bancarios, un solo commit). Es la primera DT con impacto contable real de la Fase D.

---

## Sesión 11 Nov — DT-nueva-MEDIA (depósitos) 100% + DT-nueva-BAJA (endpoint huérfano)

**Commits:** `6b5485f`, `17d0b83`, `5368b1a`, `a403c90`, `b0efa27`, `29a4e03`. Pusheados a `origin/main`.

### Objetivo 1 — Cerrar DT-nueva-MEDIA (desconciliación + ANULADO + whitelist)

**Diagnóstico previo (5 huecos reales):**
1. `editar_deposito_bancario()` aceptaba `data['estado']` sin whitelist.
2. `ANULADO` sin flujo dedicado ni auditoría.
3. No existía endpoint para desconciliar.
4. `usuario_id` existía en BD pero nunca se poblaba (auditoría rota).
5. **(Nuevo, no documentado):** `crear_deposito_bancario()` también aceptaba `estado` sin whitelist.

**Migración SQL aplicada:** 4 columnas de auditoría (`motivo_anulacion`, `fecha_anulacion`, `motivo_desconciliacion`, `fecha_desconciliacion`) en `tenant_1`, `tenant_27`, `tenant_31`. Script en `migrations/sql/2026-11-09_depositos_auditoria.sql`.

**Los 4 bloques cerrados:**

| # | Commit | Alcance |
|---|---|---|
| **4.1** | `6b5485f` | Migración SQL + `models.py` alineado (constante `ESTADOS_DEPOSITO_VALIDOS` + 4 columnas) |
| **4.2** | `6b5485f` | Whitelist de estados en `crear` y `editar` (rechaza strings libres con 400) |
| **4.3** | `17d0b83` | Auditoría `usuario_id` en crear/editar/conciliar |
| **4.4** | `5368b1a` | Endpoint `POST /anular/<id>` + modal propio + recuadro rojo + fix de totales (anulados se excluyen del KPI) |
| **4.5** | `a403c90` | Endpoint `POST /desconciliar/<id>` (solo admin) + botón UI + reutilización de modal |

**Tests:**
- 5/5 bloque A (whitelist, creación/edición).
- 5/5 bloque D (auditoría `usuario_id`).
- 5/5 bloque B (anulación UI + F12 + recuadro rojo + fix de totales).
- 3/3 bloque C (desconciliación UI + BD + guard de rol).

**Bugs colaterales detectados y resueltos en el mismo commit:**
- KPI "Total Depósitos" sumaba anulados (mismo patrón que el fix de donaciones `8304a16`). Fix en backend (`estadisticas_depositos_bancarios`) + frontend (`actualizarEstadisticas`).
- Modal de anulación "recordaba" el estado ANULADO al abrir "Nuevo Depósito". Fix: reset explícito en `abrirModalDeposito('crear')`.
- Endpoint "Ver" (`obtener_deposito_bancario`) armaba el JSON manualmente sin campos de auditoría. Fix: usar `deposito.to_dict()`.
- `confirmarAnulacion()` tenía un bloque huérfano (copy-paste viejo) que rompía el JS con `Unexpected token ':'`. Fix: eliminar el bloque.
- El botón "Desconciliar" no se ocultaba para cajeros (aunque el backend los rechaza). Fix: `window.currentUserRol` inyectado con Jinja.

### Objetivo 2 — Cerrar DT-nueva-BAJA (endpoint huérfano)

**Bug:** `def reporte_ventas()` (app.py:8261) no coincidía con su template `ventas_periodo.html`.

**Fix (commits `b0efa27` + `29a4e03`):**
- Renombrar `def reporte_ventas()` → `def reporte_ventas_periodo()`.
- Actualizar `url_for('reporte_ventas_periodo')` en 3 templates: `reportes.html:229`, `ventas_periodo.html:237`, `productos_populares.html:397`.
- **Fix colateral (en `29a4e03`):** el botón "Ver Reporte" de `reportes.html` tenía el `<a>` mal cerrado (faltaba cierre, texto fuera, `div` de la tarjeta sin cerrar). Reescrito.

### DTs nuevas / modificadas

- **Ninguna DT nueva.** Todos los hallazgos se resolvieron dentro de los mismos commits (regla #13 "No acumular DT").

### Reglas aprendidas

1. **Renombrar función de Flask requiere grep en templates.** Flask `url_for()` busca por nombre de función. Cambiar el `def` sin actualizar los templates rompe los botones con `BuildError` en runtime.
2. **`to_dict()` centraliza el JSON.** Cuando un endpoint arma el JSON manualmente (como `obtener_deposito_bancario`), los campos nuevos del modelo no se incluyen automáticamente. Usar `deposito.to_dict()` evita olvidos.
3. **Los KPIs que suman montos deben excluir `ANULADO`.** Mismo patrón que donaciones (`8304a16`): si un registro anulado sigue sumando, el reporte miente.
4. **Los modales reutilizados necesitan reset explícito.** Si un modal se usa para "crear" y "ver", el estado visual (recuadros, colores) debe resetearse en el branch `'crear'`.
5. **El `Unexpected token ':'` en JS suele ser código huérfano de un copy-paste.** Cuando se duplica una función y se olvida borrar la vieja, quedan líneas sueltas que rompen el archivo.
6. **Antes de `git add` en templates con Jinja, correr `git diff <archivo>`.** El editor puede guardar una versión intermedia (sin cerrar bien las etiquetas), y el commit toma esa versión aunque después se corrija. Lección del commit `b0efa27` → `29a4e03`.
7. **Jinja `{% if %}` dentro de JS rompe la sintaxis.** Se debe inyectar el valor en `window.variable` (con comillas) al final del `<script>` y consultar esa variable en JS puro.

### Estado al cierre

- **Working tree clean.**
- **`origin/main` en `29a4e03`.**
- **2 DTs cerradas hoy** (MEDIA + BAJA) = 6 commits.
- **Próxima tarea del HANDOFF:** MEDIA-BAJA (cierre de jornada sin filtros, `models.py:2166`).
---

## Sesión 11 Nov (tarde/noche) — MEDIA-BAJA (cierre jornada) + limpieza de JS huérfano

**Objetivo:** Cerrar la DT-nueva-MEDIA-BAJA (cierre de jornada sin filtros) y verificar si era código muerto. Resultado: sí era código muerto + encontramos un bug latente real + un JS huérfano en el POS.

**Commit:** `7ce0156` (pusheado a `origin/main`).

### Diagnóstico
- **`cerrar_jornada_actual()` (models.py:2161):** Código muerto confirmado. Cero llamadas en `app.py` (solo el `import`), cero referencias en templates. Es la predecesora de `CierreDiario` (el sistema de cierre actual).
- **Bug latente encontrado:** La DT original apuntaba a `models.py:2166` (muerta), pero el bug real de filtros estaba en **`app.py:7892`** (`obtener_ventas_dia` local, el que SÍ se ejecuta en `/api/cierre_diario/estado` y `/realizar_cierre`). Esa query filtraba `estado == 'COMPLETADA'` pero le faltaba `es_donacion == False`. Las donaciones sumaban en el cierre de caja.
- **JS huérfano:** El botón "Cierre Diario" fue eliminado del frontend por Mauricio, pero `static/js/pos-moderno.js` seguía haciendo polling a `/api/cierre_diario/estado` en segundo plano (líneas ~1570 y ~1673).

### Fix aplicado (1 commit, 3 archivos)
1. **`models.py`:** Eliminada `cerrar_jornada_actual()` (86 líneas).
2. **`app.py:1397`:** Limpiado el `import` (quitado `cerrar_jornada_actual`).
3. **`app.py:7912`:** Agregado `Venta.es_donacion == False` a la query de `obtener_ventas_dia`.
4. **`static/js/pos-moderno.js`:** Agregados early-returns (`if (!document.getElementById('btnCierreDiario')) return;`) en `procesarCierreDiario()` y `verificarEstadoCierreDiario()` para evitar llamadas huérfanas si el botón no existe.

### Tests validados
- **Test 1 (backend `/api/cierre_diario/estado`):** JSON de respuesta correcto (0 ventas = 0 total).
- **Test 3 (frontend `/reporte/cierre_caja`):** Carga sin errores.
- **Test JS (Network):** El POS ya no dispara llamadas a `/api/cierre_diario/*`. Cero polling huérfano.
- **Test Donaciones (empírico):** Se procesó una donación en el POS. El reporte de cierre mostró **Total Ventas: $0** y **Salidas No Comerciales: $1,500**, demostrando que el filtro `es_donacion == False` funciona.

### ✅ RESUELTAS el 11 Nov — MEDIA-BAJA (cierre jornada)
| # | Descripción | Commit |
|---|---|---|
| DT-nueva-MEDIA-BAJA | Cierre de jornada sin filtros (`models.py:2166`) → Código muerto eliminado + bug latente corregido en el `obtener_ventas_dia` vivo (`app.py:7892`). | `7ce0156` |
| DT-nueva-BAJA (JS huérfano) | Polling a `/api/cierre_diario/estado` desde `pos-moderno.js` sin botón en frontend → early-return agregado. | `7ce0156` |

### Estado al cierre
- **Working tree clean.** Último commit: `7ce0156`.
- **Próxima tarea del HANDOFF:** CRÍTICA-2 (renombrar schemas, con `pg_dump` previo). Es la última DT crítica antes de Dockerizar.
---

