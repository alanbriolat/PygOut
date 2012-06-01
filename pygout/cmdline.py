import sys
import argparse

import pygments.styles

from pygout.format import find_formats


class _ListStyles(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        styles = sorted(pygments.styles.get_all_styles())
        parser.exit(0, '\n'.join(styles) + '\n')


class _ListFormats(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        formats = sorted(find_formats().keys())
        parser.exit(0, '\n'.join(formats) + '\n')


def main(argv=sys.argv):
    parser = argparse.ArgumentParser(
            description='Generate color schemes in different formats')
    parser.add_argument('--help-style', nargs=0, action=_ListStyles,
                        help='Show available Pygments styles and exit')
    parser.add_argument('--help-format', nargs=0, action=_ListFormats,
                        help='Show available applications and exit')
    parser.add_argument('format', metavar='format',
                        choices=sorted(find_formats().keys()),
                        help='Target format')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-S', dest='pygments_style', metavar='STYLE',
                       choices=sorted(pygments.styles.get_all_styles()),
                       help='Use existing Pygments style')
    group.add_argument('-f', dest='style', metavar='FILE',
                       type=argparse.FileType('r'),
                       help='Use style definition file')
    args = parser.parse_args()
    print args


if __name__ == '__main__':
    main()
