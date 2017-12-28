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

import os
import time
import uuid
import configparser
import datetime

from PyQt5 import QtCore, QtWidgets

from qbirthday.databases import DataBase


class Lightning(DataBase):
    '''Thunderbird/Lightning implementation'''

    TITLE = 'Thunderbird/Icedove Lightning'
    CAN_SAVE = True

    def __init__(self, mainwindow):

        super().__init__(mainwindow)

        self.THUNDERBIRD_LOCATION = os.path.join(
            os.environ['HOME'], '.mozilla-thunderbird')
        self.cursor = None
        self.conn = None

    def get_config_file(self, configfile):
        profilefile = os.path.join(configfile, 'profiles.ini')
        if os.path.isfile(profilefile):
            conf_pars = configparser.ConfigParser()
            conf_pars.read(profilefile)
            profiles = {} # dict of founded profiles
            # get profiles from profiles.ini in thunderbird directory
            for sec in conf_pars.sections():
                if sec.lower().startswith("profile"):
                    profiles[sec] = {}
                    for opt in conf_pars.options(sec):
                        profiles[sec][opt.lower()] = conf_pars.get(sec, opt)
            # get all data from profiles.ini
            for profile in profiles:
                if profiles[profile]['isrelative']:
                    profile_location = os.path.join(
                        configfile,
                        profiles[profile]['path']
                    )
                else:
                    profile_location = profiles[profile]['path']
                #look for calendar-data/local.sqlite first 
                #(new in sunbird/lightning 1.0)
                location = os.path.join(profile_location, 'calendar-data/local.sqlite')
                print(location)
                if os.path.exists(location):
                    self.parse_birthday(location)
                    return
                # ... and now the old one
                location = os.path.join(profile_location, 'storage.sdb')
                print(location)
                if os.path.exists(location):
                    self.parse_birthday(location)
                    return
        # Missing profile file
        QtWidgets.QMessageBox.warning(
            self.mainwindow,
            QtCore.QCoreApplication.applicationName(),
            _("Error reading profile file: {}").format(configfile),
            QtWidgets.QMessageBox.Discard
        )

    def parse(self):
        '''open thunderbird sqlite-database'''
        if (os.path.exists(self.THUNDERBIRD_LOCATION)):
            self.get_config_file(self.THUNDERBIRD_LOCATION)

    def connect(self, filename):
        '''"connect" to sqlite3-database'''

        # TODO: use with connect as... syntax
        try:
            import sqlite3
        except:
            # Missing package
            QtWidgets.QMessageBox.warning(
                self.mainwindow,
                QtCore.QCoreApplication.applicationName(),
                _("Package {} is not installed.").format("SQLite3"),
                QtWidgets.QMessageBox.Discard
            )

        try:
            self.conn = sqlite3.connect(filename)
            self.cursor = self.conn.cursor()
        except Exception as msg:
            # Connexion error
            QtWidgets.QMessageBox.warning(
                self.mainwindow,
                QtCore.QCoreApplication.applicationName(),
                _("sqlite3 could not connect: {}").format(str(msg)),
                QtWidgets.QMessageBox.Discard
            )

    def parse_birthday(self, filename):
        self.connect(filename)
        qry = '''SELECT title, event_start FROM cal_events ce
              INNER JOIN cal_properties cp
              ON ce.id = cp.item_id
              WHERE cp.key == 'CATEGORIES' AND
              cp.value == 'Birthday' AND
              ce.title != '';'''
        self.cursor.execute(qry)
        for row in self.cursor:
            bday = datetime.datetime.utcfromtimestamp(int(row[1]) / 1000000)
            self.addressbook.add(row[0], str(bday).split(' ')[0])

    def add(self, name, birthday):
        # create new uuid
        event_date = int(birthday.strftime("%s"))
        event_start = (event_date + 86400) * 1000000
        event_end = (event_date + 172800) * 1000000
        uid = str(uuid.uuid4())
        create_time = str(int(time.time()) * 1000000)
        try:
            qry = '''SELECT id from cal_calendars LIMIT 1;'''
            self.cursor.execute(qry)
            rows = self.cursor.fetchall()
            calender_id = rows[0][0]
            # lets assume there is at least one calendar
            # TODO: implement code to insert new calendar if it none exists!

            qry = '''INSERT INTO "cal_events"
                (cal_id, id, time_created, last_modified, title, flags,
                event_start, event_start_tz, event_end, event_end_tz)
                VALUES
                ('%s', '%s', '%s', '%s', '%s', 28, '%s', 'floating', '%s',
                 'floating'); ''' % (
                     calender_id, uid, create_time,
                     create_time, name, event_start, event_end)

            self.cursor.execute(qry)

            qry = '''INSERT INTO cal_properties
                     (item_id, key, value)
                     VALUES
                     ('%s', 'CATEGORIES', 'Birthday');''' % uid
            self.cursor.execute(qry)
            qry = '''INSERT INTO cal_properties
                     (item_id, key, value)
                     VALUES
                     ('%s', 'TRANSP', 'TRANSPARENT');''' % uid
            self.cursor.execute(qry)
            qry = '''INSERT INTO cal_properties
                     (item_id, key, value)
                     VALUES
                     ('%s', 'X-MOZ-GENERATION', '1');''' % uid
            self.cursor.execute(qry)
            # birthday repeats yearly
            qry = '''INSERT INTO "cal_recurrence"
                     (item_id, recur_index, recur_type, is_negative, count,
                     interval)
                     VALUES
                     ('%s', 1, 'YEARLY', 0, -1, 1);''' % uid
            self.cursor.execute(qry)
            self.conn.commit()
        except Exception as msg:
            # Query error
            QtWidgets.QMessageBox.warning(
                self.mainwindow,
                QtCore.QCoreApplication.applicationName(),
                _("Could not execute {} query '{}':\n{}").format(
                    'SQLite', qry, msg),
                QtWidgets.QMessageBox.Discard
            )
        self.addressbook.add(name, str(birthday))
