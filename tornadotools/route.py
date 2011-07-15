#
# Copyright (c) 2008 Daniel Truemper truemped@googlemail.com
#
# route.py 15-Jul-2011
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# under the License.
#
#
"""
Decorator for a `tornado.web.RequestHandler` configuring the route and
initialization dict.

The `Route` decorator stores all routes inside a class level list. You can then
add all routes to the application using the `Route.routes` method. Some
examples::

    from tornadotools.route import Route

    @Route(r"/")
    class SimpleHandler(RequestHandler):
        pass

    @Route(r"/test_with_name", name="test")
    class SimpleHandler2(RequestHandler):
        pass

    @Route(r"/test_with_init", initialize={'init': 'dictionary'})
    class SimpleHandler3(RequestHandler):
        pass

    app = Application([
        # other routes
        ] + Route.routes()
    )

Tornado also support multiple hosts. When you want to use this with the `Route`
decorator, you have to create the `tornado.web.Application` like this::

    from tornadotools.route import Route

    @Route(r"/.*", host="www\.example\.com")
    class HostHandler(RequestHandler):
        pass

    app = Application([])
    Route.routes(app)
"""
from tornado.web import URLSpec


class Route(object):
    """
    The `Route` decorator.
    """

    _routes = []
    """
    Class level list of routes.
    """

    def __init__(self, route, initialize={}, name=None, host=".*$"):
        self.route = route
        self.initialize = initialize
        self.name = name
        self.host = host

    def __call__(self, handler):
        """
        Called when we decorate a class.
        """
        name = self.name or handler.__name__
        spec = URLSpec(self.route, handler, self.initialize, name=name)
        self._routes.append({'host': self.host, 'spec': spec})
        return handler

    @classmethod
    def routes(cls, application=None):
        """
        Method for adding the routes to the `tornado.web.Application`.
        """
        if application:
            for route in cls._routes:
                application.add_handlers(route['host'], route['spec'])
        else:
            return [route['spec'] for route in cls._routes]
