#!/usr/bin/env python

#-*-mode: python; encoding: utf-8-*-======================================
"""
  TODO

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
    '/usr/share/dict/words',
    '/usr/dict/words',
)

_ALPHABET = set(( chr(ord('a') + c) for c in range(26) ))

#---- Functions ----------------------------------------------------------

#=========================================================================
def _main():
    for words_file in _WORDS_FILES:
        if os.path.isfile(words_file):
            break

        words_file = None

    q = urlparse.parse_qs(os.environ.get('QUERY_STRING', ''))
    word = q.get('word', ( None, ))[0]
    misses = q.get('misses', ( None, ))[0]
    data = {}

    if words_file is None:
        status = _STATUS_501
        data['message'] = 'no dictionary found'
    elif word is None:
        status = _STATUS_400
        data['message'] = 'missing argument: "word"'
    elif misses is None:
        status = _STATUS_400
        data['message'] = 'missing argument: "misses"'
    else:
        def lettersOrPeriods(a_word):
            for c in word:
                if c in _ALPHABET:
                    yield c
                else:
                    yield '.'

        word = word.lower()
        misses = misses.lower()
        pattern = ''.join(lettersOrPeriods(word))
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
            matches = list(set(( match.lower() for match in output.split(os.linesep) if match )))
            matches.sort()
            data['candidates'] = matches
            histogram = {}

            for match in matches:
                for c in match:
                    if c not in guesses:
                        histogram[c] = histogram.get(c, 0) + 1

            if histogram:
                max_freq = max(histogram.values())
            else:
                max_freq = 1

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

