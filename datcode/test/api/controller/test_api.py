import json
import random
import unittest
import uuid

from tornado.web import HTTPError

from datcode.test.api.controller import BaseTest
from datcode.api.controller import BaseAPIController
from datcode.common.controller.decorator import (authorized, request_fields,
    owner_or_admin)
from datcode.common.model.messages import get_message
from datcode.common.model.graph.node import User, Resource
from datcode.common.model.acl import Roles


class ApiTests(BaseTest):

    def test_can_get_correct_response_content_type_from_request(self):
        content_type = 'application/json; charset=UTF-8'
        resp = self.get('/api')
        self.assertEqual(content_type, resp.headers['Content-Type'])

    def test_can_get_correct_response_format_from_request(self):
        expected = {
            'message' : str,
            'errors': list,
            'data': (list, dict),
            'time': dict,
        }
        response = self.get('/api')
        resp = self.json_response(response)

        for key, key_type in expected.items():
            self.assertIn(key, resp)
            self.assertIsInstance(resp[key], key_type)

    def test_can_get_correct_message_from_test_handler_response(self):
        test_message = 'testing %f' % random.random()
        uri = '/testing/%s' % str(uuid.uuid1())

        class TestHandler(BaseAPIController):
            def get(self):
                self.json(message=test_message)

        ROUTES = (
            (uri, TestHandler),
        )

        self.get_app().add_handlers(".*$", ROUTES)
        response = self.get(uri)
        resp = self.json_response(response)
        self.assertIn('message', resp)
        self.assertEqual(test_message, resp['message'])

    def test_can_get_correct_manual_set_status_code_from_response(self):
        test_message = 'testing %f' % random.random()
        uri = '/api/testing/%s' % str(uuid.uuid1())
        status = random.choice((200, 201, 202, 203, 206))

        class TestHandler(BaseAPIController):
            def get(self):
                self.json(status=status)


        ROUTES = (
            (uri, TestHandler),
        )

        self.get_app().add_handlers(".*$", ROUTES)

        response = self.get(uri)

        resp = self.json_response(response)
        self.assertEqual(response.code, status)

    def test_can_get_correct_raised_by_error_status_code_from_response(self):
        test_message = 'testing %f' % random.random()
        uri = '/api/testing/%s' % str(uuid.uuid1())
        status = random.choice((500, 400, 200, 408))

        class TestHandler(BaseAPIController):
            def get(self):
                raise HTTPError(status)


        ROUTES = (
            (uri, TestHandler),
        )

        self.get_app().add_handlers(".*$", ROUTES)
        response = self.get(uri)

        self.assertEqual(response.code, status)



