from . import BaseRelationshipMapper, BaseRelationship


class AddedResource(BaseRelationship):
    pass


class AddedResourceMapper(BaseRelationshipMapper):
    entity = AddedResource
