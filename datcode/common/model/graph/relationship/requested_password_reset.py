from . import BaseRelationshipMapper, BaseRelationship


class RequestedPasswordReset(BaseRelationship):
    pass


class RequestedPasswordResetMapper(BaseRelationshipMapper):
    entity = RequestedPasswordReset
