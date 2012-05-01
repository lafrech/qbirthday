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
'''Database classes:

'DataBase' from which everything inherits:
- CSV
- Evolution
- Lightning
- MySQL
- Sunbird

'''

class DataBase(object):
    '''
     inheritance class for all databases
     you can use this format to add new databases
     your DataBase implementation has to parse the data from your data source,
     and add it into the AddressBook (ab.add())
     you have to add your Database to the databases-list
    '''

    def __init__(self, title='Unknown', can_save=True, has_config=True):
        # Title that will be displayed to the user
        self.TITLE = title
        # new entries can be saved
        self.CAN_SAVE = can_save
        # additional config options for database connection or fukebane(s)
        self.HAS_CONFIG = has_config

    def parse(self, addressbook, conf):
        '''load file / open database connection'''
        # XXX: set addressbook in __init__?
        self.ab = addressbook
        pass

    def add(self, name, birthday):
        '''save new birthday to file/database (only if CAN_SAVE == true)'''
        pass

    def save_config(self, conf):
        '''record current entries in config menu into configuration'''
        pass
    
    def create_config(self, vbox, conf):
        '''create additional pygtk config in config menu'''
        pass

from csv import CSV
from evolution import Evolution
from lightning import Lightning
from mysql import MySQL
from sunbird import Sunbird

mysql_db = MySQL()
DATABASES = [CSV(), Evolution(), Lightning(), mysql_db, Sunbird()]
