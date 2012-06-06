import re


#: Valid color regex for :func:`normalise_color`.
VALID_COLOR = re.compile(r'^#(([0-9a-fA-F]{3}){1,2})$')


def normalise_color(color):
    """Normalise a color value to lowercase 6-digit hexadecimal or None.
    Raises a :exc:`~exceptions.ValueError` if the value cannot be normalised.

    >>> normalise_color('#AABBCC')
    '#aabbcc'
    >>> normalise_color('#fff')
    '#ffffff'
    >>> print normalise_color('')
    None
    >>> normalise_color('red')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ValueError: invalid color red
    """
    # false-like values are None
    if not color:
        return None

    # was the color in a valid format?
    match = VALID_COLOR.match(color)
    if not match:
        raise ValueError('invalid color {}'.format(color))
    color = match.group(1)

    # pad 3-digit colors to 6-digit
    if len(color) == 3:
        color = color[0] * 2 + color[1] * 2 + color[2] * 2

    return '#' + color.lower()


class ValueFilter(object):
    """A descriptor which applies *filter* to assigned values, which are stored
    at *attr*.  If the value is unset it is *default*.
    """
    def __init__(self, attr, filter, default=None):
        self.attr = attr
        self.filter = filter
        self.default = self.filter(default)

    def __get__(self, instance, owner):
        if instance is None:
            return getattr(owner, self.attr, self.default)
        else:
            return getattr(instance, self.attr, self.default)

    def __set__(self, instance, value):
        setattr(instance, self.attr, self.filter(value))
