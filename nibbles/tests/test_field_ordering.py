from __future__ import absolute_import

from unittest import TestCase

from ..fields import Field

# A bunch of classes for testing.
class Ordered(Field):
    a = Field()
    b = Field()
    c = Field()
    d = Field()


class Reversed(Field):
    d = Field()
    c = Field()
    b = Field()
    a = Field()


class Random(Field):
    c = Field()
    a = Field()
    b = Field()
    d = Field()


class SubClass(Ordered):
    x = Field()
    y = Field()


class SubField(Field):
    q = Field()
    r = Reversed()


class TestOrdering(TestCase):
    def test_ordered_fields(self):
        f = Ordered()
        self.assertEqual(['a', 'b', 'c', 'd'], f.declared_fields.keys())

    def test_reversed_fields(self):
        f = Reversed()
        self.assertEqual(['d', 'c', 'b', 'a'], f.declared_fields.keys())

    def test_random_fields(self):
        f = Random()
        self.assertEqual(['c', 'a', 'b', 'd'], f.declared_fields.keys())

    def test_subclass_fields(self):
        f = SubClass()
        self.assertEqual(['a', 'b', 'c', 'd', 'x', 'y'], f.declared_fields.keys())

    def test_subfield_fields(self):
        f = SubField()
        self.assertEqual(['q', 'r'], f.declared_fields.keys())
