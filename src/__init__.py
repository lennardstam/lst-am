from flask import Flask

from src.settings import Config
from .extensions import db, bcrypt, login_manager, mail
from .links.routes import main
from .users.routes import users
from .errors.handlers import errors


# def create_app(config_file='settings.py'):
def create_app(config_class=Config):
    app = Flask(__name__)
    # app.config.from_pyfile(config_file)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(errors)
    app.register_blueprint(users, url_prefix='/user')

    return app





# from src.models import *
