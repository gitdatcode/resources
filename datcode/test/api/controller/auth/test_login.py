import json
import random
import unittest

from datcode.test.api.controller import BaseTest


class LoginTests(BaseTest):
    uri = '/api/login'

    def test_can_log_in(self):
        user = self.create_graph_user()
        body = json.dumps({
            'email_address': user['email_address'],
            'password': user['password'],
        })
        resp = self.post(self.uri, body=body)

        self.assertEqual(200, resp.code)
        self.assertIn('Set-Cookie', resp.headers)

    def test_cannot_log_in_with_incorrect_password(self):
        user = self.create_graph_user()
        body = json.dumps({
            'email_address': user['email_address'],
            'password': user['password'] + 'xxxxxxxxx',
        })
        resp = self.post(self.uri, body=body)

        self.assertEqual(403, resp.code)

    def test_cannot_log_in_with_random_credentials(self):
        body = json.dumps({
            'email_address': 'email{}'.format(random.random()),
            'password': 'pass{}'.format(random.random()),
        })
        resp = self.post(self.uri, body=body)

        self.assertEqual(403, resp.code)


if __name__ == '__main__':
    unittest.main()