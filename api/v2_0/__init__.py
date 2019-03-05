from flask import Blueprint, request, jsonify
from common import configuration

api_bp_name = 'api_{an}_v2_0'.format(an=configuration.system['app_name'])
api_bp = Blueprint(api_bp_name, __name__)

from . import routes
