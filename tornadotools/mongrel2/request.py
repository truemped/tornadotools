#
# Copyright (c) 2011 Daniel Truemper truemped@googlemail.com
#
# request.py 07-Jul-2011
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
try:
    import simplejson as json
except ImportError:
    import json

import tnetstring


class MongrelRequest(object):
    """
    A Mongrel2 request object.
    """

    def __init__(self, sender, conn_id, path, headers, body):
        self.sender = sender
        self.path = path
        self.conn_id = conn_id
        self.headers = headers
        self.body = body
        
        if self.headers['METHOD'] == 'JSON':
            self.data = json.loads(body)
        else:
            self.data = {}

    @staticmethod
    def parse(msg):
        """
        Helper method for parsing a Mongrel2 request string and returning a new
        `MongrelRequest` instance.
        """
        sender, conn_id, path, rest = msg.split(' ', 3)
        headers, rest = tnetstring.pop(rest)
        body, _ = tnetstring.pop(rest)

        if type(headers) is str:
            headers = json.loads(headers)

        return MongrelRequest(sender, conn_id, path, headers, body)

    def is_disconnect(self):
        if self.headers.get('METHOD') == 'JSON':
            return self.data['type'] == 'disconnect'

    def should_close(self):
        """
        Check whether the HTTP connection of this request should be closed
        after the request is finished.

        We check for the `Connection` HTTP header and for the HTTP Version
        (only `HTTP/1.1` supports keep-alive.
        """
        if self.headers.get('connection') == 'close':
            return True
        elif 'content-length' in self.headers or \
            self.headers.get('METHOD') in ['HEAD', 'GET']:
            return self.headers.get('connection') != 'keep-alive'
        elif self.headers.get('VERSION') == 'HTTP/1.0':
            return True
        else:
            return False
