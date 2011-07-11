#
# Copyright (c) 2008 Daniel Truemper truemped@googlemail.com
#
# __init__.py 09-Jul-2011
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
A Mongrel2 handler for Tornado based web apps.

**Please note that this is considered EXPERIMENTAL!** Any feedback is very
welcome! Add issues_ or fork the code at Github_!

Usage is quite simple::

    from tornadotools.mongrel2.handler import Mongrel2Handler
    from zmq.eventloop.ioloop import IOLoop
    from zmq.eventloop.ioloop import install as install_ioloop

    # install the zmq version of the IOLoop
    install_ioloop()

    l = IOLoop.instance()

    # create the handler with the `tornado.web.Application`
    handler = Mongrel2Handler(app, "tcp://127.0.0.1:9999", "tcp://127.0.0.1:9998", io_loop=l)

    # start listening for incoming messages from Mongrel2
    handler.start()

    # enter the ioloop
    l.start()


The Mongrel2 configuration could be as simple as this::

    test_handler = Handler(
        send_spec = "tcp://127.0.0.1:9999",
        send_ident = "760deb97-b486-4e6a-b801-63fc01e93259",
        recv_spec = "tcp://127.0.0.1:9998",
        recv_ident = ""
    )

    test = Server(
        uuid = "08eb25ae-50ef-43e2-bb3d-cf70437418fa",
        name = "Test",

        chroot = "./",
        pid_file = "/run/dev.pid",
        access_log = "/logs/dev-access.log",
        error_log = "/logs/dev-error.log",

        default_host = "localhost",
        port = 6767,

        hosts = [
            Host(
                name = "localhost",
                routes={
                    "/": test_handler
                }
            )
        ]
    )

    settings = {
        "upload.temp_store" : "/tmp/mongrel2-uploads/upload.XXXXXX"
    }

    servers = [test]


When uploading data (files, e.g.), note that in contrast to plain Tornado, the
actual file storage is handled by Mongrel2 itself. What you should do in your
request handler is something like this::

    class Handler(tornado.web.RequestHandler):
        def put(self):
            if self.request.headers.get("x-mongrel2-upload-done", None):
                # file was large, thus handled by mongrel2
                filename = self.request.headers.get("x-mongrel2-upload-done")
                body = open(filename, 'r').read()
            elif len(self.request.files) > 0:
                # Tornado handled the file upload
                pass
            elif len(self.request.body) > 0:
                # small file?!
                pass

To keep Mongrel2 from handling the uploads, you simply have to remove the
`upload.temp_store` setting from the config.
"""

from .handler import Mongrel2Handler
