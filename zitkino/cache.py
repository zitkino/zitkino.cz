# -*- coding: utf-8 -*-


from hashlib import sha1
from functools import wraps

from flask import request, make_response
from werkzeug.contrib.cache import FileSystemCache


class Cache(FileSystemCache):
    """Simple file system cache for views."""

    def __init__(self, app):
        super(Cache, self).__init__(
            app.config['CACHE_DIR'],
            default_timeout=app.config['CACHE_DEFAULT_TIMEOUT']
        )

    def cached(self, timeout=None, key='view/{request.path}'):
        """View decorator."""
        timeout = timeout or self.default_timeout

        def decorator(f):
            @wraps(f)
            def decorated_view(*args, **kwargs):
                cache_key = key.format(request=request)

                response = self.get(cache_key)
                if response is not None:
                    return response.make_conditional(request)  # send HTTP 304

                rv = f(*args, **kwargs)
                response = make_response(rv)

                if isinstance(rv, unicode):  # ensure HTTP 304 for strings
                    response.set_etag(sha1(rv.encode('utf-8')).hexdigest())

                response.freeze()
                self.set(cache_key, response, timeout=timeout)

                return response
            return decorated_view
        return decorator
