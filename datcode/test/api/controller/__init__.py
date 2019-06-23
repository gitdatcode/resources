import datetime
import json
import logging
import random
import time
import os

from tornado.testing import AsyncHTTPTestCase

from pypher.builder import Pypher

# we must set the environment here
os.environ['datcode_environment'] = 'testing'

from datcode.bootstrap import create_application, MAPPER
from datcode.common.model.graph.node import User
from datcode.common.model.messages import get_message


logging.disable(logging.CRITICAL)


APPLICATION = create_application()


class BaseTest(AsyncHTTPTestCase):
    
    def get_app(self):
        return APPLICATION

    def get_message(self, message):
        return get_message(message)
    
    def setUp(self):
        super(BaseTest, self).setUp()

        self.mapper = MAPPER

    def tearDown(self):
        self.empty_graph()

    def empty_graph(self):
        p = Pypher()

        p.MATCH.node('n').DETACH.DELETE.node('n')

        self.mapper.query(pypher=p)

    def random_lat_lng(self):
        def rng(low, high):
            return random.random() * (low - high) + high

        return {
            'lat': rng(-180, 180),
            'lon': rng(-180, 180),
        }

    def get_email(self, email_address, mapping, success=True):
        from datcode.common.model.email.mapping import MAPPINGS

        subject = MAPPINGS[mapping]['subject']
        success = 'true' if success else 'false'
        q = '''
            MATCH (n:`EmailLog`)
            WHERE
                n.success = {success} AND n.email = '{email}' AND n.subject = '{subject}'
            RETURN n
        '''.format(email=email_address, success=success, subject=subject)

        return self.mapper.query(query=q)

    def iso_date(self):
        if time.localtime():
            utc_offset_sec = time.altzone
        else:
            utc_offset_sec = time.timezone

        utc_offset = datetime.timedelta(seconds=-utc_offset_sec)

        return datetime.datetime.now().replace(
            tzinfo=datetime.timezone(offset=utc_offset)).isoformat()

    def set_headers(self, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = {}

        if 'content-type' not in map(str.lower, kwargs['headers'].keys()):
            kwargs['headers'].update({'content-type': 'application/json'})

        return kwargs

    def resp_cookie(self, resp):
        if 'Set-Cookie' in resp.headers:
            return resp.headers['Set-Cookie'].split(';')[0]

        raise Exception('Resp doesnt have cookie {}'.format(resp.headers))

    def json_response(self, response):
        return json.loads(response.body.decode('utf-8'))

    def create_request_user(self, access_level=0):
        return self.create_graph_user(access_level=access_level,
            with_login=True)

    def create_graph_user(self, access_level=0, with_login=False):
        params = {
            'email_address': 'graph_user{}@email.com'.format(random.random()),
            'password': 'password',
            'password2': 'password',
            'access_level': access_level,
        }
        user = User(properties=params)
        self.mapper.save(user).send()

        if not with_login:
            return user

        r, cookie = self.login_request(params['email_address'],
            params['password'])

        return user, cookie

    def login_request(self, email_address, password):
        resp = self.post('/api/login', body=json.dumps({
            'email_address': email_address,
            'password': password,
        }))

        return resp, self.resp_cookie(resp)

    def get(self, url, *args, **kwargs):
        kwargs['method'] = 'GET'
        kwargs['allow_nonstandard_methods'] = True

        resp = self.fetch(url, *args, **kwargs)
        resp.data = json.loads(resp.body)

        return resp

    def post(self, url, *args, **kwargs):
        kwargs = self.set_headers(**kwargs)
        kwargs['method'] = 'POST'
        kwargs['allow_nonstandard_methods'] = True

        if 'body' not in kwargs:
            kwargs['body'] = ''

        resp = self.fetch(url, *args, **kwargs)
        resp.data = json.loads(resp.body)

        return resp

    def put(self, url, *args, **kwargs):
        kwargs = self.set_headers(**kwargs)
        kwargs['method'] = 'PUT'
        kwargs['allow_nonstandard_methods'] = True

        if 'body' not in kwargs:
            kwargs['body'] = ''

        resp = self.fetch(url, *args, **kwargs)
        resp.data = json.loads(resp.body)

        return resp

    def delete(self, url, *args, **kwargs):
        kwargs = self.set_headers(**kwargs)
        kwargs['method'] = 'DELETE'
        kwargs['allow_nonstandard_methods'] = True
        resp = self.fetch(url, *args, **kwargs)
        resp.data = json.loads(resp.body)

        return resp