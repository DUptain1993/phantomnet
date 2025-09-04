# app/__init__.py

from flask import Flask
from .extensions import db
from .models import *                 # noqa: F401,F403
from .routes.admin import admin_bp
from .routes.bot   import bot_bp


def create_app() -> Flask:
    """Factory for the PhantomNet C2 Flask application."""
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="change-me-in-production",
        SQLALCHEMY_DATABASE_URI="sqlite:///phantom_c2.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    db.init_app(app)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(bot_bp,   url_prefix="/bot")

    with app.app_context():
        db.create_all()

    return app