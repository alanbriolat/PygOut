from configparser import ConfigParser, ExtendedInterpolation

from pygments.token import string_to_tokentype

from pygout.format import Format
from pygout.style import TokenStyleEditor, SyntaxStyle


class PygOutConfig(Format):
    def read(self, stream):
        config = self._create_configparser()
        config.read_file(stream)

        token_styles = {}
        for name, section in config.items():
            # Ignore sections that aren't going to be allowed as token names
            if name == 'IGNORED_DEFAULT' or name[0].islower():
                continue

            token = string_to_tokentype(name)
            token_styles[token] = _read_style_section(section)

        # TODO: handle background, highlight colors
        # TODO: save palette?
        # TODO: have a style name?
        style = SyntaxStyle()
        style.styles = token_styles
        return style

    def write(self, stream, style):
        config = self._create_configparser()
        for token in sorted(style.styles.keys()):
            token_name = str(token)
            config.add_section(token_name)
            _write_style_section(config[token_name], style.styles[token])
        config.write(stream, space_around_delimiters=True)

    def _create_configparser(self):
        return ConfigParser(interpolation=ExtendedInterpolation(),
                            default_section='IGNORED_DEFAULT')


def _read_style_section(section):
    """Convert *section* to a Pygments-compatible style string.
    """
    ts = TokenStyleEditor()
    ts.inherit = section.getboolean('inherit', True)
    ts.bold = section.getboolean('bold', None)
    ts.italic = section.getboolean('italic', None)
    ts.underline = section.getboolean('underline', None)
    ts.color = section.get('color', None)
    ts.bgcolor = section.get('bgcolor', None)
    ts.border = section.get('border', None)
    return ts


def _write_style_section(section, style):
    """Modify *section* by adding options that are set in *style*.
    """
    for k in ('bold', 'italic', 'underline', 'color', 'bgcolor', 'border'):
        v = getattr(style, k)
        if v is not None:
            section[k] = str(v)
    if style.inherit is False:
        section['inherit'] = False


if __name__ == '__main__':
    import sys
    import codecs
    with codecs.open(sys.argv[1], 'r', 'utf-8') as stream:
        f = PygOutConfig()
        style = f.read(stream)
        print style
