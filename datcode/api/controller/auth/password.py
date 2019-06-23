from datcode.api.controller import BaseAPIController
from datcode.common.controller.decorator import request_fields
from datcode.common.model.graph.node.password_reset import PasswordReset


class AuthPasswordForgotController(BaseAPIController):
    """controller used to send a reset email to the lost password """

    @request_fields({
        'required': ['email_address'],
    })
    def post(self):
        try:
            user = self.user_mapper.get_by_email(
                self.request_data['email_address'])
        except:
            self.raise_entity_error()

        self.user_mapper.request_password_change(user)

        return self.json(response='USER_PASSWORD_RESET_REQUESTED')


class AuthPasswordResetController(BaseAPIController):
    """controller used to reset an email after the user clicks the email
    send out by the forgot password handler"""

    def prepare(self):
        super().prepare()
        self.password_reset_mapper = self.mapper.get_mapper(PasswordReset)

    @request_fields({
        'required': ['new_password1', 'new_password2'],
    })
    def put(self, request_uuid):
        try:
            code = self.password_reset_mapper.get_by_code(code=request_uuid)
        except:
            self.raise_entity_error(message='USER_PASSWORD_RESET_INVALID')

        try:
            rel = self.password_reset_mapper(code)['User'](
                return_relationship=True).first()
            rel_mapper = self.mapper.get_mapper(rel)
            user = rel_mapper.start(rel)
        except:
            self.raise_entity_error()

        if not user.update_password(**self.request_data):
            self.raise_entity_error(message='USER_MISMATCHED_PASSWORD')

        code.fulfill()
        self.mapper.save(user, code).send()

        return self.json(response='USER_PASSWORD_UPADTED')
