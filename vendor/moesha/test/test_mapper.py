import unittest
import json
import time

from random import random, randint

from moesha.entity import (Node, Relationship)
from moesha.property import (String, Integer, TimeStamp,
    RelatedEntity)
from moesha.mapper import (Mapper, EntityMapper, get_mapper,
    EntityRelationshipMapper)


class TestConnection(object):

    def query(*args, **kwargs):
        class res(object):
            data = []
            result_data = []

        return res()

    class driver:
        @staticmethod
        def session(*args, **kwargs):

            class Transaction:
                @staticmethod
                def begin_transaction(*args, **kwargs):

                    class Run:

                        @staticmethod
                        def run(*args, **kwargs):

                            class Resp:

                                @staticmethod
                                def data(*args, **kwargs):
                                    return []

                            return Resp()

                        @staticmethod
                        def commit(*args, **kwargs):
                            return

                        @staticmethod
                        def rollback(*args, **kwargs):
                            return

                    return Run()

            return Transaction()


TC = TestConnection()


class TestNode(Node):
    pass


class TestLabeldtNode(Node):
    _LABELS = 'TEST_LABEL_NODE'


class TestRelationship(Relationship):
    _LABELS = 'TEST_RELATIONSHIP'


class TestLabeldtNodeMapper(EntityMapper):
    entity = TestLabeldtNode


