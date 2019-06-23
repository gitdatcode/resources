from . import BaseRelationshipMapper, BaseRelationship


class HasRole(BaseRelationship):
    pass


class HasRoleMapper(BaseRelationshipMapper):
    entity = HasRole
