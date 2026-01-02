from app import create_app, db
from sqlalchemy import text

def update_db_fase12():
    app = create_app()
    with app.app_context():
        try:
            # SQL para agregar columna status a compras
            sql_script = """
            -- Migración Fase 12: Estado de Compras
            ALTER TABLE compras ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'pendiente';
            """

            # Ejecutar sentencias
            print("Ejecutando migración Fase 12 (Estado Compras)...")
            for statement in sql_script.split(';'):
                if statement.strip():
                    db.session.execute(text(statement))
            
            db.session.commit()
            print("¡Migración Fase 12 completada! Se ha agregado el campo 'status' a la tabla 'compras'.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al ejecutar la migración: {e}")

if __name__ == '__main__':
    update_db_fase12()
