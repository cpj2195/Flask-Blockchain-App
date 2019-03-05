#Backend-agnostic GUID Type
#http://docs.sqlalchemy.org/en/latest/core/custom_types.html#backend-agnostic-guid-type

from sqlalchemy.types import TypeDecorator, CHAR, BigInteger, VARCHAR, UnicodeText
from sqlalchemy.dialects import postgresql
import uuid, IPy, json, six

#override compilation of BigInteger for sqlite to Integer
#https://bitbucket.org/zzzeek/sqlalchemy/issues/2074/map-biginteger-type-to-integer-to-allow
from sqlalchemy.ext.compiler import compiles
@compiles(BigInteger, 'sqlite')
def bi_c(element, compiler, **kw):
    return "INTEGER"

class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), storing as stringified hex values.
    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)

#https://github.com/curvetips/s4u.sqlalchemy/blob/master/src/s4u/sqlalchemy/inet.py
class INET(TypeDecorator):
    """Platform-independent INET type.

    This type stores IPv4 and IPv6 addresses and netmarks. This type uses the `IPy.IP <http://pypi.python.org/pypi/IPy>`_ instances
    to store values. As input it will accept also a standard python string.
    When using a PostgreSQL backend the native INET type is used. On other databases values are stored as CHAR(42).
    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.INET())
        else:
            return dialect.type_descriptor(CHAR(42))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, IPy.IP):
                value = IPy.IP(value)
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return IPy.IP(value)

#https://sqlalchemy-utils.readthedocs.io/en/latest/_modules/sqlalchemy_utils/types/json.html
class JSON(TypeDecorator):
    """"Platform-independent JSON type.

    JSON type offers way of saving JSON data structures to database. On
    PostgreSQL the underlying implementation of this data type is 'json' while
    on other databases its simply 'text'.
    """
    impl = UnicodeText

    def __init__(self, *args, **kwargs):
        super(JSON, self).__init__(*args, **kwargs)

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.JSON())
        else:
            return dialect.type_descriptor(self.impl)

    def process_bind_param(self, value, dialect):
        if dialect.name == 'postgresql':
            return value
        if value is not None:
            value = six.text_type(json.dumps(value))
        return value

    def process_result_value(self, value, dialect):
        if dialect.name == 'postgresql':
            return value
        if value is not None:
            value = json.loads(value)
        return value
