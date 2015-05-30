import struct

from .base import Field, _filelike

class StructField(Field):
    """
    A field that can be directly unpacked with a format string.

    Sub-classes should declare the `format_string` property.

    """

    # The formatting to use for struct unpack/pack, only used if fixed_width is
    # True.
    format_string = b''

    def size(self, value=None):
        # value is unused.
        return struct.calcsize(self.format_string)

    def consume(self, f):
        f = _filelike(f)

        # Add the Endianess to the format string.
        format_string = self.endian + self.format_string

        # Calculate the number of necessary bytes.
        num_bytes = self.size()

        # Unpack the data.
        return struct.unpack(format_string, f.read(num_bytes))[0]

    def emit(self, value):
        format_string = self.endian + self.format_string
        return struct.pack(format_string, value)


class UIntField(StructField):
    format_string = b'I'

class ByteField(StructField):
    format_string = b'b'


class CString(Field):
    def size(self, value=''):
        return len(value) + 1

    def consume(self, f):
        f = _filelike(f)

        raw = b''
        # Read until a null-byte is hit.
        char = f.read(1)
        while char != '\x00':
            raw += char
            char = f.read(1)

        self = raw

        return self

    def emit(self, value):
        return value + '\x00'
