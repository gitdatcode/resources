from tornado.template import Loader


class Template:

    def __init__(self, template_path, **kwargs):
        self.loader = Loader(template_path, **kwargs)

    def render(self, template, **kwargs):
        temp = self.loader.load(template)

        return temp.generate(**kwargs)
