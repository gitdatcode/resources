import unittest
import json
import time

from random import random

from moesha.entity import (Node, Relationship)
from moesha.property import (String, Integer, TimeStamp)


class TestNode(Node):
    pass


class TesLabeldtNode(Node):
    __LABELS__ = 'TEST_LABEL_NODE'


class Test_Unlabeled_Node(Node):
    pass


class EntityTests(unittest.TestCase):

    def test_can_create_entity(self):
        n = TestNode()

        self.assertIsInstance(n, Node)

    def test_can_create_entity_and_remove_properties(self):
        class X(Node):
            pass

        id = 999
        age = 888
        p = {'eye_id': id, 'age': age}
        x = X(properties=p)
        id2 = 999
        age2 = 888
        p2 = {'eye_id': id2, 'age': age2}
        y = X(properties=p2)

        self.assertEqual(x['eye_id'], id)
        self.assertEqual(x['age'], age)

        self.assertEqual(y['eye_id'], id2)
        self.assertEqual(y['age'], age2)

    # TODO: move these tests to the mapper
    # def test_can_get_static_label_from_entity_withou_labels(self):
    #     class StaticNode(Node):
    #         pass
    #
    #     exp = 'StaticNode'
    #     labels = StaticNode.labels
    #
    #     self.assertEqual(1, len(labels))
    #     self.assertEqual(exp, labels[0])
    #
    # def test_can_get_static_underscored_label_from_entity_withou_labels(self):
    #     class StaticNode_Underscore(Node):
    #         pass
    #
    #     exp = ['StaticNode', 'Underscore']
    #     labels = StaticNode_Underscore.labels
    #
    #     self.assertEqual(2, len(labels))
    #
    #     for e in exp:
    #         self.assertIn(e, labels)
    #
    # def test_can_get_static_label_from_entity_with_labels(self):
    #     l = ['One', 'TWO', 'ABC']
    #
    #     class StaticNode(Node):
    #         __LABELS__ = l
    #
    #     exp = 'StaticNode'
    #     labels = StaticNode.labels
    #
    #     self.assertEqual(len(l), len(labels))
    #
    #     for e in l:
    #         self.assertIn(e, labels)
    #
    # def test_can_create_entities_with_labels(self):
    #     t = TestNode()
    #     tl = TesLabeldtNode()
    #     tu = Test_Unlabeled_Node()
    #     t_ls = ['TestNode']
    #     tl_ls = ['TEST_LABEL_NODE']
    #     tu_ls = ['Test', 'Unlabeled', 'Node']
    #
    #     def test_labels(labels, node):
    #         self.assertEqual(len(labels), len(node.label))
    #
    #         for l in labels:
    #             self.assertIn(l, node.label)
    #
    #     test_labels(t_ls, t)
    #     test_labels(tl_ls, tl)
    #     test_labels(tu_ls, tu)
    #
    # def test_can_inherit_properties_label_and_undefined(self):
    #     _label = 'SOME LABEL'
    #
    #     class One(Node):
    #         __ALLOW_UNDEFINED__ = True
    #         __PROPERTIES__ = {
    #             'name': String()
    #         }
    #
    #     class Two(One):
    #         __LABELS__ = [_label]
    #         __PROPERTIES__ = {
    #             'age': Integer()
    #         }
    #
    #     class TwoTwo(One):
    #         __PROPERTIES__ = {
    #             'location': String()
    #         }
    #
    #     class Three(Two, TwoTwo):
    #         __ALLOW_UNDEFINED__ = False
    #         __PROPERTIES__ = {
    #             'sex': String()
    #         }
    #
    #     t = Three()
    #     exp = ['name', 'age', 'sex', 'location']
    #
    #     for e in exp:
    #         self.assertIn(e, t.data)
    #
    #     self.assertIn(_label, t.label)
    #     self.assertFalse(t.properties.allow_undefined)
    #
    # def test_can_create_entity_with_data(self):
    #     _label = 'SOME LABEL'
    #
    #     class One(Node):
    #         __ALLOW_UNDEFINED__ = True
    #         __PROPERTIES__ = {
    #             'name': String()
    #         }
    #
    #     class Two(One):
    #         __LABELS__ = [_label]
    #         __PROPERTIES__ = {
    #             'age': Integer()
    #         }
    #
    #     class TwoTwo(One):
    #         __PROPERTIES__ = {
    #             'location': String()
    #         }
    #
    #     class Three(Two, TwoTwo):
    #         __ALLOW_UNDEFINED__ = False
    #         __PROPERTIES__ = {
    #             'sex': String()
    #         }
    #
    #     props = {'name': 'mark', 'age': 999, 'location': 'earth'}
    #     t = Three(properties=props)
    #
    #     self.assertEqual(props['name'], t['name'])
    #     self.assertEqual(props['age'], t['age'])
    #     self.assertEqual(props['location'], t['location'])
    #     self.assertEqual('', t['sex'])
    #
    # def test_can_add_undefined_property_to_entity(self):
    #
    #     class T(Node):
    #         pass
    #
    #     name = str(random())
    #     t = T()
    #     t['name'] = name
    #
    #     self.assertEqual(name, t['name'])
    #     self.assertEqual(1, len(t.data))
    #
    # def test_cannot_add_undefined_property_to_entity(self):
    #
    #     class T(Node):
    #         pass
    #
    #     name = str(random())
    #     t = T()
    #     t['name'] = name
    #
    #     self.assertEqual(None, t['name'])
    #     self.assertEqual(0, len(t.data))
    #
    # def test_can_change_datatype_for_entity(self):
    #     t = TestNode()
    #     t.data_type = 'graph'
    #
    #     self.assertEqual('graph', t.data_type)
    #
    # def test_can_delete_dynamically_added_field(self):
    #     t = TestNode()
    #     f = 'name'
    #     t[f] = 'some name'
    #
    #     del(t[f])
    #
    #     self.assertNotIn(f, t.data)
    #     self.assertEqual(0, len(t.data))
    #
    # def test_can_delete_defined_field(self):
    #     class X(Node):
    #         __PROPERTIES__ = {
    #             'name': String()
    #         }
    #
    #     t = X()
    #     f = 'name'
    #     t[f] = 'some name'
    #
    #     del(t[f])
    #
    #     self.assertNotIn(f, t.data)
    #     self.assertEqual(0, len(t.data))

    def test_can_hydrate_with_new_data(self):
        p = {'name': 'mark'}
        t = TestNode(properties=p)
        np = {'name': 'mark2', 'age': 999}
        t.hydrate(properties=np)

        self.assertEqual(2, len(t.data))

        for n, v in np.items():
            self.assertIn(n, t.data)
            self.assertEqual(v, t[n])

    def test_can_force_hyrdate_registering_no_changes(self):
        class X(Node):
            pass

        t = X()
        p = {'time': 99999}
        t.hydrate(properties=p, reset=True)

        self.assertEqual(1, len(t.data))
        self.assertEqual(p['time'], t['time'])
        self.assertEqual(0, len(t.changes))

    def test_can_get_changed_properties(self):
        p = {
            'name': 'some name',
            'location': 'some location'
        }
        n = Node(properties=p)
        n['name'] = 'some new name'
        changed = n.changes

        self.assertEqual(1, len(changed))
        self.assertIn('name', changed)

    def test_can_get_no_changed_properties(self):
        p = {
            'name': 'some name',
            'location': 'some location'
        }
        n = Node(properties=p)
        n['name'] = 'some new name'
        n['name'] = p['name']
        changed = n.changes

        self.assertEqual(0, len(changed))

    def test_can_hydrate_and_register_changed_properties(self):
        p = {
            'name': 'some name',
            'location': 'some location'
        }
        n = Node(properties=p)
        new_p = {'name': 'new name'}
        n.hydrate(properties=new_p)

        self.assertEqual(1, len(n.changes))
        self.assertEqual(new_p['name'], n['name'])


if __name__ == '__main__':
    unittest.main()
