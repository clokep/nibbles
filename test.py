from collections import OrderedDict
from copy import deepcopy

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

    def __init__(self, *args, **kwargs):
        # Increase the creation counter, and save our local copy.
        self.creation_counter = Field.creation_counter
        BaseField.creation_counter += 1

        # Add the fields to this instance of the class, deepcopy to allow
        # modification of instances.
        #for fieldname, field in self.base_fields.items():
        #    setattr(self, fieldname, deepcopy(field))

    # The raw Python object value for this field. Individual subclasses should
    # set this value.
    _raw = None
    def __get__(self, instance, owner):
        if not instance:
            raise AttributeError()

        return instance._raw
    def __set__(self, instance, value):
        """Sub-classes might want to do validation."""
        instance._raw = value


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
                #attrs.pop(key)
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

        # Add all attributes to the class.
        # for obj_name, obj in attrs.items():
        #     print("Setting %s" % obj_name)
        #     setattr(new_class, obj_name, obj)

        return new_class


class Field(BaseField):
    __metaclass__ = MetaField


class F(Field):
    a = Field()
    b = Field()


class G(F):
    c = Field()

print("Test class")
#print(F.a)
#print(F.b)

print("Test instance")
f = F()
print(f.a)
print(f.b)

f2 = F()
print(f.a is f2.a)
print(f.base_fields)


g = G()
print(g.base_fields)
