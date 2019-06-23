from . import BaseRelationshipMapper, BaseRelationship


class HasTag(BaseRelationship):
    pass


class HasTagMapper(BaseRelationshipMapper):
    entity = HasTag
