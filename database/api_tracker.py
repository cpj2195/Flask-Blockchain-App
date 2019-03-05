from . import db, BaseMixin
from .types import GUID
from sqlalchemy.orm import validates
import database
import enum
import datetime
from sqlalchemy_utils import URLType
from sqlalchemy_utils import IPAddressType



class ApiTracker(db.Model):
    __tablename__     = 'api_tracker'
    __bind_key__      = 'broker_db'
    __repr_attrs__    = ["URL","method","status"]
    id                   = db.Column(db.BigInteger, primary_key=True,autoincrement=True)
    URL			         = db.Column(URLType)
    method               = db.Column(db.String(200))
    status               = db.Column(db.String(200))
    status_code          = db.Column(db.Integer)
    execution_time       = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    request_ip 			 = db.Column(db.String)
    platform             = db.Column(db.String)
    browser              = db.Column(db.String)
    # version              = db.Column(db.String)
    def __init__(self, URL,method,status,status_code,execution_time, request_ip,platform,browser):
        self.URL                = URL
        self.method             = method
        self.status             = status
        self.status_code        = status_code
        self.execution_time     = execution_time
        self.request_ip         = request_ip
        self.platform           = platform
        self.browser            = browser
        # self.version            = version