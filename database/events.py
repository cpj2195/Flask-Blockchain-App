import datetime
import enum

from common.logging_config import applogger
from sqlalchemy import event, inspect
from sqlalchemy.sql import func

from . import BaseMixin, db
from .api_tracker import ApiTracker


class LoggerSourceEnum(enum.Enum):
    user              = "user"



log_source_mapping = {
}

class EventLevelEnum(enum.Enum):
    debug       = "debug"
    info        = "info"
    warning     = "warning"
    critical    = "critical"
    exception   = "exception"

class Event(db.Model, BaseMixin):
    __tablename__  = 'events'
    __bind_key__   = 'broker_db'
    __repr_attrs__ = ["id", "utc_time", "event_type", "log_source", "message"]
    #attributes
    id                   = db.Column(db.BigInteger,             primary_key=True)
    utc_time             = db.Column(db.DateTime,               index=True, nullable=False)
    level                = db.Column(db.Enum(EventLevelEnum),   index=True)
    event_type           = db.Column(db.String(length=256),     index=True)
    log_source           = db.Column(db.Enum(LoggerSourceEnum), index=True)
    message              = db.Column(db.Text)
    #foreign keys

    @staticmethod
    def link_event(event_source_obj, key, value, is_remove, level=EventLevelEnum.info):
        if event_source_obj.__class__ not in log_source_mapping:
            applogger.warning("source obj %s cannot be tracked and linked in the events table", event_source_obj)
        utc_time = datetime.datetime.utcnow()
        old_value  = getattr(event_source_obj, key)
        value_changed = False if value == old_value else True
        value_type = 'list' if hasattr(old_value, 'append') else 'scalar'
        if 'password' in key.lower(): display_value = "*password_hidden*"
        else:                         display_value = value
        if is_remove:
            event_type = "attr_remove"
            message    = "{a}.remove({v})".format(a=key, v=display_value)
        elif value_type == 'list':
            if old_value: event_type = "attr_append"
            else:         event_type = "attr_initialize"
            message    = "{a}.append({v})".format(a=key, v=display_value)
        elif value_type == 'scalar' and value_changed:
            if old_value: event_type = "attr_change"
            else:         event_type = "attr_initialize"
            message    = "{a}={v}".format(a=key, v=display_value)
        else:
            event_type = "no_change"
        if event_type != "no_change":
            event = Event(utc_time=utc_time, level=level, event_type=event_type, message=message, log_source=log_source_mapping[event_source_obj.__class__])
            event_source_obj.events.append(event)
            db.session.add(event)
        return value

def obj_repr(obj):
    attr_string = []
    obj_insp = inspect(obj)
    for attr_name in obj_insp.attrs.keys():
        attr_value = obj_insp.attrs[attr_name].value
        if hasattr(attr_value, 'all'):
            attr_value = attr_value.all()
        if 'password' in attr_name.lower(): attr_value = "*password_hidden*"
        attr_string.append("{a}={v}".format(a=attr_name, v=attr_value))
    return '<{cls} ({ats})>'.format(cls=obj.__class__.__name__, ats=', '.join(attr_string))

def track_db_deletes(session):
    @event.listens_for(session, 'before_flush')
    def before_flush(session, flush_context, instances):
        for obj in session.deleted:
            if obj.__class__ not in log_source_mapping:
                applogger.warning("source obj %s cannot be tracked and linked in the events table", obj)
                continue
            utc_time  = datetime.datetime.utcnow()
            level = EventLevelEnum.info
            event_type = "row_delete"
            event = Event(utc_time=utc_time, level=level, event_type=event_type, message=obj_repr(obj), log_source=log_source_mapping[obj.__class__])
            db.session.add(event)
