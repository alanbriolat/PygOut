import sys
import argparse

import pygments.styles

from pygout.application import find_apps


class _ListStyles(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        styles = sorted(pygments.styles.get_all_styles())
        parser.exit(0, '\n'.join(styles) + '\n')


class _ListApps(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        apps = sorted(find_apps().keys())
        parser.exit(0, '\n'.join(apps) + '\n')


def main(argv=sys.argv):
    parser = argparse.ArgumentParser(
            description='Generate editor color schemes')
    parser.add_argument('--help-styles', nargs=0, action=_ListStyles,
                        help='Show available Pygments styles and exit')
    parser.add_argument('--help-apps', nargs=0, action=_ListApps,
                        help='Show available applications and exit')
    parser.add_argument('application', choices=find_apps(), metavar='app',
                        help='Target application')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-S', dest='pygments_style', metavar='STYLE',
                       choices=sorted(pygments.styles.get_all_styles()),
                       help='Use existing Pygments style')
    group.add_argument('-f', dest='style', metavar='FILE',
                       type=argparse.FileType('r'),
                       choices=sorted(find_apps().keys()),
                       help='Use style definition file')
    args = parser.parse_args()
    print args
