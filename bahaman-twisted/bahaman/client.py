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

import BeautifulSoup
import functools
import json
import re
import treq
import twisted.python.failure
import urlparse
import urwid

from bahaman.util import (
    AuthenticationException,
    ControllerBase,
    ProbablyBadPasswordException,
    ProbablyBadUsernameException,
    ProbablyNeedLoginException,
    ProtocolException,
    SENTINEL,
    SIG_RSP_LOGIN,
    SIG_RSP_NEW_ACCT,
    SIG_RSP_PRISONERS,
    getReactor,
)

#---- Constants ----------------------------------------------------------

__all__ = ()

_SPACES = re.compile('\s\s+')

#---- Classes ------------------------------------------------------------

#=========================================================================
class Client(ControllerBase):
    """
    TODO
    """
    __metaclass__ = urwid.MetaSignals

    # Urwid metaclass magic
    signals = [
        SIG_RSP_LOGIN,
        SIG_RSP_NEW_ACCT,
        SIG_RSP_PRISONERS,
    ]

    #---- Constructors ---------------------------------------------------

    #=====================================================================
    def __init__(self):
        """
        Constructor.
        """
        object.__init__(self)
        self.__base_uri = None
        self.__me_uri = None
        self.__prisoners_uri = None

    #---- Public methods -------------------------------------------------

    #=====================================================================
    def newAccount(self, a_base_uri, a_auth):
        """
        TODO
        """
        d = self._jsonRequest(a_base_uri)
        d.addCallback(self.__cebNewAccountLogIn, a_base_uri, a_auth)
        d.addErrback(self.__cebNewAccountLogIn, a_base_uri, a_auth)

        return d

    #=====================================================================
    def prisoners(self, a_auth, a_prisoners = SENTINEL):
        """
        TODO
        """
        if a_prisoners is SENTINEL:
            prisoners = {
                'offset': -1,
                'items': {},
            }
        else:
            prisoners = a_prisoners

        d = self._jsonRequest(self.__prisoners_uri, a_auth)
        d.addCallback(self.__cebPrisoners, a_auth, prisoners)
        d.addErrback(self.__cebPrisoners, a_auth, prisoners)

        return d

    #=====================================================================
    def testAndSetUri(self, a_base_uri, a_auth = None):
        """
        TODO
        """
        if a_auth is not None:
            username, password = a_auth

            err = None

            if not username:
                err = ProbablyBadUsernameException('missing username')
            elif not password:
                err = ProbablyBadPasswordException('missing password')

            if err is not None:
                err.iresponse = None
                err.resp_str = None
                err.json_obj = None
                self.__cebTestAndSetUri(err, a_base_uri, a_auth)

                return

        d = self._jsonRequest(a_base_uri, a_auth = a_auth)
        d.addCallback(self.__cebTestAndSetUri, a_base_uri, a_auth)
        d.addErrback(self.__cebTestAndSetUri, a_base_uri, a_auth)

    #=====================================================================
    def _jsonRequest(self, a_uri, a_auth = None, a_method = b'GET', a_data = None):
        """
        Attempts to retrieve the resource at a_uri and parse the results
        as JSON. Usage example:

          def callback(a_arg):
            # Handle the result
            iresponse, resp_str, json_obj = a_arg
            # ...

          def errback(a_err):
            # Error handling (a_err.iresponse, a_err.resp_str, or
            # a_err.json_obj may be None)
            iresponse = a_err.iresponse
            resp_str = a_err.resp_str
            json_obj = a_err.json_obj
            msg = a_err_or_arg.message
            # ...

          d = client._jsonRequest(b'http://foo.bar/')
          d.addCallbacks(callback, errback)

        An HTTP GET will be performed, unless a_method is provided. Under
        most circumstances, its value should probably either be 'GET' or
        'POST'. a_auth, if provided, should be a tuple in the form
        ( username, password ) and will be used to perform basic
        authentication.
        """
        kwargs = {
            'auth': a_auth,
        }

        if a_data is not None:
            kwargs['data'] = a_data

        # Method and URI must be bytes, not unicode
        d = treq.request(str(a_method), str(a_uri), **kwargs)
        d.addCallback(self.__resp2Json)

        return d

    #=====================================================================
    def dbgErrbackTODO(self, *a_args, **a_kwargs):
        print('dbgErrbackTODO')
        def interact(*a_args, **a_kwargs):
            exc = [ None ]

            local = dict(globals())
            local.update(locals())
            import code
            code.interact(local = local)

            if exc[0] is not None:
                raise exc[0]

        from bahaman.util import getLoop
        interact = getLoop().event_loop.handle_exit(interact)

        return interact(self, *a_args, **a_kwargs)

    #---- Private methods ------------------------------------------------

    #=====================================================================
    def __cebNewAccountCreate(self, a_arg_or_err, a_auth):
        if isinstance(a_arg_or_err, twisted.python.failure.Failure):
            urwid.emit_signal(self, SIG_RSP_NEW_ACCT, None, a_arg_or_err.value)
        else:
            urwid.emit_signal(self, SIG_RSP_NEW_ACCT, a_auth)

    #=====================================================================
    def __cebNewAccountLogIn(self, a_arg_or_err, a_base_uri, a_auth):
        try:
            self.__logIn(a_base_uri, a_auth, a_arg_or_err)
        except Exception, e:
            urwid.emit_signal(self, SIG_RSP_NEW_ACCT, None, e)

            return

        new_account = {
            'email_address': a_auth[0],
            'password': a_auth[1],
        }
        post_data = json.dumps(new_account)
        d = self._jsonRequest(self.__me_uri, a_method = 'POST', a_data = post_data)
        d.addCallback(self.__cebNewAccountCreate, a_auth)
        d.addErrback(self.__cebNewAccountCreate, a_auth)

        return d

    #=====================================================================
    def __cebPrisoners(self, a_arg_or_err, a_auth, a_prisoners):
        if isinstance(a_arg_or_err, twisted.python.failure.Failure):
            urwid.emit_signal(self, SIG_RSP_PRISONERS, None, None, a_arg_or_err.value)

            return

        next_uri = None
        iresponse, resp_str, json_obj = a_arg_or_err
        new_items = dict(( ( i['id'], i ) for i in json_obj['items'] ))
        a_prisoners['items'].update(new_items)

        # Note, we check to see if "offset" has changed because there is a
        # bug in the server reference implementation where the "offset"
        # parameter is ignored (see "Server Issues" section in README)
        if json_obj['next'] is not None \
                and json_obj.get('offset', SENTINEL) != a_prisoners['offset']:
            next_uri = urlparse.urljoin(self.__base_uri, json_obj['next'])

        a_prisoners.update(( ( k, v ) for k, v in json_obj.items() if k != 'items' ))

        # Keep calling ourselves as long as we have somewhere to go
        if next_uri is not None:
            d = self._jsonRequest(next_uri, a_auth)
            d.addCallback(self.__cebPrisoners, a_auth, a_prisoners)
            d.addErrback(self.__cebPrisoners, a_auth, a_prisoners)

            return d

        urwid.emit_signal(self, SIG_RSP_PRISONERS, a_auth, a_prisoners['items'])

    #=====================================================================
    def __cebTestAndSetUri(self, a_arg_or_err, a_base_uri, a_auth):
        try:
            self.__logIn(a_base_uri, a_auth, a_arg_or_err)
        except Exception, e:
            urwid.emit_signal(self, SIG_RSP_LOGIN, None, None, e)
        else:
            urwid.emit_signal(self, SIG_RSP_LOGIN, a_base_uri, a_auth)

    #=====================================================================
    def __content2Json(self, a_resp_str, a_response):
        err = None
        json_obj = {}
        json_err = None

        try:
            json_obj = json.loads(a_resp_str)
        except Exception, e:
            json_err = e

        soup = BeautifulSoup.BeautifulSoup(json_obj.get('description', ''))
        description = _SPACES.sub(' ', ' '.join(soup(text = True)))
        description_lower = description.lower()

        # This is (necessarily) a mess (see "Authentication Oddities"
        # section in README)
        if a_response.code == 401:
            if a_response.request.headers.hasHeader('authorization'):
                err = ProbablyBadPasswordException(description)
            else:
                err = ProbablyNeedLoginException(description)
        elif a_response.code == 403:
            err = ProbablyBadPasswordException(description)
        elif a_response.code < 200 \
                or a_response.code >= 300:
            if json_obj is not None \
                    and description_lower.startswith('user ') \
                    and description_lower.endswith(' not found'):
                err = ProbablyBadUsernameException(description)
            else:
                err = ProtocolException(description)
        elif json_err is not None:
            err = json_err
        elif json_obj is None:
            err = ProbablyNeedLoginException()

        if err is not None:
            err.iresponse = a_response
            err.resp_str = a_resp_str
            err.json_obj = json_obj
            raise err

        return ( a_response, a_resp_str, json_obj )

    #=====================================================================
    def __logIn(self, a_base_uri, a_auth, a_arg_or_err):
        if isinstance(a_arg_or_err, twisted.python.failure.Failure):
            raise a_arg_or_err.value

        iresponse, resp_str, json_obj = a_arg_or_err

        try:
            new_me_uri = urlparse.urljoin(a_base_uri, json_obj['me'])
            new_prisoners_uri = urlparse.urljoin(a_base_uri, json_obj['prisoners'])
        except ( KeyError, e ):
            err = ProtocolException(e)

            raise err
        else:
            self.__base_uri = a_base_uri
            self.__me_uri = new_me_uri
            self.__prisoners_uri = new_prisoners_uri

    #=====================================================================
    def __resp2Json(self, a_response):
        # We can't use treq.json_content() here because we want an
        # opportunity to recover from the content received if we can't
        # parse any JSON; we also want to keep the response around, which
        # is why we don't want to just add treq.content() as a callback
        # directly to treq.request()
        d = treq.content(a_response)
        d.addCallback(self.__content2Json, a_response)

        return d
