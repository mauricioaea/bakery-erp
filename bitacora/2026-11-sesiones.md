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