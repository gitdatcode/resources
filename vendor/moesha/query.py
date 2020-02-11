import uuid

from pypher.builder import (Pypher, Param, Params, __)

from .entity import (Entity, Node, Relationship, Collection)
from .util import normalize


def get_mapper(entity):
    from .mapper import get_mapper as gm

    return gm(entity, None)


class _ValueManager(object):
    values = {}

    @classmethod
    def reset(cls):
        cls.values = {}

    @classmethod
    def set_query_var(cls, entity):
        from .mapper import EntityQueryVariable

        return EntityQueryVariable.define(entity)

    @classmethod
    def get_next(cls, entity, field):
        entity_name = entity.__class__.__name__
        name = cls.set_query_var(entity)
        field = normalize(field)

        if entity_name not in _ValueManager.values:
            _ValueManager.values[entity_name] = 0

        return '${}_{}_{}'.format(name, field,
            _ValueManager.values[entity_name]).lower()


VM = _ValueManager


class _BaseQuery(object):

    def __init__(self, params=None):
        self.params = params
        self.creates = []
        self.before_matches = []
        self.matches = []
        self.merges = []
        self.on_create_sets = []
        self.on_match_sets = []
        self.deletes = []
        self.matched_entities = []
        self.sets = []
        self.wheres = []
        self.orders = []
        self.returns = []
        self.pypher = Pypher(params=self.params)

    def reset(self):
        self.creates = []
        self.before_matches = []
        self.matches = []
        self.merges = []
        self.on_create_sets = []
        self.on_match_sets = []
        self.deletes = []
        self.matched_entities = []
        self.sets = []
        self.wheres = []
        self.orders = []
        self.returns = []

    def __iadd__(self, other):
        self.creates += other.creates
        self.matches += other.matches
        self.merges += other.merges
        self.on_create_sets += other.on_create_sets
        self.on_match_sets += other.on_match_sets
        self.deletes += other.deletes
        self.matched_entities += other.matched_entities
        self.sets += other.sets
        self.wheres += other.wheres
        self.orders += other.orders
        self.returns += other.returns

        return self

    def _node_by_id(self, entity):
        qv = entity.query_variable

        if not qv:
            qv = VM.set_query_var(entity)

        _id = VM.get_next(entity, 'id')
        _id = Param(_id, entity.id)

        return __.node(qv).WHERE(__.ID(qv) == _id)

    def _entity_by_id_builder(self, entity, id_val, add_labels=False):
        qv = entity.query_variable

        if not qv:
            qv = VM.set_query_var(entity)

        _id = VM.get_next(entity, 'id')
        _id = Param(_id, id_val)
        node_kwargs = {}

        if add_labels:
            node_kwargs['labels'] = entity.labels

        if isinstance(entity, Relationship):
            node = __.node(**node_kwargs).relationship(qv).node()
        else:
            node = __.node(qv, **node_kwargs)

        where = __.ID(qv) == _id

        self.matches.append(node)
        self.wheres.append(where)
        self.returns.append(entity.query_variable)

        return self


