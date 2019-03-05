from common import configuration, logging_config
from common.exceptions import (Forbidden, Unauthorized, raise_exception,
                               register_error_handlers)
from database import db, track_session_deletes
from flask import Flask, abort, g, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr
from schemas import ma

rate_limiter = Limiter(key_func=get_ipaddr)


def flask_config_merge(app, flask_config):
    for key, value in flask_config.items(): app.config[key] = value
    return app

def register_blueprints(app):
    #register api blueprints
    from api.v2_0 import api_bp as api_v2_0
    app.register_blueprint(api_v2_0, url_prefix='/api/v1.0')
    #register frontend blueprint
    return app

def create_app():
    app = Flask(configuration.system['app_name'])
    app = register_blueprints(app)
    app = register_error_handlers(app)
    return app

def init_app_plugins(app):
    rate_limiter.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    track_session_deletes(db.session)
    ma.init_app(app)
    return app

def create_and_initialize_app(config_name):
    configuration.load_configuration(config_name)
    logging_config.configure_app_logger(configuration.system['debug'])
    app = create_app()
    app = flask_config_merge(app, configuration.system['flask_configuration'])
    app = init_app_plugins(app)
    return app
