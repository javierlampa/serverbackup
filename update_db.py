from app import create_app, db
from sqlalchemy import text

def update_db():
    app = create_app()
    with app.app_context():
        # Crear tabla mantenimientos
        try:
            sql = """
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
            """
            db.session.execute(text(sql))
            db.session.commit()
            print("¡Tabla 'mantenimientos' creada correctamente!")
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")

if __name__ == '__main__':
    update_db()