class Query(_BaseQuery):

    def __init__(self, entities, params=None):
        super(Query, self).__init__(params=params)

        if not isinstance(entities, (Collection, list, set, tuple)):
            entities = [entities,]

        self.entities = entities

    def build_save_pypher(self, ensure_unique=False):
        for entity in self.entities:
            if isinstance(entity, Node):
                if entity.id:
                    self.update_node(entity)
                else:
                    self.create_node(entity)
            elif isinstance(entity, Relationship):
                self.save_relationship(entity=entity,
                    ensure_unique=ensure_unique)

        pypher = self.pypher

        if self.before_matches:
            for bm in self.before_matches:
                pypher.append(bm)

        if self.matches:
            for match in self.matches:
                pypher.MATCH(match)

        if self.creates:
            pypher.CREATE(*self.creates)

        if self.merges:
            pypher.MERGE(*self.merges)

        if self.on_create_sets:
            pypher.OnCreateSet(*self.on_create_sets)

        if self.on_match_sets:
            pypher.OnMatchSet(*self.on_match_sets)

        if self.sets:
            pypher.SET(*self.sets)

        pypher.RETURN(*self.returns)

        return pypher

    def save(self, ensure_unique=False):
        pypher = self.build_save_pypher(ensure_unique=ensure_unique)

        return str(pypher), pypher.bound_params

    def create_node(self, entity):
        mapper = get_mapper(entity)
        has_unique = len(mapper.unique_properties()) > 0
        props = self._properties(entity, has_unique)
        node = __.node(entity.query_variable, labels=entity.labels,
            **props)

        # if the entity has unique properties, we will build a MERGE statement
        # that looks like:
        #
        # MERGE (keanu:Person { name: 'Keanu Reeves' })
        # ON CREATE SET keanu.created = timestamp(), kenau.name = 'name
        # ON MATCH SET keanu.created = timestamp(), kenau.name = 'name
        # RETURN keanu 
        #
        # if it doesnt have unique properties, it will build a CREATE statement
        # that looks like:
        # 
        # CREATE (keanu:Person { name: 'Keanu Reeves' }) return keanu
        if has_unique:
            full_props = self._properties(entity)

            self.merges.append(node)

            for field, value in full_props.items():
                stmt = getattr(__, entity.query_variable).property(field)._
                stmt == value

                self.on_create_sets.append(stmt)
                self.on_match_sets.append(stmt)
        else:
            self.creates.append(node)

        self.returns.append(entity.query_variable)

        return self

    def update_node(self, entity):
        props = self._properties(entity)
        qv = VM.set_query_var(entity)

        for field, value in props.items():
            stmt = getattr(__, qv).property(field)._
            stmt == value
            self.sets.append(stmt)

        self.matches.append(self._node_by_id(entity))
        self.returns.append(qv)

        return self

    def save_relationship(self, entity, ensure_unique=False):
        """this method handles creating and saving relationships.
        It will hanle quite a few situations. 
        Given the structure:

        (start)-[rel]->[end]

        We can have:
        * A new start node
        * An existing start node
        * A new rel
        * An existing rel
        * A new end node
        * An existing end node

        Each start, rel, and end could have uniqueness assigned to it
        * start/end could have unique properties
        * rel could have unique relationships

        A Chyper query should be generated that looks something like this,
        depending on the settings for each of the nodes:

        MERGE (n_0:Node {`key`: val})
        ON CREATE SET n_0.key = val, n_0.key2 = val2
        ON MATCH SET n_0.key = val, n_0.key2 = val2
        CREATE (n_0)-[r_0:RelLabel, {`key`: someVal}]->(n_1:Node {`key`: val})
        RETURN n_0, n_1, r_0
        """
        start = entity.start
        start_properties = {}
        end = entity.end
        end_properties = {}
        props = self._properties(entity)

        if start is None or end is None:
            raise Exception('The relationship must have a start and end node')

        if not isinstance(start, Node):
            start = Node(id=start)

        if not isinstance(end, Node):
            end = Node(id=end)

        VM.set_query_var(start)
        VM.set_query_var(end)
        VM.set_query_var(entity)

        rel = Pypher()

        if start not in self.matched_entities:
            if start.id is not None:
                self._update_properties(start)
                self.matches.append(self._node_by_id(start))
            else:
                start_properties = self._properties(start)

            self.matched_entities.append(start)
            self.returns.append(start.query_variable)

        if end not in self.matched_entities:
            if end.id is not None:
                self._update_properties(end)
                self.matches.append(self._node_by_id(end))
            else:
                end_properties = self._properties(end)

            self.matched_entities.append(end)
            self.returns.append(end.query_variable)

        if entity.id is None:
            if start.id is not None:
                rel = rel.node(start.query_variable)
            else:
                start_query = Query(start, self.params)
                start_query.build_save_pypher()

                if len(start_query.creates):
                    rel.append(*start_query.creates)
                elif len(start_query.merges):
                    has_matches = len(self.matches) > 0
                    start_merge = Pypher()
                    start_merge.MERGE(*start_query.merges)

                    if start_query.on_create_sets:
                        start_merge.OnCreateSet(*start_query.on_create_sets)

                    if start_query.on_match_sets:
                        start_merge.OnMatchSet(*start_query.on_match_sets)

                    self.before_matches.append(start_merge)
                    rel.node(start.query_variable)

            rel.rel(entity.query_variable, labels=entity.labels,
                direction='out', **props)

            if end.id is not None:
                rel.node(end.query_variable)
            else:
                end_query = Query(end, self.params)
                end_query.build_save_pypher()

                if len(end_query.creates):
                    rel.append(*end_query.creates)
                elif len(end_query.merges):
                    end_merge = Pypher().MERGE(*end_query.merges)

                    if end_query.on_create_sets:
                        end_merge.OnCreateSet(*end_query.on_create_sets)

                    if end_query.on_match_sets:
                        end_merge.OnMatchSet(*end_query.on_match_sets)

                    self.before_matches.append(end_merge)
                    rel.node(end.query_variable)

            if ensure_unique:
                self.merges.append(rel)
            else:
                self.creates.append(rel)
        else:
            _id = VM.get_next(entity, 'id')
            _id = Param(_id, entity.id)

            if start.id is not None:
                rel = rel.node(start.query_variable)
            else:
                start_query = Query(start, self.params)
                start_query.build_save_pypher()

                if len(start_query.creates):
                    rel.append(*start_query.creates)
                elif len(start_query.merges):
                    start_merge = Pypher().MERGE(*start_query.merges)

                    if start_query.on_create_sets:
                        start_merge.OnCreateSet(*start_query.on_create_sets)

                    if start_query.on_match_sets:
                        start_merge.OnMatchSet(*start_query.on_match_sets)

                    if len(self.matches):
                        self.matches[-1].append(start_merge)
                    else:
                        self.matches.append(start_merge)

                    rel.node(start.query_variable)

            rel.rel(entity.query_variable, labels=entity.labels,
                direction='out')

            if end.id is not None:
                rel.node(end.query_variable)
            else:
                end_query = Query(end, self.params)
                end_query.build_save_pypher()

                if len(end_query.creates):
                    rel.append(*end_query.creates)
                elif len(end_query.merges):
                    end_merge = Pypher().MERGE(*end_query.merges)

                    if end_query.on_create_sets:
                        end_merge.OnCreateSet(*end_query.on_create_sets)

                    if end_query.on_match_sets:
                        end_merge.OnMatchSet(*end_query.on_match_sets)

                    if len(self.matches):
                        self.matches[-1].append(end_merge)
                    else:
                        self.matches.append(end_merge)

                    rel.node(end.query_variable)

            rel.WHERE(__.ID(entity.query_variable) == _id)
            self._update_properties(entity)
            self.matches.append(rel)

        self.returns.append(entity.query_variable)

        return self

    def delete(self, detach=False):
        for entity in self.entities:
            if not entity.id:
                continue

            if isinstance(entity, Node):
                self.delete_node(entity=entity)
            elif isinstance(entity, Relationship):
                self.delete_relationship(entity=entity)

                detach = False

        pypher = self.pypher

        if self.matches:
            for match in self.matches:
                pypher.MATCH(match)

        if detach:
            pypher.DETACH

        pypher.DELETE(*self.deletes)

        return str(pypher), pypher.bound_params

    def delete_node(self, entity):
        _id = VM.get_next(entity, 'id')
        _id = Param(_id, entity.id)
        match = __.node(entity.query_variable)
        match.WHERE(__.ID(entity.query_variable) == _id)

        self.matches.append(match)
        self.deletes.append(entity.query_variable)

        return self

    def delete_relationship(self, entity):
        _id = VM.get_next(entity, 'id')
        _id = Param(_id, entity.id)
        match = __.node()
        match.rel(entity.query_variable, labels=entity.labels)
        match.node()
        match.WHERE(__.ID(entity.query_variable) == _id)

        self.matches.append(match)
        self.deletes.append(entity.query_variable)

        return self

    def _properties(self, entity, unique_only=False):
        props = {}
        mapper = get_mapper(entity)
        properties = mapper.entity_data(entity.data, unique_only=unique_only,
            data_type='graph')

        for field, value in properties.items():
            name = VM.get_next(entity, field)
            param = Param(name=name, value=value)

            self.pypher.bind_param(param)

            props[field] = param

        return props

    def _update_properties(self, entity):
        props = self._properties(entity)
        qv = entity.query_variable

        for field, value in props.items():
            stmt = getattr(__, qv).property(field)._
            stmt == value
            self.sets.append(stmt)

        return self


