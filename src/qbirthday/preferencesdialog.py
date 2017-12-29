"""Preferences dialog"""

from PyQt5 import QtCore, QtWidgets

from qbirthday import load_ui
from .backends import BACKENDS


class IcsExportPreferencesDialog(QtWidgets.QDialog):
    '''ICS export settings dialog'''

    def __init__(self, settings, parent):

        super().__init__(parent)

        load_ui('icsexportpreferencesdialog.ui', self)

        self.settings = settings

        self.settings.beginGroup('ics_export')
        self.filePathEdit.setText(self.settings.value('filepath', type=str))
        self.alarmsCheckBox.setChecked(
            self.settings.value('alarm', False, type=bool))
        # TODO: add default values?
        self.alarmsDelaySpinBox.setValue(
            self.settings.value('alarm_days', type=int))
        self.customVeventTextEdit.setPlainText(
            self.settings.value('custom_properties', type=str))
        self.customValarmTextEdit.setPlainText(
            self.settings.value('alarm_custom_properties', type=str))
        self.settings.endGroup()

        self.filePathButton.clicked.connect(self.get_filepath)

        self.buttonBox.button(
            QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.save)
        self.buttonBox.button(
            QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.save)

        # TODO: disable OK and Apply if no path provided?

    def get_filepath(self):
        '''Get export file path'''

        # TODO: Qt5 introduces QStandardPaths. Use it as default.
        # TODO: use QFileDialog.getOpenFileName?
        dialog = QtWidgets.QFileDialog(self)
        dialog.setDirectory(self.filePathEdit.text() or QtCore.QDir.homePath())
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
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


class PreferencesDialog(QtWidgets.QDialog):

    def __init__(self, settings, main_window):

        super().__init__(main_window)

        load_ui('preferencesdialog.ui', self)

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

        self.bcknd_chkbx = {}

        for bcknd in BACKENDS:

            hbox = QtWidgets.QHBoxLayout()
            self.backendsLayout.addLayout(hbox)

            self.bcknd_chkbx[bcknd.NAME] = QtWidgets.QCheckBox(bcknd.TITLE)
            bcknd_used = self.settings.value(
                bcknd.NAME + '/enabled', type=bool)
            self.bcknd_chkbx[bcknd.NAME].setChecked(bcknd_used)
            hbox.addWidget(self.bcknd_chkbx[bcknd.NAME])
            if bcknd.CONFIG_DLG is not None:
                button = QtWidgets.QPushButton(_('Preferences'))
                button.setEnabled(bcknd_used)
                self.bcknd_chkbx[bcknd.NAME].stateChanged.connect(
                    button.setEnabled)
                button.clicked.connect(
                    # http://stackoverflow.com/questions/2295290/
                    # http://stackoverflow.com/questions/18836291/
                    lambda ignore, dlg=bcknd.CONFIG_DLG: dlg(
                        self.settings, self).exec_())
                hbox.addWidget(button)

        self.buttonBox.button(
            QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.save)
        self.buttonBox.button(
            QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.save)

    def save(self):

        # TODO: Validate settings before saving?

        # Save settings
        self.settings.setValue('firstday', self.pastSpinBox.value())
        self.settings.setValue('lastday', self.nextSpinBox.value())
        self.settings.setValue('notify_future_bdays',
                               self.notifyNextSpinBox.value())
        self.settings.setValue('ics_export/enabled',
                               self.icsExportCheckBox.isChecked())

        for bcknd in BACKENDS:
            self.settings.setValue(bcknd.NAME + '/enabled',
                                   self.bcknd_chkbx[bcknd.NAME].isChecked())

        # Refresh birthday list
        self.main_window.reload()