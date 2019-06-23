from . import BaseRelationshipMapper, BaseRelationship


class HasPost(BaseRelationship):
    pass


class HasPostMapper(BaseRelationshipMapper):
    entity = HasPost
