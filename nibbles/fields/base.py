from collections import OrderedDict

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
        # Increase the creation counter, and save our local copy.
        self.creation_counter = Field.creation_counter
        BaseField.creation_counter += 1

        # Ensure the class knows what Endianess to care about.
        if endian not in ENDIANS:
            raise ValueError("Invalid value for endianess: %s" % endian)
        self.endian = endian

        # Now set those values, if in kwargs.
        for fieldname, value in kwargs.items():
            if fieldname in self.base_fields:
                getattr(self, fieldname).value = value
            else:
                raise TypeError("Unknown field: %s" % fieldname)

    # The number of bytes represented by this field, -1 denotes a variable
    # length.
    def size(self, value=None):
        sz = 0
        # Combine the length of any children.
        for fieldname, field in self.base_fields.items():
            # Get the value and then ask the field the size.
            sz += getattr(self, fieldname).size()

        return sz

    def consume(self, data):
        """
        A factory method, it takes data and returns an instance of this Field
        object.

        """
        data = _filelike(data)

        # Ask each field to consume bytes and add it as a property (in order).
        for fieldname, field in self.base_fields.items():
            raw = getattr(self, fieldname).consume(data)

        return self

    def emit(self):
        """
        Returns the serialization of this data to a string. This is a little
        odd, that you have to pass the value into itself.

        TODO Optionally accept a filelike to write to.
        """

        # Ask each field to consume bytes and add it as a property (in order).
        res = b''
        for fieldname, field in self.base_fields.items():
            # Get the value and then ask the field to emit it.
            res += getattr(self, fieldname).emit()

        return res

    # Each field needs a Python value to return, etc. This could be a tuple, or
    # something more complex.
    _value = None

    @property
    def value(self):
        """Return a Python value for this field."""
        return self._value

    @value.setter
    def value(self, value):
        """Store a Python value for this field."""
        self._value = value

    def __call__(self):
        """Shorthand for get_value."""
        return self.value

    def __str__(self, prefix=""):
        s = ""
        for fieldname in self.base_fields.keys():
            field = getattr(self, fieldname)
            if field.base_fields:
                s += "%s%s =\n%s\n" % (prefix, fieldname, field.__str__(prefix + "\t"))
            else:
                s += "%s%s = '%s'\n" % (prefix, fieldname, field())
        return s


class MetaField(type):
    """
    Metaclass that collects Fields declared on the base classes.

    """
    def __new__(mcs, name, bases, attrs):
        # Collect fields from current class.
        current_fields = []
        for key, value in attrs.items():
            if isinstance(value, BaseField):
                current_fields.append((key, value))
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
