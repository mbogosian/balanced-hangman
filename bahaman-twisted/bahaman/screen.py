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

import functools
import os
import urwid

from bahaman.util import (
    ControllerBase,
    ProbablyBadPasswordException,
    ProbablyBadUsernameException,
    ProbablyNeedLoginException,
    ProtocolException,
    SENTINEL,
    SIG_CONFIG_UPDATED,
    SIG_REQ_LOGIN,
    SIG_REQ_NEW_ACCT,
    SIG_REQ_PRISONERS,
    getLoop,
    quit,
)

#---- Constants ----------------------------------------------------------

__all__ = ()

#---- Classes ------------------------------------------------------------

#=========================================================================
class GameWidget(urwid.WidgetWrap):
    """
    TODO
    """

    #---- Constructors ---------------------------------------------------

    #=====================================================================
    def __init__(self, a_game):
        """
        Constructor.
        """
        self.__running = False
        self.__game = a_game

    #---- Public properties ----------------------------------------------

    #=====================================================================
    def running():
        def fget(self):
            return self.__running

        def fset(self, a_running):
            self.__running = bool(a_running)

        fdel = None
        doc = """
        True if this widget is running, False otherwise.
        """

        return locals()

    running = property(**running())

#=========================================================================
class GameListItemWidget(urwid.WidgetWrap):
    """
    TODO
    """

    #---- Public constants -----------------------------------------------

    SIG_RESUME_GAME = 'resume_game'

    # Urwid metaclass magic
    signals = [
        SIG_RESUME_GAME,
    ]

    #---- Constructors ---------------------------------------------------

    #=====================================================================
    def __init__(self, a_game):
        """
        Constructor.
        """
        self.__game = a_game
        base_widget = urwid.Pile((
                ( 'pack', urwid.Text('') ),
                ( 'pack', urwid.Columns((
                            ( 'weight', 1, urwid.Text('word:', align = 'right') ),
                            ( 'weight', 1, urwid.Text(a_game.state['word']) ),
                        ), dividechars = 1) ),
                ( 'pack', urwid.Columns((
                            ( 'weight', 1, urwid.Text('hits:', align = 'right') ),
                            ( 'weight', 1, urwid.Text(repr(''.join(sorted(a_game.state['hits']))).lstrip('u')) ),
                        ), dividechars = 1) ),
                ( 'pack', urwid.Columns((
                            ( 'weight', 1, urwid.Text('misses:', align = 'right') ),
                            ( 'weight', 1, urwid.Text(repr(''.join(sorted(a_game.state['misses']))).lstrip('u')) ),
                        ), dividechars = 1) ),
                ( 'pack', urwid.Columns((
                            ( 'weight', 1, urwid.Text('started:', align = 'right') ),
                            ( 'weight', 1, urwid.Text(a_game.state['imprisoned_at'].strftime('%Y-%m-%d %H:%M:%S')) ),
                        ), dividechars = 1) ),
            ))

        if a_game.state['state'] == 'help':
            btn_resume = urwid.Button('Resume')
            urwid.connect_signal(btn_resume, 'click', lambda a_btn, a_self: urwid.emit_signal(a_self, GameListItemWidget.SIG_RESUME_GAME) and True, self)
            base_widget.contents.append(( urwid.Columns((
                        ( 'weight', 1, urwid.Text('') ),
                        ( 'weight', 3, btn_resume ),
                        ( 'weight', 1, urwid.Text('') ),
                    ), dividechars = 1), base_widget.options()
                ))

        urwid.WidgetWrap.__init__(self, base_widget)

    #---- Public properties ----------------------------------------------

    #=====================================================================
    def game():
        def fget(self):
            return self.__game

        fset = None
        fdel = None
        doc = """
        The game state associated with this object.
        """

        return locals()

    game = property(**game())

#=========================================================================
class LoadingListItemWidget(urwid.WidgetWrap):
    """
    TODO
    """

    #---- Constructors ---------------------------------------------------

    #=====================================================================
    def __init__(self):
        """
        Constructor.
        """
        base_widget = urwid.Pile((
                ( 'pack', urwid.Text('') ),
                ( 'pack', urwid.Text('Loading...', align = 'center') ),
            ))
        urwid.WidgetWrap.__init__(self, base_widget)

