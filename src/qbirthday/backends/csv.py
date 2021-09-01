"""CSV file backend"""

import datetime as dt
import csv

from PyQt5 import QtCore, QtWidgets, uic

from qbirthday.paths import UI_FILES_DIR
from qbirthday.paths import APP_DATA_LOCATION
from .base import BaseBackend
from .exceptions import BackendReadError


BACKEND_ID = "CSV"
BACKEND_NAME = "CSV-file (comma separated value)"


class CSVPreferencesDialog(QtWidgets.QDialog):
    """CSV backend settings dialog"""

    def __init__(self, settings, parent):
        super().__init__(parent)
        uic.loadUi(str(UI_FILES_DIR / "csvpreferencesdialog.ui"), self)
        self.settings = settings
        self.filePathEdit.setText(self.settings.value("CSV/filepath"))
        self.filePathButton.clicked.connect(self.get_filepath)
        self.delimiterEdit.setText(self.settings.value("CSV/delimiter"))
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(
            self.save
        )
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.save)

        # TODO: disable OK and Apply if no path provided

    def get_filepath(self):
        """Get CSV file path"""
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Choose CSV file", self.filePathEdit.text() or QtCore.QDir.homePath()
        )
        if filepath:
            self.filePathEdit.setText(filepath)

    def save(self):
        """Save CSV backend settings"""
        self.settings.setValue("CSV/filepath", self.filePathEdit.text())
        self.settings.setValue("CSV/delimiter", self.delimiterEdit.text())


class CSVBackend(BaseBackend):
    """CSV file backend"""

    CONFIG_DLG = CSVPreferencesDialog

    DEFAULTS = {"filepath": str(APP_DATA_LOCATION / "qbirthday.csv"), "delimiter": ","}

    def __init__(self, settings):
        super().__init__(settings)
        self._filepath = self.settings.value("CSV/filepath", type=str)
        self._delimiter = self.settings.value("CSV/delimiter", type=str)

    def _raise_invalid_row_error(self, row):
        raise ValueError(
            self.tr('Invalid row "{row}" in CSV file {filepath}').format(
                row=self._delimiter.join(row), filepath=self._filepath
            )
        )

    def parse(self):
        """open and parse file"""

        birthdates = []

        try:
            with open(self._filepath) as csv_file:
                # Filter empty and commented rows
                filtered_rows = (
                    r for r in csv_file if (not r.startswith("#")) and r.strip()
                )
                for row in csv.reader(filtered_rows, delimiter=self._delimiter):
                    if len(row) != 2:
                        self._raise_invalid_row_error(row)
                    try:
                        date = dt.datetime.strptime(row[0], "%Y-%m-%d").date()
                    except ValueError:
                        self._raise_invalid_row_error(row)
                    else:
                        name = row[1].strip()
                        birthdates.append((name, date))
        except OSError:
            raise BackendReadError(
                self.tr("Can't open CSV file: {}").format(self._filepath)
            )
        except ValueError as exc:
            raise BackendReadError(exc)

        return birthdates


BACKEND = CSVBackend
