import json
import random
import unittest

from datcode.test.api.controller import BaseTest


class LogoutTests(BaseTest):

    def test_can_log_out(self):
        user, cookie = self.create_request_user()
        headers = {'Cookie': cookie}
        r = self.post('/api/logout', headers=headers)

        self.assertTrue(200, r.code)

    def test_cannot_logout_with_valid_user_invalid_cookie(self):
        user, cookie = self.create_request_user()
        headers = {'Cookie': cookie + 'xxxx'}
        r = self.post('/api/logout', headers=headers)

        self.assertEqual(401, r.code)


if __name__ == '__main__':
    unittest.main()
