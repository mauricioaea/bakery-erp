-- ============================================================
-- db/schema_tenant_canonical.sql
-- Fuente única de verdad del DDL de un tenant.
-- Se ejecuta contra un schema vacío al crear un tenant nuevo.
-- Todas las tablas van aquí (migración progresiva desde app.py).
--
-- Uso: crear_tenant_saas() lee este archivo y lo ejecuta.
-- Placeholder: {schema_name} se reemplaza por el schema real.
-- ============================================================

-- =============================================
-- consecutivos_pos (depende de panaderias)
-- =============================================
CREATE TABLE IF NOT EXISTS {schema_name}.consecutivos_pos (
    id SERIAL PRIMARY KEY,
    panaderia_id INTEGER NOT NULL REFERENCES {schema_name}.panaderias(id),
    numero_actual INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =============================================
-- (Futuras tablas se agregan aquí, migrando desde app.py)
-- =============================================