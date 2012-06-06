from pygments.token import Token

from pygout.format import Format


PREAMBLE = """
set background={background}
hi clear
if exists("syntax_on")
    syntax reset
endif
let g:colors_name="{name}"

"""

TOKEN_MAP = [
    (Token, ['Normal']),
    (Token.Name, ['Identifier', 'Function', 'Label']),
    (Token.Name.Constant, ['Constant']),
    (Token.Number, ['Number']),
    (Token.Number.Float, ['Float']),
    (Token.String, ['String']),
]


class Vim(Format):
    # TODO: support cterm, not just gui
    def write(self, stream, style):
        # TODO: detect light/dark background
        # TODO: support style name
        stream.write(PREAMBLE.format(background='light', name='pygout'))

        stream.write('hi Normal guibg={}\n\n'.format(style.background_color))

        for t, vimgroups in TOKEN_MAP:
            tokenstyle = style.find_style_for_token(t)

            groupstyle = {
                'guifg': None,
                'guibg': None,
                'guisp': None,
                'gui': [k for k in ('bold', 'italic', 'underline')
                        if tokenstyle[k] is True],
            }

            if tokenstyle['color'] is not None:
                groupstyle['guifg'] = '#' + tokenstyle['color']

            if tokenstyle['bgcolor'] is not None:
                groupstyle['guibg'] = '#' + tokenstyle['bgcolor']

            if tokenstyle['border'] is not None:
                groupstyle['guisp'] = '#' + tokenstyle['border']
                groupstyle['gui'].append('undercurl')

            if len(groupstyle['gui']) > 0:
                groupstyle['gui'] = ','.join(groupstyle['gui'])
            else:
                groupstyle['gui'] = None

            stylestring = ' '.join('{}={}'.format(k, v)
                                   for k, v in groupstyle.iteritems() if v)

            if stylestring == '':
                continue

            stream.write('" {}\n'.format(t))

            for group in vimgroups:
                stream.write('hi {} {}\n'.format(group, stylestring))

            stream.write('\n')
