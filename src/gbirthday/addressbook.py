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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
import datetime
from datetime import date

class AddressBook:
    '''AdressBook that saves birthday and names'''
    bdays = {} # list of all birthdays. Format:
               # {birthday: [Name1, Name2]}
               # for example
               # {'1970-01-01': ['Bar, Foo', 'Time'], 
               #  '1967-12-12': ['Power, Max']}

    def add(self, name, birthday):
        '''add a new person'''
        birthday = str(birthday)
        if birthday in self.bdays:
            # check for double entry - we assume that people with the same name
            # and the same birthday exists only once in our universe
            if not (name in self.bdays[birthday]):
                self.bdays[birthday].append(name)
        else:
            self.bdays[birthday] = [name]

    def manageBdays(self, conf):
        now = date.today()
        bdayKeys = self.bdays.keys()
        birthday_list = []
        temporal = []
        
        for d in range(int (conf.firstday), int (conf.lastday)+1):
            sDate = now + datetime.timedelta(d)

            for k in range(len(self.bdays)):
                sDateDay = str(sDate.day)
                
                for name in self.bdays[bdayKeys[k]]:
                    if len(sDateDay) != 2: 
                        sDateDay = '0' + sDateDay
                    sDateMonth = str(sDate.month)
                    if len(sDateMonth) != 2: 
                        sDateMonth = '0' + sDateMonth

                    if bdayKeys[k].find('-'+sDateMonth+'-'+sDateDay) != -1:
                        if d == 0:
                            birthday_today = True
                            pic = 'birthdaytoday.png'
                        elif d < 0:
                            pic = 'birthdaylost.png'
                        else:
                            pic = 'birthdaynext.png'

                        bday = bdayKeys[k]
                        
                        ano, mes, dia = bday.split('-', 2)
                        ano = sDate.year - int(ano)

                        temporal = [pic, bday, name, str(d), d,
                            sDate.month, sDate.day, ano]
                        birthday_list.append(temporal)
        return birthday_list

    def checktoday(self):

        now = date.today()
        bdayKeys = self.bdays.keys()
        birthday_today = False

        for d in range(0,1):
            sDate = now + datetime.timedelta(d)

            for k in range(len(self.bdays)):
                sDateDay = str(sDate.day)
                if len(sDateDay) != 2: 
                    sDateDay = '0' + sDateDay
                sDateMonth = str(sDate.month)
                if len(sDateMonth) != 2: 
                    sDateMonth = '0' + sDateMonth

                if bdayKeys[k].find('-'+sDateMonth+'-'+sDateDay) != -1:
                    if d == 0:
                        birthday_today = True
        return birthday_today

