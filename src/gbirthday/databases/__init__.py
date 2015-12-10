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

    # Database name displayed to user
    TITLE = 'Unknown database'
    # Whether database can save new birthdates
    CAN_SAVE = True
    # Configuration dialog
    CONFIG_DLG = None
    # Default configuration values
    DEFAULTS = {}

    def __init__(self, addressbook, settings=None):

        self.addressbook = addressbook
        self.settings = settings

    def parse(self):
        '''load file / open database connection'''
        raise NotImplementedError

    def add(self, name, birthday):
        '''save new birthday to file/database (only if CAN_SAVE == true)'''
        raise NotImplementedError

    def save_config(self, conf):
        '''record current entries in config menu into configuration'''
        raise NotImplementedError
    
    def create_config(self, vbox, conf):
        '''create additional pygtk config in config menu'''
        raise NotImplementedError

from .csv import CSV
from .lightning import Lightning
from .mysql import MySQL
from .sunbird import Sunbird

DATABASES = [CSV, Lightning, MySQL, Sunbird]
