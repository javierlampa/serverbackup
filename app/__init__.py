from flask import Flask, render_template, redirect, url_for
from .config import Config
from .db import init_db

def create_app(test_config=None):
    # Crear y configurar la app
    app = Flask(__name__, instance_relative_config=True)
    
    if test_config is None:
        # Cargar config normal
        app.config.from_object(Config)
    else:
        # Cargar test config
        app.config.from_mapping(test_config)

    # Asegurar que existan directorios necesarios
    try:
        import os
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Inicializar Dependencias
    init_db(app)

    # Registrar Blueprints
    from .blueprints.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from .blueprints.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from .blueprints.admin import admin_bp
    app.register_blueprint(admin_bp)

    from .blueprints.api import api_bp
    app.register_blueprint(api_bp)

    # Iniciar Monitor de Alta Disponibilidad
    from .services.monitor import start_monitor
    start_monitor(app)

    # Ruta raiz redirige a dashboard o login
    @app.route('/')
    def root():
        return redirect(url_for('auth.login'))

    return app
