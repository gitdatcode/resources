import unittest
import json
import time

from datetime import datetime
from random import randrange, random, choice, randint
from pprint import pprint

from moesha.property import *


class PropertyTests(unittest.TestCase):

    def test_can_create_field_without_value(self):
        f = Property()

        self.assertEqual(type(f), Property)

    def test_can_create_field_without_value_with_default_value(self):
        d = str(random())
        f = Property(default=d)

        self.assertEqual(type(f), Property)
        self.assertEqual(d, f.value)

    def test_can_create_field_with_value(self):
        v = str(random())
        f = Property(value=v)

        self.assertEqual(type(f), Property)
        self.assertEqual(v, f.value)

    def test_can_create_field_with_one_callable_value(self):
        v = str(random())
        def value():
            return v

        f = Property(value=value)

        self.assertEqual(type(f), Property)
        self.assertEqual(v, f.value)

    def test_can_create_field_without_value_with_default_callable_value(self):
        d = str(random())
        def value():
            return d
        
        f = Property(default=d)

        self.assertEqual(type(f), Property)
        self.assertEqual(d, f.value)

    def test_can_limit_property_value_change(self):
        mv = 6
        r = 15
        f = Property(immutable=True, value=mv)

        for i in range(r):
            f.value = i

        self.assertEqual(mv, f.value)

    def test_can_set_immutability_and_change_it(self):
        mv = 6
        r = 15
        f = Property(immutable=True, value=mv)
        f.immutable = False

        for i in range(r):
            f.value = i

        self.assertEqual(i, f.value)


class StringTests(unittest.TestCase):

    def test_can_create_string_without_value_and_python_type_ret_empty_string(self):
        f = String()

        self.assertEqual('', f.value)

    def test_can_create_string_with_numeric_value_ret_string_for_graph(self):
        v = random()
        f = String(value=v, data_type='graph')

        self.assertIsInstance(f.value, str)

    def test_can_create_string_with_numeric_value_ret_str_value(self):
        v = random()
        f = String(value=v)

        self.assertIsInstance(f.value, str)

    def test_will_ensure_that_none_values_return_empty_string_when_converted_to_python(self):
        f = String(value=None)
        f.data_type = 'python'

        self.assertEqual(f.value, '')

    def test_will_ensure_that_none_values_return_empty_string_when_converted_to_graph(self):
        f = String(value=None)
        f.data_type = 'graph'

        self.assertEqual(f.value, '')


class IntegerTests(unittest.TestCase):

    def test_can_create_type_with_non_numeric_value_and_get_integer_python(self):

        class X:
            pass

        v = ['43.34.', X(), 'iii', '987eee']
        f = Integer(value=choice(v))

        self.assertIsInstance(f.value, int)
        self.assertEqual(f.value, 0)

    def test_can_create_type_with_non_numeric_value_and_get_integer_graph(self):

        class X:
            pass

        v = ['43.34.', X(), 'iii', '987eee']
        f = Integer(value=choice(v), data_type='graph')

        self.assertIsInstance(f.value, int)
        self.assertEqual(f.value, 0)

    def test_will_ensure_that_none_values_return_zero_when_converted_to_python(self):
        f = Integer(value=None)
        f.data_type = 'python'

        self.assertEqual(f.value, 0)

    def test_will_ensure_that_none_values_return_zero_when_converted_to_graph(self):
        f = Integer(value=None)
        f.data_type = 'graph'

        self.assertEqual(f.value, 0)


class FloatTests(unittest.TestCase):

    def test_can_get_float_with_non_numeric_value_graph_data_type(self):
        v = 'dsafsd$@#4..'
        f = Float(value=v)
        f.data_type = 'graph'

        self.assertIsInstance(f.value, float)
        self.assertEqual(f.value, 0.0)

    def test_can_convert_integer_to_float(self):
        v = 12
        f = Float(value=v)

        self.assertIsInstance(f.value, float)
        self.assertEqual(f.value, 12.0)

    def test_can_convert_integer_to_float_graph_data_type(self):
        v = 12
        f = Float(value=v)
        f.data_type = 'graph'

        self.assertIsInstance(f.value, float)
        self.assertEqual(f.value, 12.0)

    def test_will_ensure_that_none_values_return_zero_when_converted_to_python(self):
        f = Float(value=None)
        f.data_type = 'python'

        self.assertEqual(f.value, 0.0)

    def test_will_ensure_that_none_values_return_zero_when_converted_to_graph(self):
        f = Float(value=None)
        f.data_type = 'graph'

        self.assertEqual(f.value, 0.0)


