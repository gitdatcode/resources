from moesha.property import TimeStamp, RelatedEntity

from .entity import Node, Relationship
from .mapper import EntityNodeMapper, EntityRelationshipMapper
from .util import entity_to_labels
from .property import TimeStamp, JsonProperty


class SourcedEventChanges(Node):
    pass


class SourcedEventChangesMapper(EntityNodeMapper):
    entity = SourcedEventChanges
    __ALLOW_UNDEFINED_PROPERTIES__ = True
    __PROPERTIES__ = {
        'date_created': TimeStamp(),
        'changed': JsonProperty(),
        'deleted': JsonProperty(),
    }


class ChangesForEntity(Relationship):
    pass


class ChangesForEntityMapper(EntityRelationshipMapper):
    entity = ChangesForEntity
    __PROPERTIES__ = {
        'date_created': TimeStamp(),
    }


class MadeEventChange(Relationship):
    pass


class MadeEventChangeMapper(EntityRelationshipMapper):
    entity = MadeEventChange
    __PROPERTIES__ = {
        'date_created': TimeStamp(),
    }
    # __RELATIONSHIPS__ = {
    #     'Changes': RelatedEntity(relationship_entity=SourcedEventChanges,
    #         ensure_unique=True),
    # }


class EventSourceMapperMixin:
    """This mixin is used to overwrite the save method on a given EntityMapper.
    It will create an entry that represents the change that an entity (node or
    relationship) went through with the save and two relationships that connect
    the source with the saved entity

    (:SourceEntity)-[:MadeEventChange]->(:SourcedEventChanges)-[:ChangesForEntity]->(:SavedEntity)

    If the SavedEntity is a relationship, all of the entity's information
    will be saved in the SourceEventChanges node and a ChangesForEntity relationship
    will not be created. Data added to the SourceEventChanges node:
    __entity_type__: relationship
    __entity_id__: SavedEntity.id
    __relationship__: SavedEntity.labels

    to use simply add this mixin with an EntityNodeMapper or EntityRelationshipMapper
    and when calling save, pass in a source argument:

    class PostMapper(EventSourceMapperMixin, EntityNodeMapper):
        entity = Post
        __PROPERTIES__ = {
            'title': String(),
            'description': String(),
        }

    any changes made the the __PROPERTIES__ will be recorded
    """
    __RELATIONSHIPS__ = {
        'SourcedEvents': RelatedEntity(relationship_entity=MadeEventChange,
            ensure_unique=True),
    }

    def save(self, entity, source=None, ensure_unique=False, work=None,
             **kwargs):
        work = super().save(entity, ensure_unique=ensure_unique, work=work,
            **kwargs)

        if not source:
            return work

        is_relationship = isinstance(entity, Relationship)
        changed = entity.changes
        deleted = entity.deleted

        if len(changed) or len(deleted):
            properties = {}

            if len(changed):
                properties['changed'] = changed

            if len(deleted):
                properties['deleted'] = deleted

            if is_relationship:
                properties['__entity_type__'] = 'relationship'
                properties['__relationship__'] = entity_to_labels(entity)
                properties['__id__'] = entity.id

            entities = []
            changes = self.mapper.create(entity=SourcedEventChanges,
                properties=properties)

            entities.append(changes)

            if not is_relationship:
                made_changes = self.mapper.create(entity=MadeEventChange,
                    start=source, end=changes)
                changes_for_entity = self.mapper.create(
                    entity=ChangesForEntity, start=changes, end=entity)
                entities.append(made_changes)
                entities.append(changes_for_entity)

            work = self.mapper.save(*entities, work=work)

        return work
