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
'''AddressBook module'''
import datetime
from textwrap import dedent

class AddressBook(object):
    '''AdressBook that saves birthday and names'''
    
    def __init__(self, main_window, settings):
        
        self.main_window = main_window
        self.settings = settings
        
        self.firstday = settings.value('firstday', type=int)
        self.lastday = settings.value('lastday', type=int)

        self.bdays = {}  # list of all birthdays. Format:
                    # {birthday: [Name1, Name2]}
                    # for example
                    # { datetime.date(1970, 1, 1): ['Bar, Foo', 'Time'],
                    #   datetime.date(1967, 12, 12)': ['Power, Max']}

        self.bdays_dict = {} # list of all birthdays in specified period
                    # Format: {3: [Name1, Name2],
                    #          4: [Name3, Name4]}

        self.needs_update = False # new bday was added -> dict needs update

    def add(self, name, birthday):
        '''add a new person'''
        self.needs_update = True
        if isinstance(birthday, str):
            if birthday.find("-") > -1:
                # birthday is in format YYYY-MM-DD
                birthday = datetime.date(*[int(b) for b in birthday.split('-')])
            else:
                # if birthday is in format YYYYMMDD
                birthday = datetime.date(int(birthday[:4]), 
                                         int(birthday[4:6]), 
                                         int(birthday[-2:]))
                
        if birthday in self.bdays:
            # check for double entry - we assume that people with the same name
            # and the same birthday exists only once in our universe
            if not (name in self.bdays[birthday]):
                self.bdays[birthday].append(name)
        else:
            self.bdays[birthday] = [name]

    def bdays_in_period(self, firstDay=None, lastDay=None):
        '''returns True, if there is a birthday in specified period'''
        if not firstDay:
            firstDay = self.firstday
        if not lastDay:
            lastDay = self.lastday
        for day in range(firstDay, lastDay + 1):
            if day in self.bdays_dict:
                return True
        return False

    def check_day(self, day_num=0):
        '''check if on day 'day_num' is a birthday
           'day_num' should be in range(specified period)'''
        if self.needs_update:
            self.needs_update = False
            self.update()

        try:
            return self.bdays_dict[day_num]
        except KeyError:
            return []

    def reload(self):
        '''
        reload all bdays from all databases and update bdays,
        all birthdays added with addressbook.add() are deleted after
        this
        '''

        # delete bdays dict and reload again
        self.bdays = {}
        
        for name, db in self.main_window.databases.items():
            db.parse()

        self.update()

        if self.settings.value('ics_export/enabled', type=bool):
            self.export()

    def update(self):
        '''update bdays_dict to contain all bdays in specified period'''
        now = datetime.date.today()

        # delete bdays_dict
        self.bdays_dict = {}

        # iterate over specified period
        for day_num in range(self.firstday, self.lastday + 1):
            day = now + datetime.timedelta(day_num)

            # For each (D-M-Y -> Name list)
            for date, birthday in self.bdays.items():
                # If D-M match day
                if day.day == date.day and day.month == date.month:
                    # If D-M not yet in dict, add D-M -> Name list
                    if day_num not in self.bdays_dict:
                        self.bdays_dict[day_num] = birthday[:]
                    # If D-M already in dict,
                    # another (D-M-Y -> Name list) exists for the same D-M
                    # but another Y, therefore, concatenate Name lists
                    else:
                        self.bdays_dict[day_num] += birthday[:]

    def export(self):
        '''Export birthday list as iCalendar file'''

        # This loop index is used to generate unique UIDs
        index = 0

        self.settings.beginGroup('ics_export')
        conf_filepath = self.settings.value('filepath')
        conf_alarm = self.settings.value('alarm')
        conf_alarm_days = self.settings.value('alarm_days')
        conf_custom_properties = self.settings.value('custom_properties')
        conf_alarm_custom_properties = self.settings.value(
            'alarm_custom_properties')
        self.settings.endGroup()

        with open(conf_filepath,'w') as f:
            f.write(dedent("""\
                BEGIN:VCALENDAR
                VERSION:2.0
                PRODID:-//gbirthday//EN
                """))

            now = datetime.datetime.now()
            now = str(now)[0:4] + str(now)[5:7] + str(now)[8:10] + 'T' \
                + str(now)[11:13] + str(now)[14:16] + str(now)[17:19] + 'Z'

            for bd in self.bdays:
                bdate = str(bd)[0:4] + str(bd)[5:7] + str(bd)[8:10]

                f.write('BEGIN:VEVENT\n')
                f.write('UID:' + now + '-' + str(index) + '@gbirthday' + '\n')
                f.write('CREATED:' + now + '\n')
                f.write('LAST-MODIFIED:' + now + '\n')
                f.write('DTSTAMP:' + now + '\n')
                f.write('DTSTART:' + bdate + '\n')
                f.write('DURATION:PT0S\n')
                f.write('CATEGORIES:' + _("Birthday") + '\n')
                f.write('SUMMARY:' + _("Birthday: ") + self.bdays[bd][0] + '\n')
                f.write(dedent("""\
                    CLASS:PRIVATE
                    TRANSP:TRANSPARENT
                    RRULE:FREQ=YEARLY
                    """))
                if conf_alarm:
                    f.write('BEGIN:VALARM\n')
                    f.write('ACTION:DISPLAY\n')
                    f.write('TRIGGER;VALUE=DURATION:-P' \
                        + alarm_days + 'D\n')
                    f.write('DESCRIPTION:' + _("Birthday: ") \
                        + self.bdays[bd][0] + '\n')
                    if conf_alarm_custom_properties != '':
                        f.write(conf_alarm_custom_properties + '\n')
                    f.write("END:VALARM\n")
                if self.conf_custom_properties != '':
                    f.write(conf_custom_properties + '\n')
                f.write("END:VEVENT\n")

                index+=1;

            f.write("END:VCALENDAR")

