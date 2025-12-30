-- SQL Migration Script to add IP and Component Tracking columns
-- Execute this on your PostgreSQL database

ALTER TABLE productos ADD COLUMN ip_address VARCHAR(45);
ALTER TABLE productos ADD COLUMN parent_id INTEGER REFERENCES productos(id);
