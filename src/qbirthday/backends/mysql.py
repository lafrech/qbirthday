"""MySQL backend"""

from PyQt5 import QtCore, QtWidgets

from qbirthday import load_ui
from .base import BaseBackend


class MySqlPreferencesDialog(QtWidgets.QDialog):
    """MySQL backend settings dialog"""

    def __init__(self, settings, parent):

        super().__init__(parent)

        load_ui('mysqlpreferencesdialog.ui', self)

        self.settings = settings

        # Fill fields with current values
        self.settings.beginGroup('MySQL')
        self.hostEdit.setText(self.settings.value('host', type=str))
        self.portEdit.setText(self.settings.value('port', type=int))
        self.usernameEdit.setText(self.settings.value('username', type=str))
        self.passwordEdit.setText(self.settings.value('password', type=str))
        self.databaseEdit.setText(self.settings.value('database', type=str))
        self.tableEdit.setText(self.settings.value('table', type=str))
        self.nameRowEdit.setText(self.settings.value('namerow', type=str))
        self.dateRowEdit.setText(self.settings.value('daterow', type=str))
        self.settings.endGroup()

        self.buttonBox.button(
            QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.save)
        self.buttonBox.button(
            QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.save)

        # TODO: disable OK and Apply if empty/invalid field

    def save(self):
        '''Save MySQL backend settings'''

        self.settings.beginGroup('MySQL')
        self.settings.setValue('host', self.hostEdit.text())
        self.settings.setValue('port', int(self.portEdit.text()))
        self.settings.setValue('username', self.usernameEdit.text())
        self.settings.setValue('password', self.passwordEdit.text())
        self.settings.setValue('database', self.databaseEdit.text())
        self.settings.setValue('table', self.tableEdit.text())
        self.settings.setValue('namerow', self.nameRowEdit.text())
        self.settings.setValue('daterow', self.dateRowEdit.text())
        self.settings.endGroup()


class MySQLBackend(BaseBackend):
    """MySQL backend"""

    NAME = 'MySQL'
    TITLE = 'MySQL'
    CAN_SAVE = True
    CONFIG_DLG = MySqlPreferencesDialog

    DEFAULTS = {
        'host': 'localhost',
        'port': 3306,
        'username': '',
        'password': '',
        'database': '',
        'table': 'person',
        'namerow': 'name',
        'daterow': 'date',
    }

    def __init__(self, mainwindow):

        super().__init__(mainwindow)

        self.settings.beginGroup('MySQL')
        self.host = self.settings.value('host', type=str)
        self.port = self.settings.value('port', type=int)
        self.username = self.settings.value('username', type=str)
        self.password = self.settings.value('password', type=str)
        self.database = self.settings.value('database', type=str)
        self.table = self.settings.value('table', type=str)
        self.name_row = self.settings.value('namerow', type=str)
        self.date_row = self.settings.value('daterow', type=str)
        self.settings.endGroup()

        self.cursor = None
        self.conn = None

    def connect(self):
        '''establish connection'''

        # TODO: use with connect as... syntax
        try:
            import MySQLdb
        except ImportError:
            # Missing MySQLdb
            QtWidgets.QMessageBox.warning(
                self.mainwindow,
                QtCore.QCoreApplication.applicationName(),
                _("Package {} is not installed.").format("MySQLdb"),
                QtWidgets.QMessageBox.Discard
            )
            return False

        try:
            self.conn = MySQLdb.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                passwd=self.password,
                db=self.database)
            self.cursor = self.conn.cursor()
        except Exception as msg:
            # Connexion error
            QtWidgets.QMessageBox.warning(
                self.mainwindow,
                QtCore.QCoreApplication.applicationName(),
                _("Could not connect to MySQL server:\n{}").format(msg),
                QtWidgets.QMessageBox.Discard
            )
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
                self.addressbook.add(row[0], str(row[1]))
        except Exception as msg:
            # Query error
            QtWidgets.QMessageBox.warning(
                self.mainwindow,
                QtCore.QCoreApplication.applicationName(),
                _("Could not execute MySQL query '{}':\n{}").format(qry, msg),
                QtWidgets.QMessageBox.Discard
            )

        self.conn.close()

    def add(self, name, birthday):
        '''insert new Birthday to database'''
        birthday = str(birthday)
        if not self.connect():
            return
        try:
            qry = (
                "INSERT INTO %s (%s, %s) VALUES ('%s', '%s')" %
                (self.table, self.name_row, self.date_row, name, birthday))
            self.cursor.execute(qry)
        except Exception as msg:
            # Query error
            QtWidgets.QMessageBox.warning(
                self.mainwindow,
                QtCore.QCoreApplication.applicationName(),
                _("Could not execute {} query '{}':\n{}").format(
                    'MySQL', qry, msg),
                QtWidgets.QMessageBox.Discard
            )
        self.conn.close()
        self.addressbook.add(name, birthday)
