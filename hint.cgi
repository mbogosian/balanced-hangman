#!/usr/bin/env python

#-*-mode: python; encoding: utf-8-*-======================================
"""
  CGI script to take a word with one or more wildcards (non-letters; e.g.,
  "sh*tty" or "a..hole")* and a string of zero or more letters that are
  necessarily not part of the completed word, and return a JSON object
  containing list of candidate words that match the pattern as well as a
  "frequency" of letters, where frequency is scaled between 0.0 and 1.0
  and is reflective of the number of candidate words in which the letter
  appears.

  * From "shotty" or "armhole". Get your mind out of the gutter!

  Copyright (c) 2014 Matt Bogosian <mtb19@columbia.edu>.

  Please see the LICENSE (or LICENSE.txt) file which accompanied this
  software for rights and restrictions governing its use. If such a file
  did not accompany this software, then please contact the author before
  viewing or using this software in any capacity.
"""
#=========================================================================

#---- Imports ------------------------------------------------------------

from __future__ import absolute_import, division, print_function, unicode_literals, with_statement

import json
import operator
import os
import subprocess
import urlparse

#---- Constants ----------------------------------------------------------

__all__ = ()

_STATUS_200 = '200 Success'
_STATUS_400 = '400 Bad Request'
_STATUS_500 = '500 Internal Server Error'
_STATUS_501 = '501 Not Implemented'

_WORDS_FILES = (
    'words',
    '/usr/share/dict/words',
    '/usr/dict/words',
)

_ALPHABET = set(( chr(ord('a') + c) for c in range(26) ))

#---- Functions ----------------------------------------------------------

#=========================================================================
def filterMatches(a_output):
    """
    Generator for splitting an input string by lines and outputting only
    those lines that are nonempty and unambiguously encodable as unicode.

    >>> list(filterMatches(b' ThE\n    qUiCk   \n\n\n  \n\n BrOwN \nfOx\n  Is \nL\xc3\xa1Zy\n \n \n'))
    [u'the', u'quick', u'brown', u'fox', u'is']
    """
    for match in output.split(os.linesep):
        # Filter out blank lines
        if not match:
            continue

        # Filter out non ascii words
        try:
            match = unicode(match)
        except UnicodeDecodeError:
            continue

        # Filter out possessives
        if not match.endswith("'s"):
            yield match.strip().lower()

#=========================================================================
def repldots(a_word):
    """
    Generator for converting the non-letter characters of a_word to
    periods.

    >>> ''.join(repldots('a1b2c3d4e'))
    u'a.b.c.d.e'
    >>> ''.join(repldots('    a*.*.*z    '))
    u'....a.....z....'
    """
    for c in word:
        if c in _ALPHABET:
            yield c
        else:
            yield '.'

#=========================================================================
def _main():
    for words_file in _WORDS_FILES:
        if os.path.isfile(words_file):
            break

        words_file = None

    q = urlparse.parse_qs(os.environ.get('QUERY_STRING', ''), keep_blank_values = True)
    word = q.get('word', ( None, ))[0]
    misses = q.get('misses', ( '', ))[0]
    data = {}

    if words_file is None:
        status = _STATUS_501
        data['message'] = 'no dictionary found'
    elif word is None:
        status = _STATUS_400
        data['message'] = 'missing parameter: "word"'
    elif len(word) == 0:
        status = _STATUS_400
        data['message'] = '"word" parameter must have at least one character'
    else:
        word = word.lower()
        misses = misses.lower()
        pattern = ''.join(repldots(word))
        guesses = ''.join(_ALPHABET.intersection(word + misses))

        if guesses:
            blank = '[^%s]' % guesses
            pattern = pattern.replace('.', blank)

        pattern = '^%s$' % pattern
        cmd = ( 'egrep', '-i', pattern, words_file )
        egrep_proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, close_fds = True)
        output = egrep_proc.communicate()[0]

        if egrep_proc.returncode in ( 0, 1 ):
            status = _STATUS_200
            matches = list(set(filterMatches(output)))
            matches.sort()
            histogram = {}

            for match in matches:
                try:
                    match = unicode(match)
                except UnicodeDecodeError:
                    continue

                for c in set(match):
                    if c not in guesses:
                        histogram[c] = histogram.get(c, 0) + 1

            if histogram:
                max_freq = max(histogram.values())
            else:
                max_freq = 1

            data['candidates'] = ' '.join(matches)
            data['frequencies'] = dict(( ( k, v / max_freq ) for k, v in histogram.iteritems() ))
        else:
            status = _STATUS_500
            data['message'] = os.linesep.join(( ' '.join(cmd), output ))

    print('Content-Type: application/json')
    print('Status: %s' % status, end = '\n\n')
    print(json.dumps(data))

#---- Initialization -----------------------------------------------------

if __name__ == '__main__':
    _main()

