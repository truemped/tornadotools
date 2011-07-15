#
# Copyright (c) 2011 Daniel Truemper truemped@googlemail.com
#
# caching.py 12-Jul-2011
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
"""
A caching decorator for asynchronous functions.

The decorated function has to accept a `callback` parameter. The `callback`
itself has to accept only one parameter, the `result`::

    from tornadotools.caching import Cache

    def result_cb(result):
        print result

    @Cache(timedelta(hours=1))
    def get_async(argument1, argument2, callback=None):
        async_http_client.fetch(X, callback)

    def get_cached():
        get_async(1,2, result_cb)

You can also combine the `Cache` decorator with the `adisp` methods::

    from tornadotools.caching import Cache

    @adisp.async
    @Cache(timedelta(hours=1))
    def get_async(argument1, argument2, callback=None):
        async_http_client.fetch(X, callback)

    @adisp.process
    def get_cached():
        result = yield get_async(1,2, result_cb)

If your keyword argument for the `callback` has a different name, you can
change this in the decorator::

    from tornadotools.caching import Cache

    @Cache(timedelta(hours=1), cbname="cb")
    def get_async(argument1, argument2, callback=None):
        async_http_client.fetch(X, callback)
    get_async = adisp.async(get_async, cbname="cb")

By default, the `tornadotools.caching.cache_key` method will be used to compute
the key for the cache. You could also provide your own method::

    from tornadotools.caching import Cache

    def my_key_method(*args, **kwargs):
        return kwargs.get('sessionid', cache_key(*args, **kwargs))

    @Cache(timedelta(hours=1), cache_key_method=my_key_method)
    def ...
"""
from datetime import datetime, timedelta
from functools import wraps


def cache_key(*args, **kwargs):
    """
    Base method for computing the cache key with respect to the given
    arguments.
    """
    key = ""
    for arg in args:
        if callable(arg):
            key += ":%s" % repr(arg)
        else:
            key += ":%s" % str(arg)

    return key


class Cache(object):
    """
    The `Cache` decorator.
    """

    def __init__(self, ttl, cbname="callback", cache_key_method=cache_key):
        self.ttl = ttl
        self.cbname = cbname
        self.cache_key_method = cache_key_method

        self.cache = dict()
        self.func = None

    def __call__(self, func):
        self.func = func
        
        @wraps(func)
        def _inner_func(*args, **kwargs):
            self._cached_func(*args, **kwargs)

        return _inner_func

    def _cached_func(self, *args, **kwargs):
        cb = kwargs.get(self.cbname)
        key = self.cache_key_method(*args, **kwargs)

        if key in self.cache:
            (cached_result, exp_time) = self.cache[key]
            if exp_time > datetime.now():
                cb(cached_result)
                return

        kwargs[self.cbname] = self._caching_callback(key, cb)
        self.func(*args, **kwargs)

    def _caching_callback(self, key, callback):
        
        def _inner_cache(result):
            self.cache[key] = (result, datetime.now() + self.ttl)
            callback(result)

        return _inner_cache
