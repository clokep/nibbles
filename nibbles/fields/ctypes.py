import struct

from nibbles.exceptions import NotEnoughDataException
from nibbles.fields.base import Field, _filelike


class StructField(Field):
    """
    A field that can be directly unpacked with a format string.

    Sub-classes should declare the following properties:
        format_string
        default
        valid_types
    """

    def __init__(self, value=None, *args, **kwargs):
        super(StructField, self).__init__(*args, **kwargs)

        if value is None:
            value = self.default

        if not isinstance(value, self.valid_types):
            raise ValueError("Value is not a valid type: %s" % type(value))
        self._value = value

    # The formatting to use for struct unpack/pack, only used if fixed_width is
    # True.
    @property
    def format_string(self):
        raise NotImplementedError

    # The default value used in the constructor.
    @property
    def default(self):
        raise NotImplementedError

    # A tuple of valid types for value.
    @property
    def valid_types(self):
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
        self._value = struct.unpack(format_string, f.read(num_bytes))[0]

    def emit(self):
        format_string = self.endian + self.format_string
        return struct.pack(format_string, self._value)


class PadField(StructField):
    format_string = b'x'


class CharField(StructField):
    def __init__(self, value='\x00', *args, **kwargs):
        super(StructField, self).__init__(*args, **kwargs)

        if not isinstance(value, (str, bytes)):
            raise ValueError("Value is not a valid type: %s" % type(value))
        if len(value) != 1:
            raise ValueError("CharFields must be a length of 1, got %d" % len(value))
        self._value = value

    format_string = b'c'


class ByteField(StructField):
    def __init__(self, value=0, *args, **kwargs):
        super(StructField, self).__init__(*args, **kwargs)

        if not isinstance(value, int):
            raise ValueError("Value is not a valid type: %s" % type(value))
        if value < self.min_value or self.max_value < value:
            raise ValueError("Value is out of range %d <= %d <= %d" %
                             (self.min_value, value, self.max_value))
        self._value = value

    format_string = b'b'
    min_value = -128
    max_value = 127


class UnsignedByteField(ByteField):
    format_string = b'B'
    min_value = 0
    max_value = 256


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


class PStringField(CStringField):
    """The built in struct unpacking of Pascal strings is unfortunate, build our
    own."""

    def consume(self, f):
        f = _filelike(f)

        # The length is the first byte
        length = f.read(1)
        if length == '':
            raise NotEnoughDataException("0-length string is invalid P-string")
        length = ord(length)

        # Attempt to read that length.
        self._value = f.read(length)

        if len(self._value) < length:
            raise NotEnoughDataException(
                "Not enough data for P-string, expected: %d, got: %d" %
                (length, len(self._value)))

    def emit(self):
        # Remember the size is total number of bytes, but P-strings just include
        # the number of bytes *after* the length byte.
        return chr(self.size() - 1) + self._value
