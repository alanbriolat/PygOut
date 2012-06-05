from configparser import ConfigParser, ExtendedInterpolation

from pygments.token import string_to_tokentype

from pygout.format import Format
from pygout.style import TokenStyle, SyntaxStyle


class PygOutConfig(Format):
    def read(self, stream):
        config = ConfigParser(interpolation=ExtendedInterpolation(),
                              default_section='IGNORED_DEFAULT')
        config.read_file(stream)

        token_styles = {}
        for name, section in config.items():
            # Ignore sections that aren't going to be allowed as token names
            if name == 'IGNORED_DEFAULT' or name[0].islower():
                continue

            token = string_to_tokentype(name)
            token_styles[token] = _read_style_section(section)

        return token_styles


def _read_style_section(section):
    """Convert *section* to a Pygments-compatible style string.
    """
    ts = TokenStyle()
    ts.color = section.get('color', None)
    ts.bgcolor = section.get('bgcolor', None)
    ts.bold = section.getboolean('bold', None)
    ts.italic = section.getboolean('italic', None)
    ts.underline = section.getboolean('underline', None)
    ts.inherit = section.getboolean('inherit', True)
    return ts


if __name__ == '__main__':
    import sys
    import codecs
    with codecs.open(sys.argv[1], 'r', 'utf-8') as stream:
        f = PygOutConfig()
        style = f.read(stream)
        print style