#=========================================================================
class NewGameListItemWidget(urwid.WidgetWrap):
    """
    TODO
    """

    #---- Public constants -----------------------------------------------

    SIG_NEW_GAME = 'new_game'

    # Urwid metaclass magic
    signals = [
        SIG_NEW_GAME,
    ]

    #---- Constructors ---------------------------------------------------

    #=====================================================================
    def __init__(self):
        """
        Constructor.
        """
        btn_new = urwid.Button('New Game')
        urwid.connect_signal(btn_new, 'click', lambda a_btn, a_self: urwid.emit_signal(a_self, NewGameListItemWidget.SIG_NEW_GAME) and True, self)
        base_widget = urwid.Pile((
                ( 'pack', urwid.Text('') ),
                ( 'pack', urwid.Columns((
                        ( 'weight', 1, urwid.Text('') ),
                        ( 'weight', 3, btn_new ),
                        ( 'weight', 1, urwid.Text('') ),
                    ), dividechars = 1) ),
            ))
        urwid.WidgetWrap.__init__(self, base_widget)

#=========================================================================
class SettingsWidget(urwid.WidgetWrap):
    """
    TODO
    """

    #---- Public constants -----------------------------------------------

    SIG_SETTINGS_ACCEPTED = 'settings_accepted'
    SIG_SETTINGS_CANCELED = 'settings_canceled'
    SIG_SETTINGS_MODIFIED = 'settings_modified'

    # Urwid metaclass magic
    signals = [
        SIG_SETTINGS_ACCEPTED,
        SIG_SETTINGS_CANCELED,
        SIG_SETTINGS_MODIFIED,
    ]

    #---- Constructors ---------------------------------------------------

    #=====================================================================
    def __init__(self):
        """
        Constructor.
        """
        server_uri = urwid.Edit()
        urwid.connect_signal(server_uri, 'change', lambda a_edit, a_new_txt, a_self: a_self.__change(a_edit, a_new_txt) and True, self)
        username = urwid.Edit()
        urwid.connect_signal(username, 'change', lambda a_edit, a_new_txt, a_self: a_self.__change(a_edit, a_new_txt) and True, self)
        password = urwid.Edit(mask = '*')
        urwid.connect_signal(password, 'change', lambda a_edit, a_new_txt, a_self: a_self.__change(a_edit, a_new_txt) and True, self)
        btn_cancel = urwid.Button('Cancel')
        urwid.connect_signal(btn_cancel, 'click', lambda a_btn, a_self: a_self.__cancel() and True, self)
        btn_accept = urwid.Button('Accept')
        urwid.connect_signal(btn_accept, 'click', lambda a_btn, a_self: a_self.__accept() and True, self)
        msg = urwid.Text('', align = 'center')
        base_widget = urwid.Pile((
                ( 'pack', urwid.Text('') ),
                ( 'pack', msg ),
                ( 'pack', urwid.Text('') ),
                urwid.ListBox(urwid.SimpleFocusListWalker((
                        urwid.Columns((
                                ( 'weight', 30, urwid.Text('Server URI:', align = 'right') ),
                                ( 'weight', 70, server_uri ),
                            ), dividechars = 1),
                        urwid.Columns((
                                ( 'weight', 30, urwid.Text('E-mail Address:', align = 'right') ),
                                ( 'weight', 70, username ),
                            ), dividechars = 1),
                        urwid.Columns((
                                ( 'weight', 30, urwid.Text('Password:', align = 'right') ),
                                ( 'weight', 70, password ),
                            ), dividechars = 1),
                    ))),
                ( 'pack', urwid.Text('') ),
                ( 'pack', urwid.Columns((
                                ( 'weight', 1, urwid.Text('') ),
                                ( 'weight', 1, btn_cancel ),
                                ( 'weight', 1, urwid.Text('') ),
                                ( 'weight', 1, btn_accept ),
                                ( 'weight', 1, urwid.Text('') ),
                            ), dividechars = 1) ),
                ( 'pack', urwid.Text('') ),
            ))
        urwid.WidgetWrap.__init__(self, base_widget)
        self.__server_uri = server_uri
        self.__username = username
        self.__password = password
        self.__msg = msg
        self.__prev_vals = {
            self.__server_uri: self.server_uri,
            self.__username: self.username,
            self.__password: self.password,
        }
        self.__modified = False

    #---- Public properties ----------------------------------------------

    #=====================================================================
    def modified():
        def fget(self):
            return self.__modified

        fset = None
        fdel = None
        doc = """
        True if the settings have been modified since update() was called,
        False otherwise.
        """

        return locals()

    modified = property(**modified())

    #=====================================================================
    def msg():
        def fget(self):
            return self.__msg.text

        def fset(self, a_msg):
            self.__msg.set_text(a_msg)

        fdel = None
        doc = """
        The message to appear below the settings.
        """

        return locals()

    msg = property(**msg())

    #=====================================================================
    def password():
        def fget(self):
            return self.__password.edit_text

        def fset(self, a_password):
            self.__password.set_edit_text(a_password)

        fdel = None
        doc = """
        The password setting.
        """

        return locals()

    password = property(**password())

    #=====================================================================
    def server_uri():
        def fget(self):
            return self.__server_uri.edit_text

        def fset(self, a_server_uri):
            self.__server_uri.set_edit_text(a_server_uri)

        fdel = None
        doc = """
        The server URI setting.
        """

        return locals()

    server_uri = property(**server_uri())

    #=====================================================================
    def username():
        def fget(self):
            return self.__username.edit_text

        def fset(self, a_username):
            self.__username.set_edit_text(a_username)

        fdel = None
        doc = """
        The username setting.
        """

        return locals()

    username = property(**username())

    #---- Public methods -------------------------------------------------

    #=====================================================================
    def update(self, a_config = None, a_force_dirty = False):
        if a_config is not None:
            self.server_uri = a_config.get('server_uri', default = '')
            self.username = a_config.get('username', default = '')
            self.password = a_config.get('password', default = '')
            self.msg = ''
            self.__prev_vals = {
                self.__server_uri: self.server_uri,
                self.__username: self.username,
                self.__password: self.password,
            }
            self.__modified = False

        if a_force_dirty:
            self.__prev_vals = {
                self.__server_uri: SENTINEL,
                self.__username: SENTINEL,
                self.__password: SENTINEL,
            }
            self.__modified = True

    #---- Private methods -------------------------------------------------

    #=====================================================================
    def __accept(self):
        new_vals = {
            'server_uri': self.server_uri,
            'username': self.username,
            'password': self.password,
        }
        urwid.emit_signal(self, SettingsWidget.SIG_SETTINGS_ACCEPTED, new_vals)

    #=====================================================================
    def __cancel(self):
        urwid.emit_signal(self, SettingsWidget.SIG_SETTINGS_CANCELED)

    #=====================================================================
    def __change(self, a_edit, a_new_txt):
        new_vals = {
            self.__server_uri: self.server_uri,
            self.__username: self.username,
            self.__password: self.password,
        }
        new_vals[a_edit] = a_new_txt

        if new_vals == self.__prev_vals:
            self.__modified = False
        else:
            self.__modified = True

        urwid.emit_signal(self, SettingsWidget.SIG_SETTINGS_MODIFIED)