class MapperTests(unittest.TestCase):

    def test_can_create_instance(self):
        m = TestLabeldtNodeMapper()

        self.assertIsInstance(m, EntityMapper)

    def test_can_get_mapper_single_instance_from_entity_class(self):
        mapper = Mapper(TC)
        m = get_mapper(TestLabeldtNode, mapper)
        m2 = mapper.get_mapper(TestLabeldtNode)

        self.assertIsInstance(m, EntityMapper)
        self.assertIsInstance(m, TestLabeldtNodeMapper)
        self.assertIsInstance(m2, EntityMapper)
        self.assertIsInstance(m2, TestLabeldtNodeMapper)
        self.assertEqual(id(m), id(m2))

    def test_can_get_mapper_single_instance_from_entity_instance(self):
        mapper = Mapper(TC)
        tn = TestLabeldtNode()
        m = get_mapper(tn, mapper)
        m2 = mapper.get_mapper(tn)

        self.assertIsInstance(m, EntityMapper)
        self.assertIsInstance(m, TestLabeldtNodeMapper)
        self.assertIsInstance(m2, EntityMapper)
        self.assertIsInstance(m2, TestLabeldtNodeMapper)
        self.assertEqual(id(m), id(m2))

    def test_can_load_correct_mapper_for_entity(self):
        class MyNodeTest(Node):
            pass

        class MyNodeMapperTest(EntityMapper):
            entity = MyNodeTest

        mapper = Mapper(TC)
        my_mapper = mapper.get_mapper(MyNodeTest)

        self.assertIsInstance(my_mapper, MyNodeMapperTest)

    def test_can_load_generic_mapper_for_entity_without_mapper(self):
        node = Node()
        mapper = Mapper(TC)
        my_mapper = mapper.get_mapper(node)

        self.assertEqual(my_mapper.__class__.__name__, 'EntityNodeMapper')

    def test_can_create_generic_node(self):
        mapper = Mapper(TC)
        node = mapper.create()

        self.assertIsInstance(node, Node)

    def test_can_create_custom_node(self):
        class MyNode(Node):
            pass

        mapper = Mapper(TC)
        node = mapper.create(entity=MyNode)

        self.assertIsInstance(node, MyNode)

    def test_can_create_custom_node_with_undefined_properties(self):
        class MyNodeXXX(Node):
            pass

        class MyNodeXXXMapper(EntityMapper):
            entity = MyNodeXXX
            __ALLOW_UNDEFINED__ = True
            __PROPERTIES__ = {
                'name': String(),
            }

        mapper = Mapper(TC)
        name = 'name{}'.format(random())
        p = {'name': name}
        
        node = mapper.create(entity=MyNodeXXX, properties=p)
        data = node.data

        self.assertIsInstance(node, MyNodeXXX)
        self.assertEqual(1, len(data))
        self.assertEqual(name, data['name'])

    def test_can_create_generic_relationship(self):
        mapper = Mapper(TC)
        relationship = mapper.create(entity_type='relationship')

        self.assertIsInstance(relationship, Relationship)

    def test_can_create_custom_relationship(self):
        class MyRelationship(Relationship):
            pass

        mapper = Mapper(TC)
        rel = mapper.create(entity=MyRelationship)

        self.assertIsInstance(rel, MyRelationship)

    def test_can_create_before_save_event_custom(self):
        mapper = Mapper(TC)

        class MyNode(Node):
            pass

        class MyNodeMapper(EntityMapper):
            entity = MyNode

            def on_before_create(self, entity):
                self.before_save = self.updated

        mn = mapper.create(entity=MyNode)
        my_mapper = mapper.get_mapper(mn)
        my_mapper.before_save = 'BEFOERESAVE'
        my_mapper.updated = 'UDPATED{}'.format(random())
        work = mapper.save(mn)

        queries = work.queries()
        work.send()

        self.assertEqual(my_mapper.before_save, my_mapper.updated)
        self.assertEqual(1, len(queries))
        self.assertIn('CREATE', queries[0][0])

    def test_can_create_after_save_event_custom(self):
        mapper = Mapper(TC)

        class MyNode1(Node):
            pass

        class MyNodeMapper1(EntityMapper):
            entity = MyNode1

            def on_after_create(self, entity, response, **kwargs):
                self.after_save = self.updated

        mn = mapper.create(entity=MyNode1)
        my_mapper = mapper.get_mapper(mn)
        my_mapper.after_save = 'AFTERESAVE'
        my_mapper.updated = 'UDPATED{}'.format(random())
        work = mapper.save(mn)
        queries = work.queries()
        work.send()

        self.assertEqual(my_mapper.after_save, my_mapper.updated)
        self.assertEqual(1, len(queries))
        self.assertIn('CREATE', queries[0][0])

    def test_can_create_before_and_after_save_event_custom(self):
        mapper = Mapper(TC)

        class MyNode2(Node):
            pass

        class MyNodeMapper2(EntityMapper):
            entity = MyNode2

            def on_before_create(self, entity):
                self.before_save = self.updated_before

            def on_after_create(self, entity, response, **kwargs):
                self.after_save = self.updated_after

        mn = mapper.create(entity=MyNode2)
        my_mapper = mapper.get_mapper(mn)
        my_mapper.after_save = 'AFTERESAVE'
        my_mapper.before_save = 'BEFOERESAVE'
        my_mapper.updated_before = 'UDPATED{}'.format(random())
        my_mapper.updated_after = 'UDPATED{}'.format(random())
        work = mapper.save(mn)
        query = work.queries()
        work.send()

        self.assertEqual(my_mapper.after_save, my_mapper.updated_after)
        self.assertEqual(my_mapper.before_save, my_mapper.updated_before)
        self.assertEqual(1, len(query))
        self.assertIn('CREATE', query[0][0])

    def test_can_create_before_and_after_update_events_custom(self):
        mapper = Mapper(TC)

        class MyNode3(Node):
            pass

        class MyNodeMapper3(EntityMapper):
            entity = MyNode3

            def on_before_update(self, entity):
                self.before_update = self.updated_before

            def on_after_update(self, entity, response, **kwargs):
                self.after_update = self.updated_after

        mn = mapper.create(entity=MyNode3, id=999)
        my_mapper = mapper.get_mapper(mn)
        my_mapper.after_update = 'AFTERESAVE'
        my_mapper.before_update = 'BEFOERESAVE'
        my_mapper.updated_before = 'UDPATED{}'.format(random())
        my_mapper.updated_after = 'UDPATED{}'.format(random())
        work = mapper.save(mn)
        query = work.queries()
        work.send()

        self.assertEqual(my_mapper.after_update, my_mapper.updated_after)
        self.assertEqual(my_mapper.before_update, my_mapper.updated_before)
        self.assertEqual(1, len(query))
        self.assertIn('MATCH', query[0][0])

    def test_can_create_before_and_after_delete_events_custom(self):
        mapper = Mapper(TC)

        class MyNode4(Node):
            pass

        class MyNodeMapper4(EntityMapper):
            entity = MyNode4

            def on_before_delete(self, entity):
                self.before_delete = self.deleted_before

            def on_after_delete(self, entity, response, **kwargs):
                self.after_delete = self.deleted_after

        mn = mapper.create(entity=MyNode4, id=999)
        my_mapper = mapper.get_mapper(mn)
        my_mapper.after_delete = 'AFTERDELETE'
        my_mapper.before_delete = 'BEFOEREDELETE'
        my_mapper.deleted_before = 'UDPATED{}'.format(random())
        my_mapper.deleted_after = 'UDPATED{}'.format(random())
        work = mapper.delete(mn)
        query = work.queries()
        work.send()

        self.assertEqual(my_mapper.after_delete, my_mapper.deleted_after)
        self.assertEqual(my_mapper.before_delete, my_mapper.deleted_before)
        self.assertEqual(1, len(query))
        self.assertIn('MATCH', query[0][0])

    def test_can_create_before_and_after_delete_and_save_events_custom(self):
        mapper = Mapper(TC)

        class MyNode4(Node):
            pass

        class MyNodeMapper4(EntityMapper):
            entity = MyNode4

            def on_before_delete(self, entity):
                self.before_delete = self.deleted_before

            def on_after_delete(self, entity, response, **kwargs):
                self.after_delete = self.deleted_after

            def on_before_create(self, entity):
                self.before_save = self.updated_before

            def on_after_create(self, entity, response, **kwargs):
                self.after_save = self.updated_after

        mn = mapper.create(entity=MyNode4)
        my_mapper = mapper.get_mapper(mn)
        my_mapper.after_save = 'AFTERESAVE'
        my_mapper.before_save = 'BEFOERESAVE'
        my_mapper.updated_before = 'UDPATED{}'.format(random())
        my_mapper.updated_after = 'UDPATED{}'.format(random())
        work = mapper.save(mn)

        mn = mapper.create(entity=MyNode4, id=999)
        my_mapper = mapper.get_mapper(mn)
        my_mapper.after_delete = 'AFTERDELETE'
        my_mapper.before_delete = 'BEFOEREDELETE'
        my_mapper.deleted_before = 'UDPATED{}'.format(random())
        my_mapper.deleted_after = 'UDPATED{}'.format(random())
        work = mapper.delete(mn, work=work)
        query = work.queries()
        work.send()

        self.assertEqual(my_mapper.after_save, my_mapper.updated_after)
        self.assertEqual(my_mapper.before_save, my_mapper.updated_before)
        self.assertEqual(my_mapper.after_delete, my_mapper.deleted_after)
        self.assertEqual(my_mapper.before_delete, my_mapper.deleted_before)
        self.assertEqual(2, len(query))
        self.assertIn('CREATE', query[0][0])
        self.assertIn('MATCH', query[1][0])


