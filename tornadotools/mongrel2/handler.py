#
# Copyright (c) 2011 Daniel Truemper truemped@googlemail.com
#
# handler.py 07-Jul-2011
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
import uuid

from tornado.httpserver import HTTPRequest

import zmq
from zmq.eventloop import stack_context
from zmq.eventloop.ioloop import IOLoop
from zmq.eventloop.zmqstream import ZMQStream

from .request import MongrelRequest


class Mongrel2Handler(object):
    """
    A Mongrel2 handler class for use with Tornado Applications.
    """

    def __init__(self, request_callback, pull_addr=None, pub_addr=None,
        io_loop=None, ctx=None, sender_id=None, no_keep_alive=False):

        self.request_callback = request_callback
        self.io_loop = io_loop or IOLoop.instance()
        self.sender_id = sender_id or str(uuid.uuid4())
        self.no_keep_alive = no_keep_alive

        self._zmq_context = ctx or zmq.Context()
        self._listening_stream = None
        self._sending_stream = None
        self._started = False

    def add_m2_pair(self, pull_addr, pub_addr):
        """
        Add a Mongrel2 socket pair to the handler.

        By calling `add_m2_pair` multiple times, you may listen to multiple
        Mongrel2 servers.

        `pull_addr` and `pub_addr` must be valid ZeroMQ socket identifiers.
        """
        self._listening_stream = self._create_listening_stream(pull_addr)
        self._sending_stream = self._create_sending_stream(pub_addr)

    def start(self):
        """
        Start to listen for incoming requests.
        """
        assert not self._started
        self._listening_stream.on_recv(self._recv_callback)
        self._started = True

    def _create_listening_stream(self, pull_addr):
        """
        Create a stream listening for Requests. The `self._recv_callback`
        method is asociated with incoming requests.
        """
        sock = self._zmq_context.socket(zmq.PULL)
        sock.connect(pull_addr)
        stream = ZMQStream(sock, io_loop=self.io_loop)

        return stream

    def _create_sending_stream(self, pub_addr):
        """
        Create a `ZMQStream` for sending responses back to Mongrel2.
        """
        sock = self._zmq_context.socket(zmq.PUB)
        sock.setsockopt(zmq.IDENTITY, self.sender_id)
        sock.connect(pub_addr)
        stream = ZMQStream(sock, io_loop=self.io_loop)

        return stream

    def _recv_callback(self, msg):
        """
        Method is called when there is a message coming from a Mongrel2 server.
        This message should be a valid Request String.
        """
        m2req = MongrelRequest.parse(msg[0])
        MongrelConnection(m2req, self._sending_stream, self.request_callback,
            no_keep_alive=self.no_keep_alive)


class MongrelConnection(object):
    """
    Handles the connection to the Mongrel2 server.

    We execute the request callback and provide methods for sending data to the
    server/client and eventually finish the request and HTTP connection.
    """

    MessageTrackers = {}
    """
    A mapping between messages sent and their respective `MessageTacker`. This
    helps us checking if we should close the connection after a chunk of data
    has been sent to M2.
    """

    def __init__(self, m2req, stream, request_callback, no_keep_alive=False)
        self.m2req = m2req
        self.stream = stream
        self.request_callback = request_callback
        self.no_keep_alive = no_keep_alive

        self._request = None
        self._request_finished = False
        self._message_trackers = []

        self._execute = stack_context.wrap(self._begin_request)
        self._execute()

    def _begin_request(self):
        """
        Actually start executing this request.
        """
        self._request = HTTPRequest(connection=self,
            method=self.m2req.headers.get("METHOD"),
            uri=self.m2req.path,
            version=self.m2req.headers.get("VERSION"),
            headers=self.m2req.headers,
            remote_ip="")

        if len(self.m2req.body) > 0:
            req.body = self.m2req.body

        self.request_callback(self._request)

    def write(self, chunk):
        """
        Write a chunk of data to the server.
        """
        self._send(chunk)

    def finish(self):
        """
        Finish this connection.
        """
        assert self._request, "Request closed"
        self._request_finished = True
        if not self._still_sending()
            self._finish_request()

    def _still_sending(self):
        """
        Check if we have `MessageTracker` with pending messages.
        """
        for tracker in self._message_trackers:
            if not tracker.done():
                return True
            else:
                self._message_trackers.remove(tracker)

        return False

    def maybe_finish(self):
        """
        When ZeroMQ has sent a message, maybe we need to check if the HTTP
        connection needs to be closed.
        """
        if self._request_finished and not self._still_sending():
            self._finish_request()

    def _finish_request(self):
        """
        Maybe we should close the HTTP connection. If so, do this here. If not,
        we can destroy this connection and let the `Mongrel2Handler` handle the
        next request.
        """
        if self.m2req.should_close() or self.no_keep_alive:
            self._send("")
        self._request = None

    def _send(self, msg):
        """
        Raw send to the given connection ID at the given uuid, mostly used 
        internally.
        """
        uuid = self.m2req.sender
        conn_id = self.m2req.conn_id

        header = "%s %d:%s," % (uuid, len(str(conn_id)), str(conn_id))
        zmq_message = header + ' ' + msg

        if msg = "":
            # kill messages do not need to be tracked
            self.stream.send(zmq_message)
        else:
            tracker = self.stream.send(zmq_message, copy=False, track=True)
            self._message_trackers.append(tracker)
            MongrelConnection.MessageTrackers[zmq_message] = (self, tracker)
