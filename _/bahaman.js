/*=-*-mode: javascript; encoding: utf-8-*-================================
  Copyright (c) 2014 Matt Bogosian <mtb19@columbia.edu>. All rights
  reserved.
\*========================================================================*/

"use strict";

//---- Namespaces --------------------------------------------------------

/*========================================================================*\
  Bahaman namespace. */
var Bahaman = {};

//---- Classes -----------------------------------------------------------

/*========================================================================*\
  Base class for all application-specific exceptions. */
Bahaman.Exception = function () {
    Error.apply(this, arguments);
}

Bahaman.Exception.prototype = Object.create(Error.prototype);
Bahaman.Exception.prototype.constructor = Bahaman.Exception;
Bahaman.Exception.prototype.name = Bahaman.Exception.prototype.constructor.name;

/*========================================================================*\
  Class for interacting with a Balanced Hangman server (UPDATE: and now,
  as a complete hack, our own hints server). */
Bahaman.Client = function() {
    this._tested = false;
    this._email_address = null;
    this._password = null;
    this._hint_uri = urlparse.urljoin(document.baseURI, 'hint.cgi');
    this._server_uri = null;
    this._me_uri = null;
    this._prisoners_uri = null;
    // this.state = {};
}

    //---- Public class properties ---------------------------------------

Bahaman.Client.__defineGetter__('SIG_GUESS_FAIL', function() {
    return 'bahaman_guess_fail';
});

Bahaman.Client.__defineGetter__('SIG_GUESS_OKAY', function() {
    return 'bahaman_guess_okay';
});

Bahaman.Client.__defineGetter__('SIG_HINT_FAIL', function() {
    return 'bahaman_hint_fail';
});

Bahaman.Client.__defineGetter__('SIG_HINT_OKAY', function() {
    return 'bahaman_hint_okay';
});

Bahaman.Client.__defineGetter__('SIG_LOGIN_FAIL', function() {
    return 'bahaman_login_fail';
});

Bahaman.Client.__defineGetter__('SIG_LOGIN_OKAY', function() {
    return 'bahaman_login_okay';
});

Bahaman.Client.__defineGetter__('SIG_NEW_ACCT_FAIL', function() {
    return 'bahaman_new_acct_fail';
});

Bahaman.Client.__defineGetter__('SIG_NEW_ACCT_OKAY', function() {
    return 'bahaman_new_acct_okay';
});

Bahaman.Client.__defineGetter__('SIG_NEW_PRISONER_FAIL', function() {
    return 'bahaman_new_prisoner_fail';
});

Bahaman.Client.__defineGetter__('SIG_NEW_PRISONER_OKAY', function() {
    return 'bahaman_new_prisoner_okay';
});

Bahaman.Client.__defineGetter__('SIG_PRISONER_FAIL', function() {
    return 'bahaman_prisoner_fail';
});

Bahaman.Client.__defineGetter__('SIG_PRISONER_OKAY', function() {
    return 'bahaman_prisoner_okay';
});

Bahaman.Client.__defineGetter__('SIG_PRISONERS_FAIL', function() {
    return 'bahaman_prisoners_fail';
});

Bahaman.Client.__defineGetter__('SIG_PRISONERS_OKAY', function() {
    return 'bahaman_prisoners_okay';
});

    //---- Public class methods ------------------------------------------

    /*====================================================================*\
      We are hosting our own proxy as a workaround for the lack of JSONP
      support in the server reference implementation (see "Server Issues"
      section in README). */
Bahaman.Client.proxyUri = function(a_uri) {
    return Bahaman.Client._PROXY + '?' + [
        'url=' + encodeURIComponent(a_uri),
        'full_headers=1',
        'full_status=1',
    ].join('&');
}

    //---- Public properties ---------------------------------------------

    /*====================================================================*\
      Convenience getter for encoding the login e-mail address and
      password as a Basic value appropriate for the HTTP Authorization
      header. */
Bahaman.Client.prototype.__defineGetter__('auth_basic', function() {
    return (this.email_address === null
            || this.password === null)
        ? null
        : 'Basic ' + btoa(this.email_address + ':' + this.password);
});

    /*====================================================================*\
      The login e-mail address associated with this object. */
Bahaman.Client.prototype.__defineGetter__('email_address', function() {
    return this._email_address;
});

Bahaman.Client.prototype.__defineSetter__('email_address', function(a_val) {
    this._email_address = a_val;
});

    /*====================================================================*\
      The hint URI associated with this object. */
Bahaman.Client.prototype.__defineGetter__('hint_uri', function() {
    return this._hint_uri;
});

    /*====================================================================*\
      The login password associated with this object. */
Bahaman.Client.prototype.__defineGetter__('password', function() {
    return this._password;
});

