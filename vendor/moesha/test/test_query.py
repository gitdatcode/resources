import unittest

from random import random, randint

from moesha.entity import (Node, Relationship)
from moesha.query import (Query, RelatedEntityQuery, QueryException,
    RelatedQueryException)
from moesha.mapper import (Mapper, EntityMapper)
from moesha.property import String
from moesha.util import _query_debug


def get_dict_key(dict, value):
    for k, v in dict.items():
        if v == value:
            return k

    return None


class OpenNode(Node):
    _labels = ['Node',]


class OpenNodeMapper(EntityMapper):
    entity = OpenNode
    __ALLOW_UNDEFINED_PROPERTIES__ = True


class OpenRelationship(Relationship):
    _labels = ['Relationship',]


class OpenRelationshipMapper(EntityMapper):
    entity = OpenRelationship
    __ALLOW_UNDEFINED_PROPERTIES__ = True


class UniquePropertiesNode(Node):
    pass


class UniquePropertiesNodeMapper(EntityMapper):
    entity = UniquePropertiesNode
    __PROPERTIES__ = {
        'name': String(ensure_unique=True),
        'location': String(),
    }


class NodeQueryTests(unittest.TestCase):
    
    def test_can_build_single_node_create_query(self):
        name = 'mark {}'.format(random())
        n = OpenNode(properties={'name': name})
        q = Query(n)
        query, params = q.save()
        exp = 'CREATE ({var}:`{labels}` {{`name`: ${val}}}) RETURN {var}'.format(
            var=n.query_variable, val=get_dict_key(params, name), labels=n.labels[0])

        self.assertEqual(exp, query)
        self.assertEqual(1, len(params))

    def test_can_build_single_node_with_one_unique_property_create_query(self):
        name = 'mark {}'.format(random())
        loc = 'loc {}'.format(random())
        n = UniquePropertiesNode(properties={'name': name, 'location': loc})
        q = Query(n)
        query, params = q.save()
        exp = ('MERGE ({var}:`{label}` {{`name`: ${name_val}}})'
            ' ON CREATE SET {var}.`location` = ${loc_val}, {var}.`name` = ${name_val}'
            ' ON MATCH SET {var}.`location` = ${loc_val}, {var}.`name` = ${name_val}'
            ' RETURN {var}').format(
            var=n.query_variable, name_val=get_dict_key(params, name),
            loc_val=get_dict_key(params, loc), label=n.labels[0])

        self.assertEqual(exp, query)
        self.assertEqual(2, len(params))

    def test_can_build_single_node_with_multiple_unique_properties_create_query(self):

        class UniqueMultiplePropertiesNode(Node):
            pass


        class UniqueMultiplePropertiesNodeMapper(EntityMapper):
            entity = UniqueMultiplePropertiesNode
            __PROPERTIES__ = {
                'name': String(ensure_unique=True),
                'location': String(ensure_unique=True),
            }

        name = 'mark {}'.format(random())
        loc = 'loc {}'.format(random())
        n = UniqueMultiplePropertiesNode(properties={'name': name, 'location': loc})
        q = Query(n)
        query, params = q.save()
        exp = ('MERGE ({var}:`{label}` {{`location`: ${loc_val}, `name`: ${name_val}}})'
            ' ON CREATE SET {var}.`location` = ${loc_val}, {var}.`name` = ${name_val}'
            ' ON MATCH SET {var}.`location` = ${loc_val}, {var}.`name` = ${name_val}'
            ' RETURN {var}').format(
            var=n.query_variable, name_val=get_dict_key(params, name),
            loc_val=get_dict_key(params, loc), label=n.labels[0])

        self.assertEqual(exp, query)
        self.assertEqual(2, len(params))

    def test_can_build_mutiple_node_create_query(self):
        name = 'mark {}'.format(random())
        n = OpenNode(properties={'name': name})
        name2 = 'mark {}'.format(random())
        n2 = OpenNode(properties={'name': name2})
        q = Query([n, n2])
        query, params = q.save()
        exp = 'CREATE ({var}:`{var_label}` {{`name`: ${val}}}), ({var2}:`{var2_label}` {{`name`: ${val2}}}) RETURN {var}, {var2}'.format(
            var=n.query_variable, val=get_dict_key(params, name),
            var2=n2.query_variable, val2=get_dict_key(params, name2),
            var_label=n.labels[0], var2_label=n2.labels[0])

        self.assertEqual(exp, query)
        self.assertEqual(2, len(params))

    def test_can_build_single_node_update_query(self):
        name = 'mark {}'.format(random())
        _id = 999
        n = OpenNode(id=_id, properties={'name': name})
        q = Query(n)
        query, params = q.save()
        exp = "MATCH ({var}) WHERE id({var}) = ${id} SET {var}.`name` = ${val} RETURN {var}".format(
            var=n.query_variable, val=get_dict_key(params, name),
            id=get_dict_key(params, _id))

        self.assertEqual(exp, query)
        self.assertEqual(2, len(params))

    def test_can_build_multiple_node_update_query(self):
        name = 'mark {}'.format(random())
        _id = 999
        n = OpenNode(id=_id, properties={'name': name})
        name2 = 'kram {}'.format(random())
        _id2 = 888
        n2 = OpenNode(id=_id2, properties={'name': name2})
        q = Query([n, n2])
        query, params = q.save()
        exp = "MATCH ({var}) WHERE id({var}) = ${id} MATCH ({var2}) WHERE id({var2}) = ${id2} SET {var}.`name` = ${val}, {var2}.`name` = ${val2} RETURN {var}, {var2}".format(
            var=n.query_variable, val=get_dict_key(params, name),
            id=get_dict_key(params, _id), var2=n2.query_variable,
            val2=get_dict_key(params, name2), id2=get_dict_key(params, _id2))

        self.assertEqual(exp, query)
        self.assertEqual(4, len(params))

    def test_can_delete_single_existing_node(self):
        _id = 999
        n = Node(id=_id)
        q = Query(n)
        query, params = q.delete()
        exp = "MATCH ({var}) WHERE id({var}) = ${id} DELETE {var}".format(
            var=n.query_variable, id=get_dict_key(params, _id))

        self.assertEqual(exp, query)
        self.assertEqual(1, len(params))

    def test_can_detach_delete_single_existing_node(self):
        _id = 999
        n = Node(id=_id)
        q = Query(n)
        query, params = q.delete(detach=True)
        exp = "MATCH ({var}) WHERE id({var}) = ${id} DETACH DELETE {var}".format(
            var=n.query_variable, id=get_dict_key(params, _id))

        self.assertEqual(exp, query)
        self.assertEqual(1, len(params))

    def test_can_delete_multiple_existing_nodes(self):
        _id = 999
        n = Node(id=_id)
        _id2 = 777
        n2 = Node(id=_id2)
        q = Query([n, n2])
        query, params = q.delete()
        exp = ("MATCH ({var}) WHERE id({var}) = ${id}"
            " MATCH ({var2}) WHERE id({var2}) = ${id2}"
            " DELETE {var}, {var2}".format(
            var=n.query_variable, id=get_dict_key(params, _id),
            var2=n2.query_variable, id2=get_dict_key(params, _id2)))

        self.assertEqual(exp, query)
        self.assertEqual(2, len(params))

    def test_can_detach_delete_multiple_existing_nodes(self):
        _id = 999
        n = Node(id=_id)
        _id2 = 777
        n2 = Node(id=_id2)
        q = Query([n, n2])
        query, params = q.delete(detach=True)
        exp = ("MATCH ({var}) WHERE id({var}) = ${id}"
            " MATCH ({var2}) WHERE id({var2}) = ${id2}"
            " DETACH DELETE {var}, {var2}".format(
            var=n.query_variable, id=get_dict_key(params, _id),
            var2=n2.query_variable, id2=get_dict_key(params, _id2)))

        self.assertEqual(exp, query)
        self.assertEqual(2, len(params))

    def test_can_delete_multiple_existing_nodes_with_id(self):
        _id = 999
        n = Node(id=_id)
        _id2 = 777
        n2 = Node(id=_id2)
        n3 = Node()
        q = Query([n, n2])
        query, params = q.delete(detach=True)
        exp = ("MATCH ({var}) WHERE id({var}) = ${id}"
            " MATCH ({var2}) WHERE id({var2}) = ${id2}"
            " DETACH DELETE {var}, {var2}".format(
            var=n.query_variable, id=get_dict_key(params, _id),
            var2=n2.query_variable, id2=get_dict_key(params, _id2)))

        self.assertEqual(exp, query)
        self.assertEqual(2, len(params))


