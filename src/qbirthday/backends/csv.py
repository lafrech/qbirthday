"""CSV file backend"""

from PyQt5 import QtCore, QtWidgets

from qbirthday import load_ui
from .base import BaseBackend


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


class CSVBackend(BaseBackend):
    """CSV file backend"""

    NAME = 'CSV'
    TITLE = 'CSV-file (comma seperated value)'
    CAN_SAVE = True
    CONFIG_DLG = CSVPreferencesDialog

    DEFAULTS = {
        'filepath': '',
    }

    def __init__(self, mainwindow):

        super().__init__(mainwindow)

        # Possible separators
        self._separators = ['; ', ', ', ': ']

    def parse(self):
        '''open and parse file'''

        filepath = self.settings.value('CSV/filepath')

        try:
            with open(filepath) as csv_file:
                for line in csv_file:
                    # check if any of the seperators are in the text
                    for sep in self._separators:
                        if len(line.split(sep)) > 1:
                            date = line.split(sep, 1)[0]
                            name = line.split(sep, 1)[1][:-1]
                            self.addressbook.add(name, date)
                            break
        except IOError:
            # Missing CSV file
            QtWidgets.QMessageBox.warning(
                self.mainwindow,
                QtCore.QCoreApplication.applicationName(),
                'Missing CSV file: {}'.format(filepath),
                QtWidgets.QMessageBox.Discard)

    def add(self, name, birthday):
        '''add new person with birthday to end of csv-file'''

        birthday = str(birthday)

        filepath = self.settings.value('CSV/filepath')

        try:
            with open(filepath, 'a') as csv_file:
                csv_file.write(birthday + '; ' + name + '\n')
            self.addressbook.add(name, birthday)
        except IOError:
            # Missing CSV file
            QtWidgets.QMessageBox.warning(
                self.mainwindow,
                QtCore.QCoreApplication.applicationName(),
                _('Missing CSV file: {}').format(filepath),
                QtWidgets.QMessageBox.Discard
            )
