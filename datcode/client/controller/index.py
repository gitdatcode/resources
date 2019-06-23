from datcode.client.controller import BaseClientController


class IndexController(BaseClientController):

    def get(self):
        self.write('index page')
