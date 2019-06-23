from tornado import web

from datcode.config import options
from datcode.common.view.loader import Template


def build_moesha():
    from moesha.connection import Connection
    from moesha.mapper import Mapper
    # these are imported but are used to simply register the objects with
    # the python interperter at runtime
    import datcode.common.model.graph.node
    import datcode.common.model.graph.relationship

    conn = Connection(host=options.moesha_host, port=options.moesha_port,
            username=options.moesha_user, password=options.moesha_password)

    return Mapper(connection=conn)


def build_email(template=None):
    import boto.ses

    from datcode.common.model.email import Email


    template = template or TEMPLATE

    # @TODO: setup AWS SES email
    conn = boto.ses.connect_to_region(options.aws_region,
        aws_access_key_id=options.aws_access_key_id,
        aws_secret_access_key=options.aws_secret_access_key)

    return Email(connection=conn, template=template)


def create_application():
    from datcode.api.routes import ROUTES as APIROUTES
    from datcode.client.routes import ROUTES as CLIENTROUTES

    routes = CLIENTROUTES + APIROUTES


    class Application(web.Application):

        def __init__(self):
            settings = {
                'debug': options.debug,
                'autoescape': None,
                'cookie_secret': 'secret CHANGE THIS'
            }

            web.Application.__init__(self, routes, **settings)

    app = Application()
    app.mapper = MAPPER
    app.email = EMAIL

    return app


MAPPER = build_moesha()
TEMPLATE = Template(options.template_path)
EMAIL = build_email()
