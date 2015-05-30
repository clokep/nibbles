from collections import OrderedDict
from copy import deepcopy
import struct

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


def _filelike(f):
    """Ensure f is a filelike object."""
    if isinstance(f, type("")):
        return StringIO(f)
    return f


NATIVE_ENDIAN = "="
BIG_ENDIAN = ">"
LITTLE_ENDIAN = "<"
NETWORK_ENDIAN = "!"

ENDIANS = (NATIVE_ENDIAN, BIG_ENDIAN, LITTLE_ENDIAN, NETWORK_ENDIAN,)


class BaseField(object):
    """
    The actual implementation of a Field should go here, Field simply exists
    to properly set __metaclass__.

    The metaclass magic is borrowed from
    django.forms.forms.DeclarativeFieldsMetaclass, django.forms.forms.BaseForm,
    and django.forms.fields.Field, but tweaked such that the "BaseForm" and the
    "Field" are the same object.

    Each Field object should expose three methods:
        size        int                 The number of consumed bytes
        consume     Field or builtin    The object-ified representation of the binary
        emit        bytes               The binary representation of this field

    """

    # Tracks each time a Field instance is created. Used to retain order.
    creation_counter = 0

    # The endianess of this data.
    endian = NETWORK_ENDIAN

    def __init__(self, endian=NETWORK_ENDIAN, *args, **kwargs):
        """
        Foobar.

        """

        # Increase the creation counter, and save our local copy.
        self.creation_counter = Field.creation_counter
        BaseField.creation_counter += 1
        
        # Add the fields to this instance of the class, deepcopy to allow
        # modification of instances.
        for fieldname, field in self.base_fields.items():
            setattr(self, fieldname, deepcopy(field))

        # Ensure the class knows what Endianess to care about.
        if endian not in ENDIANS:
            raise ValueError("Invalid value for endianess: %s" % endian)
        self.endian = endian

    # The raw Python object value for this field. Individual subclasses should
    # set this value.
    value = None
    def __call__(self):
        return self.value

    # The number of bytes represented by this field, -1 denotes a variable
    # length.
    def size(self):
        sz = 0
        # Combine the length of any children.
        for fieldname in self.base_fields.keys():
            sz += getattr(self, fieldname).size

        return sz

    def consume(self, data):
        """
        A factory method, it takes data and returns an instance of this Field
        object.

        """
        data = _filelike(data)

        # Ask each field to consume bytes and add it as a property (in order).
        for fieldname in self.base_fields.keys():
            getattr(self, fieldname).consume(data)

        return self

    def emit(self):
        """Returns the serialization of this data to a string."""
        pass


class MetaField(type):
    """
    Metaclass that collects Fields declared on the base classes.

    """
    def __new__(mcs, name, bases, attrs):
        # Collect fields from current class.
        current_fields = []
        for key, value in list(attrs.items()):
            if isinstance(value, BaseField):
                current_fields.append((key, value))
                attrs.pop(key)
        current_fields.sort(key=lambda x: x[1].creation_counter)
        attrs['declared_fields'] = OrderedDict(current_fields)

        new_class = (super(MetaField, mcs)
            .__new__(mcs, name, bases, attrs))

        # Walk through the MRO.
        declared_fields = OrderedDict()
        for base in reversed(new_class.__mro__):
            # Collect fields from base class.
            if hasattr(base, 'declared_fields'):
                declared_fields.update(base.declared_fields)

            # Field shadowing.
            for attr, value in base.__dict__.items():
                if value is None and attr in declared_fields:
                    declared_fields.pop(attr)

        new_class.base_fields = declared_fields
        new_class.declared_fields = declared_fields

        return new_class


class Field(BaseField):
    __metaclass__ = MetaField


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
        self.value = struct.unpack(format_string, f.read(num_bytes))[0]

        return self

    def emit(self):
        return struct.pack(self.endian + self.format_string, self)


class UIntField(StructField):
    format_string = b'I'

class ByteField(StructField):
    format_string = b'b'


class CString(Field):
    def consume(self, f):
        f = _filelike(f)

        self.value = b''
        char = f.read(1)
        # Read until a null-byte is hit.
        while char != '\x00':
            self.value += char
            char = f.read(1)

        return self
