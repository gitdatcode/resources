from . import BaseNode, BaseNodeMapper

from moesha.property import String, Boolean


class LoginLog(BaseNode):
    pass


class LoginLogMapper(BaseNodeMapper):
    entity = LoginLog
    __PROPERTIES__ = {
        'email_address': String(),
        'success': Boolean(default=False),
    }
