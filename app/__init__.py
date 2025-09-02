# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models to register them with SQLAlchemy
    # Models will be imported when needed to avoid circular imports

    from app.routes import admin, api, web
    app.register_blueprint(admin.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(web.bp)

    return app