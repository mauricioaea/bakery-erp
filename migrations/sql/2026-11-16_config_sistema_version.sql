-- Paso 1: Agregar columnas a tenant_1 (solo si no existen)
ALTER TABLE tenant_1.configuracion_sistema
    ADD COLUMN IF NOT EXISTS nombre_sistema VARCHAR(100) DEFAULT 'PanaderíaPro',
    ADD COLUMN IF NOT EXISTS version VARCHAR(20) DEFAULT '1.9.4',
    ADD COLUMN IF NOT EXISTS modo_mantenimiento BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS ultima_actualizacion TIMESTAMP DEFAULT NOW();

-- Paso 2: Actualizar valores en los 4 tenants
UPDATE tenant_1.configuracion_sistema SET version = '1.9.4', nombre_sistema = 'PanaderíaPro', ultima_actualizacion = NOW();
UPDATE tenant_27.configuracion_sistema SET version = '1.9.4', nombre_sistema = 'PanaderíaPro', ultima_actualizacion = NOW();
UPDATE tenant_31.configuracion_sistema SET version = '1.9.4', nombre_sistema = 'PanaderíaPro', ultima_actualizacion = NOW();
UPDATE tenant_34.configuracion_sistema SET version = '1.9.4', nombre_sistema = 'PanaderíaPro', ultima_actualizacion = NOW();