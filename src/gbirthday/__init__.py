# vim: foldmethod=marker
#{{{ License header: GPLv2+
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#}}}
'''GBirthday

A KBirthday clone for Gnome environment, working with different
data servers:
 - CSV-file (comma-seperated value)
 - MySQL
 - Evolution
 - Thunderbird/Icedove Lightning
 - Sunbrid / IceOwl

and relatively easy to extend for other data servers.
'''
### Original source from:
## pygtk-demo Status Icon: Nikos Kouremenos
## EvoBdayReminder.py: Axel Heim. http://www.axelheim.de/

VERSION = "@VER@"

import gtk

import os
import datetime
from datetime import date
import time

""" parse locales from python module
Do you say "1. January" or "January 1."?
"""
import locale
locale.setlocale(locale.LC_ALL, '')
DAY_AT_PLACE, MONTH_AT_PLACE = 1, 2
if time.strftime('%x', (2000, 3, 1, 1, 0, 0, 0, 1, 0)).startswith("03"):
    DAY_AT_PLACE, MONTH_AT_PLACE = 2, 1

# for FreeBSD users: if no i18n is whished, no gettext package will be
# available and standard messages are displayed insted a try to use
# translated strings
try:
    import gettext
    gettext.install("gbirthday")
except ImportError:
    _ = lambda x: x

NOTIFICATION = True
try:
    import pynotify
except ImportError:
    NOTIFICATION = False

# own imports
from databases import *
from status_icon import *

# list of all availabe databases
databases = [Evolution(), Lightning(), Sunbird(), CSV(), MySQL()]
current_day = time.strftime("%d", time.localtime(time.time()))


# not needed atm, will be possibly deleted


def save_list(l):
    '''create a string that can be saved in a file'''
    return str(l)[2:-2].replace("', '", ',')


def start(ab, conf):
    '''(re)create AdressBook and parse data'''
    ab.bdays = {}
    for db in databases:
        if (db.TYPE in conf.used_databases):
            db.parse(ab=ab, conf=conf)


class Conf:

    def __init__(self):
        '''Try to read config file or initialize with default values.'''
        import ConfigParser
        self.firstday = self.lastday = None
        self.ab = None
        self.csv_files = None
        self.MySQL = None
        self.settings = ConfigParser.ConfigParser()
        try:
            self.settings.readfp(file(os.environ['HOME'] + "/.gbirthdayrc"))
        except IOError:
            self.settings.add_section("main")
            self.default_values()
        else:
            if self.settings.has_section("main"):
                self.sync_to_mem()
            else:
                self.settings.add_section("main")
                self.default_values()

    def default_values(self):
        '''Initialize with default values.'''
        self.firstday = -2
        self.lastday = 30
        self.used_databases = ['evolution']
        self.csv_files = None

    def sync_to_mem(self):
        '''Get current settings from config parser into this object.'''
        import ConfigParser

        self.firstday = self.settings.get("main", "firstday")
        self.lastday = self.settings.get("main", "lastday")
        self.csv_files = self.settings.get("main", "csv_files")
        used_db = self.settings.get("main", "databases")
        self.used_databases = used_db.split("|")
        try:
            MySQL.host = self.settings.get("mysql", "host")
            MySQL.port = self.settings.get("mysql", "port")
            MySQL.username = self.settings.get("mysql", "username")
            MySQL.passwort = self.settings.get("mysql", "password")
            MySQL.database = self.settings.get("mysql", "database")
            MySQL.table = self.settings.get("mysql", "table")
            MySQL.name_row = self.settings.get("mysql", "name_row")
            MySQL.date_row = self.settings.get("mysql", "date_row")
        except ConfigParser.NoSectionError:
            pass

    def sync_to_settings(self):
        '''Save current settings from this object to config parser.'''
        self.settings.set("main", "firstday", self.firstday)
        self.settings.set("main", "lastday", self.lastday)
        used_db = ""
        for db in self.used_databases:
            used_db += db
            used_db += "|"
        # db[:-1] because of removing the latest "|"
        self.settings.set("main", "databases", used_db[:-1])
        self.settings.set("main", "csv_files", self.csv_files)
        if self.MySQL:
            if not self.settings.has_section("mysql"):
                self.settings.add_section("mysql")
            self.settings.set("mysql", "host", self.MySQL.host)
            self.settings.set("mysql", "port", self.MySQL.port)
            self.settings.set("mysql", "username", self.MySQL.username)
            self.settings.set("mysql", "password", self.MySQL.password)
            self.settings.set("mysql", "database", self.MySQL.database)
            self.settings.set("mysql", "table", self.MySQL.table)
            self.settings.set("mysql", "name_raw", self.MySQL.name_row)
            self.settings.set("mysql", "date_raw", self.MySQL.date_raw)

    def save(self):
        '''Save current settings to disk.'''
        self.sync_to_settings()
        self.settings.write(file(os.environ['HOME'] + "/.gbirthdayrc", "w"))

showbdcheck = None


def main():
    '''Load settings, start status icon and get to work.'''
    # try to load settings
    conf = Conf()

    # load data and fill AddressBook
    ab = AddressBook()
    start(ab, conf)

    # show status icon
    status_icon = StatusIcon(ab, conf)

    # check every 60 seconds for new day
    # TODO: update until end of day according to current clock settings?
    #       (might not the best idea if user changes current time)
    import gobject
    gobject.timeout_add(60000, status_icon.check_new_day)
    gtk.main()

if __name__ == '__main__':
    main()
