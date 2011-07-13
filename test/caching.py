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
from datetime import timedelta
import random
import unittest

from tornadotools.adisp import async, process
from tornadotools.caching import Cache


class CachingTest(unittest.TestCase):

    @async
    @Cache(timedelta(hours=2))
    def echo(self, key, callback=lambda x: x):
        callback(key + random.randint(0,1000))

    @process
    def test_basic_caching(self):

        result1 = yield self.echo(0)
        result2 = yield self.echo(0)
        self.assertEqual(result1, result2)

        result3 = yield self.echo(1)
        self.assertNotEqual(result2, result3)

    @Cache(timedelta(hours=2), cbname="cb")
    def echo_cb(self, key, cb=None):
        cb(key + random.randint(0, 1000))
    echo_cb = async(echo_cb, cbname="cb")

    @process
    def test_caching_with_different_cbname(self):

        result1 = yield self.echo_cb(0)
        result2 = yield self.echo_cb(0)
        self.assertEqual(result1, result2)

        result3 = yield self.echo_cb(1)
        self.assertNotEqual(result2, result3)


if __name__ == '__main__':
    unittest.main()