class RelatedEntityQueryTests(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_can_build_single_create_relationship_with_existing_nodes_create_query(self):
        sid = 99
        n = 'mark {}'.format(random())
        start = OpenNode(id=sid, properties={'name': n})
        eid = 88
        n2 = 'kram {}'.format(random())
        end = OpenNode(id=eid, properties={'name': n2})
        since = 'yeserday'
        rel = OpenRelationship(start=start, end=end, properties={'since': since})
        q = Query(rel)
        query, params = q.save()
        label = rel.type
        exp = ("MATCH ({var}) WHERE id({var}) = ${id}"
            " MATCH ({var2}) WHERE id({var2}) = ${id2}"
            " CREATE ({var})-[{var3}:`{rel_label}` {{`since`: ${since}}}]->({var2})"
            " SET {var}.`name` = ${val1}, {var2}.`name` = ${val2}"
            " RETURN {var}, {var2}, {var3}").format(var=start.query_variable,
                var2=end.query_variable, var3=rel.query_variable, label=label,
                id=get_dict_key(params, sid), id2=get_dict_key(params, eid),
                val1=get_dict_key(params, n), val2=get_dict_key(params, n2),
                since=get_dict_key(params, since), rel_label=rel.labels)

        self.assertEqual(exp, query)
        self.assertEqual(5, len(params))

    def test_can_build_single_create_relationship_with_existing_nodes_create_query_with_ensure_unique(self):
        sid = 99
        n = 'mark {}'.format(random())
        start = OpenNode(id=sid, properties={'name': n})
        eid = 88
        n2 = 'kram {}'.format(random())
        end = OpenNode(id=eid, properties={'name': n2})
        since = 'yeserday'
        rel = OpenRelationship(start=start, end=end, properties={'since': since})
        q = Query(rel)
        query, params = q.save(ensure_unique=True)
        label = rel.type
        exp = ("MATCH ({var}) WHERE id({var}) = ${id}"
            " MATCH ({var2}) WHERE id({var2}) = ${id2}"
            " MERGE ({var})-[{var3}:`{rel_label}` {{`since`: ${since}}}]->({var2})"
            " SET {var}.`name` = ${val1}, {var2}.`name` = ${val2}"
            " RETURN {var}, {var2}, {var3}").format(var=start.query_variable,
                var2=end.query_variable, var3=rel.query_variable, label=label,
                id=get_dict_key(params, sid), id2=get_dict_key(params, eid),
                val1=get_dict_key(params, n), val2=get_dict_key(params, n2),
                since=get_dict_key(params, since), rel_label=rel.labels)

        self.assertEqual(exp, query)
        self.assertEqual(5, len(params))

    def test_can_build_single_create_relationship_with_two_new_nodes_create_query(self):
        n = 'mark {}'.format(random())
        start = OpenNode(properties={'name': n})
        n2 = 'kram {}'.format(random())
        end = OpenNode(properties={'name': n2})
        since = 'yeserday'
        rel = OpenRelationship(start=start, end=end, properties={'since': since})
        q = Query(rel)
        query, params = q.save()
        label = rel.type

        exp = ("CREATE ({var}:`{start_label}` {{`name`: ${name}}})-[{rel}:`{label}` {{`since`: ${since}}}]->({var2}:`{end_label}` {{`name`: ${name2}}})"
            " RETURN {var}, {var2}, {rel}".format(var=start.query_variable,
                rel=rel.query_variable, label=rel.labels,
                since=get_dict_key(params, since), var2=end.query_variable,
                name=get_dict_key(params, n), name2=get_dict_key(params, n2),
                start_label=start.labels[0], end_label=end.labels[0]))

        self.assertEqual(exp, query)
        self.assertEqual(3, len(params))

    # cases cover a mix of start and end with unique properties via a relationship.ensure_unique=Fase
    def test_can_build_single_create_relationship_with_two_new_nodes_with_unique_properties_create_query(self):
        n = 'mark {}'.format(random())
        start = UniquePropertiesNode(properties={'name': n})
        n2 = 'kram {}'.format(random())
        end = UniquePropertiesNode(properties={'name': n2})
        since = 'yeserday'
        rel = OpenRelationship(start=start, end=end, properties={'since': since})
        q = Query(rel)
        query, params = q.save()
        label = rel.type

        exp = ("MERGE ({start_var}:`{start_label}` {{`name`: ${start_name}}})"
            " ON CREATE SET {start_var}.`location` = ${start_loc}, {start_var}.`name` = ${start_name}"
            " ON MATCH SET {start_var}.`location` = ${start_loc}, {start_var}.`name` = ${start_name}"
            " MERGE ({end_var}:`{end_label}` {{`name`: ${end_name}}})"
            " ON CREATE SET {end_var}.`location` = ${end_loc}, {end_var}.`name` = ${end_name}"
            " ON MATCH SET {end_var}.`location` = ${end_loc}, {end_var}.`name` = ${end_name}"
            " CREATE ({start_var})-[{rel_var}:`{rel_label}` {{`since`: ${rel_since}}}]->({end_var})"
            " RETURN {start_var}, {end_var}, {rel_var}"
            ).format(start_var=start.query_variable, start_label=start.labels[0],
            start_name=get_dict_key(params, n), start_loc=get_dict_key(params, ''),
            end_var=end.query_variable, end_label=end.labels[0],
            end_name=get_dict_key(params, n2), end_loc=get_dict_key(params, ''),
            rel_var=rel.query_variable, rel_since=get_dict_key(params, since),
            rel_label=rel.labels)

       
        self.assertEqual(exp, query)
        self.assertEqual(4, len(params))

    def test_can_build_single_create_relationship_with_start_node_with_unique_properties_create_query(self):
        n = 'mark {}'.format(random())
        start = UniquePropertiesNode(properties={'name': n})
        n2 = 'kram {}'.format(random())
        end = OpenNode(properties={'name': n2})
        since = 'yeserday'
        rel = OpenRelationship(start=start, end=end, properties={'since': since})
        q = Query(rel)
        query, params = q.save()
        label = rel.type

        exp = ("MERGE ({start_var}:`{start_label}` {{`name`: ${start_name}}})"
            " ON CREATE SET {start_var}.`location` = ${start_loc}, {start_var}.`name` = ${start_name}"
            " ON MATCH SET {start_var}.`location` = ${start_loc}, {start_var}.`name` = ${start_name}"
            " CREATE ({start_var})-[{rel_var}:`{rel_label}` {{`since`: ${rel_since}}}]"
            "->({end_var}:`{end_label}` {{`name`: ${end_name}}})"
            " RETURN {start_var}, {end_var}, {rel_var}"
            ).format(start_var=start.query_variable, start_label=start.labels[0],
            start_name=get_dict_key(params, n), start_loc=get_dict_key(params, ''),
            end_var=end.query_variable, end_label=end.labels[0],
            end_name=get_dict_key(params, n2), end_loc=get_dict_key(params, ''),
            rel_var=rel.query_variable, rel_since=get_dict_key(params, since),
            rel_label=rel.labels)

       
        self.assertEqual(exp, query)
        self.assertEqual(4, len(params))

    def test_can_build_single_create_relationship_with_end_node_with_unique_properties_create_query(self):
        n = 'mark {}'.format(random())
        start = OpenNode(properties={'name': n})
        n2 = 'kram {}'.format(random())
        end = UniquePropertiesNode(properties={'name': n2})
        since = 'yeserday'
        rel = OpenRelationship(start=start, end=end, properties={'since': since})
        q = Query(rel)
        query, params = q.save()
        label = rel.type

        exp = ("MERGE ({end_var}:`{end_label}` {{`name`: ${end_name}}})"
            " ON CREATE SET {end_var}.`location` = ${end_loc}, {end_var}.`name` = ${end_name}"
            " ON MATCH SET {end_var}.`location` = ${end_loc}, {end_var}.`name` = ${end_name}"
            " CREATE ({start_var}:`{start_label}` {{`name`: ${start_name}}})-[{rel_var}:`{rel_label}` {{`since`: ${rel_since}}}]"
            "->({end_var})"
            " RETURN {start_var}, {end_var}, {rel_var}"
            ).format(start_var=start.query_variable, start_label=start.labels[0],
            start_name=get_dict_key(params, n), start_loc=get_dict_key(params, ''),
            end_var=end.query_variable, end_label=end.labels[0],
            end_name=get_dict_key(params, n2), end_loc=get_dict_key(params, ''),
            rel_var=rel.query_variable, rel_since=get_dict_key(params, since),
            rel_label=rel.labels)

       
        self.assertEqual(exp, query)
        self.assertEqual(4, len(params))

    # cases cover a mix of start and end with unique properties via a relationship.ensure_unique=True
    def test_can_build_single_create_relationship_with_two_new_nodes_with_unique_properties_create_query_with_ensure_unique_relationship(self):
        n = 'mark {}'.format(random())
        start = UniquePropertiesNode(properties={'name': n})
        n2 = 'kram {}'.format(random())
        end = UniquePropertiesNode(properties={'name': n2})
        since = 'yeserday'
        rel = OpenRelationship(start=start, end=end, properties={'since': since})
        q = Query(rel)
        query, params = q.save(ensure_unique=True)
        label = rel.type

        exp = ("MERGE ({start_var}:`{start_label}` {{`name`: ${start_name}}})"
            " ON CREATE SET {start_var}.`location` = ${start_loc}, {start_var}.`name` = ${start_name}"
            " ON MATCH SET {start_var}.`location` = ${start_loc}, {start_var}.`name` = ${start_name}"
            " MERGE ({end_var}:`{end_label}` {{`name`: ${end_name}}})"
            " ON CREATE SET {end_var}.`location` = ${end_loc}, {end_var}.`name` = ${end_name}"
            " ON MATCH SET {end_var}.`location` = ${end_loc}, {end_var}.`name` = ${end_name}"
            " MERGE ({start_var})-[{rel_var}:`{rel_label}` {{`since`: ${rel_since}}}]->({end_var})"
            " RETURN {start_var}, {end_var}, {rel_var}"
            ).format(start_var=start.query_variable, start_label=start.labels[0],
            start_name=get_dict_key(params, n), start_loc=get_dict_key(params, ''),
            end_var=end.query_variable, end_label=end.labels[0],
            end_name=get_dict_key(params, n2), end_loc=get_dict_key(params, ''),
            rel_var=rel.query_variable, rel_since=get_dict_key(params, since),
            rel_label=rel.labels)

       
        self.assertEqual(exp, query)
        self.assertEqual(4, len(params))

    def test_can_build_single_create_relationship_with_start_node_with_unique_properties_create_query_with_ensure_unique_relationship(self):
        n = 'mark {}'.format(random())
        start = UniquePropertiesNode(properties={'name': n})
        n2 = 'kram {}'.format(random())
        end = OpenNode(properties={'name': n2})
        since = 'yeserday'
        rel = OpenRelationship(start=start, end=end, properties={'since': since})
        q = Query(rel)
        query, params = q.save(ensure_unique=True)
        label = rel.type

        exp = ("MERGE ({start_var}:`{start_label}` {{`name`: ${start_name}}})"
            " ON CREATE SET {start_var}.`location` = ${start_loc}, {start_var}.`name` = ${start_name}"
            " ON MATCH SET {start_var}.`location` = ${start_loc}, {start_var}.`name` = ${start_name}"
            " MERGE ({start_var})-[{rel_var}:`{rel_label}` {{`since`: ${rel_since}}}]"
            "->({end_var}:`{end_label}` {{`name`: ${end_name}}})"
            " RETURN {start_var}, {end_var}, {rel_var}"
            ).format(start_var=start.query_variable, start_label=start.labels[0],
            start_name=get_dict_key(params, n), start_loc=get_dict_key(params, ''),
            end_var=end.query_variable, end_label=end.labels[0],
            end_name=get_dict_key(params, n2), end_loc=get_dict_key(params, ''),
            rel_var=rel.query_variable, rel_since=get_dict_key(params, since),
            rel_label=rel.labels)

       
        self.assertEqual(exp, query)
        self.assertEqual(4, len(params))

    def test_can_build_single_create_relationship_with_end_node_with_unique_properties_create_query_with_ensure_unique_relationship(self):
        n = 'mark {}'.format(random())
        start = OpenNode(properties={'name': n})
        n2 = 'kram {}'.format(random())
        end = UniquePropertiesNode(properties={'name': n2})
        since = 'yeserday'
        rel = OpenRelationship(start=start, end=end, properties={'since': since})
        q = Query(rel)
        query, params = q.save(ensure_unique=True)
        label = rel.type

        exp = ("MERGE ({end_var}:`{end_label}` {{`name`: ${end_name}}})"
            " ON CREATE SET {end_var}.`location` = ${end_loc}, {end_var}.`name` = ${end_name}"
            " ON MATCH SET {end_var}.`location` = ${end_loc}, {end_var}.`name` = ${end_name}"
            " MERGE ({start_var}:`{start_label}` {{`name`: ${start_name}}})-[{rel_var}:`{rel_label}` {{`since`: ${rel_since}}}]"
            "->({end_var})"
            " RETURN {start_var}, {end_var}, {rel_var}"
            ).format(start_var=start.query_variable, start_label=start.labels[0],
            start_name=get_dict_key(params, n), start_loc=get_dict_key(params, ''),
            end_var=end.query_variable, end_label=end.labels[0],
            end_name=get_dict_key(params, n2), end_loc=get_dict_key(params, ''),
            rel_var=rel.query_variable, rel_since=get_dict_key(params, since),
            rel_label=rel.labels)

       
        self.assertEqual(exp, query)
        self.assertEqual(4, len(params))

    def test_can_build_single_create_relationship_with_one_existing_one_new_node_create_query(self):
        sid = 99
        n = 'mark {}'.format(random())
        start = OpenNode(id=sid, properties={'name': n})
        n2 = 'kram {}'.format(random())
        end = OpenNode(properties={'name': n2})
        since = 'yeserday'
        rel = OpenRelationship(start=start, end=end, properties={'since': since})
        q = Query(rel)
        query, params = q.save()
        label = rel.type
        exp = ("MATCH ({var}) WHERE id({var}) = ${id}"
            " CREATE ({var})-[{rel}:`{label}` {{`since`: ${since}}}]->({var2}:`{end_label}` {{`name`: ${name2}}})"
            " SET {var}.`name` = ${name}"
            " RETURN {var}, {var2}, {rel}".format(var=start.query_variable,
                id=get_dict_key(params, sid),
                rel=rel.query_variable, label=rel.labels,
                since=get_dict_key(params, since), var2=end.query_variable,
                name=get_dict_key(params, n), name2=get_dict_key(params, n2),
                end_label=end.labels[0]))

        self.assertEqual(exp, query)
        self.assertEqual(4, len(params))

    def test_can_build_single_create_multiple_relationship_with_the_same_existing_nodes_create_query(self):
        sid = 99
        n = 'mark {}'.format(random())
        start = OpenNode(id=sid, properties={'name': n})
        eid = 88
        n2 = 'kram {}'.format(random())
        end = OpenNode(id=eid, properties={'name': n2})
        since = 'yeserday'
        label2 = 'knows_two'
        rel2 = OpenRelationship(start=start, end=end, labels=label2, properties={'since': since})
        rel = OpenRelationship(start=start, end=end, properties={'since': since})
        rel2.labels
        q = Query([rel, rel2])
        query, params = q.save()
        label = rel.type
        exp = ("MATCH ({var}) WHERE id({var}) = ${id}"
            " MATCH ({var2}) WHERE id({var2}) = ${id2}"
            " CREATE ({var})-[{var3}:`{rel_label}` {{`since`: ${since}}}]->({var2}),"
            " ({var})-[{var4}:`{label2}` {{`since`: ${since}}}]->({var2})"
            " SET {var}.`name` = ${val1}, {var2}.`name` = ${val2}"
            " RETURN {var}, {var2}, {var3}, {var4}").format(var=start.query_variable,
                var2=end.query_variable, var3=rel.query_variable, label=label,
                id=get_dict_key(params, sid), id2=get_dict_key(params, eid),
                val1=get_dict_key(params, n), val2=get_dict_key(params, n2),
                since=get_dict_key(params, since), var4=rel2.query_variable,
                label2=label2, rel_label=rel.labels)

        self.assertEqual(exp, query)
        self.assertEqual(5, len(params))

    def test_can_build_single_create_multiple_relationship_with_different_existing_nodes_create_query(self):
        sid = 99
        name = 'mark {}'.format(random())
        start = OpenNode(id=sid, properties={'name': name})
        eid = 88
        name2 = 'kram {}'.format(random())
        end = OpenNode(id=eid, properties={'name': name2})
        sid2 = 999
        name3 = 'mark {}'.format(random())
        start2 = OpenNode(id=sid2, properties={'name': name3})
        eid2 = 888
        name4 = 'kram {}'.format(random())
        end2 = OpenNode(id=eid2, properties={'name': name4})
        since = 'yeserday'
        since2 = 'some time ago'
        label2 = 'knows_two'
        rel = OpenRelationship(start=start, end=end, properties={'since': since})
        rel2 = OpenRelationship(start=start2, end=end2, labels=label2,
            properties={'since': since2})
        q = Query([rel, rel2])
        query, params = q.save()
        label = rel.type
        exp = ("MATCH ({var}) WHERE id({var}) = ${id}"
            " MATCH ({var2}) WHERE id({var2}) = ${id2}"
            " MATCH ({var3}) WHERE id({var3}) = ${id3}"
            " MATCH ({var4}) WHERE id({var4}) = ${id4}"
            " CREATE ({var})-[{rel}:`{rel_label}` {{`since`: ${since}}}]->({var2}),"
            " ({var3})-[{rel2}:`{rel2_label}` {{`since`: ${since2}}}]->({var4})"
            " SET {var}.`name` = ${name}, {var2}.`name` = ${name2}, {var3}.`name` = ${name3}, {var4}.`name` = ${name4}"
            " RETURN {var}, {var2}, {rel}, {var3}, {var4}, {rel2}").format(
                var=start.query_variable, id=get_dict_key(params, sid),
                var2=end.query_variable, id2=get_dict_key(params, eid),
                var3=start2.query_variable, id3=get_dict_key(params, sid2),
                var4=end2.query_variable, id4=get_dict_key(params, eid2),
                rel=rel.query_variable, since=get_dict_key(params, since),
                rel2=rel2.query_variable, since2=get_dict_key(params, since2),
                label=label2, name=get_dict_key(params, name),
                name2=get_dict_key(params, name2), name3=get_dict_key(params, name3),
                name4=get_dict_key(params, name4), rel_label=rel.type,
                rel2_label=rel2.type)

        self.assertEqual(exp, query)
        self.assertEqual(10, len(params))

    def test_can_build_single_create_multiple_relationship_with_different_existing_and_new_nodes_create_query(self):
        name = 'mark {}'.format(random())
        start = OpenNode(properties={'name': name})
        eid = 88
        name2 = 'kram {}'.format(random())
        end = OpenNode(id=eid, properties={'name': name2})
        name3 = 'mark {}'.format(random())
        start2 = OpenNode(properties={'name': name3})
        eid2 = 888
        name4 = 'kram {}'.format(random())
        end2 = OpenNode(id=eid2, properties={'name': name4})
        since = 'yeserday'
        since2 = 'some time ago'
        label2 = 'knows_two'
        rel = OpenRelationship(start=start, end=end, properties={'since': since})
        rel2 = OpenRelationship(start=start2, end=end2, labels=label2,
            properties={'since': since2})
        q = Query([rel, rel2])
        query, params = q.save()

        label = rel2.type
        exp = ("MATCH ({var2}) WHERE id({var2}) = ${id2}"
            " MATCH ({var4}) WHERE id({var4}) = ${id4}"
            " CREATE ({var}:`{start_label}` {{`name`: ${name}}})-[{rel}:`{rel_label}` {{`since`: ${since}}}]->({var2}),"
            " ({var3}:`{start2_label}` {{`name`: ${name3}}})-[{rel2}:`{label}` {{`since`: ${since2}}}]->({var4})"
            " SET {var2}.`name` = ${name2}, {var4}.`name` = ${name4}"
            " RETURN {var}, {var2}, {rel}, {var3}, {var4}, {rel2}").format(
                var=start.query_variable,
                var2=end.query_variable, id2=get_dict_key(params, eid),
                var3=start2.query_variable,
                var4=end2.query_variable, id4=get_dict_key(params, eid2),
                rel=rel.query_variable, since=get_dict_key(params, since),
                rel2=rel2.query_variable, since2=get_dict_key(params, since2),
                label=label2, name=get_dict_key(params, name),
                name2=get_dict_key(params, name2), name3=get_dict_key(params, name3),
                name4=get_dict_key(params, name4),
                start_label=start.labels[0], rel_label=rel.type, start2_label=start2.labels[0])

        self.assertEqual(exp, query)
        self.assertEqual(8, len(params))

    def test_can_build_single_update_query(self):
        sid = 99
        name = 'mark {}'.format(random())
        start = OpenNode(id=sid, properties={'name': name})
        eid = 88
        name2 = 'kram {}'.format(random())
        end = OpenNode(id=eid, properties={'name': name2})
        rid = 447788
        since = 'since {}'.format(random())
        rel = OpenRelationship(id=rid, start=start, end=end, properties={'since': since})
        q = Query(rel)
        query, params = q.save()

        exp = ("MATCH ({start}) WHERE id({start}) = ${sid}"
            " MATCH ({end}) WHERE id({end}) = ${eid}"
            " MATCH ({start})-[{rel}:`{label}`]->({end}) WHERE id({rel}) = ${rid}"
            " SET {start}.`name` = ${name}, {end}.`name` = ${name2}, {rel}.`since` = ${since}"
            " RETURN {start}, {end}, {rel}".format(start=start.query_variable,
                sid=get_dict_key(params, sid), end=end.query_variable,
                eid=get_dict_key(params, eid), rel=rel.query_variable,
                label=rel.type, name=get_dict_key(params, name),
                name2=get_dict_key(params, name2), rid=get_dict_key(params, rid),
                since=get_dict_key(params, since)))

        self.assertEqual(exp, query)
        self.assertEqual(6, len(params))

    def test_can_build_mixed_update_and_insert_query(self):
        sid = 99
        name = 'mark {}'.format(random())
        start = OpenNode(id=sid, properties={'name': name})
        eid = 88
        name2 = 'kram {}'.format(random())
        end = OpenNode(id=eid, properties={'name': name2})
        rid = 447788
        since = 'since {}'.format(random())
        rel = OpenRelationship(id=rid, start=start, end=end, properties={'since': since})
        sid2 = 887
        name3 = 'name {}'.format(random())
        start2 = OpenNode(id=sid2, properties={'name': name3})
        name4 = 'name {}'.format(random())
        end2 = OpenNode(properties={'name': name4})
        rel2 = OpenRelationship(start=start2, end=end2, properties={'since': since})
        q = Query([rel, rel2])
        query, params = q.save()

        exp = ("MATCH ({start}) WHERE id({start}) = ${sid}"
            " MATCH ({end}) WHERE id({end}) = ${eid}"
            " MATCH ({start})-[{rel}:`{rel_label}`]->({end}) WHERE id({rel}) = ${rid}"
            " MATCH ({start2}) WHERE id({start2}) = ${sid2}"
            " CREATE ({start2})-[{rel2}:`{rel2_label}` {{`since`: ${since}}}]->({end2}:`{end2_label}` {{`name`: ${name4}}})"
            " SET {start}.`name` = ${name}, {end}.`name` = ${name2}, {rel}.`since` = ${since}, {start2}.`name` = ${name3}"
            " RETURN {start}, {end}, {rel}, {start2}, {end2}, {rel2}".format(start=start.query_variable,
                sid=get_dict_key(params, sid), end=end.query_variable,
                eid=get_dict_key(params, eid), rel=rel.query_variable,
                label='Relationship', name=get_dict_key(params, name),
                name2=get_dict_key(params, name2), rid=get_dict_key(params, rid),
                since=get_dict_key(params, since), rel2=rel2.query_variable,
                name3=get_dict_key(params, name3), start2=start2.query_variable,
                sid2=get_dict_key(params, sid2), end2=end2.query_variable,
                name4=get_dict_key(params, name4), rel_label=rel.type,
                rel2_label=rel2.type, end2_label=end2.labels[0]))

        self.assertEqual(exp, query)
        self.assertEqual(9, len(params))

    def test_can_delete_single_existing_relationship(self):
        _id = 999
        n = Node(id=_id)
        _id2 = 999
        n2 = Node(id=_id2)
        _id3 = 8989
        rel = Relationship(start=n, end=n2, id=_id3)
        q = Query(rel)
        query, params = q.delete()
        exp = "MATCH ()-[{var}]-() WHERE id({var}) = ${id} DELETE {var}".format(
            var=rel.query_variable, id=get_dict_key(params, _id3),
            label=rel.type)

        self.assertEqual(exp, query)
        self.assertEqual(1, len(params))

    def test_can_delete_multiple_existing_relationships(self):
        _id = 999
        n = Node(id=_id)
        _id2 = 999
        n2 = Node(id=_id2)
        _id3 = 8989
        rel = Relationship(start=n, end=n2, id=_id3)

        _iid = 134
        nn = Node(id=_iid)
        _id22 = 323
        nn2 = Node(id=_id22)
        _id4 = 9991
        rel2 = Relationship(start=nn, end=nn2, id=_id4)

        q = Query([rel, rel2])
        query, params = q.delete()
        exp = ("MATCH ()-[{var}]-() WHERE id({var}) = ${id}"
            " MATCH ()-[{var2}]-() WHERE id({var2}) = ${id2}"
            " DELETE {var}, {var2}".format(var=rel.query_variable,
            id=get_dict_key(params, _id3),
            label=rel.type, var2=rel2.query_variable,
            id2=get_dict_key(params, _id4),
            label2=rel2.type))

        self.assertEqual(exp, query)
        self.assertEqual(2, len(params))


class RelationshipOutQueryTests(unittest.TestCase):
    direction = 'out'
    relationship_template = '-[{var}:`{label}`]->'

    def get_relationship(self, label, variable=''):
        return self.relationship_template.format(var=variable, label=label)

    def setUp(self):
        class Start(Node):
            pass

        class End(Node):
            pass

        class Other(Node):
            pass

        class Knows(Relationship):
            pass

        self.Knows = Knows()
        self.Start = Start()
        self.Other = Other()
        self.End = End()
        mapper = Mapper(connection=None)
        self.start_mapper = mapper.get_mapper(self.Start)
        self.end_mapper = mapper.get_mapper(self.End)

    def test_cannot_get_relationship_because_missing_context(self):
        self.start_mapper.reset()
        rq = RelatedEntityQuery(
            relationship_entity=self.Knows, single_relationship=False,
            direction=self.direction)
        
        def get():
            rq.query()

        self.assertRaises(RelatedQueryException, get)

    def test_can_get_realtionships_for_new_start_node(self):
        rq = RelatedEntityQuery(
            relationship_entity=self.Knows, direction=self.direction)
        start = self.start_mapper.create()
        rq.start_entity = start
        self.start_mapper(start)

        query, params = rq.query()
        rel = self.get_relationship('Knows', rq.relationship_query_variable)
        exp = 'MATCH ({start}){rel}({end}) RETURN {end}'.format(
            start=rq.start_query_variable, rel=rel,
            end=rq.end_query_variable)
        self.assertEqual(exp, query)
        self.assertEqual(0, len(params))

    def test_can_get_realtionships_for_existing_start_node(self):
        rq = RelatedEntityQuery(
            relationship_entity=self.Knows, direction=self.direction)
        i_d = randint(10, 999)
        start = self.start_mapper.create(id=i_d)
        rq.start_entity = start
        # set context
        self.start_mapper(start)

        query, params = rq.query()
        rel = self.get_relationship('Knows', rq.relationship_query_variable)
        exp = ('MATCH ({start}){rel}({end})'
            ' WHERE (id({start}) = ${id}) RETURN {end}').format(
            start=rq.start_query_variable, rel=rel,
            end=rq.end_query_variable, id=get_dict_key(params, i_d))
        self.assertEqual(exp, query)
        self.assertEqual(1, len(params))

    def test_can_get_single_realtionship_for_new_start_node(self):
        rq = RelatedEntityQuery(
            relationship_entity=self.Knows, single_relationship=True,
            direction=self.direction)
        start = self.start_mapper.create()
        rq.start_entity = start
        self.start_mapper(start)

        query, params = rq.query()
        rel = self.get_relationship('Knows', rq.relationship_query_variable)
        exp = 'MATCH ({start}){rel}({end}) RETURN {end} LIMIT 1'.format(
            start=rq.start_query_variable, rel=rel,
            end=rq.end_query_variable)

        self.assertEqual(exp, query)
        self.assertEqual(0, len(params))

    def test_can_get_single_realtionship_for_existing_start_node(self):
        rq = RelatedEntityQuery(
            relationship_entity=self.Knows, single_relationship=True,
            direction=self.direction)
        start = self.start_mapper.create()
        i_d = randint(10, 999)
        start = self.start_mapper.create(id=i_d)
        rq.start_entity = start
        self.start_mapper(start)
        query, params = rq.query()
        rel = self.get_relationship('Knows', rq.relationship_query_variable)
        exp = ('MATCH ({start}){rel}({end})'
            ' WHERE (id({start}) = ${id}) RETURN {end} LIMIT 1').format(
            start=rq.start_query_variable, rel=rel,
            end=rq.end_query_variable, id=get_dict_key(params, i_d))
        self.assertEqual(exp, query)
        self.assertEqual(1, len(params))

    def test_cannot_add_new_node_to_unrestricted_relationship(self):
        self.start_mapper.reset()
        rq = RelatedEntityQuery(
            relationship_entity=self.Knows, single_relationship=False,
            direction=self.direction)

        def add():
            end = self.end_mapper.create()
            rq.connect(end)

        self.assertRaises(RelatedQueryException, add)

    # note: The RelatedEntityQuery class utilizes the Query class and actual
    # query building tests are taken care of in
    # moesha.test.query.RelatedEntityQueryTests. No need to repeat it here


class RelationshipInQueryTests(RelationshipOutQueryTests):
    direction = 'in'
    relationship_template = '<-[{var}:`{label}`]-'


if __name__ == '__main__':
    unittest.main()
