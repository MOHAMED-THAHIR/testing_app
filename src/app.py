from flask import Flask
from flask_cors import CORS
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.env import Config
from middlewares.error_middleware import register_error_handlers
from middlewares.logging_middleware import register_logging
from routes.test_routes import test_bp
from routes.export_routes import export_bp
from routes.health_routes import health_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # CORS
    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)

    # Middleware
    register_logging(app)
    register_error_handlers(app)

    # Blueprints
    app.register_blueprint(health_bp, url_prefix="/api/v1/health")
    app.register_blueprint(test_bp, url_prefix="/api/v1/tests")
    app.register_blueprint(export_bp, url_prefix="/api/v1/export")

    return app