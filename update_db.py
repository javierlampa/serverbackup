from app import create_app, db
from sqlalchemy import text

def update_db():
    app = create_app()
    with app.app_context():
        try:
            # Intentar agregar la columna signature a la tabla loans
            db.session.execute(text('ALTER TABLE loans ADD COLUMN signature TEXT'))
            db.session.commit()
            print("Columna 'signature' agregada correctamente a la tabla 'loans'.")
        except Exception as e:
            db.session.rollback()
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("La columna 'signature' ya existe.")
            else:
                print(f"Error al actualizar la base de datos: {e}")

if __name__ == '__main__':
    update_db()
