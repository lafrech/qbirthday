"""Preferences dialog"""

from pathlib import Path

from PyQt5 import QtWidgets, uic

from .backends import BACKENDS
from .paths import UI_FILES_DIR


class IcsExportPreferencesDialog(QtWidgets.QDialog):
    """ICS export settings dialog"""

    def __init__(self, settings, parent):

        super().__init__(parent)

        uic.loadUi(str(UI_FILES_DIR / "icsexportpreferencesdialog.ui"), self)

        self.settings = settings

        self.settings.beginGroup("ics_export")
        self.filePathEdit.setText(self.settings.value("filepath", type=str))
        self.alarmsCheckBox.setChecked(self.settings.value("alarm", False, type=bool))
        # TODO: add default values?
        self.alarmsDelaySpinBox.setValue(self.settings.value("alarm_days", type=int))
        self.customVeventTextEdit.setPlainText(
            self.settings.value("custom_properties", type=str)
        )
        self.customValarmTextEdit.setPlainText(
            self.settings.value("alarm_custom_properties", type=str)
        )
        self.settings.endGroup()

        self.filePathButton.clicked.connect(self.get_filepath)

        self.buttonBox.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(
            self.save
        )
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.save)

        # TODO: disable OK and Apply if no path provided?

    def get_filepath(self):
        """Get export file path"""

        current_filepath = Path(self.filePathEdit.text()).resolve()
        current_filedir = current_filepath.parent

        # TODO: use QFileDialog.getOpenFileName?
        dialog = QtWidgets.QFileDialog(self)
        dialog.setDirectory(str(current_filedir))
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        if dialog.exec_():
            self.filePathEdit.setText(dialog.selectedFiles()[0])

    def save(self):
        """Save ICS export settings"""

        # TODO: Validate settings before saving? (filepath writable?)

        self.settings.beginGroup("ics_export")
        self.settings.setValue("filepath", self.filePathEdit.text())
        self.settings.setValue("alarm", self.alarmsCheckBox.isChecked())
        self.settings.setValue("alarm_days", self.alarmsDelaySpinBox.value())
        self.settings.setValue(
            "custom_properties", self.customVeventTextEdit.toPlainText()
        )
        self.settings.setValue(
            "alarm_custom_properties", self.customValarmTextEdit.toPlainText()
        )
        self.settings.endGroup()


class PreferencesDialog(QtWidgets.QDialog):
    """Settings dialog"""

    def __init__(self, settings, main_window):

        super().__init__(main_window)

        uic.loadUi(str(UI_FILES_DIR / "preferencesdialog.ui"), self)

        self.settings = settings
        self.main_window = main_window

        self.pastSpinBox.setValue(self.settings.value("firstday", type=int))
        self.nextSpinBox.setValue(self.settings.value("lastday", type=int))
        self.icsExportCheckBox.setChecked(
            self.settings.value("ics_export/enabled", type=bool)
        )
        self.icsExportButton.setEnabled(
            self.settings.value("ics_export/enabled", type=bool)
        )

        self.icsExportCheckBox.stateChanged.connect(self.icsExportButton.setEnabled)
        self.icsExportButton.clicked.connect(
            lambda: IcsExportPreferencesDialog(self.settings, self).exec_()
        )

        self.bcknd_chkbx = {}

        for bcknd in BACKENDS:

            hbox = QtWidgets.QHBoxLayout()
            self.backendsLayout.addLayout(hbox)
            self.bcknd_chkbx[bcknd.id] = QtWidgets.QCheckBox(bcknd.name)
            hbox.addWidget(self.bcknd_chkbx[bcknd.id])

            if bcknd.cls is not None:
                bcknd_used = self.settings.value(bcknd.id + "/enabled", type=bool)
                self.bcknd_chkbx[bcknd.id].setChecked(bcknd_used)
                if bcknd.cls.CONFIG_DLG is not None:
                    button = QtWidgets.QPushButton(self.tr("Preferences"))
                    button.setEnabled(bcknd_used)
                    self.bcknd_chkbx[bcknd.id].stateChanged.connect(button.setEnabled)
                    button.clicked.connect(
                        # http://stackoverflow.com/questions/2295290/
                        # http://stackoverflow.com/questions/18836291/
                        lambda ignore, dlg=bcknd.cls.CONFIG_DLG: dlg(
                            self.settings, self
                        ).exec_()
                    )
                    hbox.addWidget(button)
            else:
                self.bcknd_chkbx[bcknd.id].setChecked(False)
                self.bcknd_chkbx[bcknd.id].setEnabled(False)
                self.bcknd_chkbx[bcknd.id].setToolTip(bcknd.exc_str)

        self.buttonBox.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(
            self.save
        )
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.save)

    def save(self):
        """Save settings"""

        # TODO: Validate settings before saving?

        # Save settings
        self.settings.setValue("firstday", self.pastSpinBox.value())
        self.settings.setValue("lastday", self.nextSpinBox.value())
        self.settings.setValue("ics_export/enabled", self.icsExportCheckBox.isChecked())

        for bcknd in BACKENDS:
            self.settings.setValue(
                bcknd.id + "/enabled", self.bcknd_chkbx[bcknd.id].isChecked()
            )

        # Refresh birthday list
        self.main_window.reload()
