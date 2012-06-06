import re

from pygments.style import Style

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


class SyntaxStyle(object):
    """The PygOut representation of a syntax color scheme.
    """
    #: Default background color
    bgcolor = _color_value('_bgcolor', '#ffffff')
    #: Line highlight color
    hlcolor = _color_value('_hlcolor', '#ffffcc')
    #: Dict mapping Pygments tokens to :class:`TokenStyle` instances
    styles = {}

    def to_pygments_style(self):
        """Generate a Pygments ``Style`` for this style.
        """
        class PygOutStyle(Style):
            background_color = self.bgcolor
            highlight_color = self.hlcolor
            styles = dict((k, str(v)) for k, v in self.styles.iteritems())
            pygout_style = self
        return PygOutStyle

    @classmethod
    def from_pygments_style(self, style):
        """Get a ``SyntaxStyle`` from a Pygments ``Style``.

        If *style* was previously generated from a ``SyntaxStyle`` then this
        just returns the original ``SyntaxStyle``.
        """
        if hasattr(style, 'pygout_style'):
            return style.pygout_style

        s = SyntaxStyle()
        s.bgcolor = style.background_color
        s.hlcolor = style.highlight_color
        # Convert styles to TokenStyle, omitting empty (inherit-only) styles
        s.styles = dict((k, TokenStyleEditor(s))
                        for k, s in style.styles.iteritems() if s)

        return s
