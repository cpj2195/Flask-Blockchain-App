from flask import request, jsonify, url_for
from flask.views  import MethodView
from collections import defaultdict
from sqlalchemy.orm.attributes import CollectionAttributeImpl, ScalarObjectAttributeImpl
import re, json
from common import exceptions, utils
import schemas
from jquery_unparam import jquery_unparam
import collections
from common.logging_config import applogger
#http://flask.pocoo.org/docs/0.12/views/#method-views-for-apis
class MethodViewBase(MethodView):
    def get(self, *args, **kwargs)     : raise exceptions.MethodNotAllowed('The method is not allowed for the requested URL')
    def put(self, *args, **kwargs)     : raise exceptions.MethodNotAllowed('The method is not allowed for the requested URL')
    def post(self, *args, **kwargs)    : raise exceptions.MethodNotAllowed('The method is not allowed for the requested URL')
    def delete(self, *args, **kwargs)  : raise exceptions.MethodNotAllowed('The method is not allowed for the requested URL')
    def head(self, *args, **kwargs)    : raise exceptions.MethodNotAllowed('The method is not allowed for the requested URL')
    def patch(self, *args, **kwargs)   : raise exceptions.MethodNotAllowed('The method is not allowed for the requested URL')
    def trace(self, *args, **kwargs)   : raise exceptions.MethodNotAllowed('The method is not allowed for the requested URL')
    def options(self, *args, **kwargs) : raise exceptions.MethodNotAllowed('The method is not allowed for the requested URL')

class SQLAlchemyQuery(object):
    def __init__(self, db_model):
        self.db_model = db_model

    def _create_query_filter(self, filtername, attr, value):
        criteria_dict = {
            "eq"         : lambda: attr == value,
            "ne"         : lambda: attr != value,
            "lt"         : lambda: attr < value,
            "lte"        : lambda: attr <= value,
            "gt"         : lambda: attr > value,
            "gte"        : lambda: attr >= value,
            "in"         : lambda: attr.in_(value),
            "nin"        : lambda: attr.notin_(value),
            "contains"   : lambda: attr.contains(value),
            "icontains"  : lambda: attr.ilike("%" + value + "%"),
            "startswith" : lambda: attr.startswith(value),
            "istartswith": lambda: attr.ilike(value + "%"),
            "endswith"   : lambda: attr.endswith(value),
            "iendswith"  : lambda: attr.ilike("%" + value)}
        return criteria_dict[filtername]()

    def _create_filter(self, db_model, fieldname, filtername, value):
            if '.' not in fieldname:
                return self._create_attribute_filter(db_model, fieldname, filtername, value)
            else:
                return self._create_relation_filter(db_model, fieldname, filtername, value)

    def _create_attribute_filter(self, db_model, fieldname, filtername, value):
        attr = getattr(db_model, fieldname, None)
        if attr: return self._create_query_filter(filtername, attr, value)
        else:    raise exceptions.BadRequest("The filter field '{}' is not valid.".format(fieldname), fieldname=fieldname, filtername=filtername)

    def _create_relation_filter(self, db_model, fieldname, filtername, value):
        rel_name, fieldname = fieldname.split(".",1)
        rel_attr = getattr(db_model, rel_name, None)
        #https://stackoverflow.com/questions/6843144/how-to-find-sqlalchemy-remote-side-objects-class-or-class-name-without-db-queri
        try: rel_db_model = rel_attr.property.mapper.class_
        except: raise exceptions.BadRequest("The filter field '{}' is not valid.".format(rel_name+'.'+fieldname),\
                                            relation_name=rel_name, fieldname=fieldname, filtername=filtername)
        #https://stackoverflow.com/questions/22861960/sqlalchemy-check-if-relationshipproperty-is-scalar
        rel_type = 'scalar' if isinstance(rel_attr.impl, ScalarObjectAttributeImpl) else 'collection'
        query_filter = self._create_filter(rel_db_model, fieldname, filtername, value)
        if rel_type == 'collection': return rel_attr.any(query_filter)
        else:                        return rel_attr.has(query_filter)

    def sqlalchemy_filters(self, input_filters):
        criterions = []
        for fieldname, filtername, value in input_filters:
            query_filter = self._create_filter(self.db_model, fieldname, filtername, value)
            criterions.append(query_filter)
        return criterions

    def sqlalchemy_orders(self, input_sorts):
        criterions = []
        for direction, fieldname in input_sorts:
            attr = getattr(self.db_model, fieldname, None)
            if not attr: raise exceptions.BadRequest("The sort field '{}' is not valid.".format(fieldname), fieldname=fieldname, direction=direction)
            criteria_dict = {
                "+": lambda: attr.asc(),
                "-": lambda: attr.desc()}
            criterions.append(criteria_dict[direction]())
        return criterions

    def fetch_filter_sort_rows(self, input_filters=None, input_sorts=None):
        query = self.db_model.query
        if input_filters: query = query.filter(*self.sqlalchemy_filters(input_filters))
        if input_sorts:   query = query.order_by(*self.sqlalchemy_orders(input_sorts))
        return query.all()

