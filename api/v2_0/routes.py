from .events            import EventsAPI,      SingleEventAPI
from .api_tracker       import ApiTrackerAPI,    SingleApiTrackerAPI


from . import api_bp
from api import APIBase
from app import rate_limiter
from flask import jsonify, url_for
from schemas import ma
from flask_limiter.util import get_remote_address


api_mappers = [EventsAPI, SingleEventAPI, ApiTrackerAPI,SingleApiTrackerAPI]

class URLDiscoverySchema(ma.Schema):
    class Meta:
        fields = [mapper.api_endpoint for mapper in api_mappers]
        fields.extend(['url_discovery', '_self'])
    _self = ma.Hyperlinks({'url': ma.URLFor('.url_discovery'),})

class URLDiscoveryAPI(APIBase):
    '''API for discovering other API endpoints'''

    response_schema = URLDiscoverySchema
    request_schema  = URLDiscoverySchema
    api_rate_limit  = '10/minute'
    api_url         = '/*'
    api_endpoint    = 'url_discovery'

    def options(self):
        '''discover all API endpoint urls, methods and required permissions'''
        result = {}
        for mapper in api_mappers: result[mapper.api_endpoint] = mapper.get_api_doc()
        response = self.request_schema().dump(result)
        response.data['*'] = response.data['url_discovery']
        del(response.data['url_discovery'])
        return jsonify(response.data)

api_mappers.append(URLDiscoveryAPI)

for mapper_obj  in api_mappers:
    view = mapper_obj.as_view(mapper_obj.api_endpoint)
    #apply rate limit rules
    limit_string = mapper_obj.api_rate_limit
    view = rate_limiter.limit(limit_string, per_method=True, key_func=get_remote_address)(view)
    #apply rbac rules
    allowed_methods = []
    supported_methods = [m.lower() for m in view.methods]
    allowed_methods = [m.lower() for m in allowed_methods]
    unsupported_methods = [m for m in supported_methods if m not in allowed_methods]
    api_bp.add_url_rule(mapper_obj.api_url, view_func=view)