class RelatedEntityQuery(_BaseQuery):

    def __init__(self, direction='out', relationship_entity=None,
                 relationship_type=None, relationship_prpoerties=None,
                 start_entity=None, end_entity=None, params=None,
                 single_relationship=False, start_query_variable='start_node',
                 relationship_query_variable='relt',
                 end_query_variable='end_node'):
        super(RelatedEntityQuery, self).__init__()

        self.direction = direction
        self.relationship_entity = relationship_entity
        self.relationship_type = relationship_type
        self.start_query_variable = start_query_variable
        self.relationship_query_variable = relationship_query_variable
        self.end_query_variable = end_query_variable
        self._start_entity = None
        self.start_entity = start_entity
        self._end_entity = None
        self.end_entity = end_entity
        self.relationship_prpoerties = relationship_prpoerties or {}
        self.params = params
        self.skip = None
        self.limit = 1 if single_relationship else None

    def reset(self):
        super(RelatedEntityQuery, self).reset()

        self.skip = None
        self.limit = None

        if self.start_entity:
            self.start_entity.query_variable = self.start_query_variable

        if self.end_entity:
            self.end_entity.query_variable = self.end_query_variable

    def _get_relationship_entity(self):
        return self._relationship_entity

    def _set_relationship_entity(self, relationship):
        if relationship is not None and not isinstance(relationship,
            Relationship):
            raise AttributeError('Must be an <Relationship> and not'
                ' a <{t}>'.format(t=type(relationship)))

        self._relationship_entity = relationship

        return self

    relationship_entity = property(_get_relationship_entity,
        _set_relationship_entity)

    def _get_start_entity(self):
        return self._start_entity

    def _set_start_entity(self, entity):
        if entity is not None and not isinstance(entity, Node):
            raise AttributeError('entity must be a Node instance')

        if entity:
            entity.query_variable = self.start_query_variable

        self._start_entity = entity

    start_entity = property(_get_start_entity, _set_start_entity)

    def _get_end_entity(self):
        return self._end_entity

    def _set_end_entity(self, entity):
        if entity is not None and not isinstance(entity, Node):
            raise AttributeError('entity must be a Node instance')

        if entity:
            entity.query_variable = self.end_query_variable

        self._end_entity = entity

    end_entity = property(_get_end_entity, _set_end_entity)

    def _build_start(self):
        pypher = Pypher()

        if self.start_entity.id:
            qv = self.start_entity.query_variable
            where = __.ID(qv) == self.start_entity.id

            pypher.NODE(qv)
            self.wheres.append(where)
        else:
            pypher.NODE(self.start_query_variable,
                labels=self.start_entity.labels)

        return pypher

    def _build_end(self):
        pypher = Pypher()
        qv = self.end_query_variable
        labels = None

        if self.end_entity:
            qv = self.end_entity.query_variable
            labels = self.end_entity.labels

        pypher.NODE(qv, labels=labels)
        self.returns.append(qv)

        return pypher

    def _build_relationship(self):
        pypher = Pypher()

        if self.relationship_entity:
            self.relationship_entity.query_variable =\
                self.relationship_query_variable

            pypher.relationship(
                self.relationship_entity.query_variable,
                direction=self.direction,
                labels=self.relationship_entity.labels,
                **self.relationship_prpoerties)
        else:
            pypher.relationship(direction=self.direction,
                labels=self.relationship_type)

        return pypher

    def query(self, return_relationship=False, returns=None):
        if not self.start_entity:
            raise RelatedQueryException(('Related objects must have a'
                ' start entity'))

        self.pypher = Pypher()
        pypher = self.pypher

        self.matches.insert(0, self._build_end())
        self.matches.insert(0, self._build_relationship())
        self.matches.insert(0, self._build_start())

        self.pypher.MATCH

        for match in self.matches:
            self.pypher.append(match)

        if self.wheres:
            self.pypher.WHERE.CAND(*self.wheres)

        if return_relationship:
            ret = getattr(__, self.relationship_query_variable)
            self.returns = [ret,]

        returns = returns or self.returns

        self.pypher.RETURN(*returns)

        if self.orders:
            self.pypher.ORDER.BY(*self.orders)

        if self.skip is not None:
            self.pypher.SKIP(self.skip)

        if self.limit is not None:
            self.pypher.LIMIT(self.limit)

        self.reset()

        return str(pypher), pypher.bound_params

    def connect(self, entity, properties=None):
        if not self.start_entity:
            message = ('The relationship {} does not have a start'
                ' entity'.format(self.relationship_entity
                    or self.relationship_type))

            raise RelatedQueryException(('The relationship {} does not '))

        kwargs = {
            'start': self.start_entity,
            'end': entity,
            'properties': properties,
        }

        if self.relationship_entity:
            return self.relationship_entity.__class__(**kwargs)

        kwargs['labels'] = self.relationship_type

        return Relationship(**kwargs)

    def delete(self, entity):
        if isinstance(entity, Relationship):
            if entity.id:
                query = Query(entity)

                return query.delete()
            elif entity.end and entity.end.id:
                self.matches.insert(0, self._build_end())
                self.matches.insert(0, self._build_relationship())
                self.matches.insert(0, self._build_start())

                self.pypher.MATCH

                for match in self.matches:
                    self.pypher.append(match)

                self.pypher.DETACH.DELETE(self.relationship_query_variable)
                self.reset()

                return str(self.pypher), self.pypher.bound_params

    def delete_by_entity_id(self, *ids):
        if not ids:
            msg = 'There must be ids passed in to the delete method'
            raise AttributeError(msg)


        def _build_start():
            pypher = Pypher()

            if self.start_entity.id:
                qv = self.start_entity.query_variable
                where = __.ID(qv) == self.start_entity.id

                pypher.NODE(qv)
                self.wheres.append(where)
            else:
                pypher.NODE(self.start_query_variable)

            return pypher


        self.pypher = Pypher()
        self.matches.insert(0, self._build_end())
        self.matches.insert(0, self._build_relationship())
        self.matches.insert(0, _build_start())

        self.pypher.MATCH

        for match in self.matches:
            self.pypher.append(match)

        id_params = []

        for i in ids:
            key = 'end_id_{}'.format(i)
            id_params.append(Param(key, i))

        self.wheres.append(__.ID(self.end_query_variable).IN(*id_params))
        _id = __.ID(self.start_query_variable)

        if self.start_entity.id:
            self.wheres.append(_id == self.start_entity.id)
        # else:
        #     wheres.append(_id)

        self.pypher.WHERE.CAND(*self.wheres)
        self.pypher.DELETE(self.relationship_query_variable)
        self.reset()

        return str(self.pypher), self.pypher.bound_params


