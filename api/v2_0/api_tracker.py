from flask import jsonify
from database import api_tracker as api_tracker_models
import schemas
from api import APIBase
from common.logging_config import applogger
from common import exceptions



class ApiTrackerAPI(APIBase):
    '''API for working with Api tracker'''
    response_schema   = schemas.api_tracker.ApiSchema
    request_schema    = schemas.api_tracker.ApiSchema
    api_rate_limit  = '1/second'
    api_url         = '/apis'
    api_endpoint    = 'apis'

    def get(self):
        apis = self.fetch_filter_sort_rows(api_tracker_models.ApiTracker)
        return jsonify(self.select_fields(apis, many=True))
    
class SingleApiTrackerAPI(APIBase):
    '''API for working with a single API'''

    response_schema   = schemas.api_tracker.ApiSchema
    request_schema    = schemas.api_tracker.ApiSchema
    api_rate_limit  = '1/second'
    api_url         = '/api/<int:api_id>'
    api_endpoint    = 'api'

    def get(self, api_id):
        api = api_tracker_models.ApiTracker.query.filter_by(id=api_id).first()
        if not api: raise exceptions.BadRequest('no api exists with id', id=api_id)
        return jsonify(self.select_fields(api))
      