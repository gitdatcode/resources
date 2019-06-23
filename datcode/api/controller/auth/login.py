from datcode.api.controller import BaseAPIController
from datcode.common.controller.decorator import request_fields
from datcode.common.model.graph.node import User, UserMapper


class LoginController(BaseAPIController):
    """this controller will log a user into the system and set a cookie
    on successful auth"""

    def prepare(self):
        super().prepare()
        self.user_mapper = self.mapper.get_mapper(User)

    def get(self):
        pass

    @request_fields({
        'required': ['email_address', 'password'],
    })
    def post(self):
        user = self.user_mapper.auth_user(self.request_data['email_address'],
            self.request_data['password'])

        if user:
            self.cookie_login(user.id)
            message = 'LOGIN_SUCCESSFUL'
            status = 200
        else:
            message = 'LOGIN_INCORRECT'
            status = 403

        return self.json(status=status, response=message)
