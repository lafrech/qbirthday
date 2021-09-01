"""BirthdayList module

BirthdayList is a structure storing birthdates and keeping track of birthdays
in a specified period around today's date.
"""

import datetime as dt
from collections import defaultdict

from PyQt5 import QtCore

from .ics_export import ICSExport
from .backends import BACKENDS
from .backends.exceptions import BackendReadError
from .exceptions import ICSExportError


class BirthdayList(QtCore.QObject):
    """Structure storing all birthdates and birthdays in specified period"""

    def __init__(self, main_window, settings):

        super().__init__()

        self.main_window = main_window
        self.settings = settings
        self.ics_export = ICSExport(settings)

        # dict storing all birthdates
        # key: dt.date
        # value: list of names
        self._birthdates = defaultdict(list)

        # dict storing birthdays in specified period
        # key: int (index of day in period)
        # value: list of (birthdate, name) tuples
        self._birthdays = defaultdict(list)

        self._needs_update = False

    def add(self, name, birthdate):
        """Add a new birthdate to the collection

        name (str): Person name
        birthdate (datetime.date): Date of birth
        """
        self._needs_update = True
        self._birthdates[birthdate].append(name)

    def bdays_in_period(self):
        """Return True, if there is a birthday in specified period"""
        first_day = self.settings.value("firstday", type=int)
        last_day = self.settings.value("lastday", type=int)
        for day in range(first_day, last_day + 1):
            if day in self._birthdays:
                return True
        return False

    def check_day(self, day_num=0):
        """Return all birthdays for a given day index in specified period"""
        if self._needs_update:
            self._update()
            self._needs_update = False
        return self._birthdays[day_num]

    def reload(self):
        """Reload birthdates from all backends and update birthdays"""

        self._birthdates.clear()

        for bcknd in BACKENDS:
            if bcknd.cls is not None and self.settings.value(
                bcknd.id + "/enabled", type=bool
            ):
                bcknd_inst = bcknd.cls(self.settings)
                try:
                    birthdates = bcknd_inst.parse()
                except BackendReadError as exc:
                    self.main_window.show_error_message(str(exc))
                else:
                    for name, date in birthdates:
                        self.add(name, date)

        self._update()

        if self.settings.value("ics_export/enabled", type=bool):
            try:
                self.ics_export.write(self._birthdates)
            except ICSExportError as exc:
                self.main_window.show_error_message(str(exc))

    def _update(self):
        """Update self.birthdays with all birthdays in specified period"""
        self._birthdays.clear()
        for day_num in range(
            self.settings.value("firstday", type=int),
            self.settings.value("lastday", type=int) + 1,
        ):
            day = dt.date.today() + dt.timedelta(day_num)
            for date, birthdate_list in self._birthdates.items():
                if day.day == date.day and day.month == date.month:
                    self._birthdays[day_num].extend(
                        [(date, name) for name in birthdate_list]
                    )
