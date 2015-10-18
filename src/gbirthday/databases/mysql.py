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

from PyQt4 import QtCore, QtGui

from gbirthday import load_ui
from gbirthday.databases import DataBase

class MySqlPreferencesDialog(QtGui.QDialog):
    '''MySQL backend settings dialog'''

    def __init__(self, settings, parent):

        super().__init__(parent)

        load_ui('mysqlpreferencesdialog.ui', self)

        self.settings = settings

        # Fill fields with current values
        self.hostEdit.setText(self.settings.value('MySQL/host', 'localhost'))
        self.portEdit.setText(self.settings.value('MySQL/port', '3306'))
        self.usernameEdit.setText(self.settings.value('MySQL/username', ''))
        self.passwordEdit.setText(self.settings.value('MySQL/password', ''))
        self.databaseEdit.setText(self.settings.value('MySQL/database', ''))
        self.tableEdit.setText(self.settings.value('MySQL/table', 'person'))
        self.nameRowEdit.setText(self.settings.value('MySQL/namerow', 'name'))
        self.dateRowEdit.setText(self.settings.value('MySQL/daterow', 'date'))
        
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(
            self.save)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(
            self.save)

        # TODO: disable OK and Apply if empty/invalid field

    def save(self):
        '''Save MySQL backend settings'''
        
        self.settings.setValue('MySQL/host', self.hostEdit.text())
        self.settings.setValue('MySQL/port', self.portEdit.text())
        self.settings.setValue('MySQL/username', self.usernameEdit.text())
        self.settings.setValue('MySQL/password', self.passwordEdit.text())
        self.settings.setValue('MySQL/database', self.databaseEdit.text())
        self.settings.setValue('MySQL/table', self.tableEdit.text())
        self.settings.setValue('MySQL/namerow', self.nameRowEdit.text())
        self.settings.setValue('MySQL/daterow', self.dateRowEdit.text())

class MySQL(DataBase):
    '''MySQL database import'''

    TITLE = 'MySQL'
    CAN_SAVE = True
    HAS_CONFIG = True
    CONFIG_DLG = MySqlPreferencesDialog

    def __init__(self, addressbook, settings):

        super().__init__(addressbook, settings)
        
        self.host = self.settings.value('MySQL/host')
        self.port = self.settings.value('MySQL/port')
        self.username = self.settings.value('MySQL/username')
        self.password = self.settings.value('MySQL/password')
        self.database = self.settings.value('MySQL/database')
        self.table = self.settings.value('MySQL/table')
        self.name_row = self.settings.value('MySQL/namerow')
        self.date_row = self.settings.value('MySQL/daterow')

        self.cursor = None
        self.conn = None

    def connect(self):
        '''establish connection'''
        try:
            import MySQLdb
        except ImportError:
            # TODO: show_error_msg
            print(_("Package {} is not installed.").format("MySQLdb"))
            return False
        try:
            self.conn = MySQLdb.connect(host=self.host,
                                    port=int(self.port),
                                    user=self.username,
                                    passwd=self.password,
                                    db=self.database)
            self.cursor = self.conn.cursor()
        except Exception as msg:
            # TODO: show_error_msg
            print(_("Could not connect to MySQL server:\n{}").format(msg))
            return False
        return True

    def parse(self):
        '''connect to mysql-database and get data'''
        if not self.connect():
            return
        try:
            qry = ("SELECT %s, %s FROM %s"
                        % (self.name_row, self.date_row, self.table))
            self.cursor.execute(qry)
            rows = self.cursor.fetchall()
            for row in rows:
                addressbook.add(row[0], str(row[1]))
        except Exception as msg:
            # TODO: show_error_msg
            print(_("Could not execute MySQL query '{}':\n{}").format(qry, msg))
        self.conn.close()

    def add(self, name, birthday):
        '''insert new Birthday to database'''
        birthday = str(birthday)
        if not self.connect():
            return
        try:
            qry = ("INSERT INTO %s (%s, %s) VALUES ('%s', '%s')" %
                (self.table, self.name_row, self.date_row, name, birthday))
            self.cursor.execute(qry)
        except Exception as msg:
            print(_("Could not execute MySQL query '{}':\n{}").format(qry, msg))
        self.conn.close()
        self.addressbook.add(name, birthday)
