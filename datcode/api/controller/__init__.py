import datetime
import types

from timeit import default_timer as timer

from datcode.config import options
from datcode.common.exception import ApiEntityException, ApiException
from datcode.common.controller import BaseController
from datcode.common.controller.paginator import Paginator
from datcode.common.model.graph.node import User, UserMapper
from datcode.common.model.acl import Roles


class BaseAPIController(BaseController):
    
    def prepare(self):
        if options.debug:
            self._start_time = timer()

        self.user = None
        self.user_mapper = self.mapper.get_mapper(User)

    def __init__(self, application, request, **kwargs):
        super().__init__(application=application, request=request, **kwargs)
        self.mapper = application.mapper
        self.email = application.email
        self.mapper.email = self.email

        # Give the mapper a pagination method
        this = self
        self.pagination = None

        def request_pagination(*args, **kwargs):
            return this.pagination

        self.mapper.request_pagination = types.MethodType(
            request_pagination, {})

        self.paginate_total = None
        self.paginate_page = None
        self.paginator = Paginator(controller=self)
        self.request_data = {}

    def _get_request_data(self):
        return self._request_data

    def _set_request_data(self, data):
        self._request_data = data

    request_data = property(_get_request_data, _set_request_data)

    def cookie_login(self, user_id):
        self.set_secure_cookie(options.user_cookie_name, str(user_id))

    def cookie_logout(self):
        self.clear_cookie(options.user_cookie_name)

    def get_current_user(self):
        return self.get_user_by_id(self.user_id)

    def raise_entity_error(self, message='ENTITY_DOESNT_EXIST',
                           status_code=403):
        message = self.get_message(message)
        raise ApiEntityException(message['message'], status_code=status_code)

    @property
    def is_admin(self):
        user = self.get_current_user()

        return Roles.is_admin(user['access_level'])

    def is_owner(self, user, entity, relationship):
        response = self.user_mapper.is_owner(owner=user, entity=entity,
            relationship=relationship)

        return len(response) > 0

    @property
    def user_id(self):
        user = self.get_secure_cookie(options.user_cookie_name)

        if user:
            return int(user.decode('utf-8'))
        else:
            return None

    def get_user_by_id(self, user_id):
        if user_id is None:
            self.raise_entity_error()

        try:
            user = self.user_mapper.get_by_id(int(user_id))

            if not user:
                self.raise_entity_error()

            return user
        except ValueError as e:
            LOG.exception(e)
            self.raise_entity_error()

    def get_entity_by_id(self, entity_id, entity=None):
        if not entity_id:
            self.raise_entity_error()

        entity = self.mapper.get_by_id(id_val=int(entity_id), entity=entity)

        if not entity:
            self.raise_entity_error()

        return entity

    def json(self, data=None, status=200, errors=None, message=None,
             response=None, **kwargs):
        """this method is used to write a json response"""
        if not data:
            data = {}

        if not errors:
            errors = []

        message = message or ''
        code = 1000

        if response:
            response = self.get_message(response)
            message = response['message']
            code = response['id']

        resp = {
            'code': code,
            'data': data,
            'errors': errors,
            'message': message,
        }

        if options.debug:
            resp['time'] = {
                'server': datetime.datetime.utcnow().isoformat(),
                'request': timer() - self._start_time,
            }

        resp.update(kwargs)

        if self.paginate_total:
            if not self.paginate_page:
                self.paginate_page = 1

            resp['pagination'] = {
                'total': self.paginate_total,
                'page': self.paginate_page,
                'per_page': options.pagination,
            }

            next_page_total = options.pagination * self.paginate_page

            if next_page_total and next_page_total < self.paginate_total:
                resp['pagination']['next'] = self.paginate_page + 1

            self.paginate_total = None
            self.paginate_page = None

        self.set_status(int(status))
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

        return self.finish(resp)