Bahaman.Client.prototype.__defineSetter__('password', function(a_val) {
    this._password = a_val;
});

    /*====================================================================*\
      The tested server URI associated with this object. Setting this
      value will set me_uri and prisoners_uri to null. */
Bahaman.Client.prototype.__defineGetter__('server_uri', function() {
    return (this._tested)
        ? this._server_uri
        : null;
});

Bahaman.Client.prototype.__defineSetter__('server_uri', function(a_val) {
    this._tested = false;
    this._server_uri = a_val;
    this._me_uri = null;
    this._prisoners_uri = null;
});

//     /*====================================================================*\
//       The internal state of this object (useful for restoring a prior
//       state by reassignment). */
// Bahaman.Client.prototype.__defineGetter__('state', function() {
//     return {
//         tested: this._tested,
//         email_address: this._email_address,
//         password: this._password,
//         server_uri: this._server_uri,
//         me_uri: this._me_uri,
//         prisoners_uri: this._prisoners_uri,
//     };
// });

// Bahaman.Client.prototype.__defineSetter__('state', function(a_val) {
//     var state = {
//         _tested: false,
//         _email_address: null,
//         _password: null,
//         _hint_uri: urlparse.urljoin(document.baseURI, 'hint.cgi'),
//         _server_uri: null,
//         _me_uri: null,
//         _prisoners_uri: null,
//     };

//     $.extend(state, a_val);
//     $.extend(this, state);
// });

    /*====================================================================*\
      The tested me URI associated with this object. This is set (eventually) by
      a successful call to the testLogin method. */
Bahaman.Client.prototype.__defineGetter__('me_uri', function() {
    return (this._tested)
        ? this._me_uri
        : null;
});

    /*====================================================================*\
      The tested prisoners URI associated with this object. This is set
      (eventually) by a successful call to the testLogin method. */
Bahaman.Client.prototype.__defineGetter__('prisoners_uri', function() {
    return (this._tested)
        ? this._prisoners_uri
        : null;
});

    //---- Public methods ------------------------------------------------

    /*====================================================================*\
      Make an AJAX call to a_uri to submit a guess a_guess. This triggers
      either a SIG_GUESS_OKAY event or a SIG_GUESS_FAIL event. */
Bahaman.Client.prototype.guess = function(a_uri, a_guess) {
    var data = {
        guess: a_guess,
    };

    return this._jsonRequest(a_uri, Bahaman.Client.SIG_GUESS_OKAY, Bahaman.Client.SIG_GUESS_FAIL, { data: data, method: 'POST' });
}

    /*====================================================================*\
      Make an unauthorized AJAX call to get hints for a_word and a_misses.
      This triggers either a SIG_HINT_OKAY event or a SIG_HINT_FAIL
      event. */
Bahaman.Client.prototype.hint = function(a_word, a_misses) {
    var uri = this.hint_uri + '?word=' + encodeURIComponent(a_word) + '&misses=' + encodeURIComponent(a_misses);

    return this._jsonRequest(uri, Bahaman.Client.SIG_HINT_OKAY, Bahaman.Client.SIG_HINT_FAIL, { no_auth: true, raw_uri: true });
}

    /*====================================================================*\
      Make an unauthorized AJAX call to create a new account from the
      email_address and password members. This triggers either a
      SIG_NEW_ACCT_OKAY event or a SIG_NEW_ACCT_FAIL event. */
Bahaman.Client.prototype.newAccount = function() {
    var data = {
        email_address: this.email_address,
        password: this.password,
    };

    return this._jsonRequest(this.me_uri, Bahaman.Client.SIG_NEW_ACCT_OKAY, Bahaman.Client.SIG_NEW_ACCT_FAIL, { data: data, method: 'POST', no_auth: true });
}

    /*====================================================================*\
      Make an AJAX call to start a new game. This triggers either a
      SIG_NEW_PRISONER_OKAY event or a SIG_NEW_PRISONER_FAIL event. */
Bahaman.Client.prototype.newPrisoner = function() {
    return this._jsonRequest(this.prisoners_uri, Bahaman.Client.SIG_NEW_PRISONER_OKAY, Bahaman.Client.SIG_NEW_PRISONER_FAIL, { method: 'POST' });
}

    /*====================================================================*\
      Make an AJAX call to retrieve the state of an existing game. This
      triggers either a SIG_PRISONER_OKAY event or a SIG_PRISONER_FAIL
      event. */
