from app import create_app, db
from sqlalchemy import text

def add_signature_column():
    app = create_app()
    with app.app_context():
        try:
            # Check if column exists
            # This query is specific to PostgreSQL/SQLite compatibility for checking columns
            # But simpler is to just try to add it and catch error, or inspect
            
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('movimientos_stock')]
            
            if 'signature' not in columns:
                print("Agregando columna 'signature' a la tabla 'movimientos_stock'...")
                # Use text() for raw SQL
                db.session.execute(text("ALTER TABLE movimientos_stock ADD COLUMN signature TEXT"))
                db.session.commit()
                print("Columna agregada exitosamente.")
            else:
                print("La columna 'signature' ya existe en 'movimientos_stock'.")
                
        except Exception as e:
            print(f"Error al modificar la base de datos: {e}")
            db.session.rollback()

if __name__ == '__main__':
    add_signature_column()
