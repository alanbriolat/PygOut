import codecs
from configparser import ConfigParser, ExtendedInterpolation

from pygments.token import string_to_tokentype
from pygments.style import StyleMeta


def _option_prefix(section, option, prefix):
    """Get *option* value with *prefix* prepended, or None if absent.
    """
    if option not in section:
        return None
    return prefix + section.get(option)


def _option_switch(section, option, if_true, if_false):
    """Select between *if_true* and *if_false* based on boolean *option*,
    returning None if absent.
    """
    if option not in section:
        return None
    return if_true if section.getbool(option) else if_false


def _read_style_section(section):
    """Convert *section* to a Pygments-compatible style string.
    """
    styles = [
        _option_prefix(section, 'color', ''),
        _option_prefix(section, 'background', 'bg:'),
        _option_switch(section, 'bold', 'bold', 'nobold'),
        _option_switch(section, 'italic', 'italic', 'noitalic'),
        _option_switch(section, 'underline', 'underline', 'nounderline'),
        _option_switch(section, 'inherit', None, 'noinherit'),
    ]
    return ' '.join(s for s in styles if s is not None)


def read_style(configdata):
    config = ConfigParser(interpolation=ExtendedInterpolation(),
                          default_section='IGNORED_DEFAULT')
    config.read_string(configdata)

    token_styles = {}
    for name, section in config.items():
        # Ignore sections that aren't going to be allowed as token names
        if name == 'IGNORED_DEFAULT' or name[0].islower():
            continue

        token = string_to_tokentype(name)
        token_styles[token] = _read_style_section(section)

    return token_styles


if __name__ == '__main__':
    import sys
    with codecs.open(sys.argv[1], 'r', 'utf-8') as f:
        style = read_style(f.read())
        print style