Bahaman.Client.prototype.prisoner = function(a_uri) {
    return this._jsonRequest(a_uri, Bahaman.Client.SIG_PRISONER_OKAY, Bahaman.Client.SIG_PRISONER_FAIL);
}

    /*====================================================================*\
      Make an AJAX call to retrieve the states of existing games. If a_uri
      is present, it is used. Otherwise, prisoners_uri is used. (This is
      to enable paging, which appears broken; see "Server Issues" section
      in README.) This triggers either a SIG_PRISONERS_OKAY event or a
      SIG_PRISONERS_FAIL event. */
Bahaman.Client.prototype.prisoners = function(a_uri /* = null */) {
    var uri = (! a_uri)
        ? this.prisoners_uri
        : a_uri;

    return this._jsonRequest(uri, Bahaman.Client.SIG_PRISONERS_OKAY, Bahaman.Client.SIG_PRISONERS_FAIL);
}

    /*====================================================================*\
      Make an AJAX call to server_uri to check the validity of the login
      information. This triggers either a SIG_LOGIN_OKAY event or a
      SIG_LOGIN_FAIL event. */
Bahaman.Client.prototype.testLogin = function() {
    return this._jsonRequest(this._server_uri, Bahaman.Client.SIG_LOGIN_OKAY, Bahaman.Client.SIG_LOGIN_FAIL, { on_success: this._testLoginSucceed.bind(this) });
    
    // // Force authorization (even if we don't have a login yet)
    // var headers = {};

    // if (this.auth_basic === null) {
    //     var event = {
    //         type: Bahaman.Client.SIG_LOGIN_FAIL,
    //         client: this,
    //     };

    //     return $.event.trigger(event);
    // }

    // return this._jsonRequest(this._server_uri, Bahaman.Client.SIG_LOGIN_OKAY, Bahaman.Client.SIG_LOGIN_FAIL, 'GET', null, headers, this._testLoginSucceed.bind(this));
}

    //---- Private class properties --------------------------------------

Bahaman.Client.__defineGetter__('_PROXY', function() {
    return '_/3rdparty/php-simple-proxy/ba-simple-proxy.php';
});

    //---- Private methods -----------------------------------------------

    /*====================================================================*\
      Calls jQuery.ajax with a_uri and the events a_sig_success and
      a_sig_error. a_options, if provided, should contain one or more of
      the following:

      - data (default: null) - If a string, it is submitted unchanged to
        the server unchanged. If it is not a string, it is encoded as
        JSON, and submitted to server with a "Content-Type" header of
        "application/json".

      - headers (default: {}) - Overrides any request headers (e.g.,
        "Content-Type").

      - method (default: 'GET') - The request method.

      - no_auth (default: false) - If true, do not perform any
        authorization, even if credentials are available.

      - on_success (default: null) - Called with (a_req, a_event) after a
        successful AJAX call, where a_req is the jqXHR object and a_event
        is the event to be triggered.

      - on_error (default: null) - Called with (a_req, a_event) after a
        failed AJAX call.

      - raw_url (default: false) - If true, the AJAX call is made the
        request directly to a_uri, without joining or proxying.

      Returns the jqXHR promise object from the underlying jQuery.ajax
      call. */
Bahaman.Client.prototype._jsonRequest = function(a_uri, a_sig_success, a_sig_error, a_options /* = {} */) {
    var options = {
        data: null,
        headers: {},
        method: 'GET',
        no_auth: false,
        on_success: null,
        on_error: null,
        raw_url: false,
    };

    $.extend(options, a_options);

    var ajax_settings = {
        error: this._jsonRequestFail.bind(this, a_sig_error, options.on_error),
        headers: {},
        success: this._jsonRequestSucceed.bind(this, a_sig_success, a_sig_error, options.on_success, options.on_error),
        type: options.method,
    };

    if (options.data) {
        if (typeof(options.data) !== 'string') {
            options.data = JSON.stringify(options.data);
            ajax_settings.headers['Content-Type'] = 'application/json';
        }

        ajax_settings.data = options.data;
        ajax_settings.processData = false;
    }

    var auth_basic = this.auth_basic;

    if (! options.no_auth
            && auth_basic !== null) {
        ajax_settings.headers['X-Authorization'] = auth_basic;
    }

    $.extend(ajax_settings.headers, options.headers);

    var uri = a_uri;

    if (! options.raw_uri) {
        uri = Bahaman.Client.proxyUri(urlparse.urljoin(this._server_uri, uri));
    }

    return $.ajax(uri, ajax_settings);
}

    /*====================================================================*\
      Helper method called when an AJAX query returns with an error. */
