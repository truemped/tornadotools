#
# Copyright (c) 2008 Daniel Truemper truemped@googlemail.com
#
# forms_vows.py 01-Aug-2011
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
import urllib

from tornado.web import Application, RequestHandler
from wtforms import TextField, validators

from tornadotools.route import Route
from tornadotools.forms import Form

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoContext, TornadoSubContext


class SampleForm(Form):

    user = TextField('Username', [
        validators.Length(min=4,
        message="Username should have at least 4 characters!")
    ])

    email = TextField('Email', [
        validators.Length(min=5,
            message="Email should have a least 5 characters!"),
        validators.Email(
            message="This is not a valid email address")
    ])


@Route(r'/forms/')
class SampleFormHandler(RequestHandler):

    def get(self):
        form = SampleForm(self)
        if form.validate():
            self.finish({'ok': 'true'})
        else:
            self.set_status(400)
            resp = {'error': 'notvalidating'}
            if form.user.errors:
                resp['user.errors'] = form.user.errors
            if form.email.errors:
                resp['email.errors'] = form.email.errors
            self.finish(resp)


@Vows.batch
class Forms(TornadoContext):

    def _get_app(self):
        return Application(Route.routes())

    class WithAMissingParameter(TornadoSubContext):

        def topic(self):
            return self._get('/forms/?%s' % urllib.urlencode([('user', 'test')]))

        def codeShouldEqual400(self, topic):
            expect(topic.code).to_equal(400)

        def bodyShouldBe(self, topic):
            expect(topic.body).to_equal('{"email.errors": ["Email should ' \
                + 'have a least 5 characters!", "This is not a valid email ' \
                + 'address"], "error": "notvalidating"}')

    class WithAWrongParameter(WithAMissingParameter):

        def topic(self):
            return self._get('/forms/?%s' % urllib.urlencode([
                ('user', 'test'),
                ('email', 'notanemail')
            ]))

        def bodyShouldBe(self, topic):
            expect(topic.body).to_equal('{"email.errors": ["This is not a ' \
                + 'valid email address"], "error": "notvalidating"}')

    class WithACorrectInput(TornadoSubContext):

        def topic(self):
            return self._get('/forms/?%s' %
                urllib.urlencode([
                    ('user', 'test'),
                    ('email', 'email@web.de')
                ])
            )

        def shouldBeSuccessful(self, topic):
            expect(topic.code).to_equal(200)

        def bodyShouldBe(self, topic):
            expect(topic.body).to_equal('{"ok": "true"}')
