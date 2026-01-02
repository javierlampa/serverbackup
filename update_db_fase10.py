from app import create_app, db
from sqlalchemy import text

def update_db_fase10():
    app = create_app()
    with app.app_context():
        try:
            # SQL embebido directamente en el script
            sql_script = """
            -- Migración para Mejoras en Producto (Fase 10)
            ALTER TABLE productos ADD COLUMN IF NOT EXISTS vida_util VARCHAR(100);
            ALTER TABLE productos ADD COLUMN IF NOT EXISTS precio_dolar NUMERIC(10, 2);
            ALTER TABLE productos ADD COLUMN IF NOT EXISTS image_path VARCHAR(255);
            """

            # Ejecutar sentencias
            print("Ejecutando migración Fase 10...")
            for statement in sql_script.split(';'):
                if statement.strip():
                    db.session.execute(text(statement))
            
            db.session.commit()
            print("¡Migración Fase 10 (Vida Útil, Precio USD, Foto) completada con éxito!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al ejecutar la migración: {e}")

if __name__ == '__main__':
    update_db_fase10()
