import sys
import argparse

import pygments.styles

from pygout.format import find_formats


FORMATS = find_formats()
FORMAT_NAMES = sorted(FORMATS.keys())

STYLE_NAMES = sorted(pygments.styles.get_all_styles())


class _ListStyles(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        parser.exit(0, '\n'.join(STYLE_NAMES) + '\n')


class _ListFormats(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        parser.exit(0, '\n'.join(FORMAT_NAMES) + '\n')


def main(argv=sys.argv):
    parser = argparse.ArgumentParser(
            description='Generate color schemes in different formats')
    parser.add_argument('--help-style', nargs=0, action=_ListStyles,
                        help='Show available Pygments styles and exit')
    parser.add_argument('--help-format', nargs=0, action=_ListFormats,
                        help='Show available applications and exit')
    parser.add_argument('format', metavar='format',
                        choices=FORMAT_NAMES,
                        help='Target format')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-S', dest='pygments_style', metavar='STYLE',
                       choices=STYLE_NAMES,
                       help='Use existing Pygments style')
    group.add_argument('-f', dest='style', metavar='FILE',
                       type=argparse.FileType('r'),
                       help='Use style definition file')
    args = parser.parse_args()
    print args


if __name__ == '__main__':
    main()