class MapperRelationshipEventTests(unittest.TestCase):

    def test_can_create_on_relationship_added_start_mapper_custom_event(self):
        mapper = Mapper(TC)
        entities = {
            'start': {
                'start': None,
                'relationship': None,
            }
        }
        updated = {
            'start': 'start updated {}'.format(random()),
        }
        modified = {
            'start': None,
        }

        class Start_StartCustomNode(Node):
            pass

        class Start_EndCustomNode(Node):
            pass

        class Start_RelationshipCustomNode(Relationship):
            pass

        class Start_RelationshipCustomNodeMapper(EntityRelationshipMapper):
            entity = Start_RelationshipCustomNode

        class Start_StartCustomNodeMapper(EntityMapper):
            entity = Start_StartCustomNode
            __RELATIONSHIPS__ = {
                'Other': RelatedEntity(
                    relationship_entity=Start_RelationshipCustomNode),
            }

            def on_relationship_other_added(self, entity, relationship_entity,
                                            response, relationship_end,
                                            **kwargs):
                nonlocal entities, updated, modified
                modified['start'] = updated['start']
                entities['start']['start'] = entity
                entities['start']['relationship'] = relationship_entity

        start = mapper.create(entity=Start_StartCustomNode)
        end = mapper.create(entity=Start_EndCustomNode)
        start_mapper = mapper.get_mapper(start)
        rel, work = start_mapper(start)['Other'].add(end)
        work.send()

        self.assertEqual(modified['start'], updated['start'])
        self.assertEqual(start, entities['start']['start'])
        self.assertEqual(rel, entities['start']['relationship'])

    def test_can_create_on_relationship_added_end_mapper_custom_event(self):
        mapper = Mapper(TC)
        entities = {
            'end': {
                'end': None,
                'relationship': None,
            }
        }
        updated = {
            'end': 'end updated {}'.format(random()),
        }
        modified = {
            'end': None,
        }

        class End_StartCustomNode(Node):
            pass

        class End_EndCustomNode(Node):
            pass

        class End_RelationshipCustomNode(Relationship):
            pass

        class End_RelationshipCustomNodeMapper(EntityRelationshipMapper):
            entity = End_RelationshipCustomNode

        class End_StartCustomNodeMapper(EntityMapper):
            entity = End_StartCustomNode
            __RELATIONSHIPS__ = {
                'Other': RelatedEntity(
                    relationship_entity=End_RelationshipCustomNode),
            }

        class End_EndCustomNodeMapper(EntityMapper):
            entity = End_EndCustomNode
            __RELATIONSHIPS__ = {
                'Other': RelatedEntity(
                    relationship_entity=End_RelationshipCustomNode),
            }

            def on_relationship_other_added(self, entity, relationship_entity,
                                            response, relationship_end,
                                            **kwargs):
                nonlocal entities, updated, modified
                modified['end'] = updated['end']
                entities['end']['end'] = entity
                entities['end']['relationship'] = relationship_entity

        start = mapper.create(entity=End_StartCustomNode)
        end = mapper.create(entity=End_EndCustomNode)
        start_mapper = mapper.get_mapper(start)
        rel, work = start_mapper(start)['Other'].add(end)
        work.send()

        self.assertEqual(modified['end'], updated['end'])
        self.assertEqual(end, entities['end']['end'])
        self.assertEqual(rel, entities['end']['relationship'])

    def test_can_create_on_relationship_added_relationship_mapper_custom_event(self):
        mapper = Mapper(TC)
        entities = {
            'relationship': {
                'relationship': None,
            }
        }
        updated = {
            'relationship': 'relationship updated {}'.format(random()),
        }
        modified = {
            'relationship': None,
        }

        class Relationship_StartCustomNode(Node):
            pass

        class Relationship_EndCustomNode(Node):
            pass

        class Relationship_RelationshipCustomNode(Relationship):
            pass

        class Relationship_RelationshipCustomNodeMapper(EntityRelationshipMapper):
            entity = Relationship_RelationshipCustomNode

            def on_relationship_other_added(self, entity, relationship_entity,
                                            response, relationship_end,
                                            **kwargs):
                nonlocal entities, updated, modified
                modified['relationship'] = updated['relationship']
                entities['relationship']['relationship'] = entity
                entities['relationship']['relationship'] = relationship_entity

        class Relationship_StartCustomNodeMapper(EntityMapper):
            entity = Relationship_StartCustomNode
            __RELATIONSHIPS__ = {
                'Other': RelatedEntity(
                    relationship_entity=Relationship_RelationshipCustomNode),
            }

        class Relationship_EndCustomNodeMapper(EntityMapper):
            entity = Relationship_EndCustomNode
            __RELATIONSHIPS__ = {
                'Other': RelatedEntity(
                    relationship_entity=Relationship_RelationshipCustomNode),
            }

        start = mapper.create(entity=Relationship_StartCustomNode)
        end = mapper.create(entity=Relationship_EndCustomNode)
        start_mapper = mapper.get_mapper(start)
        rel, work = start_mapper(start)['Other'].add(end)
        work.send()

        self.assertEqual(modified['relationship'], updated['relationship'])
        self.assertEqual(rel, entities['relationship']['relationship'])

    def test_can_create_on_relationship_added_all_mapper_custom_event(self):
        mapper = Mapper(TC)
        entities = {
            'start': {
                'start': None,
                'relationship': None,
            },
            'end': {
                'end': None,
                'relationship': None,
            },
            'relationship': {
                'relationship': None,
            }
        }
        updated = {
            'start': 'start updated {}'.format(random()),
            'end': 'end updated {}'.format(random()),
            'relationship': 'relationship updated {}'.format(random()),
        }
        modified = {
            'start': None,
            'end': None,
            'relationship': None,
        }

        class All_StartCustomNode(Node):
            pass

        class All_EndCustomNode(Node):
            pass

        class All_RelationshipCustomNode(Relationship):
            pass

        class All_RelationshipCustomNodeMapper(EntityRelationshipMapper):
            entity = All_RelationshipCustomNode

            def on_relationship_other_added(self, entity, relationship_entity,
                                            response, relationship_end,
                                            **kwargs):
                nonlocal entities, updated, modified
                modified['relationship'] = updated['relationship']
                entities['relationship']['relationship'] = entity
                entities['relationship']['relationship'] = relationship_entity

        class All_StartCustomNodeMapper(EntityMapper):
            entity = All_StartCustomNode
            __RELATIONSHIPS__ = {
                'Other': RelatedEntity(
                    relationship_entity=All_RelationshipCustomNode),
            }
            
            def on_relationship_other_added(self, entity, relationship_entity,
                                            response, relationship_end,
                                            **kwargs):
                nonlocal entities, updated, modified
                modified['start'] = updated['start']
                entities['start']['start'] = entity
                entities['start']['relationship'] = relationship_entity

        class All_EndCustomNodeMapper(EntityMapper):
            entity = All_EndCustomNode
            __RELATIONSHIPS__ = {
                'Other': RelatedEntity(
                    relationship_entity=All_RelationshipCustomNode),
            }

            def on_relationship_other_added(self, entity, relationship_entity,
                                            response, relationship_end,
                                            **kwargs):
                nonlocal entities, updated, modified
                modified['end'] = updated['end']
                entities['end']['end'] = entity
                entities['end']['relationship'] = relationship_entity

        start = mapper.create(entity=All_StartCustomNode)
        end = mapper.create(entity=All_EndCustomNode)
        start_mapper = mapper.get_mapper(start)
        rel, work = start_mapper(start)['Other'].add(end)
        work.send()

        self.assertEqual(modified['start'], updated['start'])
        self.assertEqual(start, entities['start']['start'])
        self.assertEqual(rel, entities['start']['relationship'])
        self.assertEqual(modified['end'], updated['end'])
        self.assertEqual(end, entities['end']['end'])
        self.assertEqual(rel, entities['end']['relationship'])
        self.assertEqual(modified['relationship'], updated['relationship'])
        self.assertEqual(rel, entities['relationship']['relationship'])



