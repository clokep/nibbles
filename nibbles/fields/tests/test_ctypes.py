from unittest import TestCase

from nibbles.exceptions import NotEnoughDataException
from nibbles.fields.ctypes import *


class TestCharField(TestCase):
    def setUp(self):
        self.f = CharField()

    def test_consume(self):
        self.f.consume(b'\x01')
        self.assertEqual(self.f(), b'\x01')
        self.assertEqual(self.f.size(), 1)
        self.assertEqual(self.f.emit(), b'\x01')

    def test_empty_constructor(self):
        """The no argument constructor is equivalent to a null character."""
        self.assertEqual(self.f(), b'\x00')
        self.assertEqual(self.f.size(), 1)
        self.assertEqual(self.f.emit(), b'\x00')

    def test_constructor(self):
        self.f = CharField(b't')
        self.assertEqual(self.f(), b't')
        self.assertEqual(self.f.size(), 1)
        self.assertEqual(self.f.emit(), b't')

    def test_unicode(self):
        self.assertRaises(TypeError, CharField, u'1')

    def test_too_short(self):
        self.assertRaises(ValueError, CharField, b'')

    def test_too_long(self):
        self.assertRaises(ValueError, CharField, b'12')


class TestByteField(TestCase):
    FIELD = ByteField

    def setUp(self):
        self.f = self.FIELD()

    def test_consume(self):
        self.f.consume(b'\x01')
        self.assertEqual(self.f(), 1)
        self.assertEqual(self.f.size(), 1)
        self.assertEqual(self.f.emit(), b'\x01')

    def test_empty_constructor(self):
        """The no argument constructor is equivalent to 0."""
        self.assertEqual(self.f(), 0)
        self.assertEqual(self.f.size(), 1)
        self.assertEqual(self.f.emit(), b'\x00')

    def test_constructor(self):
        self.f = self.FIELD(2)
        self.assertEqual(self.f(), 2)
        self.assertEqual(self.f.size(), 1)
        self.assertEqual(self.f.emit(), b'\x02')

    def test_invalid_type(self):
        self.assertRaises(TypeError, self.FIELD, u'1')

    def test_too_small(self):
        self.assertRaises(ValueError, self.FIELD, self.FIELD.min_value - 1)

    def test_too_large(self):
        self.assertRaises(ValueError, self.FIELD, self.FIELD.max_value + 1)


class TestUnsignedByteField(TestByteField):
    FIELD = UnsignedByteField


class TestPStringField(TestCase):
    def setUp(self):
        self.f = PStringField()

    def test_str(self):
        """Test a basic string."""
        self.f.consume(b'\x04test')
        self.assertEqual(self.f(), b'test')
        self.assertEqual(self.f.size(), 5)
        self.assertEqual(self.f.emit(), b'\x04test')

    def test_zero_length_str(self):
        """Test an empty string (i.e. just a null byte)."""
        self.f.consume(b'\x00')
        self.assertEqual(self.f(), b'')
        self.assertEqual(self.f.size(), 1)
        self.assertEqual(self.f.emit(), b'\x00')

    def test_empty_str(self):
        """An invalid string: no data."""
        self.assertRaises(NotEnoughDataException, self.f.consume, b'')

    def test_no_end_str(self):
        """Test a string that doesn't have enough data."""
        self.assertRaises(NotEnoughDataException, self.f.consume, b'\x05test')

    def test_empty_constructor(self):
        """The no argument constructor is equivalent to an empty string."""
        self.assertEqual(self.f(), b'')
        self.assertEqual(self.f.size(), 1)
        self.assertEqual(self.f.emit(), b'\x00')

    def test_constructor(self):
        self.f = PStringField(b'test')
        self.assertEqual(self.f(), b'test')
        self.assertEqual(self.f.size(), 5)
        self.assertEqual(self.f.emit(), b'\x04test')

    def test_unicode(self):
        self.assertRaises(TypeError, PStringField, u'test')


class TestCStringField(TestCase):
    def setUp(self):
        self.f = CStringField()

    def test_str(self):
        """Test a basic string."""
        self.f.consume(b'test\x00')
        self.assertEqual(self.f(), b'test')
        self.assertEqual(self.f.size(), 5)
        self.assertEqual(self.f.emit(), b'test\x00')

    def test_zero_length_str(self):
        """Test an empty string (i.e. just a null byte)."""
        self.f.consume(b'\x00')
        self.assertEqual(self.f(), b'')
        self.assertEqual(self.f.size(), 1)
        self.assertEqual(self.f.emit(), b'\x00')

    def test_empty_str(self):
        """An invalid string: no data."""
        self.assertRaises(NotEnoughDataException, self.f.consume, b'')

    def test_no_end_str(self):
        """Test a string that doesn't end in a null-byte."""
        self.assertRaises(NotEnoughDataException, self.f.consume, b'test')

    def test_empty_constructor(self):
        """The no argument constructor is equivalent to an empty string."""
        self.assertEqual(self.f(), b'')
        self.assertEqual(self.f.size(), 1)
        self.assertEqual(self.f.emit(), b'\x00')

    def test_constructor(self):
        self.f = CStringField(b'test')
        self.assertEqual(self.f(), b'test')
        self.assertEqual(self.f.size(), 5)
        self.assertEqual(self.f.emit(), b'test\x00')

    def test_unicode(self):
        self.assertRaises(TypeError, CStringField, u'test')
