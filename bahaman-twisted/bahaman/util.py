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

import dateutil.parser
import urwid

#---- Constants ----------------------------------------------------------

__all__ = ()

# Singleton for use with the "is" comparator as a special value (e.g., for
# indicating "no value", "stop", etc.) where None or another builtin
# constant is inappropriate; like None, this will evaluate to False in
# boolean expressions
SENTINEL = type(b'Sentinel', ( object, ), { '__nonzero__': lambda self: False })()

SIG_CONFIG_UPDATED = 'config_updated'
"""
Signal handlers should have the signature (a_updated_vals).
"""

SIG_REQ_LOGIN = 'req_login'
"""
Signal handlers should have the signature (a_base_uri, a_auth = None),
where a_base_uri is the base URI for the login, and a_auth, if provided,
is in the form ( username, password ).
"""

SIG_REQ_NEW_ACCT = 'req_new_acct'
"""
Signal handlers should have the signature (a_base_uri, a_auth), where
a_base_uri is the base URI for the login, and a_auth is in the form (
username, password ).
"""

SIG_REQ_PRISONERS = 'req_prisoners'
"""
Signal handlers should have the signature (a_auth), where a_auth is in the
form ( username, password ).
"""

SIG_RSP_LOGIN = 'rsp_login'
"""
Signal handlers should have the signature (a_base_uri, a_auth,
a_err = None), where a_base_uri was the base URI tested, a_auth was the
authorization used (if any), and a_err, if provided, is any error
encountered (no error means success).
"""

SIG_RSP_NEW_ACCT = 'rsp_new_acct'
"""
Signal handlers should have the signature (a_auth, a_err = None), where
a_auth was the authorization used, and a_err, if provided, is any error
encountered (no error means success).
"""

SIG_RSP_PRISONERS = 'rsp_prisoners'
"""
Signal handlers should have the signature (a_auth, a_prisoners, a_err =
None), where a_auth was the authorization used, a_prisoners is a dict of
Games indexed by ID, and a_err, if provided, is any error encountered (no
error means success).
"""

#---- Classes ------------------------------------------------------------

#=========================================================================
class AuthenticationException(Exception):
    """
    Authentication error base class.
    """

#=========================================================================
class ProbablyBadPasswordException(AuthenticationException):
    """
    See "Authentication Oddities" section in README.rst.
    """

#=========================================================================
class ProbablyBadUsernameException(AuthenticationException):
    """
    See "Authentication Oddities" section in README.rst.
    """

#=========================================================================
class ProbablyNeedLoginException(AuthenticationException):
    """
    See "Authentication Oddities" section in README.rst.
    """

#=========================================================================
class ProtocolException(Exception):
    """
    An unexpected or insufficient response was issued by the server.
    """

#=========================================================================
class ControllerBase(object):
    """
    TODO
    """

    #---- Constructors ---------------------------------------------------

    #=====================================================================
    def __init__(self):
        """
        Constructor.
        """
        object.__init__(self)

    #---- Public methods -------------------------------------------------

    #=====================================================================
    def connectObject(self, a_obj, a_sig_name):
        """
        TODO
        """
        urwid.connect_signal(a_obj, a_sig_name, getattr(self, 'sig_' + a_sig_name))

#=========================================================================
class Game(object):
    """
    TODO
    """

    #---- Constructors ---------------------------------------------------

    #=====================================================================
    def __init__(self, a_game_state):
        """
        Constructor.
        """
        self.__parser = dateutil.parser.parser()
        self.__state = {}
        self.state = a_game_state

    #---- Public properties ----------------------------------------------

    #=====================================================================
    def state():
        def fget(self):
            return self.__state

        def fset(self, a_game_state):
            self.__state.update(a_game_state)

            if a_game_state.get('imprisoned_at', SENTINEL) is not SENTINEL:
                self.__state['imprisoned_at'] = self.__parser.parse(self.__state['imprisoned_at'])

            if a_game_state.get('hits', SENTINEL) is not SENTINEL:
                self.__state['hits'] = set(self.__state['hits'])

            if a_game_state.get('misses', SENTINEL) is not SENTINEL:
                self.__state['misses'] = set(self.__state['misses'])

        fdel = None
        doc = None

        return locals()

    state = property(**state())

    #---- Public hook methods --------------------------------------------

    #=====================================================================
    def __cmp__(self, a_obj):
        if not isinstance(a_obj, Game):
            return 1

        our_state = self.__state
        their_state = a_obj.__state

        if our_state['state'] != their_state['state']:
            if our_state['state'] == 'help':
                return -1

            if their_state['state'] == 'help':
                return 1

        return -our_state['imprisoned_at']._cmp(their_state['imprisoned_at'])

#---- Functions ----------------------------------------------------------

#=========================================================================
def getLoop():
    try:
        return _LOOP
    except NameError:
        raise ValueError('no main loop yet; must call bahaman.main.main() first')

#=========================================================================
def getReactor():
    try:
        return _REACTOR
    except NameError:
        raise ValueError('no main loop yet; must call bahaman.main.main() first')

#=========================================================================
def noop(*a_args, **a_kwargs):
    pass

#=========================================================================
def quit():
    raise urwid.ExitMainLoop()

#=========================================================================
# =-=-=-=- TODO: DELETE BELOW THIS LINE -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#=========================================================================

#---- Classes ------------------------------------------------------------

# #=========================================================================
# class Signals(urwid.Signals):
#     """
#     Class to eliminate the register() reqirement for sending/receiving
#     signals. Urwid requires one to register a class (cls) with a signal
#     via the register() method. Then it requires one to register an
#     emitting object (obj) with that signal and a callback via the
#     connect() method before sending signals. Note that cls has to match
#     *exactly* obj.__class__ or connect() will throw an exception (it's not
#     enough that isinstance(obj, cls) is True). This might have some
#     purpose, but I can't figure out what it is. In any event, it is too
#     cumbersome for this application, so I'm getting rid of the requirement
#     to call the register() method at all by way of this monkey patch. Note
#     that one avoid the urwid.*_signal() functions and urwid.Signal.
#     Instead either instantiate this class, or use the appropriate method
#     from bahaman.controller.signals.*().
#     """

#     #---- Constructors ---------------------------------------------------

#     #=====================================================================
#     def __init__(self):
#         """
#         Constructor.
#         """
#         urwid.Signals.__init__(self)
#         # See the use of self._supported in urwid.Signals.__init__(),
#         # urwid.Signals.connect(), and urwid.Signals.register() for
#         # details
#         self._supported = Signals._GetMonkeyPatch()

#     #---- Private inner classes ------------------------------------------

#     #=====================================================================
#     class _ContainsMonkeyPatch(object):

#         #---- Public hook methods ----------------------------------------

#         #=================================================================
#         def __contains__(self, a_key):
#             return True

#     #=====================================================================
#     class _GetMonkeyPatch(dict):

#         #---- Constructors -----------------------------------------------

#         #=================================================================
#         def __init__(self, *a_args, **a_kwargs):
#             """
#             Constructor.
#             """
#             dict.__init__(self)

#         #---- Public hook methods ----------------------------------------

#         #=================================================================
#         def __setitem__(self, a_key, a_val):
#             pass

#         #=================================================================
#         def get(self, a_key, a_default):
#             return Signals._ContainsMonkeyPatch()

#         #=================================================================
#         def setdefault(self, a_key, a_default = None):
#             pass

#         #=================================================================
#         def update(self, *a_args, **a_kwargs):
#             pass

#---- Globals ------------------------------------------------------------

# signals = Signals()
