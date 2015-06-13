# -*- coding: UTF-8 -*-
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
from PyQt4 import QtCore, QtGui, uic

from .databases import DATABASES

class IcsExportPreferencesDialog(QtGui.QDialog):
    '''ICS export settings dialog'''

    def __init__(self, settings, parent):

        super().__init__(parent)

        uic.loadUi('ui/icsexportpreferencesdialog.ui', self)

        self.settings = settings

        self.settings.beginGroup('ics_export')
        self.filePathEdit.setText(self.settings.value('filepath'))
        self.alarmsCheckBox.setChecked(
            self.settings.value('alarm', False, type=bool))
        self.alarmsDelaySpinBox.setValue(
            self.settings.value('alarm_days', type=int))
        self.customVeventTextEdit.setPlainText(
            self.settings.value('custom_properties'))
        self.customValarmTextEdit.setPlainText(
            self.settings.value('alarm_custom_properties'))
        self.settings.endGroup()
        
        self.filePathButton.clicked.connect(self.get_filepath)
        
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.save)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.save)

        # TODO: disable OK and Apply if no path provided?

    def get_filepath(self):
        '''Get export file path'''

        # TODO: Qt5 introduces QStandardPaths. Use it as default.
        dialog = QtGui.QFileDialog(self)
        dialog.setDirectory(self.filePathEdit.text() or QtCore.QDir.homePath())
        dialog.setFileMode(QtGui.QFileDialog.AnyFile)
        if dialog.exec_():
            self.filePathEdit.setText(dialog.selectedFiles()[0])

    def save(self):
        '''Save ICS export settings'''
        
        self.settings.beginGroup('ics_export')
        self.settings.setValue('filepath', self.filePathEdit.text())
        self.settings.setValue('alarm', self.alarmsCheckBox.isChecked())
        self.settings.setValue('alarm_days', self.alarmsDelaySpinBox.value())
        self.settings.setValue('custom_properties',
            self.customVeventTextEdit.toPlainText())
        self.settings.setValue('alarm_custom_properties',
            self.customValarmTextEdit.toPlainText())
        self.settings.endGroup()

class PreferencesDialog(QtGui.QDialog):

    def __init__(self, settings, main_window):

        super().__init__(main_window)
        
        uic.loadUi('ui/preferencesdialog.ui', self)

        self.settings = settings
        self.main_window = main_window

        self.pastSpinBox.setValue(self.settings.value('firstday', type=int))
        self.nextSpinBox.setValue(self.settings.value('lastday', type=int))
        self.notifyNextSpinBox.setValue(
            self.settings.value('notify_future_bdays', type=int))
        self.icsExportCheckBox.setChecked(
            self.settings.value('ics_export/enabled', type=bool))
        self.icsExportButton.setEnabled(
            self.settings.value('ics_export/enabled', type=bool))

        self.icsExportCheckBox.stateChanged.connect(
            self.icsExportButton.setEnabled)
        self.icsExportButton.clicked.connect(
            lambda: IcsExportPreferencesDialog(self.settings, self).exec_())

        self.db_chkbx = {}
        
        for db in DATABASES:

            hbox = QtGui.QHBoxLayout()
            self.databasesLayout.addLayout(hbox)

            self.db_chkbx[db.__name__] = QtGui.QCheckBox(db.TITLE)
            db_used = self.settings.value(db.__name__ + '/enabled',
                                          type=bool)
            self.db_chkbx[db.__name__].setChecked(db_used)
            hbox.addWidget(self.db_chkbx[db.__name__])
            if db.HAS_CONFIG:
                button = QtGui.QPushButton(_('Preferences'))
                button.setEnabled(db_used)
                self.db_chkbx[db.__name__].stateChanged.connect(button.setEnabled)
                # TODO: write conf class
                #button.clicked.connect(
                #    lambda: db.preferences_dialog(self.settings, self).exec_())
                hbox.addWidget(button)

        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.save)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.save)

    def save(self):

        # Save settings
        self.settings.setValue('firstday', self.pastSpinBox.value())
        self.settings.setValue('lastday', self.nextSpinBox.value())
        self.settings.setValue('notify_future_bdays',
            self.notifyNextSpinBox.value())
        self.settings.setValue('ics_export/enabled',
            self.icsExportCheckBox.isChecked())

        for db in DATABASES:
            self.settings.setValue(db.__name__ + '/enabled',
                self.db_chkbx[db.__name__].isChecked())

        # Refresh birthday list
        self.main_window.refresh()
