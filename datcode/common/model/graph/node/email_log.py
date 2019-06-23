from . import BaseNode, BaseNodeMapper

from moesha.property import String, Boolean


class EmailLog(BaseNode):
    pass


class EmailLogMapper(BaseNodeMapper):
    entity = EmailLog
    __PROPERTIES__ = {
        'email': String(),
        'to': String(),
        'subject': String(),
        'content': String(),
        'success': Boolean(default=False),
    }
