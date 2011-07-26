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
import unittest

from tornado.web import RequestHandler

from tornadotools.route import Route


@Route(r"/test1")
class TestHandler1(RequestHandler):
    pass


@Route(r"/test2", name="wohaa")
class TestHandler2(RequestHandler):
    pass


@Route(r"/test3", name="buh", initialize={'really': "yeah"},
    host="www\.example\.com")
class TestHandler3(RequestHandler):
    pass


class RouteTest(unittest.TestCase):

    def test_route_decorator(self):
       routes = Route.routes()

       self.assertEqual(r"/test1$", routes[0].regex.pattern)
       self.assertEqual(TestHandler1, routes[0].handler_class)
       self.assertEqual({}, routes[0].kwargs)


       self.assertEqual(r"/test2$", routes[1].regex.pattern)
       self.assertEqual(TestHandler2, routes[1].handler_class)
       self.assertEqual({}, routes[1].kwargs)
       self.assertEqual("wohaa", routes[1].name)

       self.assertEqual(r"/test3$", routes[2].regex.pattern)
       self.assertEqual(TestHandler3, routes[2].handler_class)
       self.assertEqual({'really': 'yeah'}, routes[2].kwargs)
       self.assertEqual("buh", routes[2].name)


if __name__ == '__main__':
    unittest.main()
