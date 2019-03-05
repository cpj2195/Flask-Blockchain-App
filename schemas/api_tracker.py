from database import api_tracker as api_tracker_models
from marshmallow import fields, validate
from marshmallow_enum import EnumField
from schemas import ma


class ApiSchema(ma.ModelSchema):
    class Meta:
        fields = ('id','URL' , 'method', 'status' ,'status_code', 'execution_time', 'request_ip','platform','browser',)
        model = api_tracker_models.ApiTracker
    _self          = ma.Hyperlinks({'url': ma.URLFor('.api_tracker', api_id='<id>'),})
    events         = fields.Nested('EventSchema', many=True, only=('id', '_self', 'utc_time', 'level', 'event_type', 'log_source', 'message',))