class QueryException(Exception):
    pass


class RelatedQueryException(QueryException):
    pass


class QueryBuilderException(QueryException):
    pass


class Builder(Pypher):

    def __init__(self, entity, parent=None, params=None, *args, **kwargs):
        if isinstance(entity, Entity):
            VM.set_query_var(entity)
            params = Params(prefix='', key=entity.query_variable)
            self.__entity__ = entity

        super(Builder, self).__init__(parent=parent, params=params, *args,
            **kwargs)

        if isinstance(entity, Relationship):
            self.MATCH.node(self.start).rel(entity.query_variable,
                labels=entity.labels)
            self.node(self.end)
        elif isinstance(entity, Node):
            self.MATCH.node(entity.query_variable, labels=entity.labels)
        else:
            msg = ('The entity {} must be either a Node or '
                'Relationship').format(repr(entity))
            raise QueryBuilderException(msg)

        if entity.id is not None:
            self.WHERE(__.id(self.entity) == entity.id)

    def bind_param(self, value, name=None):
        if not isinstance(value, Param):
            name = VM.get_next(self.entity, name)
            param = Param(name, value)

        return super(Builder, self).bind_param(value=Param, name=name)

    @property
    def start(self):
        return getattr(__, 'start_node')

    @property
    def end(self):
        return getattr(__, 'end_node')

    @property
    def entity(self):
        return getattr(__, self.__entity__.query_variable)