Bahaman.Client.prototype._jsonRequestFail = function(a_sig_error, a_on_error, a_req, a_status, a_err, a_data /* = null */) {
    var data = (typeof(a_data) === 'undefined'
            || a_data === null)
        ? a_req.responseJSON
        : a_data;

    var event = {
        client: this,
        err: a_err,
        status: a_status,
        type: a_sig_error,
    };

    // Intervene to override a_sig_error if we have a login error (this is
    // a best guess; see "Authentication Oddities" section in README)
    if (a_status === 401
            || a_status === 403
            || (data
                && (a_status < 200
                    || a_status >= 300)
                && 'contents' in data
                && 'description' in data.contents
                && data.contents.description.toLowerCase().startsWith('user ')
                && data.contents.description.toLowerCase().startsWith(' not found'))
            || (data
                && 'contents' in data
                && data.contents === null)) {
        event.type = Bahaman.Client.SIG_LOGIN_FAIL;
    }

    if (data) {
        event.rsp_data = data;
    }

    if (a_on_error) {
        a_on_error(a_req, event);
    }

    return $.event.trigger(event);
}

    /*====================================================================*\
      Helper method called when an AJAX query returns. Note: this may call
      _jsonRequestFail if it recognizes a failure based on the content or
      payload of an otherwise successful response. */
Bahaman.Client.prototype._jsonRequestSucceed = function(a_sig_success, a_sig_error, a_on_success, a_on_error, a_data, a_status, a_req) {
    var status = a_req.status;
    var err = a_req.statusText;

    if ('status' in a_data) {
        status = a_data.status.http_code;
    }

    if (status < 200
            || status >= 300) {
        if ('contents' in a_data
                && a_data.contents !== null) {
            if ('status' in a_data.contents) {
                err = a_data.contents.status;
            } else if ('description' in a_data.contents) {
                err = a_data.contents.description;
            } else if ('message' in a_data) {
                err = a_data.message;
            }
        }

        return this._jsonRequestFail(a_sig_error, a_on_error, a_req, status, err, a_data);
    }

    var event = {
        client: this,
        rsp_data: a_data,
        status: a_status,
        type: a_sig_success,
    };

    if (a_on_success) {
        a_on_success(a_req, event);
    }

    return $.event.trigger(event);
}

    /*====================================================================*\
      Hook function called when the testLogin method succeeds. */
Bahaman.Client.prototype._testLoginSucceed = function(a_req, a_event) {
    this._me_uri = a_event.rsp_data.contents.me;
    this._prisoners_uri = a_event.rsp_data.contents.prisoners;
    this._tested = true;
}

/*========================================================================*\
  Class to represent a single game and its state. */
Bahaman.Game = function(a_state /* = {} */) {
    var state = (typeof(a_state) === 'undefined')
        ? {}
        : a_state;

    this.state = state;
}

    //---- Public class properties ---------------------------------------

Bahaman.Game.__defineGetter__('ALPHABET', function() {
    return 'abcdefghijklmnopqrstuvwxyz';
});

    //---- Public class methods ------------------------------------------

    /*====================================================================*\
      Comparison function for two Game objects used in to sort them, first
      by whether they are active (with active games appearing first), then
      by ascending inception date. */
Bahaman.Game.compare = function(a_l, a_r) {
    var l_state = a_l._state;
    var r_state = a_r._state;

    if (l_state.state !== r_state.state) {
        if (l_state.state === 'help') {
            return -1;
        }

        if (r_state.state === 'help') {
            return 1;
        }
    }

    return l_state.imprisoned_at - r_state.imprisoned_at;
}

    //---- Public properties ---------------------------------------------

    /*====================================================================*\
      The game state associated with this object. Assignment will
      normalize certain data. */
Bahaman.Game.prototype.__defineGetter__('state', function() {
    return this._state;
});

Bahaman.Game.prototype.__defineSetter__('state', function(a_val) {
    var state = {
        hits: [],
        misses: [],
    };

    $.extend(state, a_val);

    if ('word' in state) {
        state.word = state.word.toLowerCase();
    }

    if (typeof(state.imprisoned_at) === 'string') {
        state.imprisoned_at = Date.parse(state.imprisoned_at);
        state.imprisoned_at = new Date(state.imprisoned_at);
    }

    var i;

    for (i in state.hits) {
        state.hits[i] = state.hits[i].toLowerCase();
    }

    for (i in state.misses) {
        state.misses[i] = state.misses[i].toLowerCase();
    }

    var total_guesses = state.guesses_remaining + state.hits.length + state.misses.length;

    this._state = state;
});

/*========================================================================*\
  Class for interacting with a Balanced Hangman server. */
