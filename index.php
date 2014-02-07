<!DOCTYPE html>
<html>
<!-- =====================================================================
  Copyright (c) 2014 Matt Bogosian <mtb19@columbia.edu>.

  Please see the LICENSE (or LICENSE.txt) file which accompanied this
  software for rights and restrictions governing its use. If such a file
  did not accompany this software, then please contact the author before
  viewing or using this software in any capacity.
  ======================================================================== -->
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" >

    <style type="text/css" media="all"><!--
        @import url('http://fonts.googleapis.com/css?family=Rock+Salt|Special+Elite|Ubuntu');
        @import url('_/bahaman.css');
    --></style>

    <title>BaHaMan (BAlanced HAngMAN)</title>
    <link href="" rel="stylesheet" type="text/css"></link>
</head>
<body>
    <div id="bg">
        <div id="nojs" class="overlay">
            <p><a href="http://www.enable-javascript.com/">Javascript must be enabled</a> for this application to work properly.</p>
        </div>

        <div id="main">
            <div id="main_bg"></div>

            <div id="content">
                <h1>&ldquo;BaHaMan!&rdquo;</h1>

                <h2>
                    by <a href="http://linkd.in/1fBEffR" target="_blank">Matt Bogosian</a><br>
                    <span class="small">(You know, that guy you should <em>definitely</em> hire. <a id="seriously_show" class="egg_a" href="#" target="_blank">Seriously</a>.)</span>
                </h2>

                <div id="game">
                    <div id="progress_counter" class="game_help">0</div>
                    <div id="word">b*l*ncedh*ngm*n</div>
                </div>

                <div id="guesses">
                    <div>
                        <button id="guess_a" class="best_hint">A</button>
                        <button id="guess_b" class="hit" disabled>B</button>
                        <button id="guess_c" disabled>C</button>
                        <button id="guess_d" disabled>D</button>
                        <button id="guess_e" class="hit" disabled>E</button>
                        <button id="guess_f" disabled>F</button>
                        <button id="guess_g" class="hit" disabled>G</button>
                        <button id="guess_h" class="hit" disabled>H</button>
                        <button id="guess_i" disabled>I</button>
                        <button id="guess_j" disabled>J</button>
                        <button id="guess_k" disabled>K</button>
                        <button id="guess_l" class="hit" disabled>L</button>
                        <button id="guess_m" class="hit" disabled>M</button>
                    </div>

                    <div>
                        <button id="guess_n" class="hit" disabled>N</button>
                        <button id="guess_o" disabled>O</button>
                        <button id="guess_p" disabled>P</button>
                        <button id="guess_q" disabled>Q</button>
                        <button id="guess_r" disabled>R</button>
                        <button id="guess_s" disabled>S</button>
                        <button id="guess_t" disabled>T</button>
                        <button id="guess_u" disabled>U</button>
                        <button id="guess_v" disabled>V</button>
                        <button id="guess_w" disabled>W</button>
                        <button id="guess_x" disabled>X</button>
                        <button id="guess_y" disabled>Y</button>
                        <button id="guess_z" disabled>Z</button>
                    </div>
                </div>
            </div>

            <div id="cheat">
                <p id="cheat_code"><span></span><span>&#x2191; &#x2191; &#x2193; &#x2193; &#x2190; &#x2192; &#x2190; &#x2192; B A &lt;start&gt;</span></p>
                <audio id="cheat_step" src="_/media/smb_coin.wav" preload="auto"></audio>
                <audio id="cheat_ambient" src="_/media/02-underworld.mp3" preload="auto" loop></audio>
                <audio id="cheat_go" src="_/media/smb_powerup.wav" preload="auto"></audio>
                <textarea id="hints">Hints Mode&trade; activated!</textarea>
            </div>

            <div id="prisoners">
                <button id="prisoners_first" disabled>&laquo;</button>
                <button id="prisoners_prev" disabled>&lsaquo;</button>

                <ul id="prisoners_list">
                    <li id="prisoners_list_item" style="display: none;"><div></div></li>
                    <li class="loading"><img src="_/media/spinner.gif"></img><span class="full_height"> </span>Working...</li>
                </ul>

                <button id="prisoners_last" disabled>&raquo;</button>
                <button id="prisoners_next" disabled>&rsaquo;</button>
            </div>

            <div id="message" class="controls_left pending">Loading page...</div>

            <div class="controls_right">
                <button id="help_show">Help</button>
                <button id="login_show" disabled>Account</button>
                <button id="new_prisoner" disabled>New game</button>
            </div>
        </div>
    </div>

    <div id="copyright"><span class="full_height"></span><a id="egg_show" class="egg_a" href="#">Copyright &copy; 2014, Matt Bogosian.</a> See <a id="license_show" href="#">LICENSE</a> file for details.</div>

    <div id="login" class="modal">
        <form action="#">
            <div class="controls_content">
                <fieldset>
                    <legend>Server</legend>

                    <div>
                        <label for="server_uri">Server URI:</label>
                        <input name="server_uri" type="url" placeholder="https://hangman.example.dom/" required></input>
                    </div>
                </fieldset>

                <fieldset>
                    <legend>Account</legend>

                    <div>
                        <label for="email_address">Username:</label>
                        <input name="email_address" type="email" placeholder="janedoe@example.dom" required autofocus></input>
                    </div>

                    <div>
                        <label for="password">Password:</label>
                        <input name="password" type="password" required></input>
                    </div>
                </fieldset>

                <fieldset>
                    <legend>Extras</legend>

                    <div>
                        <label for="theme_css">Theme CSS:</label>
                        <input name="theme_css" type="text" placeholder="uri_to_theme.css" disabled></input>
                    </div>
                </fieldset>

                <fieldset class="status">
                    <legend>Server status</legend>
                    <div id="login_message"></div>
                </fieldset>

            </div>

            <div class="controls_right">
                <button id="login_go" type="submit">Log in</button>
                <button id="login_create" type="submit">Create new</button>
            </div>

            <div class="controls_left"><button id="login_cancel" class="simplemodal-close" type="submit">Cancel</button></div>
        </form>
    </div>

    <div id="help" class="modal">
        <div id="help_content">
            <p>Your best friend has been arrested and charged with arson, treason, armed robbery, and public drunkeness ... <strong>plus</strong> ... murder, mayhem, ignorance, and ugliness.</p>

            <p>However, the judge, being a benevolent sort, will let your friend plea-bargain the charges down to ugliness, provided he/she has one friend. <strong>Guess who?</strong></p>

            <p>To save your friend&rsquo;s life, you must guess the secret word. Each time you guess a <strong>correct</strong> letter, it will be revealed.</p>

            <p>But <strong>beware</strong>! Each time you guess, your friend advances one step closer to <strong>doom</strong>!</p>

            <div class="small" style="bottom: 1.0em; position: absolute; right: 1.0em;">(<a href="http://bit.ly/1cuD3M8" target="_blank">inspiration</a>)</div>
        </div>
    </div>

    <iframe id="license" class="modal" src="LICENSE">&lt;<a href="LICENSE">LICENSE</a>&gt;</iframe>

    <div id="seriously" class="modal">
        <img src="http://bit.ly/1ihAxKp"></img>
    </div>

    <div id="egg" class="modal">
        <p>&ldquo;<a href="http://bit.ly/1ebG9oU" target="_blank">I don&rsquo;t know, man, but this guy&rsquo;s a character.</a>&rdquo;</p>

        <p>(&ldquo;<a href="http://bit.ly/K9ve3C" target="_blank">Skrelnick.</a>&rdquo;)</p>
    </div>

    <!-- Load scripts as late as possible to allow for earlier page
         displays -->
    <script type="text/javascript" src="http://code.jquery.com/jquery-1.11.0.min.js">
        //# sourceMappingURL=http://code.jquery.com/jquery-1.11.0.min.map
    </script>

    <!-- <script type="text/javascript" src="http://code.jquery.com/ui/1.10.4/jquery-ui.js"></script> -->
    <!-- <script type="text/javascript" src="http://code.jquery.com/ui/1.10.4/jquery-ui.min.js"></script> -->
    <script type="text/javascript" src="_/3rdparty/Lettering.js/jquery.lettering.js"></script>
    <script type="text/javascript" src="_/3rdparty/simplemodal-demo-basic-1.4.4/js/jquery.simplemodal.js"></script>
    <script type="text/javascript" src="_/3rdparty/urlparse.js"></script>
    <script type="text/javascript" src="_/bahaman.js"></script>
    <script>
        $(document).ready(function ($) {
            // Bahaman._.client.email_address = 'mtb19@columbia.edu';
            // Bahaman._.client.password = 'foobar';
        });
    </script>
</body>
</html>
