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