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

import ConfigParser
import argparse
import os

from bahaman.util import (
    SENTINEL,
)

#---- Constants ----------------------------------------------------------

__all__ = ()

#---- Classes ------------------------------------------------------------

#=========================================================================
class BahamanConfigParser(ConfigParser.SafeConfigParser):
    """
    This is somewhat of a bastardization/hack of ConfigParser, but it will
    do for our limited purposes. Note: none of this involves serial I/O
    which could cause the application to become unresponsive.
    """

    #---- Public constants -----------------------------------------------

    BASIC = 'basic'
    ADVANCED = 'advanced'

    _CONFIG_DEFAULTS = (
        ( BASIC, {
            # HTTPS appears to work, so we're using it (since passwords
            # are involved)
            'server_uri': 'https://balanced-hangman.herokuapp.com/', # 'http://balanced-hangman.herokuapp.com/'
            'username': '',
            'password': '',
        } ),
        ( ADVANCED, {
        } ),
    )

    #---- Constructors ---------------------------------------------------

    #=====================================================================
    def __init__(self, a_config_path, a_defaults = _CONFIG_DEFAULTS):
        """
        Constructor.

        a_config_path is either the argument parser used to parse the
        arguments, or the path to the configuration file. a_defaults is
        the default configuration.
        """
        ConfigParser.SafeConfigParser.__init__(self)

        if isinstance(a_config_path, argparse.ArgumentParser):
            parser = a_config_path
            ns = parser.parse_args()

            try:
                self.__config_path = os.path.realpath(ns.config)
            except AttributeError:
                self.__config_path = BahamanConfigParser.__defaultConfigPath(parser.prog)

            self.__cheat = ns.cheat
        else:
            self.__config_path = os.path.realpath(a_config_path)
            self.__cheat = False

        try:
            os.makedirs(os.path.dirname(self.__config_path))
        except OSError, e:
            if e.errno != 17:
                raise

        for section, options in a_defaults:
            self.add_section(section)

            for option, value in options.items():
                self.set(section, option, value)

    #---- Public properties ----------------------------------------------

    #=====================================================================
    def cheat():
        def fget(self):
            return self.__cheat

        fset = None
        fdel = None
        doc = """
        True if cheat mode is activated, False otherwise.
        """

        return locals()

    cheat = property(**cheat())

    #=====================================================================
    def config_path():
        def fget(self):
            return self.__config_path

        fset = None
        fdel = None
        doc = """
        The account login e-mail associated with this object.
        """

        return locals()

    config_path = property(**config_path())

    #---- Public hook methods --------------------------------------------

    #=====================================================================
    def get(self, section, option = None, raw = False, vars = None, default = SENTINEL):
        if option is None:
            new_section = BahamanConfigParser.BASIC
            new_option = section
        else:
            new_section = section
            new_option = option

        try:
            return ConfigParser.SafeConfigParser.get(self, new_section, new_option, raw, vars)
        except ConfigParser.NoOptionError:
            if default is not SENTINEL:
                return default

            raise

    #=====================================================================
    def remove_option(self, a_section, a_option = None):
        if a_option is None:
            section = BahamanConfigParser.BASIC
            option = a_section
        else:
            section = a_section
            option = a_option

        return ConfigParser.SafeConfigParser.remove_option(self, section, option)

    #=====================================================================
    def set(self, a_section, a_option, a_value = None):
        if a_value is None:
            section = BahamanConfigParser.BASIC
            option = a_section
            value = a_option
        else:
            section = a_section
            option = a_option
            value = a_value

        return ConfigParser.SafeConfigParser.set(self, section, option, value)

    #---- Public methods -------------------------------------------------

    #=====================================================================
    def readOrCreate(self):
        """
        Either reads the existing configuration file, or creates a new
        one. Return True if a new file was created, False otherwise.
        """
        fd = None

        if not os.path.isfile(self.config_path):
            try:
                # This should be equivalent to the 'wx' mode to open() (or
                # the fopen() standard library call), but we don't know if
                # the 'x' extension is supported flag on all platforms, so
                # we have to do the low-level open() ourselves
                fd = os.open(self.config_path, os.O_WRONLY | os.O_TRUNC | os.O_CREAT | os.O_EXCL)
            except OSError, e:
                if e.errno != 17:
                    raise

        if fd is not None:
            with os.fdopen(fd, 'w') as config_fobj:
                self.write(config_fobj)

        # We should probably handle this more carefully; it's possible two
        # clients have been started at approximately the same time, and
        # one may read the configuration file after the other has created
        # it, but before it has written to it; using read/write locks and
        # opening our own file descriptors is probably the better way to
        # do this, but we would also have to have each instance monitor
        # the configuration for changes while it is running, which we
        # currently don't do
        ConfigParser.SafeConfigParser.read(self, self.config_path)

        return fd is not None

    #=====================================================================
    def writeReplace(self):
        """
        TODO
        """
        with open(self.config_path, 'w') as config_fobj:
            self.write(config_fobj)

    #---- Private static methods -----------------------------------------

    #=====================================================================
    @staticmethod
    def __defaultConfigPath(a_app_name):
        """
        Derive the default config path from a_app_name and the operating
        system.
        """
        app_name = os.path.splitext(os.path.basename(a_app_name))[0]
        config_dir = None
        config_file = os.path.extsep.join(( app_name, 'cfg' ))

        if config_dir is None:
            try:
                # See <http://bit.ly/1hKtlXb>
                import AppKit
            except ImportError:
                pass
            else:
                # Args for NSSearchPathForDirectoriesInDomains are:
                #
                #   directory   = 14 (NSApplicationSupportDirectory; see
                #                     <http://bit.ly/1cXswFh>)
                #   domainMask  = 1  (NSUserDomainMask; see
                #                     <http://bit.ly/KPvWDI>)
                #   expandTilde = True
                #
                # Returns an ordered list of paths (strings); see
                # <http://bit.ly/KVQZ8l> for details
                config_dir = os.path.realpath(os.path.join(AppKit.NSSearchPathForDirectoriesInDomains(14, 1, True)[0], app_name))

        if config_dir is None:
            try:
                # See <http://bit.ly/1cGmqio>
                import win32com.shell
            except ImportError:
                pass
            else:
                config_dir = os.path.realpath(os.path.join(win32com.shell.shell.SHGetFolderPath(0, win32com.shell.shellcon.CSIDL_APPDATA, 0, 0), app_name))

        if config_dir is None:
            config_dir = os.path.realpath(os.path.join(os.path.expanduser('~'), app_name))

        return os.path.join(config_dir, config_file)