class APIBase(MethodViewBase):
    @property
    def input_filters(self):
        """:filtering:
        A url query may contain these filters, and multple criteria can be combined
        *   `eq`,          equality
        *   `ne`,          non equality
        *   `lt`,          less than
        *   `lte`,         less than or equal to
        *   `gt`,          greater than
        *   `gte`,         greater than or equal to
        *   `in`,          in the specified list
        *   `nin`,         not in the specified list
        *   `contains`,    contains string
        *   `icontains`,   contains string (case insensitive)
        *   `startswith`,  string startswith
        *   `istartswith`, string startswith (case insensitive)
        *   `endswith`,    string endswith
        *   `iendswith`,   string endswith (case insensitive)

        /api/User/?filter[name]=endswith:"Simpson"
        /api/User/?filter[parents.name]=endswith:"Home"
        /api/User/?filter[name]=in:["Homer Simpson", "Darth Vader"]&filter[age]=eq:101
        /api/User/?filter[email]=startswith:"lisa"&filter[age]=lt:20

        be careful with queries like
        /api/User/?filter[parents.children.name]=eq:"lisa"
        while this query will work, it might not work as you expect
        the query will first get all parents whose children have the name "lisa"
        then the query will return all users who have parents that are returned by the previous step.

        -raises BadRequest, If a filtername is used, which does not exist.
        -raises BadRequest, If the value of a filter is not a JSON object.
        """
        filters = []
        KEY_RE = re.compile(r"filter\[([A-z0-9_\.]+)\]")
        # The first group captures the filters, the second captures the value.
        VALUE_RE = re.compile(
            r"(eq:|ne:|lt:|lte:|gt:|gte:|in:|nin:"\
            r"|contains:|icontains:|startswith:|istartswith:|endswith:"\
            r"|iendswith:)(.*)"
        )
        for key in request.args.keys():
            for value in request.args.getlist(key):
                key_match = re.match(KEY_RE, key)
                value_match = re.match(VALUE_RE, value)
                # If the key indicates a filter, but the filtername does not exist,
                # throw a BadRequest exception.
                if key_match and not value_match:
                    filtername = value.split(':')[0]
                    raise exceptions.BadRequest("The filter '{}' does not exist.".format(filtername), source_parameter=key)
                # The key indicates a filter and the filternames exists.
                elif key_match and value_match:
                    field = key_match.group(1)
                    # Remove the tailing ":" from the filter.
                    filtername = value_match.group(1)
                    filtername = filtername[:-1]
                    # The value may be encoded as json.
                    value = value_match.group(2)
                    try: value = json.loads(value)
                    except: raise exceptions.BadRequest("The value of the filter '{}' is not a JSON object.".format(filtername), source_parameter=key)
                    # Add the filter.
                    filters.append((field, filtername, value))
        return filters

    @property
    def input_sorts(self):
        """:ordering:
        An order criterion and column name can be specified in the url
        /api/Post?sort=name,-age
        see http://jsonapi.org/format/#fetching-sorting
        """
        tmp = request.args.get('sort')
        tmp = tmp.split(",") if tmp else list()
        sort = list()
        for field in tmp:
            field = field.strip()
            if field[0] == "-":
                sort.append(("-", field[1:]))
            else:
                sort.append(("+", field))
        return sort

    def fetch_filter_sort_rows(self, db_model):
        q = SQLAlchemyQuery(db_model)
        return q.fetch_filter_sort_rows(self.input_filters, self.input_sorts)

    def select_fields(self, raw_response_data, exclude=None, many=False):
        """:feild selection:
        Fields in the response can be pre-selected by passing the feilds agrument in the query string
        /api/User?fields=name,parents.name
        -raises BadRequest, If a fieldname is not avaibale in the response data.
        """
        if not raw_response_data:
            raise exceptions.NotFound("No data available for the requested query")
        def _fetch(schema, data, many, exclude, only=None):
            kwargs = {'only': only} if only else {}
            if exclude: kwargs['exclude'] = exclude
            #many=True attribute does not work well for relationships that are dynamically lazy loaded
            if many: return [schema(**kwargs).dump(response_data).data for response_data in data]
            else:    return  schema(**kwargs).dump(data).data
        fields = request.args.get('fields', None)
        if fields:
            try: return _fetch(self.response_schema, raw_response_data, many, exclude, only=fields.split(','))
            except KeyError as err:
                raise exceptions.BadRequest("feild '{}' not found in response data".format(err.message))
        else:
            return _fetch(self.response_schema, raw_response_data, many, exclude)

    @staticmethod
    def _get_schema_fields(schema):
        fields = {}
        schema_fields = schema.fields if hasattr(schema, 'fields') else schema
        for key, value in schema_fields.items():
            if hasattr(value, 'schema'):
                fields = fields.items()
                fields.extend([("{k}.{fk}".format(k=key, fk=fk), value_type) for fk, value_type in APIBase._get_schema_fields(value.schema).items()])
                fields = dict(fields)
            value_type = value.__class__.__name__
            fields[key] = {'type'  : value_type}
            if value_type == 'EnumField': fields[key]['values'] = value.enum.__members__.keys()
        return fields

    @classmethod
    def get_api_doc(cls):
        result_data = {'_self': {}}
        url_parameter = cls.api_url.split('/')[-1]
        if 'int:' in url_parameter:
            parameter = url_parameter.strip('<>').split(':')[-1]
            url = url_for('.'+cls.api_endpoint, **{parameter: 9999999999999999})
            result_data['_self']['url'] = url.replace('9999999999999999', '{'+parameter+'}')
            result_data['_self']['templated'] = True
        else:
             result_data['_self']['url'] = url_for('.'+cls.api_endpoint)
        #add url documentation
        result_data['_self']['docs'] = cls.__doc__
        #add method documentation
        methods_doc = defaultdict(lambda: defaultdict(list))
        for perms, methods in cls.api_permissions:
            for method in methods:
                methods_doc[method]['required_permissions'].extend(perms)
                methods_doc[method]['docs'] = [l.strip() for l in str(getattr(cls, method.lower()).__doc__).\
                                               format(api_filtering_doc=cls.input_filters.__doc__,
                                                      api_sorting_doc=cls.input_sorts.__doc__,
                                                      api_field_selection_doc=cls.select_fields.__doc__).split("\n")]
                methods_doc[method]['rate_limit'] = cls.api_rate_limit
        result_data['_self']['allowed_methods'] = methods_doc.keys()
        result_data['_self']['method_docs'] = methods_doc
        #add information about returned fields
        result_data['_self']['allowed_response_fields'] = APIBase._get_schema_fields(cls.response_schema())
        result_data['_self']['allowed_request_fields']  = APIBase._get_schema_fields(cls.request_schema())
        return result_data

    def get_parsed_request_data(self):
        """combine the request data in query string and json body
        used mainly to record the requests for POST and PATCH calls
        """
        #assume query string is in the format of a jQuery param, to enable support for nested dictionaries in the query string
        #https://api.jquery.com/jQuery.param/
        query_string_dict = jquery_unparam(request.query_string)
        #override with data in json if available
        if request.json: query_string_dict.update(request.json)
        applogger.debug(request.json)
        request_data   = self.request_schema().load(query_string_dict)
        applogger.debug(request_data)
        request_errors = request_data.errors
        request_data   = request_data.data
        applogger.debug(request_data)
        if request_errors: raise exceptions.BadRequest('error in request format', errors=request_errors)
        #add additional request information to request_data
        request_data['source_ip']         = utils.get_request_ip()
        request_data['user_agent_string'] = request.user_agent.string
        request_data['user_agent']        = {'platform': request.user_agent.platform,
                                             'browser' : request.user_agent.browser,
                                             'version' : request.user_agent.version,
                                             'language': request.user_agent.language}
        return request_data

    @staticmethod 
    def convert(data):
        if isinstance(data, basestring):
            return str(data)
        elif isinstance(data, collections.Mapping):
            return dict(map(APIBase.convert, data.iteritems()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(APIBase.convert, data))
        else:
            return data

    def options(self, **kwargs):
        '''get information about allowed methods to API url'''
        return jsonify(self.__class__.get_api_doc())
