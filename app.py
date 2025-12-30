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

    from routes.categories import categories_bp
    app.register_blueprint(categories_bp)
    
    from routes.suppliers import suppliers_bp
    app.register_blueprint(suppliers_bp)

    from routes.products import products_bp
    app.register_blueprint(products_bp)
    
    from routes.purchases import purchases_bp
    app.register_blueprint(purchases_bp)
    
    from routes.movements import movements_bp
    app.register_blueprint(movements_bp)
    
    from routes.loans import loans_bp
    app.register_blueprint(loans_bp)

    from routes.users import users_bp
    app.register_blueprint(users_bp)
    
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('dashboard.index'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5002)
