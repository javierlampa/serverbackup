-- SQL Migration Script to rename tables to Spanish
-- Execute this on your PostgreSQL database

-- Rename tables
ALTER TABLE users RENAME TO usuarios;
ALTER TABLE categories RENAME TO categorias;
ALTER TABLE suppliers RENAME TO proveedores;
ALTER TABLE products RENAME TO productos;
ALTER TABLE loans RENAME TO prestamos;
ALTER TABLE stock_movements RENAME TO movimientos_stock;
ALTER TABLE purchases RENAME TO compras;
ALTER TABLE purchase_items RENAME TO items_compra;
ALTER TABLE notifications RENAME TO notificaciones;

-- Update foreign key constraints (PostgreSQL usually handles this automatically if renaming tables, 
-- but it's good to verify if any explicit constraint names need changing)

-- Example of renaming a constraint if needed (usually not required for basic table renames)
-- ALTER TABLE productos RENAME CONSTRAINT products_category_id_fkey TO productos_category_id_fkey;
