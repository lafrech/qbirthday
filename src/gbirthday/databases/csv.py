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

class CsvPreferencesDialog(QtGui.QDialog):
    '''CSV backend settings dialog'''

    def __init__(self, settings, parent):

        super().__init__(parent)

        load_ui('csvpreferencesdialog.ui', self)

        self.settings = settings

        self.filePathEdit.setText(self.settings.value('CSV/filepath'))
        
        self.filePathButton.clicked.connect(self.get_filepath)

        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.save)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.save)

        # TODO: disable OK and Apply if no path provided

    def get_filepath(self):
        '''Get CSV file path'''

        self.filePathEdit.setText(
            QtGui.QFileDialog.getOpenFileName(self, 
                "Choose CSV file",
                self.filePathEdit.text() or QtCore.QDir.homePath()))

    def save(self):
        '''Save CSV backend settings'''
        
        self.settings.setValue('CSV/filepath', self.filePathEdit.text())

class CSV(DataBase):
    '''import from CSV-file'''

    TITLE = 'CSV-file (comma seperated value)'
    CAN_SAVE = True
    HAS_CONFIG = True
    CONFIG_DLG = CsvPreferencesDialog

    DEFAULTS = {
        'filepath': '',
    }

    def __init__(self, addressbook, settings):

        super().__init__(addressbook, settings)

        # Possible separators
        self._separators = ['; ', ', ', ': '] 

    def parse(self):
        '''open and parse file'''
        
        filepath = self.settings.value('CSV/filepath')

        if filepath is None:
            # TODO: show_error_msg
            print('Wrong CSV backed config: missing CSV file path')
            return

        try:
            with open(filepath) as f:
                for line in f:
                    # check if any of the seperators are in the text
                    for sep in self._separators:
                        if len(line.split(sep)) > 1:
                            date = line.split(sep, 1)[0]
                            name = line.split(sep, 1)[1][:-1]
                            self.addressbook.add(name, date)
                            break
        except IOError as e:
            # TODO: show_error_msg
            print('Missing CSV file {}'.format(filepath))

    def add(self, name, birthday):
        '''add new person with birthday to end of csv-file'''

        birthday = str(birthday)

        filepath = self.settings.value('CSV/filepath')

        if filepath is None:
            # TODO: show_error_msg
            print('Wrong CSV backed config: missing CSV file path')
            return

        try:
            with open(filepath, 'a') as f:
                f.write(birthday + '; ' + name + '\n')
            self.addressbook.add(name, birthday)
        except IOError as e:
            # TODO: show_error_msg
            print('Missing CSV file {}'.format(filepath))
