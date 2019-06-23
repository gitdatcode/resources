import json
import uuid

from random import random

from datcode.test.api.controller import BaseTest
from datcode.common.model.graph.node import PasswordReset, EmailLog


class TestRequestPasswordChange(BaseTest):
    uri = '/api/password/forgot'

    def test_can_request_password_reset(self):
        user = self.create_graph_user()
        b = {
            'email_address': user['email_address'],
        }
        body = json.dumps(b)
        resp = self.post(self.uri, body=body)
        message = self.get_message('USER_PASSWORD_RESET_REQUESTED')['message']  

        self.assertEqual(200, resp.code)
        self.assertEqual(message, resp.data['message'])

        # ensure that the user has one connection on PasswordResetRequest
        user_mapper = self.mapper.get_mapper(user)
        codes = user_mapper(user)['PasswordResetRequest']()
        self.assertEqual(1, len(codes))

        # ensure that the email was sent
        res = self.get_email(user['email_address'], 'password_reset_request')

        self.assertEqual(1, len(res))

    def test_cannot_request_password_reset_invalid_email(self):
        user = self.create_graph_user()
        b = {
            'email_address': 'some_email{}@random.com'.format(random()),
        }
        resp = self.post(self.uri, body=json.dumps(b))
        message = self.get_message('ENTITY_DOESNT_EXIST')['message']

        self.assertEqual(403, resp.code)
        self.assertEqual(message, resp.data['message'])


class TestRequestPasswordChangeProcess(BaseTest):

    def create_reset(self):
        user = self.create_graph_user()
        user_mapper = self.mapper.get_mapper(user)
        b = {
            'email_address': user['email_address'],
        }
        self.post('/api/password/forgot', body=json.dumps(b))
        code = user_mapper(user)['PasswordResetRequest']().first()

        return user, code

    def test_can_reset_password_with_code(self):
        user, code = self.create_reset()
        new_pw = 'password_{}'.format(random())
        b = {
            'new_password1': new_pw,
            'new_password2': new_pw,
        }
        uri = '/api/password/reset/{}'.format(code['code'])
        resp = self.put(uri, body=json.dumps(b))
        message = self.get_message('USER_PASSWORD_UPADTED')['message']

        self.assertEqual(200, resp.code)
        self.assertEqual(message, resp.data['message'])

        # check the user node
        user = self.mapper.refresh(user)

        self.assertEqual(new_pw, user['password'])

        # check that the code has been used
        code = self.mapper.refresh(code)

        self.assertTrue(code['fulfilled'])

    def test_cannot_reset_password_wtih_mixmatched_passwords(self):
        user, code = self.create_reset()
        new_pw = 'password_{}'.format(random())
        new_pw2 = 'passwordsss222_{}'.format(random())
        b = {
            'new_password1': new_pw,
            'new_password2': new_pw2,
        }
        uri = '/api/password/reset/{}'.format(code['code'])
        resp = self.put(uri, body=json.dumps(b))
        message = self.get_message('USER_MISMATCHED_PASSWORD')['message']

        self.assertEqual(403, resp.code)
        self.assertEqual(message, resp.data['message'])

    def test_cannot_reset_password_with_invalid_code(self):
        code = str(uuid.uuid4())
        uri = '/api/password/reset/{}'.format(code)
        new_pw = 'password_{}'.format(random())
        b = {
            'new_password1': new_pw,
            'new_password2': new_pw,
        }
        resp = self.put(uri, body=json.dumps(b))
        message = self.get_message('USER_PASSWORD_RESET_INVALID')['message']

        self.assertEqual(403, resp.code)
        self.assertEqual(message, resp.data['message'])

    def test_cannot_reset_password_with_timeouted_code(self):
        user, code = self.create_reset()
        new_pw = 'password_{}'.format(random())
        b = {
            'new_password1': new_pw,
            'new_password2': new_pw,
        }
        uri = '/api/password/reset/{}'.format(code['code'])

        # break the code
        code['reset_timeout'] = 0
        self.mapper.save(code).send()

        resp = self.put(uri, body=json.dumps(b))
        message = self.get_message('USER_PASSWORD_RESET_INVALID')['message']

        self.assertEqual(403, resp.code)
        self.assertEqual(message, resp.data['message'])

    def test_cannot_reset_password_wtih_unfound_user(self):
        code = self.mapper.create(entity=PasswordReset)
        self.mapper.save(code).send()

        new_pw = 'password_{}'.format(random())
        b = {
            'new_password1': new_pw,
            'new_password2': new_pw,
        }
        uri = '/api/password/reset/{}'.format(code['code'])
        resp = self.put(uri, body=json.dumps(b))
        message = self.get_message('ENTITY_DOESNT_EXIST')['message']

        self.assertEqual(403, resp.code)
        self.assertEqual(message, resp.data['message'])

    def test_cannot_reset_password_with_already_fulfilled_code(self):
        user, code = self.create_reset()
        new_pw = 'password_{}'.format(random())
        b = {
            'new_password1': new_pw,
            'new_password2': new_pw,
        }
        uri = '/api/password/reset/{}'.format(code['code'])

        # break the code
        code.fulfill()
        self.mapper.save(code).send()

        resp = self.put(uri, body=json.dumps(b))
        message = self.get_message('USER_PASSWORD_RESET_INVALID')['message']

        self.assertEqual(403, resp.code)
        self.assertEqual(message, resp.data['message'])
