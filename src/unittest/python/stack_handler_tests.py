__author__ = 'mhoyer'

import unittest2
from cfn_sphere.stack_handler import StackHandler


class StackHandlerTests(unittest2.TestCase):
    def test_convert_list_to_string_returns_string(self):
        self.assertEqual("a,b,c", StackHandler.convert_list_to_string(["a", "b", "c"]))

    def test_convert_list_to_string_returns_empty_string_on_empty_list(self):
        self.assertEqual("", StackHandler.convert_list_to_string([]))

    def test_convert_list_to_string_returns_empty_string_on_none_value(self):
        self.assertEqual("", StackHandler.convert_list_to_string(None))

    def test_convert_list_to_string_returns_single_item(self):
        self.assertEqual("a", StackHandler.convert_list_to_string(["a"]))

    def test_convert_list_to_string_returns_two_items(self):
        self.assertEqual("a,b", StackHandler.convert_list_to_string(["a", "b"]))

    def test_get_parameter_key_from_ref_value_returns_valid_key(self):
        self.assertEqual("vpc.id", StackHandler.get_parameter_key_from_ref_value("Ref::vpc.id"))

    def test_get_parameter_key_from_ref_value_returns_key_on_lowercase_ref(self):
        self.assertEqual("vpc.id", StackHandler.get_parameter_key_from_ref_value("ref::vpc.id"))

    def test_get_parameter_key_from_ref_value_returns_empty_string_on_single_separator(self):
        self.assertEqual("", StackHandler.get_parameter_key_from_ref_value("Ref:vpc.id"))

    def test_get_parameter_key_from_ref_value_returns_empty_string_on_invalid_ref_value(self):
        self.assertEqual("", StackHandler.get_parameter_key_from_ref_value("Ref:vpc.id"))

    def test_get_parameter_key_from_ref_value_returns_empty_string_if_none(self):
        self.assertEqual("", StackHandler.get_parameter_key_from_ref_value(None))

    def test_is_ref_value_returns_true_for_uppercase_ref(self):
        self.assertTrue(StackHandler.is_parameter_reference("Ref::vpc.id"))

    def test_is_ref_value_returns_true_for_all_uppercase_ref(self):
        self.assertTrue(StackHandler.is_parameter_reference("REF::vpc.id"))

    def test_is_ref_value_returns_true_for_lowercase_ref(self):
        self.assertTrue(StackHandler.is_parameter_reference("ref::vpc.id"))

    def test_is_ref_value_returns_false_for_single_separator(self):
        self.assertFalse(StackHandler.is_parameter_reference("Ref:vpc.id"))

    def test_is_ref_value_returns_false_for_simple_string(self):
        self.assertFalse(StackHandler.is_parameter_reference("vpc.id"))

    def test_is_ref_value_returns_false_for_simple_string_with_separator(self):
        self.assertFalse(StackHandler.is_parameter_reference("test::vpc.id"))

    def test_is_ref_value_returns_true_for_empty_ref_value(self):
        self.assertTrue(StackHandler.is_parameter_reference("Ref::"))

    def test_is_ref_value_returns_false_for_boolean_values(self):
        self.assertFalse(StackHandler.is_parameter_reference(True))

    def test_get_stack_order_returns_a_valid_order(self):
        stacks = {'default-sg': {'parameters': {'a': 'Ref::vpc.id'}},
                  'app1': {'parameters': {'a': 'Ref::vpc.id', 'b': 'Ref::default-sg.id'}},
                  'app2': {'parameters': {'a': 'Ref::vpc.id', 'b': 'Ref::default-sg.id', 'c': 'Ref::app1.id'}},
                  'vpc': {'parameters': {'logBucketName': 'is24-cloudtrail-logs', 'includeGlobalServices': False}},
        }

        result = ['vpc', 'default-sg', 'app1', 'app2']

        self.assertEqual(result, StackHandler.get_stack_order(stacks))

    def test_get_stack_order_includes_independent_stacks(self):
        stacks = {'default-sg': {'parameters': {}},
                  'app1': {'parameters': {'a': 'Ref::vpc.id'}},
                  'app2': {'parameters': {'a': 'Ref::vpc.id', 'c': 'Ref::app1.id'}},
                  'vpc': {'parameters': {'logBucketName': 'is24-cloudtrail-logs', 'includeGlobalServices': False}},
        }

        result = 4

        self.assertEqual(result, len(StackHandler.get_stack_order(stacks)))

    def test_get_stack_order_accepts_stacks_without_parameters_key(self):
        stacks = {'default-sg': {},
                  'app1': None,
                  'app2': {},
                  'vpc': {},
        }

        result = 4

        self.assertEqual(result, len(StackHandler.get_stack_order(stacks)))

    def test_get_stack_order_raises_exception_on_cyclic_dependency(self):
        stacks = {'app1': {'parameters': {'a': 'Ref::app2.id'}},
                  'app2': {'parameters': {'a': 'Ref::app1.id'}}
        }
        with self.assertRaises(Exception):
            StackHandler.get_stack_order(stacks)

    def test_get_stack_name_from_ref_value_returns_stack_name(self):
        self.assertEqual("a", StackHandler.get_stack_name_from_ref_value("a.b"))

    def test_get_stack_name_from_ref_value_raises_exception_if_dot_is_missing(self):
        with self.assertRaises(AssertionError):
            self.assertEqual("a", StackHandler.get_stack_name_from_ref_value("ab"))

    def test_get_stack_name_from_ref_value_raises_exception_if_value_starts_with_dot(self):
        with self.assertRaises(AssertionError):
            self.assertEqual("a", StackHandler.get_stack_name_from_ref_value(".ab"))

    def test_get_stack_name_from_ref_value_raises_exception_for_empty_value(self):
        with self.assertRaises(AssertionError):
            self.assertEqual("", StackHandler.get_stack_name_from_ref_value(""))

    def test_get_stack_name_from_ref_value_raises_exception_for_none_value(self):
        with self.assertRaises(AssertionError):
            self.assertEqual("", StackHandler.get_stack_name_from_ref_value(None))