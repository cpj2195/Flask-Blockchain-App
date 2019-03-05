from marshmallow import fields
from marshmallow_enum import EnumField
from database import events as event_models
from schemas import ma

class EventSchema(ma.ModelSchema):
    class Meta:
        fields = ('id', 'utc_time', 'level', 'event_type', 'log_source', 'message', '_self')
        model  = event_models.Event
    _self             = ma.Hyperlinks({'url': ma.URLFor('.event', event_id='<id>'),})
    level             = EnumField(event_models.EventLevelEnum, by_value=True)
    log_source        = EnumField(event_models.LoggerSourceEnum, by_value=True)