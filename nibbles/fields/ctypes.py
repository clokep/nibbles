import struct

from nibbles.exceptions import NotEnoughDataException
from nibbles.fields.base import Field, _filelike

class StructField(Field):
    """
    A field that can be directly unpacked with a format string.

    Sub-classes should declare the `format_string` property.

    """

    # The formatting to use for struct unpack/pack, only used if fixed_width is
    # True.
    @property
    def format_string(self):
        raise NotImplementedError

    def size(self):
        # value is unused.
        return struct.calcsize(self.format_string)

    def consume(self, f):
        f = _filelike(f)

        # Add the Endianess to the format string.
        format_string = self.endian + self.format_string

        # Calculate the number of necessary bytes.
        num_bytes = self.size()

        # Unpack the data.
        self._value = struct.unpack_from(format_string, f)[0]

    def emit(self):
        format_string = self.endian + self.format_string
        return struct.pack(format_string, self._value)


class PadField(StructField):
    format_string = b'x'

class CharField(StructField):
    format_string = b'c'

class ByteField(StructField):
    format_string = b'b'

class UnsignedByteField(StructField):
    format_string = b'B'

class BoolField(StructField):
    format_string = b'?'

class ShortField(StructField):
    format_string = b'h'

class UnsignedShortField(StructField):
    format_string = b'H'

class IntegerField(StructField):
    format_string = b'i'

class UnsignedIntegerField(StructField):
    format_string = b'I'

class LongField(StructField):
    format_string = b'l'

class UnsignedLongField(StructField):
    format_string = b'L'

class LongLongField(StructField):
    format_string = b'q'

class UnsignedLongLongField(StructField):
    format_string = b'Q'

class FloatField(StructField):
    format_string = b'f'

class DoubleField(StructField):
    format_string = b'd'

class StringField(StructField):
    format_string = b's'

class PStringField(StructField):
    format_string = b'p'

class VoidField(StructField):
    format_string = b'P'

class CStringField(Field):
    def __init__(self, value=b'', *args, **kwargs):
        super(CStringField, self).__init__(*args, **kwargs)

        if not isinstance(value, (str, bytes)):
            raise ValueError("Value is not a string type: %s" % type(value))
        self._value = value

    def size(self):
        return len(self._value) + 1

    def consume(self, f):
        f = _filelike(f)

        raw = b''
        # Read until a null-byte is hit.
        char = f.read(1)
        while char != b'\x00':
            if char == b'':
                raise NotEnoughDataException("End of C-string not reached")

            raw += char
            char = f.read(1)

        self._value = raw

    def emit(self):
        return self._value + b'\x00'
