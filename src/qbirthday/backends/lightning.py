"""Thunderbird/Lightning backend"""

import configparser
import datetime as dt
from pathlib import Path

from .base import BaseBackend, try_import
from .exceptions import BackendMissingLibraryError, BackendReadError


BACKEND_ID = 'Lightning'
BACKEND_NAME = 'Thunderbird/Icedove Lightning'


try:
    # pylint: disable=invalid-name
    sqlite3 = try_import('sqlite3')
except BackendMissingLibraryError as exc:
    exc.bcknd_id = BACKEND_ID
    exc.bcknd_name = BACKEND_NAME
    raise exc


class LightningBackend(BaseBackend):
    """Thunderbird/Lightning backend"""

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
            self.conn = sqlite3.connect(str(filepath))
            self.cursor = self.conn.cursor()
        except Exception as exc:
            raise ConnectionError(exc)


BACKEND = LightningBackend
