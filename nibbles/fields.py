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

    def __init__(self, endian=NETWORK_ENDIAN, *args, **kwargs):
        """
        Foobar.

        """

        # Increase the creation counter, and save our local copy.
        self.creation_counter = Field.creation_counter
        BaseField.creation_counter += 1
        
        # Add the fields to this instance of the class, deepcopy to allow
        # modification of instances.
        for f, v in self.base_fields.items():
            setattr(self, f, deepcopy(v))

        # Ensure the class knows what Endianess to care about.
        if endian not in ENDIANS:
            raise ValueError("Invalid value for endianess: %s" % endian)
        self.endian = endian

    # The raw Python object value for this field. Individual subclasses should
    # set this value.
    _raw = None

    # The number of bytes represented by this field, -1 denotes a variable
    # length.
    def size(self):
        sz = 0
        # Combine the length of any children.
        for f in self.base_fields.keys():
            sz += getattr(self, f).size

        return sz

    @classmethod
    def consume(cls, data):
        """
        A factory method, it takes data and returns an instance of this Field
        object.

        """
        return cls(self.fobar)

    def emit(self, filelike):
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
    @property
    def format_string(self):
        # Combine the formats of any children.
        fmt = ''
        for f in self.base_fields.keys():
            fmt += getattr(self, f).format_string

        return fmt

    @property
    def size(self):
        return struct.calcsize(self.struct_format)

    @classmethod
    def consume(cls, f, *args, **kwargs):
        f = _filelike(f)

        endian = kwargs.get('endian', NETWORK_ENDIAN)

        values = struct.unpack(endian + cls.struct_format,
                               f.read(cls.length))
        args = list(values) + args

        return cls(*args, **kwargs)

    def emit(self, value):
        return struct.pack(self.endian + self.struct_format, self)


class UIntField(FixedWidthField):
    format_string = b'I'

class ByteField(FixedWidthField):
    format_string = b'b'


class CString(Field):
    @classmethod
    def consume(cls, f, *args, **kwargs):
        f = _filelike(f)

        res = b''
        char = f.read(1)
        while char != '\x00':
            res += char
            char = f.read(1)

        return cls(res, *args, **kwargs)
