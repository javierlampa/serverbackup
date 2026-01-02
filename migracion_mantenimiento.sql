-- Migración para el Módulo de Mantenimiento
CREATE TABLE IF NOT EXISTS mantenimientos (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL,
    descripcion TEXT NOT NULL,
    costo NUMERIC(10, 2) DEFAULT 0.00,
    fecha_inicio TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP WITHOUT TIME ZONE,
    estado VARCHAR(20) DEFAULT 'en_proceso',
    tecnico VARCHAR(100)
);

-- Nota: Asegúrate de ejecutar este script en tu base de datos PostgreSQL.
