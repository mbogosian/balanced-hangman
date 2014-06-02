#-*-mode: python; encoding: utf-8-*-======================================
"""
  Copyright (c) 2014 Matt Bogosian <mtb19@columbia.edu>.

  Please see the LICENSE (or LICENSE.txt) file which accompanied this
  software for rights and restrictions governing its use. If such a file
  did not accompany this software, then please contact the author before
  viewing or using this software in any capacity.
"""
#=========================================================================

#---- Imports ------------------------------------------------------------

from __future__ import absolute_import, division, print_function, unicode_literals

import twisted.internet.reactor
import time

#---- Constants ----------------------------------------------------------

__all__ = ()

#---- Classes ------------------------------------------------------------

#=========================================================================
class Timer(object):
    """
    TODO
    """

    #---- Constructors ---------------------------------------------------

    #=====================================================================
    def __init__(self, a_func, a_period, a_reactor = None):
        """
        Constructor.

        a_func is a callable. a_period is the period in seconds at which
        to call a_func. a_reactor, if given, is the reactor used for
        triggering the callback.
        """
        object.__init__(self)
        self.__period = a_period
        self.__func = a_func
        self.__next = None
        self.__done = False

        if a_reactor is not None:
            self.__reactor = a_reactor
        else:
            self.__reactor = twisted.internet.reactor

    #---- Public properties ----------------------------------------------

    #=====================================================================
    def func():
        def fget(self):
            return self.__func

        fset = None
        fdel = None
        doc = """
        The function to call every self.period seconds.
        """

        return locals()

    func = property(**func())

    #=====================================================================
    def period():
        def fget(self):
            return self.__period

        fset = None
        fdel = None
        doc = """
        The period at which to call self.func.
        """

        return locals()

    period = property(**period())

    #---- Public hook methods --------------------------------------------

    #=====================================================================
    def __call__(self, *a_args, **a_kwargs):
        """
        TODO
        """
        self.func(*a_args, **a_kwargs)

    #---- Public methods -------------------------------------------------

    #=====================================================================
    def go(self, a_next = None):
        """
        TODO
        """
        now = time.time()

        if a_next is not None:
            self.__next = a_next
        elif self.__next is None:
            self.__next = now + self.period
        else:
            ( now - self.__next ) // a_period
            self.__next += self.period

        self.__reactor.callLater(self.__next - time.time(), self.__trigger)

        return self

    #=====================================================================
    def stop(self):
        """
        TODO
        """
        self.__done = True

    #---- Private methods ------------------------------------------------

    #=====================================================================
    def __trigger(self):
        """
        TODO
        """
        if self.__done:
            return

        self()
        self.go()
