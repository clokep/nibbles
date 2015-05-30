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

    @property
    def size(self):
        return struct.calcsize(self.format_string)

    def consume(self, f):
        f = _filelike(f)

        # Add the Endianess to the format string.
        format_string = self.endian + self.format_string

        # Calculate the number of necessary bytes.
        num_bytes = self.size

        # Unpack the data.
        return struct.unpack(format_string, f.read(num_bytes))[0]

    def emit(self):
        return struct.pack(self.endian + self.format_string, self)


class UIntField(StructField):
    format_string = b'I'

class ByteField(StructField):
    format_string = b'b'


class CString(Field):
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
