from datcode.api.controller import BaseAPIController
from datcode.common.controller.decorator import authorized


class LogoutController(BaseAPIController):

    def get(self):
        return self.post()

    def put(self):
        return self.post()

    def delete(self):
        return self.post()

    @authorized
    def post(self):
        self.cookie_logout()

        return self.json(response='LOGOUT_SUCCESSFUL')
