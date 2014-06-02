.. -*-mode: rst; encoding: utf-8-*-=======================================
.. Copyright (c) 2014 Matt Bogosian <mtb19@columbia.edu>.
..
.. Please see the LICENSE (or LICENSE.txt) file which accompanied this
.. software for rights and restrictions governing its use. If such a file
.. did not accompany this software, then please contact the author before
.. viewing or using this software in any capacity.
.. =======================================================================

Installation
------------

There are several prerequisites:

  - `BeautifulSoup`_
  - `dateutil`_
  - `treq`_
  - `Twisted`_
  - `Urwid`_
  - `pyOpenSSL`_ (required for SSL support)
  - `PyPy`_ (optional, but it kicks so much ass, why on earth wouldn’t you
    already have it?!)
  - `virtualenv`_ (optional, but makes installing and running much easier)

While I have tried to mirror the production of a PyPI package as much as
practically possible thus far, this is not ready for release. As such,
there is a small effort involved to get this running. The following is
probably the least painful way, but you’ll need virtualenv installed. This
is for demonstration purposes only. If you’re already familiar with the
tools, this should be pretty straightforward. That being said, there’s no
error checking, so don’t just blindly run these commands if you don’t
understand what’s going on. *Ye have been warned! Arg[v]!*

::

  # Make sure you have virtualenv installed
  virtualenv --version || pip install virtualenv

  # Get to the top-level directory (i.e., the one in which this README
  # file can be found)
  cd .../bahaman-twisted

  # Create a new virtual environment and prefer pypy if it’s available
  virtualenv -p pypy .virtualenv || virtualenv .virtualenv

  # Activate the virtual environment (your shell prompt should change at
  # this point to reflect activation; if it doesn’t something’s probably
  # wrong)
  . .virtualenv/bin/activate

  # Install the prerequisites
  pip install BeautifulSoup pyOpenSSL pytest treq twisted urwid
  pip install http://bit.ly/1kATmNl # dateutil

  # TODO

.. _`BeautifulSoup`: http://bit.ly/192QRyo
.. _`dateutil`: http://bit.ly/K0bxvJ
.. _`treq`: http://bit.ly/192QRyo
.. _`Twisted`: http://bit.ly/1fstZHf
.. _`Urwid`: http://bit.ly/19CN0GK
.. _`pyOpenSSL`: http://bit.ly/1a9k1qS
.. _`PyPy`: http://bit.ly/1etG0Qk
.. _`virtualenv`: http://bit.ly/1cWXbGJ

Known Issues
------------

- Despite the direction at the top of the screen that one should be able
  to use the arrow keys, keyboard navigation between different screen
  elements doesn’t always work. If your terminal does not support mouse
  input, there parts of the screen to which you will not be able to
  navigate. This is a bug. Urwid does not have a lot of documentation on
  changing focus between certain widgets. Yes, I realize this defeats the
  entire purpose of having a curses-based console application. What can I
  say? It’s an alpha release....

- Little thought has been given to concurrency corner cases. For example,
  if you change a user’s password from one client while the another is
  running for that same user, the latter does not deal gracefully with the
  failures. Games started on one client may not show up on another for a
  while, etc. Due to an apparent server-side bug in the paging API,
  unpredictable behavior is compounded once a user extends past ten games
  (see `Server Issues`_). Aside from the paging issue, solutions for these
  problems do exist, but none has been implemented at this point.

- I have likely made poor decisions that result in some unpleasant user
  experiences. For example, I overload a single overlay area for many
  purposes (e.g., help screen, settings screen, status, etc.). The
  contents of this overlay can change in response to user input as well as
  asyncronous events. For example if a user clicks on the “Help” button
  while the application is attempting to log in, the help screen may be
  shown briefly until the log-in status changes, at which time the
  instructions will be replaced by the status without any input from the
  user. I would consider this is a bug. If time allows, I would probably
  scrap the current interface behavior in favor of something more familiar
  like pico or emacs.

- The settings screen “Cancel” button does not restore its previous
  state. Instead the user’s edits are preserved and shown next time the
  settings screen is displayed. This is a bug.

- The authentication model in the server reference implementation doesn’t
  jive with the retry logic in many libraries’ authentication
  handlers. But this implementation’s the rather silly blind submission of
  a hand-created Authorization header with certain requests seems to work.

- The UI does not expose functionality to change one’s account password,
  even though such functionality exists on the server. This should be easy
  enough to add, perhaps through the settings screen.

- The account password is stored in clear text in the configuration
  file. It probably goes without saying this isn’t very secure.

- SSL is not enforced. A smarter implementation would test SSL/TLS
  availability when following the discovery URI, enforce it where
  available, and provide a warning where it was not. Instead, it just
  blindly follows whatever protocol is designed.

- SSL certificates are apparently `not validated by treq`_ or the
  underlying Twisted client libraries. However, because Twisted uses
  pyOpenSSL, this may not be true. I have not attempted to verify either
  way.

- The application saves minimal state in its configuration file. That file
  is read and written using the ``ConfigParser`` standard Python
  library. Those operations have not been made asynchronous. Because
  configuration files are typically much less than one physical block in
  size, when reading/writing to functioning local media (like a
  locally-mounted hard drive), the deficiency is negligible. However, it
  could cause the application to become unresponsive (e.g., when dealing
  with bad blocks, an intermittent NFS connection, etc.).

- While it should theoretically work, this has *not* been tested on
  Windows in any way, shape, or form.

- Upon login, this implementation tries to gather *all* games (by paging
  through the ``prisoners`` URI with the ``offset`` parameter. This
  probably doesn’t scale very well for users with hundreds or thousands of
  games. That particular API is probably more well suited to an AJAX-y
  paging interface rather than this implementation.

.. _`not validated by treq`: http://bit.ly/1g8eogr