class MapperCreateTests(unittest.TestCase):

    def setUp(self):
        self.mapper = Mapper(TC)

        return self

    def tearDown(self):
        self.mapper.reset()

    def test_mapper_can_create_single_node(self):
        name = 'mark {}'.format(random())
        p = {'name': name}
        n = Node(properties=p)
        work = self.mapper.save(n)
        queries = work.queries()
        query, params = queries[0]

        # generic Node and Relationship entites do not allow for setting of
        # undefined properties
        self.assertEqual(0, len(params))
        self.assertEqual(1, len(queries))
        self.assertTrue(query.startswith('CREATE'))

    def test_mapper_can_create_multiple_nodes(self):
        name = 'mark {}'.format(random())
        p = {'name': name}
        n = Node(properties=p)
        n2 = Node(properties=p)
        n3 = Node(properties=p)

        work = self.mapper.save(n)
        self.mapper.save(n2, work=work)
        self.mapper.save(n3, work=work)

        queries = work.queries()

        self.assertEqual(3, len(queries))

        for query in queries:
            self.assertTrue(query[0].startswith('CREATE'))

    def test_can_create_single_relationship(self):
        p = {'name': 'somename'}
        start = Node(properties=p)
        end = Node(properties=p)
        rel = Relationship(start=start, end=end)
        work = self.mapper.save(rel)
        queries = work.queries()

        self.assertEqual(1, len(queries))
        self.assertTrue(queries[0][0].startswith('CREATE'))
        self.assertTrue('RETURN' in queries[0][0])


