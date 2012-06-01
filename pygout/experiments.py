import itertools

from pygments.styles import get_style_by_name
from pygments.token import Token
from pygments.style import Style, StyleMeta


def get_token_style(style, token):
    hierarchy = reversed(token.split())
    for t in hierarchy:
        if style.styles_token(t):
            return style.style_for_token(t)
StyleMeta.find_style_for_token = get_token_style


def newstyle(default, styles_):
    class NewStyle(Style):
        default_style = default
        styles = styles_
    return NewStyle


def newstyle2(name, **kwargs):
    return StyleMeta(name, (Style,), kwargs)


class Application(object):
    def __init__(self):
        pass

    def read(self, definition):
        raise NotImplementedError

    def generate(self, style):
        raise NotImplementedError


class Vim(Application):
    def __init__(self):
        self.tokens = [
            (Token, ['Normal'], self.generate_basic_rule),
            (Token.String, ['String'], self.generate_basic_rule),
            (Token.String.Lolol, ['Roffle'], self.generate_basic_rule),
        ]

    def generate_basic_rule(self, token, groups, style):
        tstyle = get_token_style(style, token)
        fg = '#' + tstyle['color'] if tstyle['color'] else 'none'
        bg = '#' + tstyle['bgcolor'] if tstyle['bgcolor'] else 'none'
        gui = 'none'    # TODO: fixme
        for g in groups:
            yield "hi {} guifg={} guibg={} gui={}".format(g, fg, bg, gui)
            # TODO: generate 256-color color codes for cterm*

    def generate(self, style):
        return '\n'.join(itertools.chain(*(f(t, g, style)
                         for (t, g, f) in self.tokens)))
