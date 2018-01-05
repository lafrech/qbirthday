"""Thunderbird/Lightning backend"""

import time
import uuid
import configparser
import datetime as dt
from pathlib import Path

from .base import BaseRWBackend
from .exceptions import (
    BackendMissingLibraryError, BackendReadError, BackendWriteError)


class LightningBackend(BaseRWBackend):
    """Thunderbird/Lightning backend"""

    NAME = 'Lightning'
    TITLE = 'Thunderbird/Icedove Lightning'

    def __init__(self, settings):

        super().__init__(settings)

        self.thunderbird_location = Path.home() / '.mozilla-thunderbird'
        self.cursor = None
        self.conn = None

    def _parse_birthday(self, filepath):
        try:
            self._connect(filepath)
        except ConnectionError as exc:
            raise BackendReadError(exc)
        qry = '''SELECT title, event_start FROM cal_events ce
              INNER JOIN cal_properties cp
              ON ce.id = cp.item_id
              WHERE cp.key == 'CATEGORIES' AND
              cp.value == 'Birthday' AND
              ce.title != '';'''
        self.cursor.execute(qry)
        birthdates = []
        for row in self.cursor:
            bday = dt.datetime.utcfromtimestamp(int(row[1]) / 1000000).date()
            birthdates.append((row[0], bday))
        return birthdates

    def parse(self):
        '''open thunderbird sqlite-database'''
        profile_dir = self.thunderbird_location
        profilefile = profile_dir / 'profiles.ini'
        if profilefile.is_file():
            conf_pars = configparser.ConfigParser()
            conf_pars.read(str(profilefile))
            profiles = {}  # dict of founded profiles
            # get profiles from profiles.ini in thunderbird directory
            for sec in conf_pars.sections():
                if sec.lower().startswith("profile"):
                    profiles[sec] = {}
                    for opt in conf_pars.options(sec):
                        profiles[sec][opt.lower()] = conf_pars.get(sec, opt)
            # get all data from profiles.ini
            for profile in profiles:
                if profiles[profile]['isrelative']:
                    profile_location = profile_dir / profiles[profile]['path']
                else:
                    profile_location = profiles[profile]['path']
                db_location = profile_location / 'calendar-data/local.sqlite'
                self._parse_birthday(db_location)
        # Missing profile file
        raise BackendReadError(
            self.tr("Error reading profile file: {}").format(profile_dir),
        )

    def _connect(self, filepath):
        '''"connect" to sqlite3-database'''

        # TODO: use with connect as... syntax
        try:
            import sqlite3
        except ImportError:
            raise BackendMissingLibraryError(
                self.tr("Missing {} library.").format("SQLite3"))

        try:
            self.conn = sqlite3.connect(str(filepath))
            self.cursor = self.conn.cursor()
        except Exception as exc:
            raise ConnectionError(exc)

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
            # TODO: implement code to insert new calendar if none exists!

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
            raise BackendWriteError(
                self.tr("Could not execute SQLite query '{}':\n{}").format(
                    qry, msg)
            )
