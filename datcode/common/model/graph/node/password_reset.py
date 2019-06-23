from datetime import datetime
from uuid import uuid4

from moesha.property import String, Boolean, DateTime, RelatedEntity

from . import BaseNode, BaseNodeMapper
from datcode.config import options



class PasswordReset(BaseNode):

    def fulfill(self):
        self['fulfilled'] = True
        self['date_fulfilled'] = datetime.utcnow().timestamp()

        return self


class PasswordResetMapper(BaseNodeMapper):
    from .user import User
    from datcode.common.model.graph.relationship import RequestedPasswordReset

    entity = PasswordReset
    __PROPERTIES__ = {
        'code': String(default=uuid4),
        'fulfilled': Boolean(default=False),
        'date_fulfilled': DateTime(),
        'reset_timeout': DateTime(
            default=lambda: datetime.utcnow().timestamp()\
                + options.password_reset_timeout),
    }
    __RELATIONSHIPS__ = {
        'User': RelatedEntity(relationship_entity=RequestedPasswordReset,
            direction='in'),
    }

    def get_by_code(self, code, current_time=None):
        current_time = current_time or datetime.utcnow().timestamp()
        pypher = self.builder()
        pypher.WHERE.CAND(pypher.entity.__code__ == code,
            pypher.entity.__reset_timeout__ >= current_time,
            pypher.entity.__fulfilled__ == False)
        pypher.RETURN(pypher.entity)

        return self.mapper.query(pypher=pypher).first()