class MapperUpdateTests(unittest.TestCase):

    def setUp(self):
        self.mapper = Mapper(TC)

    def test_can_udpate_single_node(self):
        class SingleUpdate(Node):
            pass

        class SingleUpdateMapper(EntityMapper):
            entity = SingleUpdate
            __PROPERTIES__ = {
                'name': String(),
            }

        id = 999
        name = 'some name'
        n = SingleUpdate(id=id)
        n['name'] = name
        work = self.mapper.save(n)
        query = work.queries()
        params = query[0][1]

        self.assertEqual(1, len(query))
        self.assertEqual(2, len(params))
        self.assertIn('SET', query[0][0])
        self.assertIn(name, params.values())
        self.assertIn(id, params.values())

    def test_can_update_multiple_nodes(self):
        class SingleUpdate(Node):
            pass

        class SingleUpdateMapper(EntityMapper):
            entity = SingleUpdate
            __PROPERTIES__ = {
                'name': String(),
            }

        id = 999
        name = 'some name'
        n = SingleUpdate(id=id)
        n['name'] = name

        id2 = 9992
        name2 = 'some name222'
        n2 = SingleUpdate(id=id2)
        n2['name'] = name2
        work = self.mapper.save(n)
        self.mapper.save(n2, work=work)
        query = work.queries()

        self.assertEqual(2, len(query))
        self.assertIn('SET', query[0][0])
        self.assertIn('SET', query[1][0])
        self.assertIn(name, query[0][1].values())
        self.assertIn(id, query[0][1].values())
        self.assertIn(name2, query[1][1].values())
        self.assertIn(id2, query[1][1].values())

    def test_can_update_single_relationship(self):

        class SingleUpdate(Node):
            pass

        class SingleUpdateMapper(EntityMapper):
            entity = SingleUpdate
            __PROPERTIES__ = {
                'name': String(),
            }

        class SingleRelationship(Relationship):
            pass

        class SingleRelationshipMapper(EntityMapper):
            entity = SingleRelationship

        id = 999
        name = 'some name'
        n = SingleUpdate(id=id)
        n['name'] = name

        id2 = 9992
        name2 = 'some name222'
        n2 = SingleUpdate(id=id2)
        n2['name'] = name2
        rid = 9988
        rel = SingleRelationship(start=n, end=n2, id=rid)
        work = self.mapper.save(rel)
        query = work.queries()

        self.assertEqual(1, len(query))
        self.assertIn('SET', query[0][0])
        self.assertIn(name, query[0][1].values())
        self.assertIn(id, query[0][1].values())
        self.assertIn(name2, query[0][1].values())
        self.assertIn(id2, query[0][1].values())
        self.assertIn(rid, query[0][1].values())

    def test_can_update_multiple_relationships(self):
    
        class SingleUpdate(Node):
            pass

        class SingleUpdateMapper(EntityMapper):
            entity = SingleUpdate
            __PROPERTIES__ = {
                'name': String(),
            }

        class SingleRelationship(Relationship):
            pass

        class SingleRelationshipMapper(EntityMapper):
            entity = SingleRelationship

        id = 999
        name = 'some name'
        n = SingleUpdate(id=id)
        n['name'] = name

        id2 = 9992
        name2 = 'some name222'
        n2 = SingleUpdate(id=id2)
        n2['name'] = name2
        rid = 9988
        rel = SingleRelationship(start=n, end=n2, id=rid)

        id3 = 997
        name3 = 'some name ed'
        n3 = SingleUpdate(id=id3)
        n3['name'] = name3

        id4 = 99929
        name4 = 'some name222 3'
        n4 = SingleUpdate(id=id4)
        n4['name'] = name4
        rid2 = 99887
        rel2 = SingleRelationship(start=n3, end=n4, id=rid2)

        work = self.mapper.save(rel)
        self.mapper.save(rel2, work=work)
        query = work.queries()

        self.assertEqual(2, len(query))
        self.assertIn('SET', query[0][0])
        self.assertIn(name, query[0][1].values())
        self.assertIn(id, query[0][1].values())
        self.assertIn(name2, query[0][1].values())
        self.assertIn(id3, query[1][1].values())
        self.assertIn(rid, query[0][1].values())
        self.assertIn(id4, query[1][1].values())
        self.assertIn(name3, query[1][1].values())
        self.assertIn(name4, query[1][1].values())

    def test_can_see_single_property_changes(self):
        mapper = Mapper(TC)
        before_value = 'before'
        after_value = 'after {}'.format(random())
        properties = {'name': before_value}
        changed_props = {}

        class MyNodex(Node):
            __PROPERTIES__ = {
                'name': String()
            }


        class MyNodeMapperx(EntityMapper):
            entity = MyNodex

            def on_name_property_changed(self, entity, field, value_from, value_to):
                changed_props[field] = value_to

        n = MyNodex(id=999, properties=properties)
        n['name'] = after_value

        self.mapper.save(n).send()

        self.assertEqual(1, len(changed_props))
        self.assertIn('name', changed_props)
        self.assertEqual(changed_props['name'], n['name'])

    def test_can_see_single_property_with_weird_name_changes(self):
        mapper = Mapper(TC)
        before_value = 'before'
        after_value = 'after {}'.format(random())
        prop_name = 'some--weird!!   name'
        properties = {prop_name: before_value}
        changed_props = {}

        class MyNodexy(Node):
            __PROPERTIES__ = {
                prop_name: String()
            }


        class MyNodeMapperxy(EntityMapper):
            entity = MyNodexy

            def __init__(self, mapper):
                super(MyNodeMapperxy, self).__init__(mapper)
                self._property_change_handlers[prop_name] = self.on_weird_property_changed

            def on_weird_property_changed(self, entity, field, value_from, value_to):
                changed_props[field] = value_to

        n = MyNodexy(id=999, properties=properties)
        n[prop_name] = after_value

        self.mapper.save(n).send()

        self.assertEqual(1, len(changed_props))
        self.assertIn(prop_name, changed_props)
        self.assertEqual(changed_props[prop_name], n[prop_name])

    def test_can_see_multiple_properties_changes(self):
        mapper = Mapper(TC)
        before_value = 'before'
        after_value = 'after {}'.format(random())
        after_age_value = 'age {}'.format(random())
        properties = {'name': before_value, 'age': 1}
        changed_props = {}

        class MyNodexx(Node):
            __PROPERTIES__ = {
                'name': String(),
                'age': Integer()
            }


        class MyNodeMapperxx(EntityMapper):
            entity = MyNodexx

            def on_name_property_changed(self, entity, field, value_from, value_to):
                changed_props[field] = value_to

            def on_age_property_changed(self, entity, field, value_from, value_to):
                changed_props[field] = value_to

        n = MyNodexx(id=999, properties=properties)
        n['name'] = after_value
        n['age'] = after_age_value

        self.mapper.save(n).send()

        self.assertEqual(2, len(changed_props))
        self.assertIn('name', changed_props)
        self.assertIn('age', changed_props)
        self.assertEqual(changed_props['name'], n['name'])
        self.assertEqual(changed_props['age'], n['age'])


