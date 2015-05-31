class NibblesException(Exception):
    pass


class NotEnoughDataException(NibblesException):
    """Not enough data to read the field."""
