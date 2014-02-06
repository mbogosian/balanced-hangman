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
  Class for interacting with a Balanced Hangman server. */
Bahaman.Client = function() {
    this.state = {};
}

    //---- Public class properties ---------------------------------------

Bahaman.Client.__defineGetter__('SIG_GUESS_FAIL', function() {
    return 'bahaman_guess_fail';
});

Bahaman.Client.__defineGetter__('SIG_GUESS_OKAY', function() {
    return 'bahaman_guess_okay';
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
    this._dirty();
    this._email_address = a_val;
});

    /*====================================================================*\
      The login password associated with this object. */
Bahaman.Client.prototype.__defineGetter__('password', function() {
    return this._password;
});

Bahaman.Client.prototype.__defineSetter__('password', function(a_val) {
    this._dirty();
    this._password = a_val;
});

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype.__defineGetter__('server_uri', function() {
    return (this._tested)
        ? this._server_uri
        : null;
});

Bahaman.Client.prototype.__defineSetter__('server_uri', function(a_val) {
    this._dirty();
    this._server_uri = a_val;
    this._me_uri = null;
    this._prisoners_uri = null;
});

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype.__defineGetter__('state', function() {
    return {
        tested: this._tested,
        email_address: this._email_address,
        password: this._password,
        server_uri: this._server_uri,
        me_uri: this._me_uri,
        prisoners_uri: this._prisoners_uri,
    };
});

Bahaman.Client.prototype.__defineSetter__('state', function(a_val) {
    var state = {
        tested: false,
        email_address: null,
        password: null,
        server_uri: null,
        me_uri: null,
        prisoners_uri: null,
    };

    $.extend(state, a_val);
    $.extend(this, state);
});

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype.__defineGetter__('me_uri', function() {
    return (this._tested)
        ? this._me_uri
        : null;
});

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype.__defineGetter__('prisoners_uri', function() {
    return (this._tested)
        ? this._prisoners_uri
        : null;
});

    //---- Public methods ------------------------------------------------

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype.guess = function(a_uri, a_guess) {
    var data = {
        guess: a_guess,
    };

    return this._jsonRequest(a_uri, this._guessSucceed.bind(this), this._guessFail.bind(this), 'POST', data);
}

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype.newAccount = function() {
    var data = {
        email_address: this.email_address,
        password: this.password,
    };

    return this._jsonRequest(this.me_uri, this._newAccountSucceed.bind(this), this._newAccountFail.bind(this), 'POST', data);
}

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype.prisoners = function(a_uri /* = null */) {
    var uri = (! a_uri)
        ? this.prisoners_uri
        : a_uri;

    return this._jsonRequest(uri, this._prisonersSucceed.bind(this), this._prisonersFail.bind(this));
}

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype.testLogin = function() {
    // Make sure we don't trigger an event
    this._tested = false;

    // Reset the dependent URIs
    this.server_uri = this._server_uri;

    // Force authorization (even if we don't have a login yet)
    var headers = {};

    if (this.auth_basic === null) {
        this.triggerNoLogin();

        return;
    }

    return this._jsonRequest(this._server_uri, this._testLoginSucceed.bind(this), this._testLoginFail.bind(this), 'GET', null, headers);
}

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype.triggerNoLogin = function() {
    var event = {
        type: Bahaman.Client.SIG_LOGIN_FAIL,
        client: this,
    };

    return $.event.trigger(event);
}

    //---- Private class properties --------------------------------------

