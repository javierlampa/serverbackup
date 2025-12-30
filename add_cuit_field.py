"""
Script de migración para agregar el campo CUIT a la tabla suppliers
"""
from app import create_app, db
from sqlalchemy import text

def add_cuit_field():
    """Agrega el campo cuit a la tabla suppliers"""
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar si la columna ya existe
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='suppliers' AND column_name='cuit'
            """))
            
            if result.fetchone():
                print("✓ El campo 'cuit' ya existe en la tabla suppliers")
                return
            
            # Agregar la columna
            db.session.execute(text("""
                ALTER TABLE suppliers 
                ADD COLUMN cuit VARCHAR(13)
            """))
            
            db.session.commit()
            print("✓ Campo 'cuit' agregado exitosamente a la tabla suppliers")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error al agregar el campo: {e}")
            raise

if __name__ == '__main__':
    print("Iniciando migración: Agregar campo CUIT a suppliers...")
    add_cuit_field()
    print("Migración completada!")
