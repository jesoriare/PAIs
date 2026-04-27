from flask import Flask

from .routes import bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    app.config["SECRET_KEY"] = "dev-only-secret"
    app.register_blueprint(bp)
    return app
