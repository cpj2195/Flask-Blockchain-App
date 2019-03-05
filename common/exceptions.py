#http://flask.pocoo.org/docs/0.12/patterns/apierrors/
from flask import jsonify


class HTTPError(Exception):

    def __init__(self, message, status_code, error_type, **kwargs):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        self.payload = kwargs

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['error_type'] = self.error_type
        return rv

class BadRequest(HTTPError):
    def __init__(self, message, **kwargs):
        HTTPError.__init__(self, message, status_code=400, error_type='bad_request', **kwargs)

class Unauthorized(HTTPError):
    def __init__(self, message, **kwargs):
        HTTPError.__init__(self, message, status_code=401, error_type='unauthorized', **kwargs)

class Forbidden(HTTPError):
    def __init__(self, message, **kwargs):
        HTTPError.__init__(self, message, status_code=403, error_type='forbidden', **kwargs)

class NotFound(HTTPError):
    def __init__(self, message, **kwargs):
        HTTPError.__init__(self, message, status_code=404, error_type='not_found', **kwargs)

class MethodNotAllowed(HTTPError):
    def __init__(self, message, **kwargs):
        HTTPError.__init__(self, message, status_code=405, error_type='method_not_allowed', **kwargs)

class TooManyRequests(HTTPError):
    def __init__(self, message, **kwargs):
        HTTPError.__init__(self, message, status_code=429, error_type='too_many_requests', **kwargs)

class ServiceUnavailable(HTTPError):
    def __init__(self, message, **kwargs):
        HTTPError.__init__(self, message, status_code=503, error_type='service_unavailable', **kwargs)

def handle_http_error(error, headers=None):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    if headers:
        for key, value in headers.items():
            response.headers[key] = value
    return response

def raise_exception(ex):
    raise ex

def register_error_handlers(app):
    #handle 400
    app.errorhandler(BadRequest)        (handle_http_error)
    app.errorhandler(400)               (lambda e: handle_http_error(BadRequest(e.description)))
    #handle 401
    app.errorhandler(Unauthorized)      (lambda e: handle_http_error(e, headers={'WWW-Authenticate': 'Basic realm="Login Required"'}))
    app.errorhandler(401)               (lambda e: handle_http_error(Unauthorized(e.description), headers={'WWW-Authenticate': 'Basic realm="Login Required"'}))
    #handle 403
    app.errorhandler(Forbidden)         (handle_http_error)
    app.errorhandler(403)               (lambda e: handle_http_error(Forbidden(e.description)))
    #handle 404
    app.errorhandler(NotFound)          (handle_http_error)
    app.errorhandler(404)               (lambda e: handle_http_error(NotFound(e.description)))
    #handle 405
    app.errorhandler(MethodNotAllowed)  (handle_http_error)
    app.errorhandler(405)               (lambda e: handle_http_error(MethodNotAllowed(e.description)))
    #handle 429
    app.errorhandler(TooManyRequests)   (handle_http_error)
    app.errorhandler(429)               (lambda e: handle_http_error(TooManyRequests('api ratelimit exceeded', rate_limit=e.description)))
    #handle 503
    app.errorhandler(ServiceUnavailable)(handle_http_error)
    app.errorhandler(503)               (lambda e: handle_http_error(ServiceUnavailable(e.description)))
    #handle 404
    app.errorhandler(NotFound)          (handle_http_error)
    app.errorhandler(404)               (lambda e: handle_http_error(NotFound(e.description)))
    return app
