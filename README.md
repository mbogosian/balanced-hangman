<!-- -*-mode: markdown; encoding: utf-8-*-================================
  Copyright (c) 2014 Matt Bogosian <mtb19@columbia.edu>.

  Please see the LICENSE (or LICENSE.txt) file which accompanied this
  software for rights and restrictions governing its use. If such a file
  did not accompany this software, then please contact the author before
  viewing or using this software in any capacity.
  ======================================================================== -->

BaHaMan - BAlanced HAngMAN
==========================

After falling *months* behind, I was recently getting caught up on my
ChangeLog podcasts when I heard [an interesting
challenge](http://bit.ly/1bWmcNO) alluded to by guest, Marshall
Jones. This is an attempt to address that challenge (also posed via
[Jareau Wade’s blog post](http://bit.ly/1cWX1Pu) as well as Marshall
Jones’s and his [GitHub Gist page](http://bit.ly/1kqF5R0).

Installation
------------

Fork and open `index.html`:

    $ git clone https://github.com/mbogosian/balanced-hangman
    ...
    $ firefox balanced-hangman/index.html

Or on OS X:

    $ git clone https://github.com/mbogosian/balanced-hangman
    ...
    $ open balanced-hangman/index.html

Known Issues
------------

- Little thought has been given to concurrency corner cases. For example,
  if you change a user’s password from one client while the another is
  running for that same user, the latter does not deal gracefully with the
  failures. Games started on one client may not show up on another for a
  while, etc. Due to an apparent server-side bug in the paging API,
  unpredictable behavior is compounded once a user extends past ten games
  (see `Server Issues`_). Aside from the paging issue, solutions for these
  problems do exist, but none has been implemented at this point.

- I will reiterate this again later, but I am *not* very experienced in UI
  design/implementation (see [Notes On The Architecture](#Notes On The
  Architecture)). As such, I have likely made poor decisions that result
  in some unpleasant user experiences.

- The authentication model in the server reference implementation doesn’t
  jive with the retry logic in many libraries’ authentication handlers
  (see [Authentication Oddities](#Authentication Oddities)). But this
  implementation’s the rather silly blind submission of a hand-created
  Authorization header with certain requests seems to work.

- The UI does not expose functionality to change one’s account password,
  even though such functionality exists on the server. This should be easy
  enough to add, perhaps through the settings screen.

- No thought has been given to [I18n/L10n](http://bit.ly/1cktcE8). This is
  probably bad. In my experience, this is difficult to retrofit through
  refactoring (it is one of those rare cases in software development where
  it often saves to do the work up front and is not generally considered
  [premature optimization](http://bit.ly/18Wh3uj) where a UI is
  involved). However, given that this is a quick prototype, I pray to the
  almighty gods of hacking for forgiveness. Rest assured that I have made
  the appropriate backyard sacrifices in compliance with all governing ISO
  standards.

- SSL is not enforced. A smarter implementation would test SSL/TLS
  availability when following the discovery URI, enforce it where
  available, and provide a warning where it was not. Instead, it just
  blindly follows whatever protocol is designed.

- While it should theoretically work, this has *not* been tested on
  Internet Explorer in any way, shape, or form.

Notes On The Architecture
-------------------------

Let me start by saying this was a learning experience for me. I am *not* a
UI designer, nor do I have any real experience implementing a full
[MVC](http://bit.ly/1lIZSQl) stack. (I’ve played around with a few toy
demos, but that’s about it.)

I usually play (very happily) in the back-end systems realm, thinking
about things like concurrence, bottlenecks, transactional integrity,
scalability, business cost of edge cases, failure recovery, and all kinds
of other yummy stuff.

What I’m trying to get at is that this design might suck. A lot. Please
take that into account when examining the code (especially those parts
which appear more [pasta-like](http://bit.ly/1ktB6p2) than expected). I
appreciate guidance and feedback from people who have traveled further
down than I (which is pretty much everyone, as near as I can tell).

TODO - describe architecture here

Observations About The Server Reference Implementation
------------------------------------------------------

If there’s an API doc published somewhere, I haven’t found it. Maybe
finding the docs was part of the test, but if that’s the case, I’ve
clearly failed. The good news is that the basic parts of the protocol (at
least enough to get the game working) are easily deduced with some basic
prodding.

The general conventions I’ve discovered are as follows:

- Valid requests are HTTP `GET` or `POST` operations (depending on the
  context) and responses are generally of type `application/json`.

- HTTP+SSL is silently supported, but not enforced.

- `GET` operations generally correspond to operations that do not change
  server state (i.e., “reads”), while `POST` operations generally
  correspond to operations that do change server state (i.e.,
  “writes”). As far as I can tell `PUT` and `DELETE` operations are not
  used for anything.

- The [index URI](https://balanced-hangman.herokuapp.com/) is used for
  discovery of URIs for performing two basic operations:

  `me`
    Requests pertaining to user accounts.

  `prisoners`
    Requests pertaining to games.

  Each of the above may reference other URIs for related operations (e.g.,
  `.../users/[user ID]` for referencing user accounts by user ID).

- New accounts are created by an unauthenticated `POST` to the `me` URI
  with the following data:

  > ...
  > Content-Type: application/x-www-form-urlencoded
  > ...
  > email_address=[RCF2822 compliant e-mail address]&amp;password=[cleartext password]

  Or (alternatively)::

  > ...
  > Content-Type: application/json
  > ...
  > { "email_address": "[RCF2822 compliant e-mail address]",
  >   "password": "[cleartext password]" }

- An account password is changed by a `POST` to the `me` URI with data
  similar to account creation, but for an existing account. Credentials
  *can* be provided. However, if credentials are *not* provided, **this
  will blindly overwrite whatever password exists for that account**! This
  means that as long as one has an account’s e-mail address, one can
  hijack it by overwriting the password, and then using the account as
  one’s own (at least until the owner of the account figures it out and
  does the same thing to hijack it back).

- I have not discovered a way to delete an account once it is created.

- User IDs are URI-safe Base64 encoded binary strings. If those binary
  strings are serialized data, I do not recognize the encoding (they don’t
  look like BSON, gzip, etc.). Someone with more experience in binary
  serialization might be able to easily recognize them, but I moved on to
  other things.<a href="#1" name="1ref"><sup>1</sup></a>

- Most of the operations require some form of authentication, but the
  server behavior is occasionally not [RFC2616]-compliant (see
  [Authentication Oddities](#Authentication Oddities) below).

- Details about past/pending games are gleaned by an authenticated `GET`
  to the `prisoners` URI. New games are started by an authenticated `POST`
  to the same URI, but with a blank payload.

The rest becomes pretty obvious after some poking around with the above
operations.

Server Issues
`````````````

There are a few issues I’ve observed in the server reference
implementation:

- Paging using the `prisoners` URI appears to be broken on the server
  side. Various server responses do provide URIs with the `offset`
  parameter, and that parameter, when supplied, does not result in an
  error, but it appears that it is ignored. With 12 games, for example,
  the outpot of `/prisoners` is identical to `prisoners?offset=10`. When
  executed in succession without an intervening call to create a new game,
  both URIs list the same games, and both list a `previous` paging URI as
  `null`. While the order of the games listed in the `items` list does
  change slightly, and on occasion, it is not clear to me how the games
  are sorted (it does not appear to depend on `uri`, `id`, `state`, or
  `imprisoned_at`). Unfortunately, there doesn’t appear to be a reliable
  way to gain access to more than 10 games.

- I’m not sure what performing a `GET` on the `guesses` URI is for. It
  returns `hits` and `misses` for the given ID, but that’s it. It would
  seem to me that if one were to provide a separate URI for retrieving the
  updated guess state of a particular game (as opposed to fetching the
  entire state via the `prisoners` URI), that it should also return at
  least `state`, if not `guesses_remaining` as well (so that the caller
  knows when the game is finished). As of right now, I don’t see a use for
  that API, so my implementation does not make use of it, but I may be
  overlooking something.

- The server appears to allow nonsensical guesses (i.e., things that would
  *never* appear in an answer, like `"*"` or `"\u0000"`). Assuming the words
  come from `/usr/share/dict/words`, there’s a *very* good chance that only
  letters are used::

  > % python -c 'with open("/usr/share/dict/words") as f: print repr("".join(sorted(set(f.read().lower()))))'
  > '\nabcdefghijklmnopqrstuvwxyz'

  I’ve decided to limit guesses to ascii letters below `0x7f` (i.e., no
  “extended” ascii characters, like “ç” or “ö”) on the client side. This
  depends on my fairly large assumption that the words are exclusively in
  English and that no abbreviations or accents are used (e.g., “2nd” or
  “resumé”). Anecdotally, I have not seen any counterevidence, but this
  does make me a little nervous. It introduces fragility into the client
  (although probably no more than it already had; see note on I18n/L10n
  above).

- The server does *not* appear to support JSONP. This makes hosting an
  AJAX-y web-based solution that calls the server reference implementation
  slightly more difficult. See <http://bit.ly/1di4MMy> for a detailed
  description of the problem and some solutions.

  In the end, I decided to host my own proxy. I was prepared to write my
  own, but (thankfully) [someone beat me to it](http://bit.ly/MLeMsB). The
  only problem was that particular implementation doesn’t support HTTP
  authorization. Fifteen minutes of hacking on the script took care of
  that. As I was searching through the project’s exising issues to see if
  I could submit a pull request, I found (again) someone else beat me to
  it with [a more complete implementation](http://bit.ly/1n56ZR0). (I am
  apparently frequently late to the party, and often underdressed when I
  finally arrive.)

  This approach does impose additional requirements for this
  implementation. For example, it must be hosted from a web server that
  supports PHP (with [the Client URL
  library](http://bit.ly/1fOcqRV)). Also, one needs to be careful about
  encrypting *all* connections if preserving password security is
  important (see, however, [Observations About The Server Reference
  Implementation](#Observations About The Server Reference Implementation)
  regarding the apparent ability for anyone to change anyone else’s
  password). Because authorization information is passed to the proxy,
  merely using `https` to access the server reference implementation is
  not enough. The proxy URL must be encrypted as well. As it is currently
  implemented, the proxy URL is relative to the application page, so it’s
  best to access everything either locally (i.e., via `localhost` on a
  machine not shared with anyone) or via `https` if at all possible.

  Note: there are no PHP directives in `index.php`. It could have just as
  easily been `index.html`. The `.php` suffix is chosen to remind
  installing users that a web server running PHP is required.

[RFC2616]: http://bit.ly/1kr0n0B

Authentication Oddities
```````````````````````

The server reference implementation exhibits some behavioral oddities that
don’t play well with [standard methods for dealing with HTTP
authentication](http://bit.ly/1erYDUW). Specifically, sometimes response
code 403 is returned when 401 is likely more appropriate.<a href="#2"
name="2ref"><sup>2</sup></a> Sometimes response code 200 is returned, even
though the context is meaningless without authentication. More
specifically:

- 401 (unauthorized) is returned only *after* a valid username is
  presented, but with the wrong password. Where credentials are not
  presented, some cases result in a 403 (forbidden) rather than
  a 401. Where credentials are presented, but without a valid username, a
  500 (internal server error) is returned. Neither are helpful. Many
  libraries (and browsers) will automatically retry requests with known
  credentials in response to a 401 (but not for a 403 or a 500). This
  makes sense if one understands the differences between the error
  codes.

  From [RFC2616], section [10.4.2](http://bit.ly/1jqKFEK):

  > 401 Unauthorized [¶] The request requires user authentication. The
  > response MUST include a WWW-Authenticate header field ... *containing a
  > challenge applicable to the requested resource*. The client MAY repeat
  > the request with a suitable Authorization header field ... . ...

  > (*Emphasis* added.)

  Compare that with section [10.4.4](http://bit.ly/JM2uxZ):

  > 403 Forbidden [¶] The server understood the request, but is refusing to
  > fulfill it. *Authorization will not help and the request SHOULD NOT be
  > repeated.* ...

  > (*Emphasis* added.)

  And section [10.5.1](http://bit.ly/1etWQ1C):

  > 500 Internal Server Error [¶] The server encountered an *unexpected
  > condition* which prevented it from fulfilling the request.

  > (*Emphasis* added.)

  I don’t think it’s reasonable to assert that someone mistyping their
  username is an “unexpected” condition. It happens all the time.

  To see this in action, from a browser (e.g., Firefox) try doing a plain
  `GET` on
  `http://balanced-hangman.herokuapp.com/users/[valid_user_id]`. You’ll
  get an error page without any prompting for credentials. Now compare
  that with doing a plain `GET` on a [compliant
  example](http://bit.ly/1fJRMTZ) (see the [author’s explanation
  page](http://bit.ly/1bfpDiC) for details).

- When a 401 is returned, the `WWW-Authenticate` header is unhelpful. It
  generally merely reads `401: Unauthorized` instead of providing a [list
  of potentially accepted challenges](http://bit.ly/1fMf1g0) (see also
  [RFC2617](http://bit.ly/1ds1cRD)).

- To make matters even more confusing, a `GET` on
  `http://balanced-hangman.herokuapp.com/me` returns a 200 with a JSON
  body of `null` when no authentication is used. It seems that a 401 would
  be appropriate (or at least a misapplied 403 to be consistent with
  behavior observed elsewhere in the application; see above), but this
  behaves more like a web application that displays one version of an
  otherwise correct page where a user is not logged in, and another where
  she is. That approach is fine, but mixing it with HTTP authentication is
  probably not [the Right Thing](http://bit.ly/1l1VjNH)™. The
  inconsistencies just confuse the heck out of standards-compliant parsers
  (a standard which the server *claims* to follow by starting all of its
  responses with `HTTP/1.1`; [jus’ sayin’](http://bit.ly/18XVKmY)).

My unsolicited recommendation is to either use 4xx properly (and in all
circumstances), or not at all (and represent authentication failures
exclusively in the JSON payloads). *But*, since we can’t change the
ill-behaved server, we might as well [try to accommodate
it](http://bit.ly/192R2Ym).

For at least the above reasons, we basically have to either guess or
hard-code what responses are semantically equivalent to a 401.

Auto-Didactic Socratic Method (As Opposed To Frequently Asked) Questions
------------------------------------------------------------------------

- *Why on earth would you write your client using Twisted and Urwid?!*

  The server provides responses in JSON. The obvious approach is to throw
  together a static HTML/JavaScript implementation that could be served by
  any modern browser.

  But that’s *boring*.

  While I have been experimenting with asynchronous programming and
  cooperative multitasking in I/O-heavy environments, I had precious
  little exposure to Twisted. I also knew very little about ncurses
  programming. (I still know very little as Urwid hides much of the
  details. However, Urwid plays somewhat nicely<a href="#3"
  name="3ref"><sup>3</sup></a> with Twisted, so I really can’t complain.)

  In other words, I needed motivation to learn Twisted, and this seemed to
  fit the bill, since both call/response over a network and UI-interaction
  are natural fits for callback-based programming.

- *But Twisted sucks!*

  Yes it does, but not in the way that most people articulate. Twisted
  does not have a sharp learning curve because it is asynchronous. That
  part isn’t actually that difficult. If you’re not familiar with the
  concept, imagine writing software that is entirely
  interrupt-based. (Think signal handlers, if you like. People with
  experience with `Qt`_ know what I’m talking about.) Programmers have
  been comfortable with variations of that concept for decades. The
  Twisted `reactor` is just another variant. (Dave Peticolas’s
  “`Introduction to Asynchronous Programming and Twisted`_” is an aptly
  named starting point for the unindoctrinated.)

  The difficulty comes in that beyond the `reactor`, the purported
  “value add” of Twisted over other cooperative multitasking environments
  like `gevent`_ or `asyncore`_ (or even `PyZMQ`_, sort of) is its
  extensive library of protocol implementations. Unfortunately, that
  library is in constant development and is not well documented beyond
  some very simple use cases. There is not much guidance on best
  practices. Those are left to be discovered again and again by each new
  developer through reading source code and experimentation. In other
  words, it’s not very efficient, and can be immensely frustrating.

  Additionally, Twisted associates itself strongly with `TDD`_, but
  writing tests for asynchronous frameworks is not trivial. Some
  `rudimentary guidance`_ is provided, but if you want to test *only* the
  client side of a REST-based application while extending Twisted’s own
  protocol implementations (which is one way that you *should* use
  Twisted), you’re on your own, back to looking at source code, and trying
  to guess at which of the dozens of approaches is best for your
  situation. Again, it’s not very efficient.

  Which is why I copped out and used treq and Urwid, instead of
  implementing the entire thing using just Twisted. Maybe someday I’ll go
  back and try it (and maybe even make the look and feel more like
  `(al)pine or pico`_, just for ol’ times’ sake).

  Don’t get me wrong, Twisted is *cool*. And on `PyPy`_, it is *blazingly*
  fast. But it is almost as difficult to grok Twisted from a client
  developer’s perspective, as it is to become a regular contributor
  tinkering around with its internals. I think that puts the barrier to
  entry a little high for something that strives to be a reusable
  framework.

  That’s just my [$1.05](http://bit.ly/1fqjCDn).

.. _`Qt`: http://bit.ly/1lxcuHj
.. _`Introduction to Asynchronous Programming and Twisted`: http://bit.ly/1dPRdpl
.. _`gevent`: http://bit.ly/19YFPZq
.. _`asyncore`: http://bit.ly/18W7YBP
.. _`PyZMQ`: http://bit.ly/1kYyOfy
.. _`TDD`: http://bit.ly/19EoVff
.. _`rudimentary guidance`: http://bit.ly/KiYtBb
.. _`(al)pine or pico`: http://bit.ly/1aeO0xt

Copyright
---------

Copyright (c) 2014 Matt Bogosian &lt;mtb19@columbia.edu%gt;.

Please see the LICENSE (or LICENSE.txt) file which accompanied this
software for rights and restrictions governing its use. If such a file
did not accompany this software, then please contact the author before
viewing or using this software in any capacity.

Notes
-----

<a href="#1ref" name="1"><sup>1</sup></a> I will note that decoding user
IDs *might* be related to `mjallday`’s [apparent invitation to root the
app](http://bit.ly/1kqF5R0). In fact, I’m reluctant to take that
invitation any other way based on what I’ve observed so far. I am very
reluctant to experiment with discovering and exploiting buffer overflow
vulnerabilities. Why (besides the fact that I am not very experienced at
cracking)? Because it’s running on Heroku. I have no idea with the
execution context is. I certainly can’t predict what negative side effects
would result, and how they would affect innocent parties. So, I will
politely abstain. I hope that isn’t counted against me.

<a href="#2ref" name="2"><sup>2</sup></a> Not to be confused with [another type of 401 vs. 403 analysis](http://cnnmon.ie/19BldpY).


<a href="#3ref" name="3"><sup>3</sup></a> Urwid actually does a form of
busy waiting with the Twisted reactor (see [Ian Ward’s
comment](http://bit.ly/1kkLYWl) in
``urwid.main_loop.TwistedEventLoop._enable_twisted_idle()``). This is
obviously less than ideal.
