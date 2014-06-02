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

#---- Constants ----------------------------------------------------------

__all__ = ()

#---- Functions ----------------------------------------------------------

#=========================================================================
def main():
    import argparse
    import functools
    import sys
    import twisted.internet.reactor
    import urwid

    from bahaman.client import (
        Client,
    )

    from bahaman.config import (
        BahamanConfigParser,
    )

    from bahaman.controller import (
        Controller,
    )

    from bahaman.screen import (
        Screen,
    )

    # Get the command-line configuration
    arg_parser = argparse.ArgumentParser(description = 'Play some hangman!')
    arg_parser.add_argument('--config', metavar = 'CONFIG_FILE', help = 'read/write to this configuration file instead of the default one')
    arg_parser.add_argument('--cheat', action = 'store_true', default = False, help = 'activates cheat mode')
    arg_parser.add_argument('--no-cheat', action = 'store_false', help = 'deactivates cheat mode (default)', dest = 'cheat')
    arg_parser.add_argument('--version', action = 'version', version = '%(prog)s 0.1.0a1')
    config_parser = BahamanConfigParser(arg_parser)
    new_config = config_parser.readOrCreate()

    # Set up the main loop and keep track of some important stuff
    import bahaman.util
    screen = Screen()
    event_loop = urwid.TwistedEventLoop()
    bahaman.util._REACTOR = event_loop.reactor
    bahaman.util._LOOP = urwid.MainLoop(screen, event_loop = event_loop)
    client = Client()

    # Wire it together, and...
    controller = Controller(config_parser, client, screen)
    bahaman.util._LOOP.set_alarm_in(1, lambda a_loop, a_user_data: controller.wireItUpAndGo(new_config))
        # (as an aside, we could use reactor.callLater(1, ...) instead of
        # loop.set_alarm_in(1, ...), but the choice is kind of arbitrary;
        # we probably want to pick one or the other and be as consistent
        # as possible)

    # ...let 'er rip!
    bahaman.util._LOOP.run()

#---- Initialization -----------------------------------------------------

if __name__ == '__main__':
    main()
