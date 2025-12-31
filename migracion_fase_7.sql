-- SQL Migration Script for Price History and Maintenance
-- Execute this on your PostgreSQL database

CREATE TABLE historial_precios (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
    price NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE productos ADD COLUMN last_price_update TIMESTAMP WITHOUT TIME ZONE;

-- Note: Maintenance table will be added in the next phase