Bahaman.Client.__defineGetter__('_PROXY', function() {
    return '_/3rdparty/php-simple-proxy/ba-simple-proxy.php';
});

    //---- Private methods -----------------------------------------------

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype._dirty = function() {
    if (! this._tested) {
        return;
    }

    this._tested = false;
    //this.triggerNoLogin();
}

    /*====================================================================*\
      Calls jQuery.ajax with a_uri and the handlers a_on_success and
      a_on_error. The signature of those handlers should be (a_req,
      a_event), where a_req is the jqXHR object and a_event is the event
      to be triggered upon return of the handler. If provided, a_method
      determines the request method. If a_data is provided and is a
      string, it is submitted unchanged to the server. If it is not a
      string, it is encoded as JSON, and submitted to server with a
      "Content-Type" header of "application/json". a_headers, if submitted
      is merged with any headers submitted to the server just before
      submission (i.e., it can be used to override any header set by this
      method, such as "Content-Type"). Returns the jqXHR promise object
      from the underlying jQuery.ajax call. */
Bahaman.Client.prototype._jsonRequest = function(a_uri, a_on_success, a_on_error, a_method /* = 'GET' */, a_data /* = null */, a_headers /* = {} */) {
    var method = (typeof(a_method) === 'undefined')
        ? 'GET'
        : a_method;

    var data = (typeof(a_data) === 'undefined')
        ? null
        : a_data;

    var headers = (typeof(a_headers) === 'undefined')
        ? {}
        : a_headers;

    var ajax_settings = {
        error: this._jsonRequestFail.bind(this, a_on_error),
        headers: {},
        success: this._jsonRequestSucceed.bind(this, a_on_success, a_on_error),
        type: method,
    };

    if (data) {
        if (typeof(data) !== 'string') {
            data = JSON.stringify(data);
            ajax_settings.headers['Content-Type'] = 'application/json';
        }

        ajax_settings.data = data;
        ajax_settings.processData = false;
    }

    var auth_basic = this.auth_basic;

    if (auth_basic !== null) {
        ajax_settings.headers['X-Authorization'] = auth_basic;
    }

    $.extend(ajax_settings.headers, headers);

    return $.ajax(Bahaman.Client.proxyUri(urlparse.urljoin(this._server_uri, a_uri)), ajax_settings);
}

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype._jsonRequestFail = function(a_on_error, a_req, a_status, a_err, a_data /* = null */) {
    var data = (typeof(a_data) === 'undefined')
        ? null
        : a_data;

    var event = {
        client: this,
        err: a_err,
        status: a_status,
    };

    if (data) {
        event.rsp_data = a_data;
    }

    a_on_error(a_req, event);

    return $.event.trigger(event);
}

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype._jsonRequestSucceed = function(a_on_success, a_on_error, a_data, a_status, a_req) {
    if (a_data.status.http_code < 200
            || a_data.status.http_code >= 300) {
        var status = null;

        if ('contents' in a_data
                && a_data.contents !== null) {
            if ('status' in a_data.contents) {
                status = a_data.contents.status;
            } else if ('description' in a_data.contents) {
                status = a_data.contents.description;
            }
        }

        return this._jsonRequestFail(a_on_error, a_req, a_data.status.http_code, status, a_data);
    }

    var event = {
        client: this,
        rsp_data: a_data,
        status: a_status,
    };

    a_on_success(a_req, event);

    return $.event.trigger(event);
}

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype._guessFail = function(a_req, a_event) {
    a_event.type = Bahaman.Client.SIG_GUESS_FAIL;
}

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype._guessSucceed = function(a_req, a_event) {
    a_event.type = Bahaman.Client.SIG_GUESS_OKAY;
}

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype._newAccountFail = function(a_req, a_event) {
    a_event.type = Bahaman.Client.SIG_NEW_ACCT_FAIL;
}

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype._newAccountSucceed = function(a_req, a_event) {
    a_event.type = Bahaman.Client.SIG_NEW_ACCT_OKAY;
}

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype._prisonersFail = function(a_req, a_event) {
    a_event.type = Bahaman.Client.SIG_PRISONERS_FAIL;
}

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype._prisonersSucceed = function(a_req, a_event) {
    a_event.type = Bahaman.Client.SIG_PRISONERS_OKAY;
}

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype._testLoginFail = function(a_req, a_event) {
    a_event.type = Bahaman.Client.SIG_LOGIN_FAIL;
}

    /*====================================================================*\
      TODO */
