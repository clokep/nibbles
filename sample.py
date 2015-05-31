from nibbles import fields
from nibbles.fields import LITTLE_ENDIAN

EXPECTED = '\x01abcdf\x00'

class Struct(fields.Field):
    code = fields.ByteField()
    description = fields.CString()

s = Struct(code=1, description='abcdf', endian=LITTLE_ENDIAN)
assert s.emit() == EXPECTED

s = Struct().consume(EXPECTED)
assert s.code() == 1
assert s.description() == 'abcdf'

assert s.emit() == EXPECTED
assert s.size() == len(EXPECTED)


class ComplexStruct(fields.Field):
    a = fields.ByteField()
    s = Struct()
    b = fields.ByteField()

s2 = ComplexStruct(a=1, s=s, b=17)
assert s2.a() == 1
assert isinstance(s2.s, Struct)
assert s2.s.code() == 1
assert s2.s.description() == 'abcdf'
assert s2.b() == 17
assert s2.emit() == '\x01\x01abcdf\x00\x11'
