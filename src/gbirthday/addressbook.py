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

        for d in range(int(conf.firstday), int(conf.lastday) + 1):
            sDate = now + datetime.timedelta(d)

            for k in range(len(self.bdays)):
                sDateDay = str(sDate.day)

                for name in self.bdays[bday_keys[k]]:
                    if len(sDateDay) != 2:
                        sDateDay = '0' + sDateDay
                    sDateMonth = str(sDate.month)
                    if len(sDateMonth) != 2:
                        sDateMonth = '0' + sDateMonth

                    if bday_keys[k].find('-' + sDateMonth
                                        + '-' + sDateDay) != -1:
                        if d == 0:
                            pic = 'birthdaytoday.png'
                        elif d < 0:
                            pic = 'birthdaylost.png'
                        else:
                            pic = 'birthdaynext.png'

                        bday = bday_keys[k]

                        year = bday[:4]
                        year = sDate.year - int(year)

                        temporal = [pic, bday, name, str(d), d,
                            sDate.month, sDate.day, year]
                        birthday_list.append(temporal)
        return birthday_list

    def checktoday(self):

        now = date.today()
        bday_keys = self.bdays.keys()
        birthday_today = False

        for d in range(0, 1):
            sDate = now + datetime.timedelta(d)

            for k in range(len(self.bdays)):
                sDateDay = str(sDate.day)
                if len(sDateDay) != 2:
                    sDateDay = '0' + sDateDay
                sDateMonth = str(sDate.month)
                if len(sDateMonth) != 2:
                    sDateMonth = '0' + sDateMonth

                if bday_keys[k].find('-' + sDateMonth + '-'
                                    + sDateDay) != -1:
                    if d == 0:
                        birthday_today = True
        return birthday_today
