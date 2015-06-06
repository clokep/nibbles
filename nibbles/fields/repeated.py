from copy import deepcopy

from .base import _filelike, Field


class RepeatedField(Field):
    def __init__(self, repeated, *args, **kwargs):
        super(RepeatedField, self).__init__(*args, **kwargs)

        # The field to repeat.
        self.repeated = repeated
        self.value = []

    def consume(self, data):
        data = _filelike(data)

        # While there's still data, then parse more objects.
        while data.len < data.tell():
            # Make a new copy of the field.
            field = deepcopy(self.repeated)
            # Parse data.
            self.value.append(field.consume(data))

        return self


class DependentField(Field):
    """
    A field where one of the constructor arguments depends on the value of
    another field. Replaces itself with the constructed field.
    """

    def __init__(self, field_class, args=(), kwargs={}, dep_kwargs={}, *_args, **_kwargs):
        """
        args and kwargs get passed to the callable field_class directly,
        dep_kargs is a mapping of keyword to a string which is an attribute on
        the parent.

        The attribute can be a field (in which case the value of it is used) or
        a property which will be directly used.

        """

        super(DependentField, self).__init__(*_args, **_kwargs)

        self.field_class = field_class
        self.args = args
        self.kwargs = kwargs
        self.dep_kwargs = dep_kwargs

        # The field once it is created.
        self.value = None

    def consume(self, data):
        # Create an instance of the field.
        kwargs = deepcopy(self.kwargs)
        for keyword, attribute in self.dep_kwargs.items():
            field = getattr(self.parent, attribute)
            if isinstance(field, Field):
                value = field()
            # TODO Support callables?
            else:
                value = field

            # Update kwargs.
            kwargs[keyword] = value

        # Finally create the class and consume data.
        self.value = self.field_class(*self.args, **kwargs)
        self.value.consume(data)

        return self
