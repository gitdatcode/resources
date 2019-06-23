import json
# import traceback

from timeit import default_timer as timer

from tornado import web

from datcode import LOG
from datcode.common.exception import convert_exeception
from datcode.common.utils import strip_tags
from datcode.common.model.messages import get_message
from datcode.config import options


class BaseController(web.RequestHandler):

    def log_exception(self, typ, value, tb):
        LOG.error(value, exc_info=True)

    def write_error(self, status_code, **kwargs):
        message = self.get_message('REQUEST_ERROR')
        errors = []
        status = status_code
        exc = None

        if 'exc_info' in kwargs:
            exc = convert_exeception(kwargs['exc_info'][1])
            message = exc.value if hasattr(exc, 'value') else str(exc)

            if isinstance(message, (list, tuple,)):
                errors = message

            if hasattr(exc, 'errors'):
                errors = exc.errors

            if hasattr(exc, 'status_code'):
                status = exc.status_code

        # send sms and email for 500 errors
        if status > 499 and options.notify_errors:
            # error_message = ('there was a {} error on the'
            #     ' GotSkills server').format(status)

            # disable email for now
            # if exc:
            #     ERROR_LOG.error(exc, exc_info=True)
            #     tb = traceback.format_exc()
            #     content = self.render_string('email/error/500.html', e=exc,
            #         tb=tb).decode('utf-8')
            #     self.email.email(to=options.error_email,
            #         subject=error_message, content=content)
            pass
        elif status == 303:
            pass

        return self.json(status=status, errors=errors, message=message)

    def get_message(self, message):
        return get_message(message)

    def strip_tags(self, text):
        return strip_tags(text)

    if options.debug:
        def echo(self, item):
            from pprint import pprint

            pprint(item)

    @property
    def is_ajax(self):
        return ('X-Requested-With' in self.request.headers and
                self.request.headers['X-Requested-With'] == 'XMLHttpRequest')

    def get_arg(self, name, default=None):
        """
        method used to get the argument from the request
        all requests are sent as encoded json tied to the body argument
        PUT methods do not get data from self.request.get_argument
        so direct parsing of self.request.body is used
        """

        try:
            body = json.loads(self.request.body.decode('utf-8'))

            if name:
                body = body.get(name, default)
        except Exception:
            body = self.get_argument(name, default)

        return self.strip_tags(body)
