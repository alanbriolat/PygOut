import re

import pygments.style
from pygments.token import Token
from pygments.styles import get_style_by_name

from pygout.util import normalise_color, ValueFilter


def _color_value(attr, default=None):
    return ValueFilter(attr, normalise_color, default)


def _enum_value(attr, values, default):
    def validate(value):
        if value in values:
            return value
        raise ValueError('{} not in {}'.format(value, values))
    return ValueFilter(attr, validate, default)


class TokenStyleEditor(object):
    """A utility class for manipulating Pygments token styles.

    Supporting seamless conversion between instances of this class and Pygments
    token style strings as documented in http://pygments.org/docs/styles/, this
    class allows easy programmatic manipulation of token styles.  Most
    attributes support using the None value to indicate inheritance.  Color
    attributes will raise :class:`~exceptions.ValueError` if the value
    assigned is not a valid color (3- or 6-digit hexadecimal).
    """

    #: Inherit styles from parent (*True* or *False*).
    inherit = _enum_value('_inherit', set((True, False)), True)
    #: Text is bold (*True*, *False* or *None*).
    bold = _enum_value('_bold', set((True, False, None)), None)
    #: Text is italic (*True*, *False* or *None*).
    italic = _enum_value('_italic', set((True, False, None)), None)
    #: Text is underlined (*True*, *False* or *None*).
    underline = _enum_value('_underline', set((True, False, None)), None)
    #: Text color (valid color or *None*).
    color = _color_value('_color')
    #: Background color (valid color or *None*)
    bgcolor = _color_value('_bgcolor')
    #: Border color (valid color or *None*)
    border = _color_value('_border')

    def __init__(self, style=''):
        if style:
            self.apply(style)

    def apply(self, style):
        """Apply another style, overriding elements of this style.

        *style* is converted a string before being treated as a Pygments style
        string, so this method can be used to apply another
        :class:`TokenStyleEditor`.

        Based very heavily on :class:`pygments.style.StyleMeta`.
        """
        style = str(style)
        for styledef in style.split():
            if styledef == 'noinherit':
                self.inherit = False
            elif styledef == 'bold':
                self.bold = True
            elif styledef == 'nobold':
                self.bold = False
            elif styledef == 'italic':
                self.italic = True
            elif styledef == 'noitalic':
                self.italic = False
            elif styledef == 'underline':
                self.underline = True
            elif styledef == 'nounderline':
                self.underline = False
            elif styledef.startswith('#'):
                self.color = styledef
            elif styledef.startswith('bg:'):
                self.bgcolor = styledef[3:]
            elif styledef.startswith('border:'):
                self.border = styledef[7:]
            # Pygments supports the following, but their behaviour isn't
            # defined anywhere and they probably won't map onto most uses of
            # color schemes anyway, so we ignore them.
            elif styledef == 'roman':
                pass
            elif styledef == 'sans':
                pass
            elif styledef == 'mono':
                pass
            else:
                raise ValueError("unrecognised style '{}'".format(styledef))

    def __str__(self):
        """Assemble a Pygments style string.
        """
        parts = [
            self._bool_select('inherit', None, 'noinherit'),
            self._bool_select('bold', 'bold', 'nobold'),
            self._bool_select('italic', 'italic', 'noitalic'),
            self._bool_select('underline', 'underline', 'nounderline'),
            self._prefix_or_none('color', ''),
            self._prefix_or_none('bgcolor', 'bg:'),
            self._prefix_or_none('border', 'border:'),
        ]
        return ' '.join(p for p in parts if p is not None)

    def __eq__(self, other):
        """If two :class:`TokenStyleEditor`s are equal, their strings are too.
        """
        return str(self) == str(other)

    def _bool_select(self, attr, if_true, if_false):
        """Select between two values based on a boolean attribute, defaulting
        to None.
        """
        value = getattr(self, attr)

        if value is True:
            return if_true
        elif value is False:
            return if_false
        else:
            return None

    def _prefix_or_none(self, attr, prefix):
        """Get an attribute value with *prefix* prepended, or None if the
        attribute is set to None.
        """
        value = getattr(self, attr)

        if value is None:
            return None
        else:
            return prefix + value


class StyleMeta(pygments.style.StyleMeta):
    """Extend the Pygments style metaclass to provide extra functionality.
    """
    def find_style_for_token(cls, token):
        """Like Pygments' :meth:`StyleMeta.style_for_token`, but searches up
        the hierarchy if *token* doesn't have a style, defaulting to the base
        :const:`~pygments.token.Token`.
        """
        hierarchy = reversed(token.split())
        for t in hierarchy:
            if cls.styles_token(t):
                return cls.style_for_token(t)
        # Fallback: use Token style
        return cls.style_for_token(Token)


class Style(pygments.style.Style):
    """A replacement for Pygments' :class:`~pygments.style.Style` class which
    uses PygOut's :class:`StyleMeta`.

    (Not sure if this needs to exist or not.)
    """
    __metaclass__ = StyleMeta


def create_style(name, styles, bgcolor=None, hlcolor=None):
    """Create a :class:`Style` from a map of :class:`Token` to
    :class:`TokenStyleEditor`.

    The resulting :class:`Style` will have *pygout_name* and *pygout_styles*
    attributes corresponding to the *name* and *styles* arguments.
    """
    bgcolor = normalise_color(bgcolor)
    hlcolor = normalise_color(hlcolor)

    attrs = {
        'background_color': bgcolor or Style.background_color,
        'highlight_color': hlcolor or Style.highlight_color,
        'styles': dict((k, str(v)) for k, v in styles.iteritems()),
        'pygout_name': name,
        'pygout_styles': styles,
    }

    return StyleMeta('PygOutGeneratedStyle', (Style,), attrs)


def create_style_from_pygments(name):
    """Create a :class:`Style` from a named Pygments style.

    The resulting :class:`Style` will have a *pygout_name* attribute with the
    value of *name*, and a *pygout_styles* attribute which contains all of the
    Pygments style's non-empty token styles converted to
    :class:`TokenStyleEditor` instances.
    """
    pygments_style = get_style_by_name(name)

    attrs = {
        'background_color': pygments_style.background_color,
        'highlight_color': pygments_style.highlight_color,
        'styles': pygments_style.styles,
        'pygout_name': name,
        'pygout_styles':
            dict((k, TokenStyleEditor(v))
                 for k, v in pygments_style.styles.iteritems() if v),
    }

    return StyleMeta(pygments_style.__name__, (Style,), attrs)