Bahaman.Screen = function() {
    // Wire up the handlers
    var guessOkay = this._guessOkay.bind(this);
    var guessFail = this._guessFail.bind(this);
    var hintOkay = this._hintOkay.bind(this);
    var hintFail = this._hintFail.bind(this);
    var loginOkay = this._loginOkay.bind(this);
    var loginFail = this._loginFail.bind(this);
    var newPrisonerOkay = this._newPrisonerOkay.bind(this);
    var prisonersOkay = this._prisonersOkay.bind(this);
    $(document).on(Bahaman.Client.SIG_GUESS_OKAY, guessOkay);
    $(document).on(Bahaman.Client.SIG_GUESS_FAIL, guessFail);
    $(document).on(Bahaman.Client.SIG_HINT_OKAY, hintOkay);
    $(document).on(Bahaman.Client.SIG_HINT_FAIL, hintFail);
    $(document).on(Bahaman.Client.SIG_LOGIN_OKAY, loginOkay);
    $(document).on(Bahaman.Client.SIG_LOGIN_FAIL, loginFail);
    $(document).on(Bahaman.Client.SIG_NEW_ACCT_OKAY, loginOkay);
    $(document).on(Bahaman.Client.SIG_NEW_ACCT_FAIL, loginFail);
    $(document).on(Bahaman.Client.SIG_NEW_PRISONER_OKAY, newPrisonerOkay);
    $(document).on(Bahaman.Client.SIG_NEW_PRISONER_FAIL, loginFail);
    $(document).on(Bahaman.Client.SIG_PRISONER_OKAY, guessOkay);
    $(document).on(Bahaman.Client.SIG_PRISONERS_OKAY, prisonersOkay);
    $(document).on(Bahaman.Client.SIG_PRISONERS_FAIL, loginFail);

    // Set up the initial screen
    $('#nojs').css('display', 'none');
    Bahaman.Screen._word($('#word').text());

    // Set up our various modals
    $('#seriously_show').click(function (e) {
        $('#seriously').modal();

        return false;
    });

    $('#login_show').click(function (e) {
        // TODO: don't use the global reference here; it works, but it's
        // bad form
        Bahaman._.screen.loginShow();

        return false;
    });

    $('#login_go').click(this.loginGo.bind(this));
    $('#login form').submit(this.loginGo.bind(this));
    $('#login_create').click(this.loginGo.bind(this));
    $('#new_prisoner').click(this.newPrisonerGo.bind(this));

    $('#help_show').click(function (e) {
        $('#help').modal();

        return false;
    });

    $('#license_show').click(function (e) {
        $('#license').modal();

        return false;
    });

    $('#egg_show').click(function (e) {
        $('#egg').modal();

        return false;
    });

    $('#egg > a').click(function (e) {
        return true;
    });

    $('#guesses button').click(this.guessGo.bind(this));

    var cheat_ambient = $('#cheat_ambient')[0];
    cheat_ambient.volume -= 0.5;
    var cheat_go = $('#cheat_go')[0];
    cheat_go.volume -= 0.5;
    var cheat_step = $('#cheat_step')[0];
    cheat_step.volume -= 0.5;

    $('#guess_a').bind('click.cheat_start', function(a_event) {
        $('#guess_a').unbind('click.cheat_start');
        cheat_ambient.play();
    });

    $('#guess_a').bind('click.cheat_step', function(a_event) {
        var visible = $('#cheat_code > span:first-of-type');
        var hidden = $('#cheat_code > span:last-of-type');
        var hidden_text = hidden.text();
        var next_break = hidden_text.indexOf(' ');

        if (next_break > 0) {
            visible.text(visible.text() + ' ' + hidden_text.slice(0, next_break));
            hidden.text(hidden_text.slice(next_break + 1));
        } else {
            visible.text(visible.text() + ' ' + hidden_text);
            hidden.text('');
            $('#guess_a').unbind('click.cheat_step');

            $('#guess_a').bind('click.cheat_end', function(a_event) {
                $('#cheat_code').css('display', 'none');
                $('#hints').css('display', 'inline-block');
                $('#guess_a').unbind('click.cheat_end')
                    .prop('disabled', true);
                cheat_ambient.pause();
                cheat_ambient.currentTime = 0;
                cheat_go.play();
            });
        }

        cheat_step.pause();
        cheat_step.currentTime = 0;
        cheat_step.play();
    });
}

    //---- Public methods ------------------------------------------------

    /*====================================================================*\
      Activate a game selected from the prisoners list. */
Bahaman.Screen.prototype.gameSelect = function(a_event) {
    return this._activateGame($(a_event.target).parents('#prisoners_list li').prop('_game'));
}

    /*====================================================================*\
      Submits a guess. */
Bahaman.Screen.prototype.guessGo = function(a_event) {
    var button = a_event.target;
    var game = $('#game').prop('_game');
    var guess = $(button).prop('id');

    if (! game
            || typeof(guess) !== 'string'
            || guess.indexOf('guess_') !== 0) {
        return;
    }

    guess = guess.slice(-1);
    this._messagePending('Submitting guess...');
    Bahaman._.client.guess(game.state.guesses, guess);

    return false;
}

    /*====================================================================*\
      Attempts a login from the account window. */
