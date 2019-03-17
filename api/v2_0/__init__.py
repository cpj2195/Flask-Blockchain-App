from flask import Blueprint, request, jsonify
from common import configuration
from uuid import uuid4


from common import blockchain as blkch
api_bp_name = 'api_{an}_v2_0'.format(an=configuration.system['app_name'])
api_bp = Blueprint(api_bp_name, __name__)

blockchain_list = blkch.BlockChain()
node_address = str(uuid4()).replace('-','')

from . import routes
