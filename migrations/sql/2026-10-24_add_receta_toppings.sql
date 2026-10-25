-- ============================================================
-- Migration: Add receta_toppings table
-- Fecha: 24 Oct 2026
-- Feature: Ajuste de recetas con toppings
--
-- Crea la tabla receta_toppings en todos los tenants existentes.
-- Para tenants nuevos, la tabla se crea automáticamente en
-- crear_tenant_saas() (ver app.py:~399).
--
-- Ejecutar contra los tenants: tenant_1, tenant_27.
-- ============================================================

-- Tenant 1
CREATE TABLE IF NOT EXISTS tenant_1.receta_toppings (
    id SERIAL PRIMARY KEY,
    receta_id INTEGER NOT NULL REFERENCES tenant_1.recetas(id) ON DELETE CASCADE,
    materia_prima_id INTEGER REFERENCES tenant_1.materias_primas(id),
    sub_receta_id INTEGER REFERENCES tenant_1.recetas(id),
    cantidad_por_unidad FLOAT NOT NULL DEFAULT 0,
    unidad_medida VARCHAR(20),
    costo_unitario FLOAT DEFAULT 0,
    costo_total FLOAT DEFAULT 0,
    panaderia_id INTEGER NOT NULL REFERENCES tenant_1.panaderias(id),
    activo BOOLEAN DEFAULT TRUE,
    CONSTRAINT chk_topping_tipo_1 CHECK (
        (materia_prima_id IS NOT NULL AND sub_receta_id IS NULL) OR
        (materia_prima_id IS NULL AND sub_receta_id IS NOT NULL)
    )
);

-- Tenant 27
CREATE TABLE IF NOT EXISTS tenant_27.receta_toppings (
    id SERIAL PRIMARY KEY,
    receta_id INTEGER NOT NULL REFERENCES tenant_27.recetas(id) ON DELETE CASCADE,
    materia_prima_id INTEGER REFERENCES tenant_27.materias_primas(id),
    sub_receta_id INTEGER REFERENCES tenant_27.recetas(id),
    cantidad_por_unidad FLOAT NOT NULL DEFAULT 0,
    unidad_medida VARCHAR(20),
    costo_unitario FLOAT DEFAULT 0,
    costo_total FLOAT DEFAULT 0,
    panaderia_id INTEGER NOT NULL REFERENCES tenant_27.panaderias(id),
    activo BOOLEAN DEFAULT TRUE,
    CONSTRAINT chk_topping_tipo_27 CHECK (
        (materia_prima_id IS NOT NULL AND sub_receta_id IS NULL) OR
        (materia_prima_id IS NULL AND sub_receta_id IS NOT NULL)
    )
);

-- ============================================================
-- Verificación (ejecutar por separado si querés confirmar):
-- SELECT table_schema, table_name
-- FROM information_schema.tables
-- WHERE table_name = 'receta_toppings';
-- ============================================================