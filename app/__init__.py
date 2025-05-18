from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    app.config.update(
        SECRET_KEY="dev_key",
        SQLALCHEMY_DATABASE_URI="sqlite:///data.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "main.login"
    login_manager.login_message = "Merci de vous connecter pour accéder à cette page."

    from .routes import main
    from .routine_routes import routine_bp

    app.register_blueprint(main)  # sans url_prefix
    app.register_blueprint(routine_bp)

    @app.errorhandler(404)
    def not_found_error(error):
        return "Page non trouvée", 404

    return app
