import os
import sys

# Añadir el directorio actual al path para poder importar la app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def migrate_purchase_system():
    app = create_app()
    with app.app_context():
        print("Iniciando migración del sistema de compras...")
        
        try:
            # 1. Eliminar tabla antigua si existe (para evitar conflictos de esquema)
            # NOTA: En producción esto debería ser un ALTER TABLE, pero aquí recreamos para limpieza
            db.session.execute(text("DROP TABLE IF EXISTS purchase_items CASCADE;"))
            db.session.execute(text("DROP TABLE IF EXISTS purchases CASCADE;"))
            db.session.commit()
            print("Tablas antiguas eliminadas.")

            # 2. Crear las nuevas tablas
            # Importamos los modelos para que SQLAlchemy los reconozca
            from models.purchase import Purchase
            from models.purchase_item import PurchaseItem
            
            db.create_all()
            print("Nuevas tablas 'purchases' y 'purchase_items' creadas exitosamente.")
            
            db.session.commit()
            print("Migración completada con éxito.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error durante la migración: {e}")

if __name__ == "__main__":
    migrate_purchase_system()
