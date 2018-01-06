"""MySQL backend"""

from PyQt5 import QtWidgets, uic

from qbirthday.paths import UI_FILES_DIR
from .base import BaseBackend
from .exceptions import BackendMissingLibraryError, BackendReadError


class MySqlPreferencesDialog(QtWidgets.QDialog):
    """MySQL backend settings dialog"""

    def __init__(self, settings, parent):

        super().__init__(parent)

        uic.loadUi(str(UI_FILES_DIR / 'mysqlpreferencesdialog.ui'), self)

        self.settings = settings

        # Fill fields with current values
        self.settings.beginGroup('MySQL')
        self.hostEdit.setText(self.settings.value('host', type=str))
        self.portEdit.setText(str(self.settings.value('port', type=int)))
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

    def __init__(self, settings):

        super().__init__(settings)

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

    def _connect(self):
        '''establish connection'''

        try:
            import MySQLdb
        except ImportError:
            raise BackendMissingLibraryError(
                self.tr("Missing {} library.").format("MySQLdb"))

        try:
            self.conn = MySQLdb.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                passwd=self.password,
                db=self.database)
            self.cursor = self.conn.cursor()
        except Exception as exc:
            raise ConnectionError(exc)

    def parse(self):
        '''connect to mysql-database and get data'''

        # TODO: use a context manager
        try:
            self._connect()
        except ConnectionError as exc:
            raise BackendReadError(exc)

        try:
            qry = ("SELECT %s, %s FROM %s"
                   % (self.name_row, self.date_row, self.table))
            self.cursor.execute(qry)
            rows = self.cursor.fetchall()
            birthdates = []
            for row in rows:
                birthdates.append((row[0], row[1]))
        except Exception as msg:
            raise BackendReadError(
                self.tr("Could not execute SQL query '{}':\n{}").format(
                    qry, msg))
        else:
            return birthdates
        finally:
            self.conn.close()
