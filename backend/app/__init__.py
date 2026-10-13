import os
from flask import Flask
from app.config import config_by_name
from app.extensions import db, migrate, jwt, cors
from app.utils.errors import register_error_handlers
from app.tasks.scheduler import init_scheduler

def create_app(config_name: str = None) -> Flask:
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    flask_app = Flask(__name__)
    flask_app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Initialize extensions
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    jwt.init_app(flask_app)
    cors.init_app(flask_app, resources={r"/api/*": {"origins": flask_app.config.get("CORS_ORIGINS", "*")}})

    # Register error handlers
    register_error_handlers(flask_app)

    # Register blueprints
    from app.api.auth import auth_bp
    from app.api.chat import chat_bp
    from app.api.uploads import uploads_bp
    from app.api.health import health_bp

    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(chat_bp)
    flask_app.register_blueprint(uploads_bp)
    flask_app.register_blueprint(health_bp)

    # Auto-create tables for development/testing ease
    with flask_app.app_context():
        import app.models  # Ensure all models are imported
        db.create_all()

    # Initialize scheduler
    if not flask_app.config.get("TESTING") and not os.environ.get("WERKZEUG_RUN_MAIN") == "false":
        try:
            init_scheduler(flask_app)
        except Exception:
            pass

    return flask_app
