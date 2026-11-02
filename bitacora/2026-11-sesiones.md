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

**Commit:** `PENDIENTE_HASH` (se asigna al commitear)

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
| Bug CRÍTICA-1 | `editar_deposito_bancario()` sin validación de estado → early-return 403 + `logger.warning` con usuario | `PENDIENTE_HASH` |
| Fix preexistente | `from datetime import date` local redundante + mal indentado en `editar_deposito_bancario()` (bug latente `NameError`) | `PENDIENTE_HASH` |
| Feature frontend | `setModalModoLectura()` + botón "Ver" del CONCILIADO como solo-lectura (`btn-secondary`, sin Guardar) | `PENDIENTE_HASH` |
| QA | Smoke test 7/7 (UI + backend 403 + log + no-regresión) | — |

### Hallazgos nuevos (anotados, NO tocados — Fase D)
1. **DT-nueva-MEDIA (desconciliación):** `CONCILIADO` es inmutable por este fix, pero **no existe endpoint para desconciliar**. Si en el futuro se requiere, agregar `POST /depositos_bancarios/desconciliar/<id>` con auditoría (usuario, motivo, fecha). Por ahora: no hay flujo.
2. **DT-nueva-MEDIA (estado `ANULADO` sin flujo):** el modal de edición permite setear `estado='ANULADO'` directamente (select en `gestion_financiera.html:690-694`), sin endpoint dedicado ni auditoría. Revisar si `ANULADO` debe existir en el select o manejarse como `conciliar` (endpoint dedicado). **No afecta CRÍTICA-1** (nuestro guard bloquea CONCILIADO, pero ANULADO sigue siendo editable → se puede "revertir" un ANULADO a REGISTRADO sin control). Anotar para Fase D.
3. **DT-nueva-MEDIA (whitelist `estado` backend):** `editar_deposito_bancario()` acepta `data['estado']` sin validar contra `{'REGISTRADO', 'CONCILIADO', 'ANULADO'}`. Persistiría cualquier string. No explota visualmente pero es un hueco. Anotar para Fase D (mismo commit que el punto 2).

### Estado al cierre
- Último commit: `PENDIENTE_HASH`. Próxima tarea: **DT-nueva-MEDIA-ALTA** (donaciones suman en "Ingresos" del reporte Análisis Productos).