import os
import struct

from nibbles.exceptions import NotEnoughDataException
from nibbles.fields.base import Field, _filelike


class StructField(Field):
    """
    A field that can be directly unpacked with a format string.

    Sub-classes should declare the following properties:
        _format_string
        default
        valid_types
    """

    def __init__(self, value=None, *args, **kwargs):
        super(StructField, self).__init__(*args, **kwargs)

        # Build the format string.
        self.format_string = b'%s' % self._format_string

        # If a value was given, use the default.
        if value is None:
            value = self.default
        self.value = value

    def _check_value(self, value):
        """Ensure the new value is of the proper type."""
        if not isinstance(value, self.valid_types):
            raise TypeError("Value is not a valid type: %s" % type(value))

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        """Store a Python value for this field."""
        self._check_value(value)
        self._value = value

    # The formatting to use for struct unpack/pack, only used if fixed_width is
    # True.
    @property
    def _format_string(self):
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
        self.value = struct.unpack(format_string, f.read(num_bytes))[0]

    def emit(self):
        format_string = self.endian + self.format_string

        return struct.pack(format_string, self.value)

    def __call__(self):
        return self.value


class PadField(StructField):
    _format_string = b'x'
    # TODO


class CharField(StructField):
    def _check_value(self, value):
        super(CharField, self)._check_value(value)

        if len(value) != 1:
            raise ValueError("Attempting to set a %d length string to a character field, character fieldss must be exactly 1 character in length." % len(value))

    _format_string = b'c'
    default = b'\x00'
    valid_types = (str, bytes)


class ByteField(StructField):
    def _check_value(self, value):
        super(ByteField, self)._check_value(value)

        if value < self.min_value or self.max_value < value:
            raise ValueError("Value is out of range %d <= %d <= %d" %
                             (self.min_value, value, self.max_value))

    _format_string = b'b'
    valid_types = (int, long)
    default = 0
    min_value = -128
    max_value = 127


class UnsignedByteField(ByteField):
    _format_string = b'B'
    min_value = 0
    max_value = 256


class BoolField(StructField):
    _format_string = b'?'
    valid_types = bool
    default = False


class ShortField(ByteField):
    _format_string = b'h'
    min_value = -32768
    max_value = 32767


class UnsignedShortField(ByteField):
    _format_string = b'H'
    min_value = 0
    max_value = 65535


class IntegerField(ByteField):
    _format_string = b'i'
    min_value = -2147483648
    max_value = 2147483647


class UnsignedIntegerField(ByteField):
    _format_string = b'I'
    min_value = 0
    max_value = 4294967295


class LongField(IntegerField):
    _format_string = b'l'


class UnsignedLongField(UnsignedIntegerField):
    _format_string = b'L'


class LongLongField(ByteField):
    _format_string = b'q'
    min_value = -9223372036854775808
    max_value = 9223372036854775807


class UnsignedLongLongField(ByteField):
    _format_string = b'Q'
    min_value = 0
    max_value = 18446744073709551615


class FloatField(StructField):
    _format_string = b'f'
    default = float(0)
    valid_types = float


class DoubleField(FloatField):
    _format_string = b'd'


class StringField(StructField):
    _format_string = b's'
    default = b''
    valid_types = (str, bytes)

    def __init__(self, length=0, *args, **kwargs):
        super(StringField, self).__init__(*args, **kwargs)

        # Allow strings to be multiple characters.
        self.format_string = b'%d%s' % (length, self._format_string)


class VoidField(StructField):
    _format_string = b'P'


class RepeatStructFieldMixin(object):
    """A mixin to have a field be repeated multiple times."""

    # ff


class CStringField(Field):
    def __init__(self, value=b'', *args, **kwargs):
        super(CStringField, self).__init__(*args, **kwargs)

        if not isinstance(value, (str, bytes)):
            raise TypeError("Value is not a string type: %s" % type(value))
        self.value = value

    def size(self):
        return len(self.value) + 1

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

        self.value = raw

    def emit(self):
        return self.value + b'\x00'


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
        self.value = f.read(length)

        if len(self.value) < length:
            raise NotEnoughDataException(
                "Not enough data for P-string, expected: %d, got: %d" %
                (length, len(self.value)))

    def emit(self):
        # Remember the size is total number of bytes, but P-strings just include
        # the number of bytes *after* the length byte.
        return chr(self.size() - 1) + self.value
