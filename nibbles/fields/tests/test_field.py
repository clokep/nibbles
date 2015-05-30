from __future__ import absolute_import

from unittest import TestCase

from ..base import Field


class CompoundField(Field):
    a = Field()
    b = Field()


class RaisingField(Field):
    class GetException(Exception):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    def __get__(self, instance, owner):
        raise RaisingField.GetException(self, instance, owner)


class RaisingCompoundField(Field):
    a = RaisingField()
    b = RaisingField()


class TestCompoundField(TestCase):
    def test_accessing_properties(self):
        """On the class, the fields should return themselves."""
        f = CompoundField()

        self.assertIsInstance(CompoundField.a, Field)
        self.assertIsInstance(CompoundField.b, Field)

    def test_descriptor(self):
        """Ensure the decorated __get__ method is called for fields."""
        f = RaisingCompoundField()

        self.assertRaises(RaisingField.GetException, lambda: f.a)

    def test_separate_fields(self):
        """
        Ensure that different instances of CompoundField have separate
        underlying instances of F.
        """
        f = CompoundField()
        f2 = CompoundField()

        # Duh.
        self.assertFalse(f is f2)

        # If we don't set one of the values, then both will be None.
        f.a = ['a']

        self.assertFalse(f.a is f.b)

        f.b = {}
        self.assertFalse(f.a is f2.a)
        self.assertFalse(f.b is f2.b)
