#!/usr/bin/env python
import datetime
import os

import app
from common import configuration, exceptions, utils
from common.logging_config import applogger
from database import db
from database.api_tracker import ApiTracker
from database.events import Event, EventLevelEnum, LoggerSourceEnum
from database.types import GUID, INET
from flask import request
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

activate_this = './venv/bin/activate_this.py'
activate_this = os.path.join(os.path.dirname(__file__), activate_this)
execfile(activate_this, dict(__file__=activate_this))


APP = app.create_and_initialize_app(os.getenv('FLASK_CONFIG') or 'default_config')
MANAGER = Manager(APP)

def add_context_to_shell(flaskapp, manager):
    def make_shell_context():
        return dict(app=flaskapp, db=db, mainapp=app, configuration=configuration,
                    Event=Event,ApiTracker=ApiTracker, LoggerSourceEnum=LoggerSourceEnum, EventLevelEnum=EventLevelEnum,)
    manager.add_command("shell", Shell(make_context=make_shell_context))
add_context_to_shell(APP, MANAGER)

MIGRATE = Migrate(APP, db)
MANAGER.add_command("db", MigrateCommand)

@MANAGER.command
def profile(length=25, dir_profile=None, host='127.0.0.1', port=5000):
    """Start the application under the code profiler"""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    APP.wsgi_app = ProfilerMiddleware(APP.wsgi_app, restrictions=[length],
                                      profile_dir=dir_profile)
    APP.run(host=host, port=port)

@MANAGER.command
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade
    upgrade()   
    

@APP.after_request
def per_request_callbacks(response):
    status_as_string = response.status
    status_as_integer = response.status_code
    api = ApiTracker(URL=request.url,method=request.method,status=response.status,status_code=response.status_code,execution_time=datetime.datetime.now(), request_ip=utils.get_request_ip(),platform=request.user_agent.platform,browser=request.user_agent.browser)                                  
    db.session.add(api)
    db.session.commit()

    return response


if __name__ == "__main__":

    MANAGER.run()
