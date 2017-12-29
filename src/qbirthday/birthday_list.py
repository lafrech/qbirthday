"""BirthdayList module

BirthdayList is a structure storing birthdates and keeping track of birthdays
in a specified period around today's date.
"""

import datetime as dt
from textwrap import dedent
from collections import defaultdict

from .backends import BACKENDS


class BirthdayList:
    """Structure storing all birthdates and birthdays in specified period"""

    def __init__(self, main_window, settings):

        self.main_window = main_window
        self.settings = settings

        self.backends = {}

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
        first_day = self.settings.value('firstday', type=int)
        last_day = self.settings.value('lastday', type=int)
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

        self.backends.clear()
        for bcknd_cls in BACKENDS:
            if self.settings.value(bcknd_cls.NAME + '/enabled', type=bool):
                bcknd = bcknd_cls(self.main_window)
                bcknd.parse()
                self.backends[bcknd_cls.NAME] = bcknd

        self._update()

        if self.settings.value('ics_export/enabled', type=bool):
            self._export()

    @property
    def read_write_backends(self):
        """Return list of all read-write backends (exclude RO backends)"""
        return [bcknd for bcknd in self.backends.values() if bcknd.CAN_SAVE]

    def _update(self):
        """Update self.birthdays with all birthdays in specified period"""
        self._birthdays.clear()
        for day_num in range(self.settings.value('firstday', type=int),
                             self.settings.value('lastday', type=int) + 1):
            day = dt.date.today() + dt.timedelta(day_num)
            for date, birthdate_list in self._birthdates.items():
                if day.day == date.day and day.month == date.month:
                    self._birthdays[day_num].extend(
                        [(date, name) for name in birthdate_list])

    def _export(self):
        '''Export birthday list as iCalendar file'''

        # This loop index is used to generate unique UIDs
        index = 0

        self.settings.beginGroup('ics_export')
        conf_filepath = self.settings.value(
            'filepath', type=str)
        conf_alarm = self.settings.value(
            'alarm', type=bool)
        conf_alarm_days = self.settings.value(
            'alarm_days', type=int)
        conf_custom_properties = self.settings.value(
            'custom_properties', type=str)
        conf_alarm_custom_properties = self.settings.value(
            'alarm_custom_properties', type=str)
        self.settings.endGroup()

        with open(conf_filepath, 'w') as f:
            f.write(dedent("""
                BEGIN:VCALENDAR
                VERSION:2.0
                PRODID:-//qbirthday//EN
                """))

            now = dt.datetime.now().strftime('%Y%m%dT%H%M%SZ')

            for bday in self._birthdates:
                bdate = bday.strftime('%Y%m%d')

                f.write('BEGIN:VEVENT\n')
                f.write('UID:' + now + '-' + str(index) + '@qbirthday' + '\n')
                f.write('CREATED:' + now + '\n')
                f.write('LAST-MODIFIED:' + now + '\n')
                f.write('DTSTAMP:' + now + '\n')
                f.write('DTSTART:' + bdate + '\n')
                f.write('DURATION:PT0S\n')
                f.write('CATEGORIES:' + _("Birthday") + '\n')
                f.write('SUMMARY:' + _("Birthday: ") + self._birthdates[
                    bday][0] + '\n')
                f.write(dedent("""
                    CLASS:PRIVATE
                    TRANSP:TRANSPARENT
                    RRULE:FREQ=YEARLY
                    """))
                if conf_alarm:
                    f.write('BEGIN:VALARM\n')
                    f.write('ACTION:DISPLAY\n')
                    f.write('TRIGGER;VALUE=DURATION:-P'
                            + str(conf_alarm_days) + 'D\n')
                    f.write('DESCRIPTION:' + _("Birthday: ")
                            + self._birthdates[bday][0] + '\n')
                    if conf_alarm_custom_properties != '':
                        f.write(conf_alarm_custom_properties + '\n')
                    f.write("END:VALARM\n")
                if conf_custom_properties != '':
                    f.write(conf_custom_properties + '\n')
                f.write("END:VEVENT\n")

                index += 1

            f.write("END:VCALENDAR")
