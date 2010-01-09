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
from datetime import date


class AddressBook:
    '''AdressBook that saves birthday and names'''
    def __init__(self):
        self.bdays = {}  # list of all birthdays. Format:
                    # {birthday: [Name1, Name2]}
                    # for example
                    # {'1970-01-01': ['Bar, Foo', 'Time'],
                    #  '1967-12-12': ['Power, Max']}

        self.bdays_dict = {} # list of all birthdays in specified period
                    # Format: {3: [Name1, Name2],
                    #          4: [Name3, Name4]}

    def add(self, name, birthday):
        '''add a new person'''
        birthday = str(birthday)

        # if birthday is in format JJJJMMDD modify it to JJJJ-MM-DD
        if birthday.find("-") is -1:
            birthday = birthday[:4] + "-" + birthday[4:6] + "-" + birthday[-2:]

        if birthday in self.bdays:
            # check for double entry - we assume that people with the same name
            # and the same birthday exists only once in our universe
            if not (name in self.bdays[birthday]):
                self.bdays[birthday].append(name)
        else:
            self.bdays[birthday] = [name]

    def manage_bdays(self, conf):
        '''Get current birthdays in specified period.'''
        now = date.today()
        bday_keys = self.bdays.keys()
        birthday_list = []
        temporal = []

        for day_num in range(int(conf.firstday), int(conf.lastday) + 1):
            day_date = now + datetime.timedelta(day_num)

            for k in range(len(self.bdays)):
                day_date_day = str(day_date.day)
                if len(day_date_day) == 1:
                    day_date_day = '0' + day_date_day

                for name in self.bdays[bday_keys[k]]:
                    day_date_month = str(day_date.month)
                    if len(day_date_month) == 1:
                        day_date_month = '0' + day_date_month

                    if bday_keys[k].find('-' + day_date_month
                                        + '-' + day_date_day) != -1:
                        if day_num == 0:
                            pic = 'birthdaytoday.png'
                        elif day_num < 0:
                            pic = 'birthdaylost.png'
                        else:
                            pic = 'birthdaynext.png'

                        bday = bday_keys[k]

                        year = bday[:4]
                        year = day_date.year - int(year)

                        temporal = [pic, bday, name, str(day_num), day_num,
                            day_date.month, day_date.day, year]
                        birthday_list.append(temporal)
        return birthday_list

    def checktoday(self):
        '''Check, if today is a bithday.'''

        now = date.today()
        bday_keys = self.bdays.keys()
        birthday_today = False

        for day_num in range(0, 1):
            day_date = now + datetime.timedelta(day_num)

            for k in range(len(self.bdays)):
                day_date_day = str(day_date.day)
                if len(day_date_day) != 2:
                    day_date_day = '0' + day_date_day
                day_date_month = str(day_date.month)
                if len(day_date_month) != 2:
                    day_date_month = '0' + day_date_month

                if bday_keys[k].find('-' + day_date_month + '-'
                                    + day_date_day) != -1:
                    if day_num == 0:
                        birthday_today = True
        return birthday_today

    def reload(self):
        '''reload all bdays from all databases and update bdays'''
        # TODO reload from all databases
        self.update()

    def update(self):
        '''update bdays_dict to contain all bdays in specified period'''
        pass