class DateTimeTests(unittest.TestCase):

    def test_can_create_empty_datetime_field(self):
        f = DateTime()

        self.assertEqual(0.0, f.value)

    def test_can_create_datetime_with_datetime_instance(self):
        d = datetime.today()
        f = DateTime(value=d)

        self.assertIsInstance(f.value, float)
        self.assertEqual(f.value, d.timestamp())

    def test_can_create_datetime_with_number(self):
        v = random()
        f = DateTime(value=v)

        self.assertIsInstance(f.value, float)
        self.assertEqual(f.value, v)

    def test_will_ensure_that_none_values_return_zero_when_converted_to_python(self):
        f = DateTime(value=None)
        f.data_type = 'python'

        self.assertEqual(f.value, 0.0)

    def test_will_ensure_that_none_values_return_zero_when_converted_to_graph(self):
        f = DateTime(value=None)
        f.data_type = 'graph'

        self.assertEqual(f.value, 0.0)


class TimeStampTests(unittest.TestCase):

    def test_can_create_timestamp(self):
        d = datetime.now()
        f = TimeStamp()

        time.sleep(0.5)

        self.assertIsInstance(f.value, float)
        self.assertNotEqual(d.timestamp(), f.value)
        self.assertTrue(f.value > d.timestamp())

    def test_can_create_timestamp_with_value(self):
        t = random()
        f = TimeStamp(value=t)

        self.assertEqual(t, f.value)


class IncrementTests(unittest.TestCase):

    def test_can_create_increment_without_default_value(self):
        f = Increment()

        self.assertEqual(0, f.value)

    def test_can_set_default_value(self):
        d = 9
        f = Increment(value=d)
        v = f.value

        self.assertEqual(v, d)

    def test_will_only_increment_when_data_type_is_graph(self):
        f = Increment()
        f.data_type = 'graph'
        v = f.value

        self.assertEqual(v, 1)

    def test_will_increment_when_data_type_is_graph_with_default_value(self):
        d = 9
        f = Increment(value=d)
        f.data_type = 'graph'
        v = f.value

        self.assertEqual(v, d + 1)

    def test_will_increment_multiple_times(self):
        d = v = 9
        l = choice(range(4, 15))
        f = Increment(value=d)
        f.data_type = 'graph'

        for _ in range(l):
            v = f.value

        self.assertEqual(v, d + l)


class BooleanTests(unittest.TestCase):

    def test_can_create_boolean_without_value_and_get_false(self):
        f = Boolean()

        self.assertIsInstance(f.value, bool)
        self.assertFalse(f.value)

    def test_can_create_boolean_without_value_and_get_false_for_graph(self):
        f = Boolean(data_type='graph')

        self.assertIsInstance(f.value, bool)
        self.assertFalse(f.value)

    def test_can_get_boolean_from_non_bool_val(self):
        f = Boolean(value='ooo')

        self.assertIsInstance(f.value, bool)
        self.assertTrue(f.value)

    def test_can_get_boolean_from_none_graph_data_type(self):
        f = Boolean()
        f.data_type = 'graph'

        self.assertFalse(f.value)

    def test_can_get_boolean_value_from_boolean_strings(self):
        f = Boolean(value='true')

        self.assertIsInstance(f.value, bool)
        self.assertTrue(f.value)

        f = Boolean(value='false')

        self.assertIsInstance(f.value, bool)
        self.assertFalse(f.value)

    def test_can_get_graph_boolean_from_non_bool_val(self):
        f = Boolean(value='ooo')
        f.data_type = 'graph'

        self.assertTrue(f.value)

    def test_will_ensure_that_none_values_return_false_when_converted_to_python(self):
        f = Boolean()
        f.data_type = 'python'

        self.assertFalse(f.value)

    def test_will_ensure_that_none_values_return_false_when_converted_to_graph(self):
        f = Boolean()
        f.data_type = 'graph'

        self.assertFalse(f.value)


