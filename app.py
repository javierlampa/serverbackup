from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Registrar Blueprints
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from routes.categorias import categorias_bp
    app.register_blueprint(categorias_bp)
    
    from routes.proveedores import proveedores_bp
    app.register_blueprint(proveedores_bp)

    from routes.productos import productos_bp
    app.register_blueprint(productos_bp)
    
    from routes.compras import compras_bp
    app.register_blueprint(compras_bp)
    
    from routes.movimientos import movimientos_bp
    app.register_blueprint(movimientos_bp)
    
    from routes.prestamos import prestamos_bp
    app.register_blueprint(prestamos_bp)

    from routes.usuarios import usuarios_bp
    app.register_blueprint(usuarios_bp)
    
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('dashboard.index'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5002)