Bahaman.Screen.prototype.loginGo = function(a_event) {
    $('#login_show').prop('disabled', true);
    $('#new_prisoner').prop('disabled', true);
    this._prisonersLoading();
    var new_account = (a_event.target === $('#login_create')[0]);

    console.log(JSON.stringify(Bahaman._.client));
    console.log(a_event.target);
    console.log(new_account);

    if (new_account) {
        this._messagePending('Creating account...');
        Bahaman._.client.newAccount();
    } else {
        var email_address = $("#login input[name='email_address'][type='email']").val();
        var password = $("#login input[name='password'][type='password']").val();
        var server_uri = $("#login input[name='server_uri'][type='url']").val();

        if (Bahaman._.client.server_uri !== server_uri) {
            console.log('server_uri was: ' + Bahaman._.client.server_uri);
            Bahaman._.client.server_uri = 'https://balanced-hangman.herokuapp.com/';
            console.log('Set server_uri to: ' + Bahaman._.client._server_uri);
        }

        Bahaman._.client.email_address = email_address;
        Bahaman._.client.password = password;
        this._messagePending('Logging in...');
        Bahaman._.client.testLogin();
    }

    $.modal.close();

    return false;
}

    /*====================================================================*\
      Shows the account window. */
Bahaman.Screen.prototype.loginShow = function(a_msg /* = null */) {
    var msg = (typeof(a_msg) === 'undefined')
        ? null
        : a_msg;

    var updateModalLoginMessage = this._updateModalLoginMessage.bind(this);
 
    var shown = $('#login').modal({
        onShow: function(a_dialog) {
            updateModalLoginMessage(msg);
        },
    });

    if (! shown) {
        updateModalLoginMessage(msg);
    }

    return false;
}

    /*====================================================================*\
      Attempts to start a new game. */
Bahaman.Screen.prototype.newPrisonerGo = function(a_event) {
    this._messagePending('Starting new game...');
    Bahaman._.client.newPrisoner();

    return false;
}

    /*====================================================================*\
      Attempts to update the prisoners list. */
Bahaman.Screen.prototype.prisonersGo = function(a_event /* = null */) {
    var event = (typeof(a_event) === 'undefined')
        ? null
        : a_event;

    var uri = null;

    if (event !== null
            && 'target' in event) {
        uri = $(event.target).prop('_prisoners_nav_uri');
    }

    this._prisonersLoading();
    this._messagePending('Retrieving games...');
    Bahaman._.client.prisoners(uri);

    return false;
}

    //---- Private methods -----------------------------------------------

    /*====================================================================*\
      Set the active game. */
Bahaman.Screen.prototype._activateGame = function(a_game /* = null */) {
    var game = (typeof(a_game) === 'undefined')
        ? null
        : a_game;

    $('#guess_a').unbind('click.cheat_start')
        .unbind('click.cheat_step')
        .unbind('click.cheat_end');

    if (game) {
        this.prisonersGo();
        this._updateSelectedGame(game);
    }

    return false;
}

    /*====================================================================*\
      Handle a failed submitted guess. */
Bahaman.Screen.prototype._guessFail = function(a_event) {
    var game = $('#game').prop('_game');

    // Refresh the game state
    if (game) {
        Bahaman._.client.prisoner(game.state.uri);
    }

    return false;
}

    /*====================================================================*\
      Handle a successfully submitted guess. */
Bahaman.Screen.prototype._guessOkay = function(a_event) {
    var game = $('#game').prop('_game');

    if (game.state.id === a_event.rsp_data.contents.id) {
        game.state = a_event.rsp_data.contents;
        this._updateSelectedGame(game);
        this._messageLoggedIn();
    }

    return false;
}

    /*====================================================================*\
      Handle a failed hint request. */
Bahaman.Screen.prototype._hintFail = function(a_event) {
    var msg = '';

    if ('rsp_data' in a_event
            && 'message' in a_event.rsp_data) {
        msg += a_event.rsp_data.message;
    } else if ('err' in a_event) {
        msg += (msg
                ? ': '
                : '') + a_event.err;
    }

    $('#hints').text(msg);

    return false;
}

    /*====================================================================*\
      Handle a successful hint request. */
Bahaman.Screen.prototype._hintOkay = function(a_event) {
    var frequencies = a_event.rsp_data.frequencies;

    for (var c in frequencies) {
        var freq = frequencies[c];
        var button = $('#guess_' + c);
        button.removeClass();

        if (freq === 1.0) {
            button.addClass('best_hint');
        } else {
            button.addClass('hint');
        }
    }

    $('#hints').text(a_event.rsp_data.candidates);

    return false;
}

    /*====================================================================*\
      Hanle a failed login. */