class Helpers(object):

    def get_by_id(self, entity, id_val=None):
        '''This method is used to build a query that will return an entity
        --Node, Relationship-- by its id. It will create a query that looks
        like:

            MATCH ()-[r0:`Labels`]-() WHERE id(r0) = $r0_id_0 RETURN DISTINCT r

        for relationships OR for nodes

            MATCH (n0:`Labels`) WHERE id(n0) = $n0_id_0 RETURN DISTINCT n0
        '''
        entity.id = id_val
        b = Builder(entity)

        b.RETURN.DISTINCT(b.entity)

        return str(b), b.bound_params

    def get_by_ids(self, entity, ids):
        p = Pypher()
        p.MATCH

        if isinstance(entity, Relationship):
            var = 'rel'
            p.node().rel(var, labels=entity.labels).node()
        else:
            var = 'node'
            p.node(var, labels=entity.labels)

        id_params = []

        for i in ids:
            key = 'entity_id_{}'.format(i)
            id_params.append(Param(key, i))

        p.WHERE.COR(__.ID(var).IN(*id_params))
        p.RETURN(var)

        return str(p), p.bound_params

    def get_start(self, entity):
        b = Builder(entity)

        b.RETURN(b.start)

        return str(b), b.bound_params

    def get_end(self, entity):
        b = Builder(entity)

        b.RETURN(b.end)

        return str(b), b.bound_params
