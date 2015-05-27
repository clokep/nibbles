from collections import OrderedDict

class Field(object):

    # Tracks each time a Field instance is created. Used to retain order.
    creation_counter = 0


class ModelBase(type):
    """
    Metaclass that collects Fields declared on the base classes.

    Borrowed from django.forms.forms.DeclarativeFieldsMetaclass.
    """
    def __new__(mcs, name, bases, attrs):
        # Collect fields from current class.
        current_fields = []
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                current_fields.append((key, value))
                attrs.pop(key)
        current_fields.sort(key=lambda x: x[1].creation_counter)
        attrs['declared_fields'] = OrderedDict(current_fields)

        new_class = (super(ModelBase, mcs)
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


class Model(object):
    __metaclass__ = ModelBase


class Model1(Model):
    a = Field()
    b = Field()
    c = Field()
    z = Field()

class Model2(Model):
    c = Field()
    z = Field()
    b = Field()
    a = Field()

class Model3(Model1):
    p = Field()
    q = Field()


print([f for f in Model1().declared_fields])
print([f for f in Model2().declared_fields])
print([f for f in Model3().declared_fields])