Bahaman.Screen.prototype._loginFail = function(a_event) {
    var msg = null;

    if ('rsp_data' in a_event
            && a_event.rsp_data !== null
            && 'contents' in a_event.rsp_data
            && a_event.rsp_data.contents !== null
            && 'description' in a_event.rsp_data.contents) {
        msg = a_event.rsp_data.contents.description;
    } else if ('err' in a_event) {
        msg = a_event.err;
    }

    this._messageErr('Not logged in');
    $('#login_show').prop('disabled', false);
    $('#new_prisoner').prop('disabled', true);
    $('#prisoners_list .loading')
        .css('display', 'none');
    this.loginShow(msg);

    return false;
}

    /*====================================================================*\
      Handle a successful login. */
Bahaman.Screen.prototype._loginOkay = function(a_event) {
    if (Bahaman._.client.email_address === null) {
        return this._loginFail(a_event);
    }

    this._messageLoggedIn();
    $('#new_prisoner').prop('disabled', false);

    return this.prisonersGo();
}

    /*====================================================================*\
      Update the status message with a_err. */
Bahaman.Screen.prototype._messageErr = function(a_err) {
    return $('#message').removeClass('okay pending')
        .addClass('err')
        .text(a_err);
}

    /*====================================================================*\
      Update the status message with the current login. */
Bahaman.Screen.prototype._messageLoggedIn = function() {
    this._messageOkay('Logged in as <' + Bahaman._.client.email_address + '>');
}

    /*====================================================================*\
      Update the status message with a_msg. */
Bahaman.Screen.prototype._messageOkay = function(a_msg) {
    return $('#message').removeClass('err pending')
        .addClass('okay')
        .text(a_msg);
}

    /*====================================================================*\
      Update the status message with a_msg, where a_msg is a temporary
      status message. */
Bahaman.Screen.prototype._messagePending = function(a_msg) {
    return $('#message').removeClass('err okay')
        .addClass('pending')
        .text(a_msg);
}

    /*====================================================================*\
      Handle a successful request to start a new game. */
Bahaman.Screen.prototype._newPrisonerOkay = function(a_event) {
    return this._activateGame(new Bahaman.Game(a_event.rsp_data.contents));
}

    /*====================================================================*\
      Clear the prisoners list and show a loading graphic. */
Bahaman.Screen.prototype._prisonersLoading = function() {
    $('#prisoners_first').prop('disabled', true)
        .removeProp('_prisoners_nav_uri')
        .unbind('click');
    $('#prisoners_prev').prop('disabled', true)
        .removeProp('_prisoners_nav_uri')
        .unbind('click');
    $('#prisoners_next').prop('disabled', true)
        .removeProp('_prisoners_nav_uri')
        .unbind('click');
    $('#prisoners_last').prop('disabled', true)
        .removeProp('_prisoners_nav_uri')
        .unbind('click');

    var prisoners_list_items = $('#prisoners_list li');

    for (var i = 2;
            i < prisoners_list_items.length;
            ++i) {
        prisoners_list_items[i].remove();
    }

    $('#prisoners_list .loading').css('display', 'inline');
}

    /*====================================================================*\
      Handle a successful request to retrieve a list of prisoners. */
