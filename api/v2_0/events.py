from flask import jsonify
from api import APIBase
import schemas
from database import events as event_models

class EventsAPI(APIBase):
    '''API for working with Events'''

    response_schema = schemas.events.EventSchema
    request_schema  = schemas.api_base.FilterOrderSelectSchema
    api_rate_limit  = '10/minute'
    api_url         = '/events'
    api_endpoint    = 'events'

    def get(self):
        '''get all events
        {api_filtering_doc}
        {api_sorting_doc}
        {api_field_selection_doc}'''
        events = self.fetch_filter_sort_rows(event_models.Event)
        return jsonify(self.select_fields(events, many=True))

class SingleEventAPI(APIBase):
    '''API for working with a single Event'''

    response_schema = schemas.events.EventSchema
    request_schema  = schemas.api_base.FieldSelectionSchema
    api_rate_limit  = '10/minute'
    api_url         = '/event/<int:event_id>'
    api_endpoint    = 'event'

    def get(self, event_id):
        '''get a single event specified by <event_id>
        {api_field_selection_doc}'''
        event = event_models.Event.query.filter_by(id=event_id).first()
        return jsonify(self.select_fields(event))
