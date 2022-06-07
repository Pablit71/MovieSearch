from flask import Flask
from flask_restx import Api

from app.config import Config
from app.database import db
from app.models import User
from app.views.directors import directors_ns
from app.views.genres import genres_ns
from app.views.movies import movies_ns
from app.views.users import users_ns, auth_ns


def create_app(config: Config) -> Flask:
    application = Flask(__name__)
    application.config.from_object(config)
    application.app_context().push()
    return application


def configure_app(application: Flask):
    db.init_app(application)
    api = Api(app)
    api.add_namespace(movies_ns)
    api.add_namespace(genres_ns)
    api.add_namespace(directors_ns)
    api.add_namespace(users_ns)
    api.add_namespace(auth_ns)


if __name__ == '__main__':
    app_config = Config()
    app = create_app(app_config)
    configure_app(app)
    app.run()
