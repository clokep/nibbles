from __future__ import absolute_import

from unittest import TestCase

from .. import fields


class CompoundField(fields.Field):
    a = fields.UIntField()
    b = fields.UIntField()


class TestUIntField(TestCase):
    def setUp(self):
        self.f = fields.UIntField()

    def test_properties(self):
        self.assertEqual(self.f.length, 4)
        self.assertEqual(self.f.endian, fields.NETWORK_ENDIAN)

    def test_unpack(self):
        self.assertEqual(self.f.consume(b'\x00\x00\x00\x01'), 1)

    def test_pack(self):
        self.assertEqual(self.f.emit(1), b'\x00\x00\x00\x01')


class TestCompoundField(TestCase):
    def setUp(self):
        self.f = CompoundField()
        #print(self.f.a)
        #help(self.f)

    def test_properties(self):
        #self.assertEqual(self.f.length, 8)
        self.assertEqual(self.f.endian, fields.NETWORK_ENDIAN)

    def test_fields(self):
        self.assertIsInstance(self.f.a, fields.UIntField)
        self.assertIsInstance(self.f.b, fields.UIntField)

    def test_unpack(self):
        print(self.f)
        print(self.f.__dict__)
    
    def test_pack(self):
        pass