class MapperDeleteTests(unittest.TestCase):

    def setUp(self):
        self.mapper = Mapper(TC)

    def test_can_delete_single_node(self):
        _id = 999
        n = Node(id=_id)
        work = self.mapper.delete(n)
        query = work.queries()

        self.assertEqual(1, len(query))
        self.assertEqual(1, len(query[0][1]))
        self.assertTrue('DETACH DELETE' in query[0][0])

    def test_can_delete_multiple_nodes(self):
        _id = 999
        n = Node(id=_id)
        _id2 = 9998
        n2 = Node(id=_id2)
        work = self.mapper.delete(n)
        self.mapper.delete(n2, work=work)
        query = work.queries()

        self.assertEqual(2, len(query))
        self.assertEqual(1, len(query[0][1]))
        self.assertEqual(1, len(query[1][1]))

        for q in query:
            self.assertTrue('DETACH DELETE' in q[0])

    def test_can_delete_single_relationship(self):
        _id = 999
        n = Node(id=_id)
        _id2 = 999
        n2 = Node(id=_id2)
        _id3 = 8989
        rel = Relationship(start=n, end=n2, id=_id3)
        work = self.mapper.delete(rel)
        query = work.queries()

        self.assertEqual(1, len(query))
        self.assertEqual(1, len(query[0][1]))
        self.assertTrue('DELETE' in query[0][0])

    def test_can_delete_multiple_relationships(self):
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
        work = self.mapper.delete(rel)
        work.delete(rel2)
        query = work.queries()

        self.assertEqual(2, len(query))
        self.assertEqual(1, len(query[0][1]))
        self.assertEqual(1, len(query[1][1]))

        for q in query:
            self.assertTrue('DELETE' in q[0])

# TODO move to integration testing
# class MapperBuilderTests(unittest.TestCase):
#
#     def setUp(self):
#         self.mapper = Mapper(TC)
#
#     def test_can_get_by_id(self):
#         import pudb; pu.db
#         id_val = randint(1, 9999)
#         query, params = self.mapper.get_by_id(id_val=id_val)
#         import pudb; pu.db


if __name__ == '__main__':
    unittest.main()
