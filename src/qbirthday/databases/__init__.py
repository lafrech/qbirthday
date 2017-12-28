"""Base class for all backends"""


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

    def __init__(self, mainwindow):

        self.mainwindow = mainwindow
        self.addressbook = mainwindow.addressbook
        self.settings = mainwindow.settings

    def parse(self):
        '''load file / open database connection'''
        raise NotImplementedError

    def add(self, name, birthday):
        '''save new birthday to file/database (only if CAN_SAVE == true)'''
        raise NotImplementedError


from .csv import CSV
from .lightning import Lightning
from .mysql import MySQL
from .sunbird import Sunbird

DATABASES = [CSV, Lightning, MySQL, Sunbird]
