from app import create_app, db
from models import Usuario

app = create_app()

def init_db():
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        print("✅ Tablas creadas correctamente en PostgreSQL.")

        # Crear usuario admin si no existe
        if not Usuario.query.filter_by(username='admin').first():
            admin = Usuario(username='admin', email='admin@stock.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("👤 Usuario 'admin' creado con contraseña 'admin123'.")
        else:
            print("ℹ️ El usuario 'admin' ya existe.")

if __name__ == '__main__':
    init_db()
