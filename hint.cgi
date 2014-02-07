#!/usr/bin/env python

#-*-mode: python; encoding: utf-8-*-======================================
"""
  CGI script to take a word with one or more wildcards (non-letters; e.g.,
  'sh*tty' or 'a..hole')* and a string of zero or more letters that are
  necessarily not part of the completed word, and return a JSON object
  containing list of candidate words that match the pattern as well as a
  'frequency' of letters, where frequency is scaled between 0.0 and 1.0
  and is reflective of the number of candidate words in which the letter
  appears.

  * From 'shotty' or 'armhole'. Get your mind out of the gutter!

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
import sys
import unittest
import urlparse

#---- Constants ----------------------------------------------------------

__all__ = ()

_STATUS_200 = '200 Success'
_STATUS_400 = '400 Bad Request'
_STATUS_500 = '500 Internal Server Error'
_STATUS_501 = '501 Not Implemented'

_WORDS_PATHS = (
    '_/words',
    '/usr/share/dict/words',
    '/usr/dict/words',
)

_ALPHABET = set(( chr(ord('a') + c) for c in range(26) ))

#---- Classes ------------------------------------------------------------

#=========================================================================
class HintError(BaseException):
    """
    Class to implement an execution error with an HTTP status code and
    descriptive error message.
    """

#=========================================================================
class TestEvalQuery(unittest.TestCase):

    #---- Public hook methods --------------------------------------------

    #=====================================================================
    def testAllMisses(self):
        import urllib

        qs = urllib.urlencode(( ( 'word', '************' ), ( 'misses', 'zxqj' ) ))
        regex, guesses = evalQuery(qs)
        self.assertEqual(regex, r'^[^jqxz][^jqxz][^jqxz][^jqxz][^jqxz][^jqxz][^jqxz][^jqxz][^jqxz][^jqxz][^jqxz][^jqxz]$')
        self.assertEqual(guesses, set('jqxz'))

    #=====================================================================
    def testCompleteWord(self):
        import urllib

        qs = urllib.urlencode(( ( 'word', 'armhole' ), ( 'misses', 's' ) ))
        regex, guesses = evalQuery(qs)
        self.assertEqual(regex, r'^armhole$')
        self.assertEqual(guesses, set('aehlmors'))

        qs = urllib.urlencode(( ( 'word', 'shotty' ), ( 'misses', 'i' ) ))
        regex, guesses = evalQuery(qs)
        self.assertEqual(regex, r'^shotty$')
        self.assertEqual(guesses, set('hiosty'))

    #=====================================================================
    def testFunkyMisses(self):
        import urllib

        qs = urllib.urlencode(( ( 'word', '********' ), ( 'misses', b' 1 2 # $ \xc3\xa0\n\t\b\r' ) ))
        regex, guesses = evalQuery(qs)
        self.assertEqual(regex, r'^........$')
        self.assertEqual(guesses, set(''))

        qs = urllib.urlencode(( ( 'word', '*ad*' ), ( 'misses', '=-=-=-= V.v.V =-=-=-=' ) ))
        regex, guesses = evalQuery(qs)
        self.assertEqual(regex, r'^[^adv]ad[^adv]$')
        self.assertEqual(guesses, set('adv'))

    #=====================================================================
    def testNoGuesses(self):
        import urllib

        qs = urllib.urlencode(( ( 'word', '*****' ), ))
        regex, guesses = evalQuery(qs)
        self.assertEqual(regex, r'^.....$')
        self.assertEqual(guesses, set(''))

        qs = urllib.urlencode(( ( 'word', '********' ), ( 'misses', '' ) ))
        regex, guesses = evalQuery(qs)
        self.assertEqual(regex, r'^........$')
        self.assertEqual(guesses, set(''))

    #=====================================================================
    def testNoMisses(self):
        import urllib

        qs = urllib.urlencode(( ( 'word', '***a*i' ), ))
        regex, guesses = evalQuery(qs)
        self.assertEqual(regex, r'^[^ai][^ai][^ai]a[^ai]i$')
        self.assertEqual(guesses, set('ai'))

        qs = urllib.urlencode(( ( 'word', 'fee***g' ), ( 'misses', '' ) ))
        regex, guesses = evalQuery(qs)
        self.assertEqual(regex, r'^fee[^efg][^efg][^efg]g$')
        self.assertEqual(guesses, set('efg'))

        qs = urllib.urlencode(( ( 'word', 'u**u*************' ), ))
        regex, guesses = evalQuery(qs)
        self.assertEqual(regex, r'^u[^u][^u]u[^u][^u][^u][^u][^u][^u][^u][^u][^u][^u][^u][^u][^u]$')
        self.assertEqual(guesses, set('u'))

        qs = urllib.urlencode(( ( 'word', 'u**u*************' ), ( 'misses', 'q' ) ))
        regex, guesses = evalQuery(qs)
        self.assertEqual(regex, r'^u[^qu][^qu]u[^qu][^qu][^qu][^qu][^qu][^qu][^qu][^qu][^qu][^qu][^qu][^qu][^qu]$')
        self.assertEqual(guesses, set('qu'))

    #=====================================================================
    def testNoWord(self):
        import urllib

        try:
            evalQuery('')
        except HintError, e:
            self.assertEqual(e.args[0], _STATUS_400)

        qs = urllib.urlencode(( ( 'word', '' ), ))

        try:
            evalQuery(qs)
        except HintError, e:
            self.assertEqual(e.args[0], _STATUS_400)

    #=====================================================================
    def testRepldots(self):
        phrase = "I can't believe it's not butter! Zowy!"
        self.assertEqual(''.join(repldots("I can't believe it's not butter! Zowy!")), '..can.t.believe.it.s.not.butter...owy.')
        self.assertEqual(''.join(repldots(b'bl\xc3\xa1h\n\t\n')), 'bl..h...')
        self.assertEqual(''.join(repldots('\u2665 \u2665 \u2665 V.v.V \u2665 \u2665 \u2665')), '........v........')

#=========================================================================
class TestFindMatches(unittest.TestCase):

    #---- Public constants -----------------------------------------------

    WORDS_PATH = os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), '_', 'test_words')

    #---- Public hook methods --------------------------------------------

    #=====================================================================
    def testAllMatches(self):
        import operator

        candidates, frequencies = findMatches(TestFindMatches.WORDS_PATH, r'^....................$', set(''))
        self.assertEqual(len(set(candidates.split())), 198)
        self.assertEqual(''.join(( i[0] for i in sorted(frequencies.items(), key = operator.itemgetter(1)) )), 'kqjxfzvbdgumyhspncletriao')

    #=====================================================================
    def testBadExec(self):
        try:
            findMatches(TestFindMatches.WORDS_PATH, b'-\t', set(''))
        except HintError, e:
            self.assertEqual(e.args[0], _STATUS_500)

    #=====================================================================
    def testNoMatches(self):
        candidates, frequencies = findMatches(TestFindMatches.WORDS_PATH, r'^.$', set(''))
        self.assertEqual(len(set(candidates.split())), 0)
        self.assertEqual(len(frequencies), 0)

    #=====================================================================
    def testSomeMatches(self):
        import urllib

        qs = urllib.urlencode(( ( 'word', 'u**u*************' ), ))
        regex, guesses = evalQuery(qs)
        candidates, frequencies = findMatches(TestFindMatches.WORDS_PATH, regex, guesses)
        self.assertEqual(len(set(candidates.split())), 10)
        self.assertTrue('unquestionability' in candidates)
        self.assertEqual(set(( i for i in frequencies if frequencies[i] == 1.0 )), set('en'))
        self.assertEqual(set(( i for i in frequencies if frequencies[i] == 0.5 )), set('o'))

        qs = urllib.urlencode(( ( 'word', 'u**u*************' ), ( 'misses', 'q' ) ))
        regex, guesses = evalQuery(qs)
        candidates, frequencies = findMatches(TestFindMatches.WORDS_PATH, regex, guesses)
        self.assertEqual(len(set(candidates.split())), 8)
        self.assertTrue('unquestionability' not in candidates)
        self.assertEqual(set(( i for i in frequencies if frequencies[i] == 1.0 )), set('en'))
        self.assertEqual(set(( i for i in frequencies if frequencies[i] == 0.5 )), set('pr'))

#---- Functions ----------------------------------------------------------

#=========================================================================
def findMatches(a_words_path, a_regex, a_guesses):
    cmd = ( 'egrep', '-i', a_regex, a_words_path )
    egrep_proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, close_fds = True)
    output = egrep_proc.communicate()[0]

    if egrep_proc.returncode not in ( 0, 1 ):
        raise HintError(_STATUS_500, os.linesep.join(( ' '.join(cmd), output )))

    matches = list(set(filterMatches(output)))
    matches.sort()
    histogram = {}

    for match in matches:
        try:
            match = unicode(match)
        except UnicodeDecodeError:
            continue

        for c in set(match):
            if c not in a_guesses:
                histogram[c] = histogram.get(c, 0) + 1

    if histogram:
        max_freq = max(histogram.values())
    else:
        max_freq = 1

    candidates = ' '.join(matches)
    frequencies = dict(( ( k, v / max_freq ) for k, v in histogram.iteritems() ))

    return candidates, frequencies

#=========================================================================
def filterMatches(a_output):
    """
    Generator for splitting an input string by lines and outputting only
    those lines that are nonempty and unambiguously encodable as unicode.

    >>> list(filterMatches(b' ThE\\n    qUiCk   \\n\\n\\n  \\n\\n BrOwN \\nfOx\\n  Is \\nL\\xc3\\xa1Zy\\n \\n \\n'))
    [u'the', u'quick', u'brown', u'fox', u'is']
    """
    for match in a_output.split(os.linesep):
        # Filter out non ascii words
        try:
            match = unicode(match)
        except UnicodeDecodeError:
            continue

        # Filter out possessives
        if match.endswith("'s"):
            continue

        match = match.strip().lower()

        # Filter out blank lines
        if match:
            yield match

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
    for c in a_word:
        if c in _ALPHABET:
            yield c
        else:
            yield '.'

#=========================================================================
def evalQuery(a_qs):
    """
    Extract and return ( regex, guesses ) from the 'words' and optional
    'misses' parameters in the a_qs.
    """
    q = urlparse.parse_qs(a_qs, keep_blank_values = True)
    status = None
    msg = None
    word = q.get('word', ( None, ))[0]
    misses = q.get('misses', ( '', ))[0]

    if word is None:
        raise HintError(_STATUS_400, 'missing parameter: "word"')
    elif len(word) == 0:
        raise HintError(_STATUS_400, '"word" parameter must have at least one character')

    regex = r''.join(repldots(word.lower()))
    guesses = r''.join(sorted(_ALPHABET.intersection(word + misses.lower())))

    if guesses:
        blank = r'[^%s]' % guesses
        regex = regex.replace(r'.', blank)

    regex = r'^%s$' % regex

    return regex, set(guesses)

#=========================================================================
def _main():
    for words_path in _WORDS_PATHS:
        if os.path.isfile(words_path):
            break

        words_path = None

    data = {}
    status = _STATUS_200

    try:
        if words_path is None:
            raise HintError(_STATUS_501, 'no dictionary found')

        regex, guesses = evalQuery(os.environ.get('QUERY_STRING', ''))
        data['candidates'], data['frequencies'] = findMatches(words_path, regex, guesses)
        data['words_path'] = words_path
    except HintError, e:
        status, data['message'] = e.args
    except:
        status = _STATUS_500
        data['message'] = 'an unexpected error occurred'

    print('Content-Type: application/json')
    print('Status: %s' % status, end = '\n\n')
    print(json.dumps(data))

#=========================================================================
def _test():
    import doctest

    finder = doctest.DocTestFinder(exclude_empty = False)
    suite = doctest.DocTestSuite(test_finder = finder)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    result = unittest.TextTestRunner().run(suite)

    if not result.wasSuccessful():
        sys.exit(1)

#---- Initialization -----------------------------------------------------

if __name__ == '__main__':
    try:
        import argparse
        arg_parser = argparse.ArgumentParser(description = b'CGI hint engine for BaHaMan', version = b'%(prog)s 0.1.0a1')
    except:
        # Backward compatibility for <= 2.6
        import optparse
        arg_parser = optparse.OptionParser(description = b'CGI hint engine for BaHaMan', version = os.path.basename(sys.argv[0]) + b' 0.1.0a1')
        arg_parser.add_argument = arg_parser.add_option

    arg_parser.add_argument(b'--test', action = b'store_true', default = False, help = b'performs unit tests instead of hints')
    arg_parser.add_argument(b'--no-test', action = b'store_false', help = b'deactivates test mode (default)', dest = b'test')
    args = arg_parser.parse_args()

    if type(args) in ( list, tuple ):
        # Backward compatibility for <= 2.6
        args = args[0]

    if args.test:
        _test()
    else:
        _main()
