from flask import Flask

from .extensions import db, bcrypt, login_manager
from .main.routes import main
from .users.routes import users
from .errors.handlers import errors


def create_app(config_file='settings.py'):
    app = Flask(__name__)

    app.config.from_pyfile(config_file)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(errors)
    app.register_blueprint(users)

    return app



# from src.models import *
