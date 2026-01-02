from app import create_app, db
from sqlalchemy import text

def update_db_fase11():
    app = create_app()
    with app.app_context():
        try:
            # SQL para cambiar vida_util a fecha_fin_vida_util
            sql_script = """
            -- Migración Fase 11: Cambio de Vida Útil a Fecha
            ALTER TABLE productos ADD COLUMN IF NOT EXISTS fecha_fin_vida_util DATE;
            ALTER TABLE productos DROP COLUMN IF EXISTS vida_util;
            """

            # Ejecutar sentencias
            print("Ejecutando migración Fase 11 (Refactor Vida Útil)...")
            for statement in sql_script.split(';'):
                if statement.strip():
                    db.session.execute(text(statement))
            
            db.session.commit()
            print("¡Migración Fase 11 completada! Se ha reemplazado 'vida_util' por 'fecha_fin_vida_util'.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al ejecutar la migración: {e}")

if __name__ == '__main__':
    update_db_fase11()