#=========================================================================
class Screen(urwid.WidgetWrap, ControllerBase):
    """
    TODO
    """

    #---- Public constants -----------------------------------------------

    # Urwid metaclass magic
    signals = [
        SIG_CONFIG_UPDATED,
        SIG_REQ_LOGIN,
        SIG_REQ_NEW_ACCT,
        SIG_REQ_PRISONERS,
    ]

    TITLE_SETTINGS = 'Settings'
    TITLE_SETTINGS_MODIFIED = TITLE_SETTINGS + ' (Changed)'

    #---- Public static methods ------------------------------------------

    #=====================================================================
    @staticmethod
    def overlay(a_container_widget, a_top_widget, a_bottom_widget, a_title = ''):
        return ( urwid.Overlay(urwid.LineBox(a_bottom_widget, a_title), a_top_widget, align = 'center', width = ( 'relative', 80 ), valign = 'middle', height = ( 'relative', 80 ), min_width = 40, min_height = 10), a_container_widget.options() )

    #---- Constructors ---------------------------------------------------

    #=====================================================================
    def __init__(self):
        """
        Constructor.
        """
        self.__game_widget = urwid.Text('select a game on the right to begin', align = 'center')
        new_game_widget = NewGameListItemWidget()
        self.__stat_widget = urwid.ListBox([ new_game_widget ])
        self.__settings_widget = SettingsWidget()
        btn_cancel = urwid.Button('No')
        urwid.connect_signal(btn_cancel, 'click', lambda a_btn, a_self: a_self.showSettings() and True, self)
        btn_accept = urwid.Button('Yes')
        urwid.connect_signal(btn_accept, 'click', lambda a_btn, a_self: a_self.__newAccount() and True, self)
        self.__new_acct_widget = urwid.Pile((
                ( 'pack', urwid.Text('') ),
                urwid.Filler(urwid.Text('Unrecognized login. Create new account?', align = 'center'), valign = 'middle'),
                ( 'pack', urwid.Text('') ),
                ( 'pack', urwid.Columns((
                            ( 'weight', 1, urwid.Text('') ),
                            ( 'weight', 1, btn_cancel ),
                            ( 'weight', 1, urwid.Text('') ),
                            ( 'weight', 1, btn_accept ),
                            ( 'weight', 1, urwid.Text('') ),
                        ), dividechars = 1) ),
                ( 'pack', urwid.Text('') ),
            ))
        btn_thanks = urwid.Button("Thanks (for nuthin')")
        urwid.connect_signal(btn_thanks, 'click', lambda a_btn, a_self: a_self.showMain() and True, self)
        self.__help_widget = urwid.Pile((
                ( 'pack', urwid.Text('') ),
                urwid.Filler(urwid.Text(Screen.__INSTRUCTIONS), valign = 'middle'),
                ( 'pack', urwid.Text('') ),
                ( 'pack', urwid.Columns((
                            ( 'weight', 1, urwid.Text('') ),
                            ( 'weight', 1, btn_thanks ),
                            ( 'weight', 1, urwid.Text('') ),
                        ), dividechars = 1) ),
                ( 'pack', urwid.Text('') ),
            ))
        game = urwid.Filler(self.__game_widget, valign = 'middle')
        stat = self.__stat_widget
        self.__top = urwid.Columns((
                ( 'weight', 70, game ),
                ( 'weight', 30, stat ),
            ))
        self.__msg = urwid.Text('not logged in', align = 'center')
        header = urwid.Pile((
                ( 'pack', urwid.Text(( urwid.AttrSpec('underline', 'default'), 'BAlanced HAngMAN' ), align = 'center') ),
                ( 'pack', urwid.Text('<\u2190 \u2192 \u2191 \u2193> or mouse to navigate, <enter> or click to activate', align = 'center') ),
                ( 'pack', self.__msg ),
                ( 'pack', urwid.Divider(u'\u2500') ),
            ))
        btn_help = urwid.Button('Help')
        urwid.connect_signal(btn_help, 'click', lambda a_btn, a_self: self.__showHelp() and True, self)
        btn_settings = urwid.Button('Settings')
        urwid.connect_signal(btn_settings, 'click', lambda a_btn, a_self: a_self.showSettings() and True, self)
        btn_quit = urwid.Button('Quit')
        urwid.connect_signal(btn_quit, 'click', lambda a_btn: quit() and True)
        footer = urwid.Pile((
                ( 'pack', urwid.Divider(u'\u2500') ),
                ( 'pack', urwid.Columns((
                            ( 'weight', 1, urwid.Text('') ),
                            ( 'weight', 1, btn_help ),
                            ( 'weight', 1, urwid.Text('') ),
                            ( 'weight', 1, btn_settings ),
                            ( 'weight', 1, urwid.Text('') ),
                            ( 'weight', 1, btn_quit ),
                            ( 'weight', 1, urwid.Text('') ),
                        ), dividechars = 1) ),
                ( 'pack', urwid.Text('Copyright (c) 2014, Matt Bogosian.', align = 'center') ),
            ))
        base_widget = urwid.Frame(self.__top, header, footer)
        urwid.WidgetWrap.__init__(self, base_widget)
        ControllerBase.__init__(self)
        self.__cheat = False
        self.connectObject(self.__settings_widget, SettingsWidget.SIG_SETTINGS_ACCEPTED)
        self.connectObject(self.__settings_widget, SettingsWidget.SIG_SETTINGS_CANCELED)
        self.connectObject(self.__settings_widget, SettingsWidget.SIG_SETTINGS_MODIFIED)
        self.connectObject(new_game_widget, NewGameListItemWidget.SIG_NEW_GAME)
        # More fun: <http://bit.ly/K9ve3C>
        self.__showPalm('<http://bit.ly/1ebG9oU>')

    #---- Public properties ----------------------------------------------

    #=====================================================================
    def game_widget():
        def fget(self):
            return self.__game_widget

        fset = None
        fdel = None
        doc = """
        The widget for displaying the currently active game.
        """

        return locals()

    game_widget = property(**game_widget())

    #=====================================================================
    def msg():
        def fget(self):
            return self.__msg.text

        def fset(self, a_msg):
            self.__msg.set_text(a_msg)

        fdel = None
        doc = """
        The message to appear below the settings.
        """

        return locals()

    msg = property(**msg())

    #=====================================================================
    def stat_widget():
        def fget(self):
            return self.__stat_widget

        fset = None
        fdel = None
        doc = """
        The widget for displaying the status of the account.
        """

        return locals()

    stat_widget = property(**stat_widget())

    #=====================================================================
    def settings_widget():
        def fget(self):
            return self.__settings_widget

        fset = None
        fdel = None
        doc = """
        The widget for displaying and changing the settings.
        """

        return locals()

    settings_widget = property(**settings_widget())

    #---- Public hook methods --------------------------------------------

    #=====================================================================
    def sig_new_game(self):
        return True

    #=====================================================================
    def sig_resume_game(self):
        return True

    #=====================================================================
    def sig_settings_accepted(self, a_new_vals):
        if self.__settings_widget.modified:
            self.__logIn(a_new_vals['server_uri'], ( a_new_vals['username'], a_new_vals['password'] ))
        else:
            self.showMain()

        return True

    #=====================================================================
    def sig_settings_canceled(self):
        # self.__settings_widget.update()
        self.showMain()

        return True

    #=====================================================================
    def sig_settings_modified(self):
        if self.__settings_widget.modified:
            self.__setSettingsTitle(Screen.TITLE_SETTINGS_MODIFIED)
        else:
            self.__setSettingsTitle(Screen.TITLE_SETTINGS)

        return True

    #---- Public methods -------------------------------------------------

    #=====================================================================
    def loginFailure(self, a_err):
        try:
            raise a_err
        except ProbablyBadPasswordException:
            if self.__settings_widget.password:
                msg = 'probably a bad password%s("%s")' % ( os.linesep, a_err )
            else:
                msg = 'missing password'
        except ProbablyBadUsernameException:
            if self.__settings_widget.username:
                self.__overlay(self.__new_acct_widget)

                return

            msg = 'missing username'
        except ProbablyNeedLoginException:
            msg = 'login needed (probably a bug in this client)%s("%s")' % ( os.linesep, a_err )
        except ProtocolException:
            msg = 'probably a bad server URI (or a miscreant server)%s("%s")' % ( os.linesep, a_err )
        except Exception:
            try:
                msg = a_err.message
            except AttributeError:
                msg = str(a_err)

        self.__settings_widget.msg = Screen.__formatErrorMessage(msg)
        self.showSettings()

    #=====================================================================
    def loginSuccess(self, a_base_uri, a_auth):
        updated_vals = {
            'server_uri': self.__settings_widget.server_uri,
            'username': self.__settings_widget.username,
            'password': self.__settings_widget.password,
        }

        urwid.emit_signal(self, SIG_CONFIG_UPDATED, updated_vals)
        self.__showPalm('Logging in...SUCCESS!')
        self.msg = 'logged in as <%s>' % self.__settings_widget.username
        getLoop().set_alarm_in(1, lambda a_loop, a_user_data: self.showMain())
        getLoop().set_alarm_in(1, lambda a_loop, a_user_data: urwid.emit_signal(self, SIG_REQ_PRISONERS, a_auth))

    #=====================================================================
    def newAccountFailure(self, a_err):
        msg = None

        try:
            raise a_err
        except ( ProbablyBadUsernameException, ProtocolException ):
            self.__settings_widget.msg = Screen.__formatErrorMessage(a_err)
            self.showSettings()
        except Exception:
            self.loginFailure(self.__settings_widget.server_uri, a_auth, a_err)

    #=====================================================================
    def newAccountSuccess(self, a_auth):
        self.__showPalm('Creating new account...SUCCESS!')
        getLoop().set_alarm_in(1, lambda a_loop, a_user_data: self.__logIn(self.__settings_widget.server_uri, ( self.__settings_widget.username, self.__settings_widget.password )))

    #=====================================================================
    def showMain(self):
        self._w.contents['body'] = ( self.__top, self._w.options() )
        self.__forceRedraw()

    #=====================================================================
    def showSettings(self, a_config = None, a_force_dirty = False):
        self.__settings_widget.update(a_config, a_force_dirty)
        self.__overlay(self.__settings_widget, Screen.TITLE_SETTINGS)

    #=====================================================================
    def showLoggingIn(self):
        body = self.__stat_widget.body
        body.contents[1:] = ( LoadingListItemWidget(), )
        self.__showPalm('Logging in...        ')

    #=====================================================================
    def start(self, a_config, a_first_run):
        self.__cheat = a_config.cheat

        if a_first_run \
                or not a_config.get('server_uri', default = '') \
                or not a_config.get('username', default = '') \
                or not a_config.get('password', default = ''):
            self.showSettings(a_config, a_force_dirty = True)
        else:
            self.__settings_widget.update(a_config, a_force_dirty = True)
            self.__logIn(self.__settings_widget.server_uri, ( self.__settings_widget.username, self.__settings_widget.password ))

    #=====================================================================
    def updatePrisoners(self, a_auth, a_prisoners):
        try:
            game_list_items = [ GameListItemWidget(i) for i in a_prisoners ]

            for game_list_item in game_list_items:
                self.connectObject(game_list_item, GameListItemWidget.SIG_RESUME_GAME)

            body = self.__stat_widget.body
            body.contents[1:] = game_list_items
        except Exception, e:
            # TODO
            local = dict(globals())
            local.update(locals())
            import code
            code.interact(local = local)

        self.__forceRedraw()

    #---- Private constants ----------------------------------------------

    # From <http://bit.ly/1inKNkH>
    __PALM = """
mm###########mmm
m####################m
m#####`\"#m m###\"\"\"'######m
######*\"  \"   \"   \"mm#######
m####\"  ,             m\"#######m
m#### m*\" ,'  ;     ,   \"########m
####### m*   m  |#m  ;  m ########
|######### mm#  |####  #m##########|
###########|  |######m############
\"##########|  |##################\"
\"#########  |## /##############\"
########|  # |/ m###########
\"#######      ###########\"
\"\"\"\"\"\"       \"\"\"\"\"\"\"\"\"
""".strip()

    # Inspired by <http://bit.ly/1cuD3M8>
    __INSTRUCTIONS = """
Your best friend has been arrested and charged with arson, treason, armed robbery, and public drunkeness ... PLUS ... murder, mayhem, ignorance, and ugliness.

However, the judge, being a benevolent sort, will let your friend plea-bargain the charges down to ugliness, provided he/she has one friend. GUESS WHO?

To save your friend's life, you must guess the secret word. Each time you guess a CORRECT letter, it will be revealed.

But BEWARE! Each time you guess an INCORRECT letter, your friend advances one step closer to DOOM!
""".strip()

    #---- Private static methods -----------------------------------------

    #=====================================================================
    @staticmethod
    def __formatErrorMessage(a_msg):
        return '>>>>>>>>>>>>>>>> ERROR <<<<<<<<<<<<<<<<%s%s%s>>>>>>>>>>>>>>>> ERROR <<<<<<<<<<<<<<<<' % ( os.linesep, a_msg, os.linesep )

    #---- Private methods ------------------------------------------------

    #=====================================================================
    def __forceRedraw(self):
        self._invalidate()

        try:
            loop = getLoop()
        except ValueError:
            pass # No loop yet, so don't redraw
        else:
            loop.draw_screen()

    #=====================================================================
    def __logIn(self, a_server_uri, a_auth):
        self.showLoggingIn()
        urwid.emit_signal(self, SIG_REQ_LOGIN, a_server_uri, a_auth)

    #=====================================================================
    def __newAccount(self):
        self.__showPalm('Creating new account...        ')
        urwid.emit_signal(self, SIG_REQ_NEW_ACCT, self.__settings_widget.server_uri, ( self.__settings_widget.username, self.__settings_widget.password ))

    #=====================================================================
    def __overlay(self, a_widget, a_title = ''):
        self._w.contents['body'] = Screen.overlay(self._w, self.__top, a_widget, a_title)
        self.__forceRedraw()

    #=====================================================================
    def __setSettingsTitle(self, a_title):
        widget = self._w.contents['body'][0]

        if not isinstance(widget, urwid.Overlay):
            return

        widget = widget.contents[1][0]

        if not isinstance(widget, urwid.LineBox):
            return

        if widget.title_widget.text != a_title:
            widget.set_title(a_title)

    #=====================================================================
    def __showHelp(self):
        self.__overlay(self.__help_widget, ' Instructions')

    #=====================================================================
    def __showPalm(self, a_msg):
        self.__overlay(urwid.Filler(urwid.Text('%s\n\n%s' % ( Screen.__PALM, a_msg ), align = 'center')))
