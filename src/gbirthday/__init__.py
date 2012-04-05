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

import os, shutil
import datetime
from datetime import date
import time
from textwrap import dedent
import ConfigParser

# TODO check for needed modules
from databases import DATABASES
import databases

# parse locales from python module
# Do you say "1. January" or "January 1."?
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

CURRENT_DAY = time.strftime("%d", time.localtime(time.time()))

class Conf:
    '''Class for handle all configurations.'''

    def __init__(self):
        '''Try to read config file or initialize with default values.'''
        self.firstday = self.lastday = None
        self.notify_future_bdays = None
        self.used_databases = None
        self.csv_files = None
        self.mysql = databases.mysql_db
        self.settings = ConfigParser.ConfigParser()

        # If XDG_CONFIG_HOME is defined, use it to store config files
        if 'XDG_CONFIG_HOME' in os.environ:
            self.base_config_path = os.environ['XDG_CONFIG_HOME'] + "/gbirthday"
            # If no config file here, check for config files in ~/.config
            if not os.path.isdir(self.base_config_path):
                if os.path.isdir(os.environ['HOME'] + "/.config/gbirthday"):
                    shutil.copytree(os.environ['HOME'] + "/.config/gbirthday",
                                    self.base_config_path)
                else:
                    os.makedirs(self.base_config_path)
        # else, use ~/.config
        else:
            self.base_config_path = os.environ['HOME'] + "/.config/gbirthday"
            if not os.path.isdir(self.base_config_path):
                os.makedirs(self.base_config_path)

        # If no config in base path, check old path ~/.gbirthdayrc
        # This is here for backward compatibility, remove it when time has come
        if not os.path.exists(self.base_config_path + '/gbirthdayrc'):
            if os.path.exists(os.environ['HOME'] + '/.gbirthdayrc'):
                shutil.copy2(os.environ['HOME'] + '/.gbirthdayrc',
                             self.base_config_path + '/gbirthdayrc')

        # If XDG_DATA_HOME is defined, use it to store data files
        if 'XDG_DATA_HOME' in os.environ:
            self.base_data_path = os.environ['XDG_DATA_HOME'] + "/gbirthday"
        # else, use ~/.local/share
        else:
            self.base_data_path = os.environ['HOME'] + "/.local/share/gbirthday"

        try:
            self.settings.readfp(file(self.base_config_path + '/gbirthdayrc'))
        except IOError:
            pass
        
        self.sync_to_mem()

        self.correct_settings()

    # TODO introduced after 0.6, remove if time has come
    def correct_settings(self):
        '''correct new settings, e.g. Evolution and not evolution anymore'''
        def replace(old, new, changed):
            '''replace old with new'''
            for num, item in enumerate(self.used_databases):
                if self.used_databases[num] == old:
                    changed = True
                    self.used_databases[num] = new
            return changed

        changed = False
        changed = replace('evolution', 'Evolution', changed)
        changed = replace('mysql', 'MySQL', changed)
        changed = replace('csv', 'CSV', changed)
        changed = replace('lightning', 'Lightning', changed)
        changed = replace('sunbird', 'Sunbird', changed)
        if changed:
            self.save()

    def sync_to_mem(self):
        '''Get current settings from config parser into this object.'''

        def get_setting_value(section, value, default):
            '''Get setting value. If not found, return default'''
            try:
                return self.settings.get(section, value)
            except (ConfigParser.NoOptionError, \
                    ConfigParser.NoSectionError):
                return default

        self.firstday = int(get_setting_value("main", "firstday", -2))
        self.lastday = int(get_setting_value("main", "lastday", 30))
        used_db = get_setting_value("main", "databases", "")
        if used_db != "":
            self.used_databases = used_db.split("|")
        else:
            self.used_databases = []
        self.notify_future_bdays = int(get_setting_value("main",
                                       "notify_future_bdays", 0))
        
        self.csv_files = eval(get_setting_value("main", "csv_files", 'None'))
        
        self.ics_export = eval(get_setting_value("ics_export", "export",
                                                 'False'))
        self.ics_filepath = get_setting_value("ics_export", "filepath",
                                        self.base_data_path + '/gbirthday.ics')
        self.ics_custom_properties = get_setting_value("ics_export",
                                                "custom_properties", '')
        self.ics_alarm = eval(get_setting_value("ics_export", "alarm", 'False'))
        self.ics_alarm_days = get_setting_value("ics_export", "alarm_days", '5')
        self.ics_alarm_custom_properties = get_setting_value("ics_export",
                                                "alarm_custom_properties", '')

        try:
            self.mysql.host = self.settings.get("mysql", "host")
            self.mysql.port = self.settings.get("mysql", "port")
            self.mysql.username = self.settings.get("mysql", "username")
            self.mysql.password = self.settings.get("mysql", "password")
            self.mysql.database = self.settings.get("mysql", "database")
            self.mysql.table = self.settings.get("mysql", "table")
            self.mysql.name_row = self.settings.get("mysql", "name_row")
            self.mysql.date_row = self.settings.get("mysql", "date_row")
        except ConfigParser.NoSectionError:
            pass

    def sync_to_settings(self):
        '''Save current settings from this object to config parser.'''
        # main
        if not self.settings.has_section("main"):
            self.settings.add_section("main")
        self.settings.set("main", "firstday", self.firstday)
        self.settings.set("main", "lastday", self.lastday)
        self.settings.set("main", "notify_future_bdays",
                self.notify_future_bdays)
        used_db = ""
        for database in self.used_databases:
            used_db += database
            used_db += "|"
        # db[:-1] because of removing the last "|"
        self.settings.set("main", "databases", used_db[:-1])
        self.settings.set("main", "csv_files", self.csv_files)
        
        # mysql
        if self.mysql:
            if not self.settings.has_section("mysql"):
                self.settings.add_section("mysql")
            self.settings.set("mysql", "host", self.mysql.host)
            self.settings.set("mysql", "port", self.mysql.port)
            self.settings.set("mysql", "username", self.mysql.username)
            self.settings.set("mysql", "password", self.mysql.password)
            self.settings.set("mysql", "database", self.mysql.database)
            self.settings.set("mysql", "table", self.mysql.table)
            self.settings.set("mysql", "name_row", self.mysql.name_row)
            self.settings.set("mysql", "date_row", self.mysql.date_row)

        # ics_export
        if not self.settings.has_section("ics_export"):
            self.settings.add_section("ics_export")
        self.settings.set("ics_export", "export", self.ics_export)
        self.settings.set("ics_export", "filepath", self.ics_filepath)
        self.settings.set("ics_export", "custom_properties",
                            self.ics_custom_properties)
        self.settings.set("ics_export", "alarm", self.ics_alarm)
        self.settings.set("ics_export", "alarm_days", self.ics_alarm_days)
        self.settings.set("ics_export", "alarm_custom_properties", 
                            self.ics_alarm_custom_properties)
    
    def save(self):
        '''Save current settings to disk.'''
        self.sync_to_settings()
        self.settings.write(file(self.base_config_path + '/gbirthdayrc', "w"))

def main():
    '''Load settings, start status icon and get to work.'''
    from addressbook import AddressBook
    from status_icon import StatusIcon
    # try to load settings
    conf = Conf()

    # load data and fill AddressBook
    addressbook = AddressBook(conf)
    addressbook.reload()

    # show status icon
    status_icon = StatusIcon(addressbook, conf)

    # check every 60 seconds for new day
    # TODO: update until end of day according to current clock settings?
    #       (might not the best idea if user changes current time)
    import gobject
    gobject.timeout_add(60000, status_icon.check_new_day)
    gtk.main()

if __name__ == '__main__':
    main()
