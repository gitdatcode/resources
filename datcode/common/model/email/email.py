from tornado.template import Loader

from datcode import LOG
from datcode.config import options


class Email:

    def __init__(self, connection, template):
        self.connection = connection
        self.template = template

    @property
    def stats(self):
        return self.connection.get_send_statistics()

    @property
    def quota(self):
        return self.connection.get_send_quota()

    def render(self, template, **kwargs):
        return self.template.render(template=template, **kwargs)

    def email_mapping(self, key, to, source=None, **kwargs):
        """
        method used to get the email template and subject from the MAPPINGS
        dict allowing automatic template rendering and subject definition
        """
        from .mapping import MAPPINGS

        if key not in MAPPINGS:
            msg = '{} is not a valid email mapping option'.format(key)
            raise AttributeError(msg)

        if not isinstance(to, (list, set, tuple)):
            to = [to,]

        subject = MAPPINGS[key]['subject']
        content = self.render(MAPPINGS[key]['template'], **kwargs)

        return self.email(to=to, subject=subject, content=content,
            source=source)

    def email(self, to, subject, content, format='html', source=None):
        source = source or options.from_email

        return self.connection.send_email(source=source,
                subject=subject, body=content, to_addresses=to,
                format=format)