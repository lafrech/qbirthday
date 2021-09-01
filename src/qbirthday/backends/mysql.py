"""MySQL backend"""

from PyQt5 import QtWidgets, uic

from qbirthday.paths import UI_FILES_DIR
from .base import BaseBackend, try_import
from .exceptions import BackendMissingLibraryError, BackendReadError


BACKEND_ID = "MySQL"
BACKEND_NAME = "MySQL database"


try:
    # pylint: disable=invalid-name
    MySQLdb = try_import("MySQLdb", "mysqlclient")
except BackendMissingLibraryError as exc:
    exc.bcknd_id = BACKEND_ID
    exc.bcknd_name = BACKEND_NAME
    raise exc


class MySqlPreferencesDialog(QtWidgets.QDialog):
    """MySQL backend settings dialog"""

    def __init__(self, settings, parent):

        super().__init__(parent)

        uic.loadUi(str(UI_FILES_DIR / "mysqlpreferencesdialog.ui"), self)

        self.settings = settings

        # Fill fields with current values
        self.settings.beginGroup("MySQL")
        self.hostEdit.setText(self.settings.value("host", type=str))
        self.portEdit.setText(str(self.settings.value("port", type=int)))
        self.usernameEdit.setText(self.settings.value("username", type=str))
        self.passwordEdit.setText(self.settings.value("password", type=str))
        self.databaseEdit.setText(self.settings.value("database", type=str))
        self.tableEdit.setText(self.settings.value("table", type=str))
        self.nameColEdit.setText(self.settings.value("namecol", type=str))
        self.dateColEdit.setText(self.settings.value("datecol", type=str))
        self.settings.endGroup()

        self.buttonBox.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(
            self.save
        )
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.save)

        # TODO: disable OK and Apply if empty/invalid field

    def save(self):
        """Save MySQL backend settings"""

        self.settings.beginGroup("MySQL")
        self.settings.setValue("host", self.hostEdit.text())
        self.settings.setValue("port", int(self.portEdit.text()))
        self.settings.setValue("username", self.usernameEdit.text())
        self.settings.setValue("password", self.passwordEdit.text())
        self.settings.setValue("database", self.databaseEdit.text())
        self.settings.setValue("table", self.tableEdit.text())
        self.settings.setValue("namecol", self.nameColEdit.text())
        self.settings.setValue("datecol", self.dateColEdit.text())
        self.settings.endGroup()


class MySQLBackend(BaseBackend):
    """MySQL backend"""

    CONFIG_DLG = MySqlPreferencesDialog

    DEFAULTS = {
        "host": "localhost",
        "port": 3306,
        "username": "",
        "password": "",
        "database": "",
        "table": "person",
        "namecol": "name",
        "datecol": "date",
    }

    def __init__(self, settings):

        super().__init__(settings)

        self.settings.beginGroup("MySQL")
        self.host = self.settings.value("host", type=str)
        self.port = self.settings.value("port", type=int)
        self.username = self.settings.value("username", type=str)
        self.password = self.settings.value("password", type=str)
        self.database = self.settings.value("database", type=str)
        self.table = self.settings.value("table", type=str)
        self.name_col = self.settings.value("namecol", type=str)
        self.date_col = self.settings.value("datecol", type=str)
        self.settings.endGroup()

        self.cursor = None
        self.conn = None

    def _connect(self):
        """establish connection"""

        try:
            self.conn = MySQLdb.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                passwd=self.password,
                db=self.database,
            )
            self.cursor = self.conn.cursor()
        except Exception as exc:
            raise ConnectionError(exc)

    def parse(self):
        """connect to mysql-database and get data"""

        # TODO: use a context manager
        try:
            self._connect()
        except ConnectionError as exc:
            raise BackendReadError(exc)

        try:
            qry = f"SELECT {self.name_col}, {self.date_col} FROM {self.table}"
            self.cursor.execute(qry)
            rows = self.cursor.fetchall()
            birthdates = []
            for row in rows:
                birthdates.append((row[0], row[1]))
        except Exception as msg:
            raise BackendReadError(
                self.tr("Could not execute SQL query '{}':\n{}").format(qry, msg)
            )
        else:
            return birthdates
        finally:
            self.conn.close()


BACKEND = MySQLBackend
