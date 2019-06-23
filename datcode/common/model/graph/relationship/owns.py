from . import BaseRelationshipMapper, BaseRelationship


class Owns(BaseRelationship):
    pass


class OwnsMapper(BaseRelationshipMapper):
    entity = Owns
