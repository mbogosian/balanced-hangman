#-*-python-*-=============================================================
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

import json

try:
    import unittest2 as py_unittest
except ImportError:
    import unittest as py_unittest

import twisted.internet.defer as tx_defer
import twisted.test.proto_helpers as tx_proto_helpers
import twisted.trial.unittest as tx_unittest
import twisted.web._newclient as tx_newclient
import urlparse

from bahaman.protocol.transport import (
    JsonGetterProtocol,
    BadLoginException,
    Transport,
)
from tests.protocol import *

#---- Constants ----------------------------------------------------------

__all__ = (
    'TestJsonGetter',
    'TestTransport',
)

#---- Classes ------------------------------------------------------------

#=========================================================================
class TestBalancedHangman(tx_unittest.TestCase):

    #---- Public hook methods --------------------------------------------

    #=====================================================================
    def setUp(self):
        pass

    #=====================================================================
    def tearDown(self):
        pass

    #=====================================================================
    def testShit(self):
        pass

#=========================================================================
class TestTransport(py_unittest.TestCase):

    #---- Public hook methods --------------------------------------------

    #=====================================================================
    def setUp(self):
        self.t = Transport()

    #=====================================================================
    def tearDown(self):
        del self.t

    #=====================================================================
    def testDiscover(self):
        index_url = 'https://balanced-hangman.herokuapp.com/'
        t = Transport(index_url)
        t.discover()

        me_url = urlparse.urljoin(index_url, '/me')
        self.assertEqual(t.me_url, me_url)

        prisoners_url = urlparse.urljoin(index_url, '/prisoners')
        self.assertEqual(t.prisoners_url, prisoners_url)

    #=====================================================================
    def testClone(self):
        t1 = self.t
        t2 = t1.clone()

        self.assertEqual(t1.index_url, t2.index_url)
        self.assertEqual(t1.me_url, t2.me_url)
        self.assertEqual(t1.prisoners_url, t2.prisoners_url)
        self.assertEqual(t1.credentials, t2.credentials)

        t1.credentials = TEST_CREDENTIALS
        t2 = t1.clone()
        self.assertEqual(t1.credentials, t2.credentials)

    #=====================================================================
    def testCredentials(self):
        t = self.t
        self.assertIsNone(t.credentials)

        t.credentials = TEST_CREDENTIALS
        self.assertEqual(t.credentials, TEST_CREDENTIALS)

        try:
            t.credentials = None
            self.fail()
        except ValueError:
            pass

        try:
            t.credentials = ( 1, 2, 3 )
            self.fail()
        except ValueError:
            pass

        try:
            t.credentials = "hello"
            self.fail()
        except ValueError:
            pass

    #=====================================================================
    def testMe(self):
        t = self.t

        try:
            t.httpJsonRpc(t.me_url)
        except BadLoginException:
            pass

        t.credentials = TEST_CREDENTIALS
        url, data = t.httpJsonRpc(t.me_url)
        self.assertEqual(url, t.me_url)
        self.assertIsNotNone(data)
        me_keys = set(( 'email_address', 'id', 'prisoners', 'stats', 'uri' ))
        self.assertEqual(set(data.keys()), me_keys)
        me_stats_keys = set(( 'dead', 'ended_at', 'help', 'rescued', 'started_at' ))
        self.assertEqual(set(data['stats'].keys()), me_stats_keys)
