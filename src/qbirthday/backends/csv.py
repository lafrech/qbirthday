"""CSV file backend"""

import datetime as dt

from PyQt5 import QtCore, QtWidgets

from qbirthday import load_ui
from .base import BaseRWBackend
from .exceptions import BackendReadError, BackendWriteError


class CSVPreferencesDialog(QtWidgets.QDialog):
    """CSV backend settings dialog"""

    def __init__(self, settings, parent):
        super().__init__(parent)
        load_ui('csvpreferencesdialog.ui', self)
        self.settings = settings
        self.filePathEdit.setText(self.settings.value('CSV/filepath'))
        self.filePathButton.clicked.connect(self.get_filepath)
        self.buttonBox.button(
            QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.save)
        self.buttonBox.button(
            QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.save)

        # TODO: disable OK and Apply if no path provided

    def get_filepath(self):
        '''Get CSV file path'''
        self.filePathEdit.setText(
            QtWidgets.QFileDialog.getOpenFileName(
                self,
                "Choose CSV file",
                self.filePathEdit.text() or QtCore.QDir.homePath()
            )[0])

    def save(self):
        '''Save CSV backend settings'''
        self.settings.setValue('CSV/filepath', self.filePathEdit.text())


class CSVBackend(BaseRWBackend):
    """CSV file backend"""

    NAME = 'CSV'
    TITLE = 'CSV-file (comma seperated value)'
    CONFIG_DLG = CSVPreferencesDialog

    DEFAULTS = {
        'filepath': '',
    }

    def __init__(self, settings):
        super().__init__(settings)
        # Possible separators
        # TODO: Pick only one separator? Exclude comma?
        self._separators = ['; ', ', ', ': ']

    def parse(self):
        '''open and parse file'''

        filepath = self.settings.value('CSV/filepath', type=str)

        birthdates = []

        try:
            with open(filepath) as csv_file:
                for line in csv_file:
                    # check if any of the seperators are in the text
                    for sep in self._separators:
                        if len(line.split(sep)) > 1:
                            date = dt.datetime.strptime(
                                line.split(sep, 1)[0], '%Y-%m-%d').date()
                            name = line.split(sep, 1)[1][:-1]
                            birthdates.append((name, date))
                            break
        except IOError:
            raise BackendReadError(
                _("Can't open CSV file: {}").format(filepath))

        return birthdates

    def add(self, name, birthday):
        '''add new person with birthday to end of csv-file'''

        filepath = self.settings.value('CSV/filepath', type=str)

        try:
            with open(filepath, 'a') as csv_file:
                csv_file.write(str(birthday) + '; ' + name + '\n')
        except IOError:
            raise BackendWriteError(
                _("Can't open CSV file: {}").format(filepath))
