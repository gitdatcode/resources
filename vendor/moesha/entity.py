import copy

from .util import entity_to_labels, MOESHA_ENTITY_TYPE


class Entity(object):

    def __init__(self, id=None, labels=None, properties=None):
        properties = properties or {}
        self.query_variable = ''
        self.id = id
        self._data = {}
        self._initial = {}
        self._changes = {}
        self._deleted = {}

        # call the method directly, seems to be an issue with properties
        # and subclasses
        self._set_labels(labels or [])

        self.hydrate(properties=properties, reset=True)

    def __repr__(self):
        fields = ' '.join(['{}={}'.format(k, v) for k,v in self.data.items()])

        return ('<moesha.Entity.{}: {} at {}>').format(self.__class__.__name__,
            fields, id(self))

    @property
    def data(self):
        if isinstance(self, Relationship):
            self._data[MOESHA_ENTITY_TYPE] = 'relationship'
        elif isinstance(self, Node):
            self._data[MOESHA_ENTITY_TYPE] = 'node'

        return self._data

    @property
    def changes(self):
        return self._changes

    @property
    def deleted(self):
        return self._deleted

    def _get_labels(self):
        if self._labels and not isinstance(self._labels, (list, set, tuple)):
            self._labels = [self._labels]

        self._labels.sort()

        return self._labels

    def _set_labels(self, labels):
        self._labels = self.lbl(labels)

        return self

    labels = property(_get_labels, _set_labels)

    @classmethod
    def lbl(cls, labels=None):
        """utility method used to get the labels for the entity"""

        if not labels:
            if isinstance(cls, type):
                name = cls.__name__
            else:
                name = cls.__class__.__name__

            if name not in ['Node', 'Relationship']:
                labels = entity_to_labels(cls).split(':')
            else:
                labels = []

        if not isinstance(labels, (list, set, tuple)):
            labels = [labels,]

        labels.sort()

        return labels

    def hydrate(self, properties=None, reset=False):
        properties = properties or {}

        if reset:
            self._data = copy.copy(properties)
            self._initial = copy.copy(properties)
            self._deleted = {}
        else:
            for k, v in properties.items():
                self[k] = v

        return self

    def get(self, name, default=None):
        """this works differently than the typical dict.get method. The default
        argument will only be returned if it is not None. otherwise the field's
        default value will be returned"""
        value = self[name]

        if default is not None and not value:
            return default

        return value

    def __getitem__(self, name):
        return self._data.get(name, None)

    def __setitem__(self, name, value):
        if name in self._initial:
            if value != self._initial[name]:
                self._changes[name] = {
                    'from': self._initial[name],
                    'to': value,
                }
            else:
                try:
                    del self._changes[name]
                except:
                    pass

        self._data[name] = value

        return self

    def __delitem__(self, name):
        if name in self._data:
            self._deleted[name] = self._data[name]
            del self._data[name]

    def __eq__(self, entity):
        return (self.id == entity.id and self.labels == entity.labels and
            self.data == entity.data)


class Node(Entity):
    pass


class Relationship(Entity):

    def __init__(self, id=None, start=None, end=None, properties=None,
                 labels=None):
        super(Relationship, self).__init__(id=id, properties=properties,
            labels=labels)
        self.start = start
        self.end = end

    def _get_labels(self):
        labels = super(Relationship, self).labels

        try:
            return labels[0]
        except:
            return None

    def _set_labels(self, labels):
        return super(Relationship, self)._set_labels(labels=labels)

    labels = property(_get_labels, _set_labels)

    @property
    def type(self):
        return self.labels

    @classmethod
    def lbl(cls, labels=None):
        labels = super().lbl(labels=labels)

        return labels[0]


class Collection(object):

    def __init__(self, entities=None):
        if entities and not isinstance(entities, (list, set, tuple)):
            entities = [entities,]
        elif isinstance(entities, Collection):
            entities = entities.entities

        self.entities = entities or []
        self.index = 0

    def get_data(self, item):
        from .mapper import get_mapper

        if isinstance(item, (Node, Relationship)):
            mapper = get_mapper(item, None)
            item = mapper.data(item)

        if isinstance(item, (list, set, tuple, frozenset, Collection)):
            return [self.get_data(i) for i in item]

        if isinstance(item, dict):
            return {k: self.get_data(v) for k, v in item.items()}

        return item

    @property
    def data(self):
        return [self.get_data(e) for e in self]

    def __getitem__(self, field):
        return [entity[field] for entity in self]

    def __setitem__(self, field, value):
        for entity in self:
            entity[field] = value

        return self

    def __delitem__(self, field):
        for entity in self:
            del(entity[field])

        return self

    def __iter__(self):
        return self
    
    def __iter__(self):
        return self

    def __next__(self):
        entity = self[self.index]
        self.index += 1

        return entity

    def first(self):
        return self[0]

    def last(self):
        return self[-1]
