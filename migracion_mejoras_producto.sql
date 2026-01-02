-- Migración para Mejoras en Producto (Fase 10)
-- Agrega campos para Vida Útil, Precio en Dólares y Foto

ALTER TABLE productos ADD COLUMN IF NOT EXISTS vida_util VARCHAR(100);
ALTER TABLE productos ADD COLUMN IF NOT EXISTS precio_dolar NUMERIC(10, 2);
ALTER TABLE productos ADD COLUMN IF NOT EXISTS image_path VARCHAR(255);

-- Nota: Ejecutar este script en la base de datos PostgreSQL.