Bahaman.Screen.prototype._prisonersOkay = function(a_event) {
    $('#login_show').prop('disabled', false);
    $('#prisoners_list .loading').css('display', 'none');

    var contents = a_event.rsp_data.contents;
    var first = contents.first;
    var prev = contents.prev;
    var next = contents.next;
    var last = contents.last;

    if (prev) {
        $('#prisoners_first').click(this.prisonersGo.bind(this))
            .prop('_prisoners_nav_uri', first)
            .prop('disabled', false);
        $('#prisoners_prev').click(this.prisonersGo.bind(this))
            .prop('_prisoners_nav_uri', prev)
            .prop('disabled', false);
    }

    if (next) {
        $('#prisoners_next').click(this.prisonersGo.bind(this))
            .prop('_prisoners_nav_uri', next)
            .prop('disabled', false);
        $('#prisoners_last').click(this.prisonersGo.bind(this))
            .prop('_prisoners_nav_uri', last)
            .prop('disabled', false);
    }

    var list = $('#prisoners_list');
    var list_item_tmpl = $('#prisoners_list_item');
    var games = [];

    for (var item in contents.items) {
        games.push(new Bahaman.Game(contents.items[item]));
    }

    var active_game = $('#game').prop('_game');
    games.sort(Bahaman.Game.compare);
    var now = Date.now();

    for (var game in games) {
        game = games[game];

        // Skip the active game, if it appears in the list
        if (active_game
            && game.state.id === active_game.state.id) {
            continue;
        }

        var list_item = list_item_tmpl.clone();
        list_item.removeAttr('id')
            .removeAttr('style')
            .addClass('game_' + game.state.state)
            .appendTo(list);
        var list_item_div = list_item.find('div:first-of-type');
        var word = list_item_div.text(game.state.word)
            .html();
        var list_item_div_html = '';

        if (game.state.state === 'help') {
            var uri = list_item_div.text(game.state.uri)
                .html();
            list_item_div_html += '<a href="#">' + word + '</a>';
        } else {
            list_item_div_html += word;
        }

        list_item_div_html += '<br>';
        var guesses = [];
        var i;

        for (i in game.state.hits) {
            guesses.push({
                'l': list_item_div.text(game.state.hits[i])
                    .html(),
                's': 'hit',
            });
        }

        for (i in game.state.misses) {
            guesses.push({
                'l': list_item_div.text(game.state.misses[i])
                    .html(),
                's': 'miss',
            });
        }

        guesses.sort(function (a_l, a_r) {
            return (a_l.l < a_r.l)
                ? -1
                : (a_l.l > a_r.l)
                    ? 1
                    : 0;
        });

        for (i = 0;
                i < guesses.length;
                ++i) {
            guesses[i] = '<span class="' + guesses[i].s + '">'
                + guesses[i].l
                + '</span>';
        }

        list_item_div_html += guesses.join('')
            + '<br>'
            + parseInt((now - game.state.imprisoned_at) / 86400000) + ' days old';

        if (game.state.state === 'help') {
            list_item_div_html += '<br>'
                + game.state.guesses_remaining + ' tries left';
        }

        list_item_div.html(list_item_div_html)
            .find('a')
            .click(this.gameSelect.bind(this));
        list_item.prop('_game', game);
    }

    this._messageLoggedIn();

    return false;
}

    /*====================================================================*\
      Update the server status message in the account window. */
Bahaman.Screen.prototype._updateModalLoginMessage = function(a_msg) {
    $("#login input[name='server_uri'][type='url']").val(Bahaman._.client._server_uri);
    $("#login input[name='email_address'][type='email']").val(Bahaman._.client.email_address);
    $("#login input[name='password'][type='password']").val(Bahaman._.client.password);

    if (a_msg) {
        $('#login .status').css('display', 'block')
            .addClass('err');
        $("#login_message").html(a_msg);
        $("#login_create").prop('disabled', false);
    } else {
        $('#login .status').css('display', 'none')
            .removeClass('err');
        $("#login_create").prop('disabled', true);
    }
}

    /*====================================================================*\
      Update the state of the active game. */
Bahaman.Screen.prototype._updateSelectedGame = function(a_game) {
    $('#game').prop('_game', a_game);
    var done = a_game.state.state !== 'help';
    Bahaman.Screen._word(a_game.state.word);
    $('#progress_counter').removeClass()
        .text(a_game.state.guesses_remaining)
        .css('opacity', 0.8);

    if (done) {
        $('#progress_counter').addClass('done');
    }

    $('#guesses button').prop('disabled', true);

    var hits = a_game.state.hits.join('');
    var misses = a_game.state.misses.join('');

    for (var c in Bahaman.Game.ALPHABET) {
        c = Bahaman.Game.ALPHABET[c];
        var button = $('#guess_' + c);
        button.removeClass();

        if (hits.indexOf(c) >= 0) {
            button.addClass('hit');
        } else if (misses.indexOf(c) >= 0) {
            button.addClass('miss');
        } else if (! done) {
            button.prop('disabled', false);
        }
    }

    var hints = $('#hints');

    if (hints.css('display') !== 'none') {
        hints.text('Retrieving hints...');
        Bahaman._.client.hint(a_game.state.word, misses);
    }
}

    //---- Private class methods -----------------------------------------

    /*====================================================================*\
      Helper method to replace asterisks with '&emsp;' for displaying the
      word associated with the active game. */
Bahaman.Screen._word = function(a_word) {
    var word = $('#word');
    word.text(a_word)
        .html(word.text().replace(/\*/g, '&emsp;'))
        .lettering();
}

//---- Initialization ----------------------------------------------------

window.Bahaman = Bahaman;

// Instance namespace
Bahaman._ = {};

$(document).ready(function ($) {
    Bahaman._.screen = new Bahaman.Screen();
    Bahaman._.client = new Bahaman.Client();
});

$(window).on('load', function() {
    console.log('server_uri was: ' + Bahaman._.client.server_uri);
    Bahaman._.client.server_uri = 'https://balanced-hangman.herokuapp.com/';
    console.log('Set server_uri to: ' + Bahaman._.client._server_uri);
    Bahaman._.client.testLogin();
});
