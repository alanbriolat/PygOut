import re

from pygments.style import Style


class _Color(object):
    """A clever descriptor that throws a :exc:`ValueError` if an invalid color
    is assigned.
    """
    #: Regex to match only valid 3- and 6-digit hex colors
    VALID_COLOR = re.compile(r'^#(([0-9a-fA-F]{3}){1,2})$')

    def __init__(self, attr):
        self.attr = attr

    def __get__(self, instance, owner):
        if instance is None:
            return getattr(owner, self.attr)
        else:
            return getattr(instance, self.attr)

    def __set__(self, instance, value):
        # empty/false-like value unsets the color
        if not value:
            setattr(instance, self.attr, None)
            return

        # was the color in a valid format?
        match = self.VALID_COLOR.match(value)
        if not match:
            raise ValueError('invalid color {}'.format(value))
        color = match.group(1)

        # pad 3-character colors to 6-character
        if len(color) == 3:
            color = color[0] * 2 + color[1] * 2 + color[2] * 2

        setattr(instance, self.attr, '#' + color.lower())


def _switch_if_set(value, if_true, if_false):
    if value == True:
        return if_true
    if value == False:
        return if_false
    return None


class TokenStyle(object):
    inherit = True
    _color = None
    color = _Color('_color')
    _bgcolor = None
    bgcolor = _Color('_bgcolor')
    bold = None
    italic = None
    underline = None
    # Understood by Pygments, but not useful to us
    #border = None
    #roman = None
    #sans = None
    #mono = None

    #: Data attributes that together define a token style
    FIELDS = ('inherit', 'color', 'bgcolor', 'bold', 'italic', 'underline')

    def __init__(self, style=None, **kwargs):
        if style:
            self.apply_pygments_style(style)

        for k, v in kwargs.iteritems():
            if k in self.FIELDS:
                setattr(self, k, v)

    def apply_pygments_style(self, style):
        """Update the style from a Pygments style string.

        This is largely based on the implementation of
        :class:`pygments.style.StyleMeta`.
        """
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
            elif styledef.startswith('bg:'):
                self.bgcolor = styledef[3:]
            elif styledef.startswith('#'):
                self.color = styledef
            # Ignore roman, sans and mono - these don't really map to useful
            # things for an editor.  We won't be using them, but existing
            # Pygments styles might even though they are undocumented.

    def __str__(self):
        """Get the Pygments style string that represents this style.
        """
        parts = [
            'noinherit' if self.inherit == False else None,
            self.color,
            self.bgcolor and 'bg:' + self.bgcolor,
            _switch_if_set(self.bold, 'bold', 'nobold'),
            _switch_if_set(self.italic, 'italic', 'noitalic'),
            _switch_if_set(self.underline, 'underline', 'nounderline'),
        ]
        return ' '.join(p for p in parts if p is not None)

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, str(self))

    def __eq__(self, other):
        return all(getattr(self, k) == getattr(other, k) for k in self.FIELDS)

    def __ne__(self, other):
        return not self == other


class SyntaxStyle(object):
    """The PygOut representation of a syntax color scheme.
    """
    _bgcolor = '#ffffff'
    #: Default background color
    bgcolor = _Color('_bgcolor')
    _hlcolor = '#ffffcc'
    #: Line highlight color
    hlcolor = _Color('_hlcolor')
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
        s.styles = dict((k, TokenStyle(s))
                        for k, s in style.styles.iteritems() if s)

        return s
