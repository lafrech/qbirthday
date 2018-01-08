"""Thunderbird/Lightning backend"""

import configparser
import datetime as dt
from pathlib import Path
import sqlite3

from .base import BaseBackend
from .exceptions import BackendReadError


BACKEND_ID = 'Lightning'
BACKEND_NAME = 'Thunderbird/Icedove Lightning'


class LightningBackend(BaseBackend):
    """Thunderbird/Lightning backend"""

    def __init__(self, settings):

        super().__init__(settings)

        self.thunderbird_location = Path.home() / '.mozilla-thunderbird'
        self.cursor = None
        self.conn = None

    @staticmethod
    def _parse_profile(filepath):
        try:
            with sqlite3.connect(str(filepath)) as conn:
                cursor = conn.cursor()
                qry = '''SELECT title, event_start FROM cal_events ce
                      INNER JOIN cal_properties cp
                      ON ce.id = cp.item_id
                      WHERE cp.key == 'CATEGORIES' AND
                      cp.value == 'Birthday' AND
                      ce.title != '';'''
                cursor.execute(qry)
                birthdates = [
                    (name, dt.datetime.utcfromtimestamp(
                        int(bdate_ts) / 1000000).date())
                    for name, bdate_ts in cursor]
                return birthdates
        except sqlite3.Error as exc:
            raise BackendReadError(exc)

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
                return self._parse_profile(db_location)
        # Missing profile file
        raise BackendReadError(
            self.tr("Error reading profile file: {}").format(profile_dir),
        )


BACKEND = LightningBackend
