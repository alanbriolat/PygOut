import sys
from setuptools import setup, find_packages

import pygout


readme = open('README.rst', 'r').read()
DESCRIPTION = readme.split('\n')[0]
LONG_DESCRIPTION = readme

INSTALL_REQUIRES = [
        'Pygments == 1.5',
]

if sys.version_info < (2, 7):
    INSTALL_REQUIRES.append('argparse >= 1.1')

if sys.version_info < (3, 0):
    INSTALL_REQUIRES.append('configparser >= 3.0')

setup(
    name = 'PygOut',
    version = pygout.__version__,
    url = 'http://github.com/alanbriolat/PygOut',
    license = 'BSD License',
    author = 'Alan Briolat, Helen M. Gray',
    description = DESCRIPTION,
    long_descrption = LONG_DESCRIPTION,
    packages = find_packages(),
    platforms = 'any',
    install_requires = INSTALL_REQUIRES,
    entry_points = {
        'console_scripts': ['pygout = pygout.cmdline:main'],
    },
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)
