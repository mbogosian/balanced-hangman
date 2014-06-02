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

try:
    import unittest2 as py_unittest
except ImportError:
    import unittest as py_unittest

import urlparse

from bahaman.protocol.account import (
    Account,
)
from tests.protocol import *

#---- Constants ----------------------------------------------------------

__all__ = (
    'TestAccount',
)

#---- Classes ------------------------------------------------------------

#=========================================================================
class TestAccount(py_unittest.TestCase):

    #---- Public hook methods --------------------------------------------

    #=====================================================================
    def setUp(self):
        pass

    #=====================================================================
    def tearDown(self):
        pass
