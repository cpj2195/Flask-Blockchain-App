from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(session_options={"autoflush": False, "autocommit": False})

class BaseMixin(object):
    def __repr__(self):
        attr_string = ["{a}={v}".format(a=repr_attr, v=getattr(self, repr_attr)) for repr_attr in self.__repr_attrs__]
        return '<{cls} ({ats})>'.format(cls=self.__class__.__name__, ats=', '.join(attr_string))

from . import events,api_tracker

def track_session_deletes(session):
    events.track_db_deletes(session)