Bahaman.Client.prototype._testLoginSucceed = function(a_req, a_event) {
    this._me_uri = a_event.rsp_data.contents.me;
    this._prisoners_uri = a_event.rsp_data.contents.prisoners;
    this._tested = true;
    a_event.type = Bahaman.Client.SIG_LOGIN_OKAY;
}

/*========================================================================*\
  TODO */
Bahaman.Game = function(a_state /* = {} */) {
    var state = (typeof(a_state) === 'undefined')
        ? null
        : a_state;

    this.state = state;
}

    //---- Public class properties ---------------------------------------

Bahaman.Game.__defineGetter__('ALPHABET', function() {
    return 'abcdefghijklmnopqrstuvwxyz';
});

    //---- Public class methods ------------------------------------------

    /*====================================================================*\
      TODO */
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
      TODO */
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
    $(document).on(Bahaman.Client.SIG_GUESS_OKAY, this.guessOkay.bind(this));
    $(document).on(Bahaman.Client.SIG_GUESS_FAIL, this.loginFail.bind(this));
    $(document).on(Bahaman.Client.SIG_LOGIN_OKAY, this.loginOkay.bind(this));
    $(document).on(Bahaman.Client.SIG_LOGIN_FAIL, this.loginFail.bind(this));
    $(document).on(Bahaman.Client.SIG_PRISONERS_OKAY, this.prisonersOkay.bind(this));
    $(document).on(Bahaman.Client.SIG_PRISONERS_FAIL, this.loginFail.bind(this));

    $('#nojs').css('display', 'none');
    this._word($('#word').text());

    $('#seriously_show').click(function (e) {
        $('#seriously').modal();

        return false;
    });

    $('#login_show').click(function (e) {
        Bahaman._.screen.loginShow();

        return false;
    });

    $('#login_go').click(this.loginGo.bind(this));
    $('#login form').submit(this.loginGo.bind(this));

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
}

    //---- Public methods ------------------------------------------------

    /*====================================================================*\
      TODO */
Bahaman.Screen.prototype.gameSelect = function(a_event) {
    var game = $(a_event.target).parents('#prisoners_list li').prop('_game');

    if (game) {
        this._updateSelectedGame(game);
    }

    return false;
}

    /*====================================================================*\
      TODO */
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
      TODO */
Bahaman.Screen.prototype.guessOkay = function(a_event) {
    var game = $('#game').prop('_game');
    game.state = a_event.rsp_data.contents;
    this._updateSelectedGame(game);
    this._messageLoggedIn();

    return false;
}

    /*====================================================================*\
      TODO */
Bahaman.Screen.prototype.loginFail = function(a_event) {
    var status = null;

    if ('rsp_data' in a_event
            && a_event.rsp_data !== null
            && 'contents' in a_event.rsp_data
            && a_event.rsp_data.contents !== null
            && 'description' in a_event.rsp_data.contents) {
        status = a_event.rsp_data.contents.description;
    } else if ('status' in a_event) {
        status = a_event.status;
    }

    this._messageErr('Not logged in');
    $('#login_show').prop('disabled', false);
    $('#new_game').prop('disabled', true);
    $('#prisoners_list .loading')
        .css('display', 'none');
    this.loginShow(status);

    return false;
}

    /*====================================================================*\
      TODO */
Bahaman.Screen.prototype.loginGo = function(a_event) {
    var target = a_event.target;
    var server_uri = $("#login input[name='server_uri'][type='url']").val();
    var email_address = $("#login input[name='email_address'][type='email']").val();
    var password = $("#login input[name='password'][type='password']").val();
    Bahaman._.client.server_uri = server_uri;
    Bahaman._.client.email_address = email_address;
    Bahaman._.client.password = password;
    $('#login_show').prop('disabled', true);
    $('#new_game').prop('disabled', true);
    this._prisonersLoading();
    this._messagePending('Logging in...');
    Bahaman._.client.testLogin();
    $.modal.close();

    return false;
}

    /*====================================================================*\
      TODO */
