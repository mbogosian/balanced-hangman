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

import urwid

from bahaman.util import (
    ControllerBase,
    Game,
    SIG_CONFIG_UPDATED,
    SIG_REQ_LOGIN,
    SIG_REQ_NEW_ACCT,
    SIG_REQ_PRISONERS,
    SIG_RSP_LOGIN,
    SIG_RSP_NEW_ACCT,
    SIG_RSP_PRISONERS,
)

#---- Constants ----------------------------------------------------------

__all__ = ()

#---- Classes ------------------------------------------------------------

#=========================================================================
class Controller(ControllerBase):
    """
    TODO
    """

    #---- Constructors ---------------------------------------------------

    #=====================================================================
    def __init__(self, a_config, a_client, a_screen):
        """
        Constructor.

        a_config is the ConfigParser. a_screen is the Screen.
        """
        ControllerBase.__init__(self)
        self.__config = a_config
        self.__client = a_client
        self.__screen = a_screen

    #---- Public hook methods --------------------------------------------

    #=====================================================================
    def sig_config_updated(self, a_updated_vals):
        changed = False

        for k, new_v in a_updated_vals.items():
            try:
                section, option = k.split(':', 1)
            except ValueError:
                section, option = self.__config.BASIC, k

            old_v = self.__config.get(section, option)

            if old_v != new_v:
                changed = True

            self.__config.set(section, option, new_v)

        if changed:
            self.__config.writeReplace()

        return True

    #=====================================================================
    def sig_req_login(self, a_base_uri, a_auth = None):
        d = self.__client.testAndSetUri(a_base_uri, a_auth)

        return d

    #=====================================================================
    def sig_req_new_acct(self, a_base_uri, a_auth):
        d = self.__client.newAccount(a_base_uri, a_auth)

        return d

    #=====================================================================
    def sig_req_prisoners(self, a_auth):
        d = self.__client.prisoners(a_auth)

        return d

    #=====================================================================
    def sig_rsp_login(self, a_base_uri, a_auth, a_err = None):
        if a_err is None:
            self.__screen.loginSuccess(a_base_uri, a_auth)
        else:
            self.__screen.loginFailure(a_err)

    #=====================================================================
    def sig_rsp_new_acct(self, a_auth, a_err = None):
        if a_err is None:
            self.__screen.newAccountSuccess(a_auth)
        else:
            self.__screen.newAccountFailure(a_err)

    #=====================================================================
    def sig_rsp_prisoners(self, a_auth, a_prisoners, a_err = None):
        if a_err is None:
            prisoners = [ Game(i) for i in a_prisoners.values() ]
            prisoners.sort()
            self.__screen.updatePrisoners(a_auth, prisoners)

    #---- Public hook methods --------------------------------------------

    #=====================================================================
    def wireItUpAndGo(self, a_first_run):
        self.connectObject(self.__screen, SIG_CONFIG_UPDATED)
        self.connectObject(self.__screen, SIG_REQ_LOGIN)
        self.connectObject(self.__screen, SIG_REQ_NEW_ACCT)
        self.connectObject(self.__screen, SIG_REQ_PRISONERS)
        self.connectObject(self.__client, SIG_RSP_LOGIN)
        self.connectObject(self.__client, SIG_RSP_NEW_ACCT)
        self.connectObject(self.__client, SIG_RSP_PRISONERS)
        self.__screen.start(self.__config, a_first_run)
