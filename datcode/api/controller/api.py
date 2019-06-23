from ..controller import BaseAPIController


class ApiController(BaseAPIController):
    services = ['api']

    def check_service_status(self, service):
        return True

    def get(self):
        try:
            user = self.get_current_user()
            auth = user.id
        except:
            auth = False

        data = {
            'authenticated': auth,
        }

        for service in self.services:
            data[service] = self.check_service_status(service)

        return self.response(data=data)