Bahaman.Screen.prototype.loginOkay = function(a_event) {
    this._messageLoggedIn();
    $('#new_game').prop('disabled', false);

    return this.prisonersGo();
}

    /*====================================================================*\
      TODO */
Bahaman.Screen.prototype.loginShow = function(a_status /* = null */) {
    var status = (typeof(a_status) === 'undefined')
        ? null
        : a_status;

    var updateModalLoginStatus = this._updateModalLoginStatus.bind(this);
 
    var shown = $('#login').modal({
        onShow: function(a_dialog) {
            updateModalLoginStatus(status);
        },
    });

    if (! shown) {
        updateModalLoginStatus(status);
    }

    return false;
}

    /*====================================================================*\
      TODO */
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

    /*====================================================================*\
      TODO */
Bahaman.Screen.prototype.prisonersOkay = function(a_event) {
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

    games.sort(Bahaman.Game.compare);
    var now = Date.now();

    for (var game in games) {
        game = games[game];
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

        list_item_div_html += '<br />';
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
            + '<br />'
            + parseInt((now - game.state.imprisoned_at) / 86400000) + ' days old';

        if (game.state.state === 'help') {
            list_item_div_html += '<br />'
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

    //---- Private methods -----------------------------------------------

    /*====================================================================*\
      TODO */
Bahaman.Screen.prototype._messageErr = function(a_msg) {
    return $('#message').removeClass('okay pending')
        .addClass('err')
        .text(a_msg);
}

    /*====================================================================*\
      TODO */
Bahaman.Screen.prototype._messageLoggedIn = function() {
    this._messageOkay('Logged in as <' + Bahaman._.client.email_address + '>');
}

    /*====================================================================*\
      TODO */
Bahaman.Screen.prototype._messageOkay = function(a_msg) {
    return $('#message').removeClass('err pending')
        .addClass('okay')
        .text(a_msg);
}

    /*====================================================================*\
      TODO */
Bahaman.Screen.prototype._messagePending = function(a_msg) {
    return $('#message').removeClass('err okay')
        .addClass('pending')
        .text(a_msg);
}

    /*====================================================================*\
      TODO */
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
      TODO */
Bahaman.Screen.prototype._updateModalLoginStatus = function(a_status) {
    $("#login input[name='server_uri'][type='url']").val(Bahaman._.client._server_uri);
    $("#login input[name='email_address'][type='email']").val(Bahaman._.client.email_address);
    $("#login input[name='password'][type='password']").val(Bahaman._.client.password);

    if (a_status) {
        $('#login .status').css('display', 'block')
            .addClass('err');
        $("#login_message").html(a_status);
    } else {
        $('#login .status').css('display', 'none')
            .removeClass('err');
    }
}

    /*====================================================================*\
      TODO */
Bahaman.Screen.prototype._updateSelectedGame = function(a_game) {
    $('#game').prop('_game', a_game);
    var done = a_game.state.state !== 'help';
    this._word(a_game.state.word);
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
}

    /*====================================================================*\
      TODO */
Bahaman.Screen.prototype._word = function(a_word) {
    var word = $('#word');
    word.text(a_word)
        .html(word.text().replace(/\*/g, '&emsp;'))
        .lettering();
}

//---- Functions ---------------------------------------------------------

/*========================================================================*\
  TODO */

//---- Initialization ----------------------------------------------------

window.Bahaman = Bahaman;

// Instance namespace
Bahaman._ = {};

$(document).ready(function ($) {
    Bahaman._.screen = new Bahaman.Screen();
    Bahaman._.client = new Bahaman.Client();
});

$(window).on('load', function() {
    Bahaman._.client.server_uri = 'https://balanced-hangman.herokuapp.com/';
    //Bahaman._.client.triggerNoLogin();
    Bahaman._.screen._messagePending('Logging in...');
    Bahaman._.client.testLogin();
});
