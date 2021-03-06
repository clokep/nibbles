from __future__ import absolute_import

from unittest import TestCase

from nibbles.fields.base import Field


class CompoundField(Field):
    a = Field()
    b = Field()


class TestCompoundField(TestCase):
    def test_accessing_properties(self):
        """On the class, the fields should return themselves."""
        f = CompoundField()

        self.assertIsInstance(CompoundField.a, Field)
        self.assertIsInstance(CompoundField.b, Field)

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
        f.a.value = 'a'
        self.assertFalse(f.a is f.b)

        f.b = {}
        self.assertFalse(f.a is f2.a)
        self.assertFalse(f.b is f2.b)

    def test_field_instances(self):
        """Ensure fields are not shared."""
        f = CompoundField()
        f2 = CompoundField()

        f.foo = 1
        self.assertRaises(AttributeError, lambda: f2.foo)
        self.assertEqual(f.foo, 1)


class TestComplexField(TestCase):
    def test_complex(self):
        """Ensure subfields of subfields can be reached."""
        class CompoundCompoundField(CompoundField):
            c = CompoundField()
            f = Field()

        c = CompoundCompoundField()
        self.assertIsInstance(c, CompoundCompoundField)
        self.assertIsInstance(c.c, CompoundField)
        self.assertIsInstance(c.c.a, Field)
        self.assertIsInstance(c.f, Field)
