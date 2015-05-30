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
        
        # Add the fields to this instance of the class.
        #for fieldname, field in self.base_fields.items():
        #    setattr(self, fieldname, field)

        # Ensure the class knows what Endianess to care about.
        if endian not in ENDIANS:
            raise ValueError("Invalid value for endianess: %s" % endian)
        self.endian = endian

    # The descriptor is set up to allow each instance to have it's own value,
    # even when belonging to different classes. See the tests near
    # nibbles.fields.test_field.TestCompoundField.test_separate_fields.
    _raws = {}
    def _gen_key(self, instance):
        """
        The key is based on both self (i.e. the instance of the descriptor) and
        instance (i.e. the object that is accessing the descriptor.
        """
        return (id(self), id(instance))

    def __get__(self, instance, owner):
        # If there is no instance, then we must be called from a class obejct.
        if not instance:
            return self

        # If there are any sub-fields, pass the real field back.
        if self.base_fields:
            return self

        key = self._gen_key(instance)
        if not self._raws.has_key(key):
            self.__set__(instance, None)

        return self._raws[key]

    def __set__(self, instance, value):
        """Sub-classes might want to do validation."""
        self._raws[self._gen_key(instance)] = value

    def __delete__(self, instance):
        del self._raws[self._gen_key(instance)]

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
        for fieldname, field in self.base_fields.items():
            # Don't get *this* instances field, since it will lie and return the
            # underlying Python value. Use the shared instance that is in
            # base_fields directly.
            raw = field.consume(data)
            # Setting the attribute will set the raw Python value to be stored,
            # however.
            setattr(self, fieldname, raw)

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
