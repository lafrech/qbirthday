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
from .__init__ import DATABASES


class AddressBook:
    '''AdressBook that saves birthday and names'''
    def __init__(self, conf=None):
        self.conf = conf
        if self.conf:
            self.firstday = conf.firstday
            self.lastday = conf.lastday
        else:
            self.firstday = -2
            self.lastday = 30
        self.bdays = {}  # list of all birthdays. Format:
                    # {birthday: [Name1, Name2]}
                    # for example
                    # {'1970-01-01': ['Bar, Foo', 'Time'],
                    #  '1967-12-12': ['Power, Max']}

        self.bdays_dict = {} # list of all birthdays in specified period
                    # Format: {3: [Name1, Name2],
                    #          4: [Name3, Name4]}

        self.needs_update = False # new bday was added -> dict needs update

    def add(self, name, birthday):
        '''add a new person'''
        self.needs_update = True
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
        if not self.conf:
            # when no config class exists do a simple reload and exit
            self.update()
            return

        for database in DATABASES:
            if (database.__class__.__name__ in self.conf.used_databases):
                database.parse(addressbook=self, conf=self.conf)
        self.update()

    def update(self):
        '''update bdays_dict to contain all bdays in specified period'''
        now = datetime.date.today()

        # delete bdays_dict
        self.bdays_dict = {}
        # iterate over specified period
        for day in range(self.firstday, self.lastday + 1):
            new_day = now + datetime.timedelta(day)
            searchfor = str(new_day)[4:]

            # is date in bdays.keys -> add to dict
            for date, birthdays in self.bdays.items():
                if date.find(searchfor) != -1:
                    self.bdays_dict[day] = birthdays
