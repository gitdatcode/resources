from datetime import datetime

from moesha.entity import Node
from moesha.property import TimeStamp, DateTime
from moesha.mapper import StructuredNodeMapper

from datcode.common.model.graph import BaseMapper


class BaseNode(Node):
    pass


class BaseNodeMapper(BaseMapper, StructuredNodeMapper):
    __PROPERTIES__ = {
        'date_created': TimeStamp(),
        'date_updated': DateTime(datetime.now),
    }


from .email_log import EmailLog, EmailLogMapper
from .login_log import LoginLog, LoginLogMapper
from .password_reset import PasswordReset, PasswordResetMapper
from .resource import Resource, ResourceMapper
from .tag import Tag, TagMapper
from .user import User, UserMapper
