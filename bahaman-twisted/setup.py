#!/usr/bin/env python

#-*-mode: python; encoding: utf-8-*-======================================
"""
  Copyright (c) 2013 Matt Bogosian <mtb19@columbia.edu>.

  Please see the LICENSE (or LICENSE.txt) file which accompanied this
  software for rights and restrictions governing its use. If such a file
  did not accompany this software, then please contact the author before
  viewing or using this software in any capacity.
"""
#=========================================================================

#---- Imports ------------------------------------------------------------

from __future__ import absolute_import, division, print_function, unicode_literals

# See this e-mail thread:
# <http://www.eby-sarna.com/pipermail/peak/2010-May/003348.html>
import multiprocessing, logging #@UnusedImport
import os
import setuptools
import sys

#---- Constants ----------------------------------------------------------

__all__ = ()

_HERE = os.path.realpath(os.path.dirname(__file__))
_LONG_DESC = []
_README = open(os.path.join(_HERE, 'README.rst')).read()
_LONG_DESC.append(_README)
del _HERE, _README
_LONG_DESC = (os.linesep * 2).join(_LONG_DESC).strip()

_SETUP_ARGS = {
    'name'               : 'bahaman',
    'version'            : '0.1.0a1',
    'author'             : 'Matt Bogosian',
    'author_email'       : 'mtb19@columbia.edu',
    'url'                : '',
    'license'            : 'MIT License',
    'description'        : "Python implementation for Balanced's Hangman challenge and reference client.",
    'long_description'   : _LONG_DESC,

    # From <http://pypi.python.org/pypi?%3Aaction=list_classifiers>
    'classifiers'        : (
        'Development Status :: 3 - Alpha',
        'Environment :: Console :: Curses',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Games/Entertainment :: Puzzle Games',
        'Topic :: Education',
        'Topic :: Other/Nonlisted Topic',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),

    'namespace_packages' : ( 'bahaman', ),
    'packages'           : [ 'bahaman.%s' % i for i in setuptools.find_packages('bahaman') ],
    'install_requires'   : ( 'pyOpenSSL', 'treq', 'twisted', 'urwid', ),
    # We'll get this to work later; right now, we run tests with trial
    'setup_requires'     : ( 'pytest-runner >= 1.0, < 2.0dev' ),
    'test_suite'         : 'tests',
    'tests_require'      : ( 'pytest-twisted >= 1.0, < 2.0dev' ),
}

#---- Initialization -----------------------------------------------------

if __name__ == '__main__':
    setuptools.setup(**_SETUP_ARGS)