class JsonPropertyTests(unittest.TestCase):
    
    def test_can_create_json_without_value_and_get_dict(self):
        f = JsonProperty()

        self.assertIsInstance(f.value, dict)

    def test_can_create_json_without_value_and_get_empty_string_for_graph(self):
        f = JsonProperty(data_type='graph')

        self.assertIsInstance(f.value, str)
        self.assertEquals(f.value, '""')

    def test_can_get_json_from_simple_dict(self):
        d = {'name': 'mark'}
        f = JsonProperty(data_type='graph', value=d)

        self.assertEquals(f.value, json.dumps(d))

    def test_can_convert_json_to_dict(self):
        d = {'name': 'mark'}
        jd = json.dumps(d)
        f = JsonProperty(value=jd)

        self.assertIsInstance(f.value, dict)

        for k,v in d.items():
            self.assertEqual(f.value[k], v)

    def test_can_convert_json_to_list(self):
        l = ['mark', 'was', 'here']
        jl = json.dumps(l)
        f = JsonProperty(value=jl)

        self.assertIsInstance(f.value, list)

        for i, v in enumerate(l):
            self.assertEqual(f.value[i], v)

    def test_will_not_double_encode_json_string(self):
        d = {'name': 'mark'}
        jd = json.dumps(d)
        f = JsonProperty(value=jd, data_type='graph')

        self.assertEquals(f.value, jd)


class PropertyManagerTests(unittest.TestCase):

    def test_can_create_a_field_manager_without_fields(self):
        f = PropertyManager()
        data = f.data()

        self.assertIsInstance(f, PropertyManager)
        self.assertEqual(0, len(data))

    def test_can_create_a_field_manager_with_one_field(self):
        string = String()
        fields = {'string': string}
        f = PropertyManager(fields)
        data = f.data()

        self.assertIsInstance(f, PropertyManager)
        self.assertEqual(1, len(f.properties))
        self.assertEqual(1, len(data))

    def test_can_create_a_field_manager_with_one_field_and_add_value(self):
        string = String()
        fields = {'string': string}
        f = PropertyManager(fields)
        v = str(random())
        f['string'] = v
        data = f.data()

        self.assertIsInstance(f, PropertyManager)
        self.assertEqual(1, len(f.properties))
        self.assertEqual(1, len(data))
        self.assertEqual('', f['string'])
        self.assertEqual(v, data['string'])

    def test_can_create_manager_with_no_fields_and_dynamically_add_string(self):
        f = PropertyManager(allow_undefined=True)
        key = 'str_key' + str(random())
        val = 'str_val' + str(random())
        f[key] = val

        self.assertEqual(1, len(f.properties))
        self.assertIn(key, f.properties)
        self.assertEqual(val, f[key])
        self.assertIsInstance(f.properties[key], String)

    def test_can_create_manager_with_no_fields_and_dynamically_add_integer(self):
        f = PropertyManager(allow_undefined=True)
        key = 'int_key' + str(random())
        val = randint(1, 1000)
        f[key] = val

        self.assertEqual(1, len(f.properties))
        self.assertIn(key, f.properties)
        self.assertEqual(val, f[key])
        self.assertIsInstance(f.properties[key], Integer)

    def test_can_create_manager_with_no_fields_and_dynamically_add_float(self):
        f = PropertyManager(allow_undefined=True)
        key = 'float_key' + str(random())
        val = random()
        f[key] = val

        self.assertEqual(1, len(f.properties))
        self.assertIn(key, f.properties)
        self.assertEqual(val, f[key])
        self.assertIsInstance(f.properties[key], Float)

    def test_can_create_manager_with_no_fields_and_dynamically_add_boolean(self):
        f = PropertyManager(allow_undefined=True)
        key = 'bool_key' + str(random())
        val = choice([True, False])
        f[key] = val

        self.assertEqual(1, len(f.properties))
        self.assertIn(key, f.properties)
        self.assertEqual(val, f.properties[key].value)
        self.assertIsInstance(f.properties[key], Boolean)

    def test_can_get_all_values_from_manager(self):
        f = PropertyManager(allow_undefined=True)
        k = 'key' + str(random())
        k2 = 'key2' + str(random())
        v = random()
        v2 = random()
        f[k] = v
        f[k2] = v2
        values = f.data()

        self.assertEqual(2, len(values))
        self.assertIn(k, values)
        self.assertIn(k2, values)
        self.assertEqual(v, f[k])
        self.assertEqual(v2, f[k2])


if __name__ == '__main__':
    unittest.main()