class DecoratorTests(BaseTest):

    def test_can_retrieve_failuure_from_post_based_on_requried_fields(self):
        uri = '/testing/%s' % str(uuid.uuid1())
        status_code = 422
        error = (self.get_message('FIELD_REQURIED')['message']).format(field='sex')
        errors = [error,]

        data = {
            'name': 'mark',
            'email': 'email'
        }

        class TestHandler(BaseAPIController):
            @request_fields({
                'required': ['name', 'email', 'sex',]
            })
            def post(self):
                try:
                    data = yield self.request_data
                except:
                    pass

        ROUTES = (
            (uri, TestHandler),
        )

        self.get_app().add_handlers(".*$", ROUTES)

        response = self.post(uri, body=json.dumps(data))
        j = self.json_response(response)

        self.assertEqual(response.code, status_code)
        self.assertEqual(len(j['errors']), 1)
        self.assertEqual(j['errors'][0], errors[0])

    def test_can_successfully_post_and_fulfill_requried_fields(self):
        uri = '/testing/%s' % str(uuid.uuid1())
        status_code = 200
        message = 'hey, it worked! %s' % str(uuid.uuid1())
        data = {
            'name': 'mark',
            'email': 'email',
            'sex': 'male'
        }
        def_request_fields =  {
            'required': ['name', 'email', 'sex',]
        }

        class TestHandler(BaseAPIController):

            @request_fields(def_request_fields)
            def post(self):
                data = self.request_data
                self.json(message=message)

        ROUTES = (
            (uri, TestHandler),
        )

        self.get_app().add_handlers(".*$", ROUTES)

        response = self.post(uri, body=json.dumps(data))
        j = self.json_response(response)
        self.assertEqual(response.code, status_code)
        self.assertEqual(len(j['errors']), 0)
        self.assertEqual(j['message'], message)

    def test_can_successfully_post_based_on_optional_fields(self):
        uri = '/testing/%s' % str(uuid.uuid1())
        status_code = 200
        message = 'hey, it worked! %s' % str(uuid.uuid1())
        data = {
            'name': 'mark',
            'email': 'email',
            'sex': 'male'
        }
        def_request_fields =  {
            'optional': ['name', 'email', 'sex',]
        }

        class TestHandler(BaseAPIController):
            @request_fields(def_request_fields)
            def post(self):
                try:
                    data = self.request_data
                    self.json(message=message)
                except:
                    pass

        ROUTES = (
            (uri, TestHandler),
        )

        self.get_app().add_handlers(".*$", ROUTES)

        response = self.post(uri, body=json.dumps(data))
        j = self.json_response(response)
        self.assertEqual(response.code, status_code)
        self.assertEqual(len(j['errors']), 0)
        self.assertEqual(j['message'], message)

    def test_can_successfuly_convert_types_on_request_fields(self):
        uri = '/testing/%s' % str(uuid.uuid1())
        data = {
            'name': 'mark',
            'email': 'email',
            'age': '1111'
        }
        optional = ['name:str', 'email:bool', 'age:int',]
        def_request_fields =  {
            'optional': optional
        }
        test = self

        class TestFieldTypeHandler(BaseAPIController):
            @request_fields(def_request_fields)
            def post(self):
                data = self.request_data

                for opt in optional:
                    field, f_type = opt.split(':')

                    test.assertIn(field, data)
                    test.assertIsInstance(data[field], getattr(builtins, f_type))

                return self.json(data={})

        ROUTES = (
            (uri, TestFieldTypeHandler),
        )

        self.get_app().add_handlers(".*$", ROUTES)
        self.post(uri, body=json.dumps(data))

    def test_can_successfully_convert_iso_date_field(self):
        uri = '/testing/%s' % str(uuid.uuid1())
        status_code = 200
        message = 'hey, it worked! %s' % str(uuid.uuid1())
        test_date = self.iso_date()
        data = {
            'date': test_date,
        }
        optional = ['date:date',]
        def_request_fields =  {
            'optional': optional
        }
        test = self

        class TestFieldTypeISOFieldHandler(BaseAPIController):
            @request_fields(def_request_fields)
            def post(self):
                data = self.request_data
                date = parse(test_date).timestamp()
                test.assertEqual(date, data['date'])
                return self.json()

        ROUTES = (
            (uri, TestFieldTypeISOFieldHandler),
        )

        self.get_app().add_handlers(".*$", ROUTES)
        self.post(uri, body=json.dumps(data))

    def test_cannot_convert_iso_date_field(self):
        uri = '/testing/%s' % str(uuid.uuid1())
        test_date = 'self.iso_date()'
        data = {
            'date': test_date,
        }
        optional = ['date:date',]
        def_request_fields =  {
            'optional': optional
        }
        test = self

        class TestFieldTypeISOFieldHandlerFail(BaseAPIController):
            @request_fields(def_request_fields)
            def post(self):
                pass

        ROUTES = (
            (uri, TestFieldTypeISOFieldHandlerFail),
        )

        self.get_app().add_handlers(".*$", ROUTES)
        res = self.post(uri, body=json.dumps(data))
        rdata = res.data
        msg = self.get_message('FIELD_TYPE_DATE_ERROR')['message'].format(
            field='date', value=test_date)

        self.assertEqual(422, res.code)
        self.assertEqual(1, len(rdata['errors']))
        self.assertEqual(msg, rdata['errors'][0])

    def test_cannot_get_authorized_request(self):
        uri = '/testing/%s' % str(uuid.uuid1())
        status_code = 401

        class TestCannotAuthHandler(BaseAPIController):
            @authorized
            def get(self):
                pass

        ROUTES = (
            (uri, TestCannotAuthHandler),
        )

        self.get_app().add_handlers(".*$", ROUTES)

        response = self.get(uri)
        j = self.json_response(response)

        self.assertEqual(response.code, status_code)
        self.assertEqual(len(j['errors']), 0)
        self.assertEqual(j['message'], self.get_message('LOGIN_REQUIRED')['message'])

    def test_can_get_authorized_request(self):
        uri = '/testing/%s' % str(uuid.uuid1())
        status_code = 200
        message = 'Success ' + str(uuid.uuid4())
        user, cookie = self.create_request_user()
        headers = {'COOKIE': cookie}

        class TestHandler(BaseAPIController):
            @authorized
            def get(self):
                self.json(message=message)

        ROUTES = (
            (uri, TestHandler),
        )

        self.get_app().add_handlers(".*$", ROUTES)

        response = self.get(uri, headers=headers)
        j = self.json_response(response)

        self.assertEqual(response.code, status_code)
        self.assertEqual(len(j['errors']), 0)
        self.assertEqual(j['message'], message)

    def test_cannot_get_request_not_owner_not_admin(self):
        uid = str(uuid.uuid4())
        uri_regex = r'/testing/notownernotadmin/%s/(\d+)' % uid
        status_code = 401
        cd = {'title': 'title '+ str(random.random())}
        user_resp, cookie = self.create_request_user()
        project = self.mapper.create(properties=cd, entity=Resource)
        self.mapper.save(project).send()
        uri = '/testing/notownernotadmin/%s/%s' % (uid, project.id)
        headers = {'COOKIE': cookie}

        class TestNotOwnerHandler(BaseAPIController):
            @owner_or_admin
            def get(self, project_id):
                self.json()

        ROUTES = (
            (uri_regex, TestNotOwnerHandler),
        )

        self.get_app().add_handlers(".*$", ROUTES)

        response = self.get(uri, headers=headers)
        j = self.json_response(response)
        self.assertEqual(response.code, status_code)
        self.assertEqual(len(j['errors']), 0)
        self.assertEqual(j['message'], self.get_message('ACCESS_DENIED')['message'])

    def test_can_get_request_is_owner_not_admin(self):
        uri_regex = r'/testing/can/get/owner/not/admin/(\d+)'
        status_code = 200
        d = {'email_address': 'test', 'password': 'testtest'}
        cd = {'title': 'title '+ str(random.random())}
        user = self.mapper.create(properties=d, entity=User)
        project = self.mapper.create(properties=cd, entity=Resource)
        user_mapper = self.mapper.get_mapper(user)
        user_mapper.add_ownership(user, project)
        resp, cookie = self.login_request(user['email_address'], user['password'])
        headers = {'Cookie': cookie}
        message = 'Success'+ str(random.random())
        uri = '/testing/can/get/owner/not/admin/{}'.format(project.id)

        class TestNotAdminHandler(BaseAPIController):
            @owner_or_admin
            def get(self, _id):
                self.json(message=message)

        ROUTES = (
            (uri_regex, TestNotAdminHandler),
        )

        self.get_app().add_handlers(".*$", ROUTES)

        response = self.get(uri, headers=headers)
        j = self.json_response(response)

        self.assertEqual(response.code, status_code)
        self.assertEqual(len(j['errors']), 0)
        self.assertEqual(j['message'], message)

    def test_can_get_request_is_admin_not_owner(self):
        status_code = 200
        d = {'email_address': 'test', 'password': 'testtest'}
        a = {
            'email_address': 'admin',
            'access_level': Roles.ADMIN.value,
            'password': 'testtest'}
        cd = {'title': 'title '+ str(random.random())}
        user = self.mapper.create(properties=d, entity=User)
        admin = self.mapper.create(properties=a, entity=User)
        project = self.mapper.create(properties=cd, entity=Resource)
        user_mapper = self.mapper.get_mapper(user)

        self.mapper.save(user, admin, project).send()
        user_mapper.add_ownership(user, project)
        resp, cookie = self.login_request(admin['email_address'],
            admin['password'])
        uri = '/testing/can/get/admin/{}'.format(project.id)

        user_mapper = self.mapper.get_mapper(User)
        headers = {'Cookie': cookie}
        message = 'Success'+ str(random.random())

        class TestIsAdminHandler(BaseAPIController):
            @owner_or_admin
            def get(self, _id):
                self.json(message=message)

        ROUTES = (
            (r'/testing/can/get/admin/([\w\-]+)', TestIsAdminHandler),
        )

        self.get_app().add_handlers(".*$", ROUTES)

        response = self.get(uri, headers=headers)
        j = self.json_response(response)

        self.assertEqual(response.code, status_code)
        self.assertEqual(len(j['errors']), 0)
        self.assertEqual(j['message'], message)

    def test_can_get_request_is_admin_and_owner(self):
        uri_regex = r'/testing/can/get/owner/is/admin/(\d+)'
        status_code = 200
        d = {
            'email_address': 'test',
            'password': 'testtest',
            'access_level': Roles.ADMIN.value,
        }
        cd = {'name': 'title '+ str(random.random())}
        user = self.mapper.create(properties=d, entity=User)
        project = self.mapper.create(properties=cd, entity=Resource)
        user_mapper = self.mapper.get_mapper(user)
        user_mapper.add_ownership(user, project)
        resp, cookie = self.login_request(user['email_address'], user['password'])
        headers = {'Cookie': cookie}
        message = 'Success'+ str(random.random())
        uri = '/testing/can/get/owner/is/admin/{}'.format(project.id)

        class TestIsAdminHandler(BaseAPIController):
            @owner_or_admin
            def get(self, _id):
                self.json(message=message)

        ROUTES = (
            (uri_regex, TestIsAdminHandler),
        )

        self.get_app().add_handlers(".*$", ROUTES)

        response = self.get(uri, headers=headers)
        j = self.json_response(response)

        self.assertEqual(response.code, status_code)
        self.assertEqual(len(j['errors']), 0)
        self.assertEqual(j['message'], message)


if __name__ == '__main__':
    unittest.main()
