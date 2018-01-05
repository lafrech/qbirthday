"""Status icon"""

from PyQt5 import QtCore, QtGui, QtWidgets, uic

from .preferencesdialog import PreferencesDialog
from .aboutdialog import AboutDialog
from .backends.exceptions import BackendWriteError
from .paths import PICS_PATHS, UI_FILES_DIR


class StatusIcon(QtWidgets.QSystemTrayIcon):
    """Status icon"""

    def __init__(self, main_window, settings):

        # TODO: enlarge icon to best fit
        super().__init__(QtGui.QIcon(PICS_PATHS['birthday']), main_window)

        self.main_window = main_window
        self.bday_list = main_window.bday_list
        self.settings = settings

        # TODO: Add action enabled only if at least one DB selected
        # TODO: Is there a standard translation in Qt for those menu actions?
        menu = QtWidgets.QMenu()
        menu.addAction(
            QtGui.QIcon.fromTheme("view-refresh"),
            self.tr("Refresh"),
            self.main_window.reload)
        menu.addAction(
            QtGui.QIcon.fromTheme("list-add"),
            self.tr("Add"),
            self.add_single_manual)
        menu.addAction(
            QtGui.QIcon.fromTheme("preferences-other"),
            self.tr("Preferences"),
            lambda: PreferencesDialog(self.settings, self.main_window).exec_())
        menu.addAction(
            QtGui.QIcon.fromTheme("help-about"),
            self.tr("About"),
            lambda: AboutDialog(self.main_window).exec_())
        menu.addAction(
            QtGui.QIcon.fromTheme("application-exit"),
            self.tr("Quit"),
            QtCore.QCoreApplication.instance().quit)

        # Set context menu to open on right click
        self.setContextMenu(menu)

        # Display birthdays on left click
        def tray_icon_activated_cb(reason):
            if (reason == QtWidgets.QSystemTrayIcon.Trigger or
                    reason == QtWidgets.QSystemTrayIcon.DoubleClick):
                # Toggle birthday window visibility
                self.main_window.setVisible(not self.main_window.isVisible())
        self.activated.connect(tray_icon_activated_cb)

        self._show_when_systray_available()

    def _show_when_systray_available(self):
        """Show status icon when system tray is available

        If available, show icon, otherwise, set a timer to check back later.
        This is a workaround for https://bugreports.qt.io/browse/QTBUG-61898
        """
        if self.isSystemTrayAvailable():
            self.show()
        else:
            QtCore.QTimer.singleShot(1000, self._show_when_systray_available)

    def reload_set_icon(self):
        """Set icon according to birthday status"""
        if self.bday_list.bdays_in_period():
            if self.bday_list.check_day(0):
                # Birthday today
                self.setIcon(QtGui.QIcon(PICS_PATHS['birthdayred']))
            else:
                self.setIcon(QtGui.QIcon(PICS_PATHS['birthday']))
        else:
            self.setIcon(QtGui.QIcon(PICS_PATHS['nobirthday']))

    # TODO: Make dedicated class for add birthdate widget
    def add_single_manual(self):
        """Add birthday dialog"""

        add_widget = uic.loadUi(str(UI_FILES_DIR / 'add.ui'))

        # Fill backend combobox
        # TODO: use index to allow DB name translation
        for bcknd in self.bday_list.read_write_backends:
            add_widget.saveComboBox.addItem(bcknd.TITLE)

        # Apply and OK enabled only if name not empty
        def entry_modification_cb():
            # TODO: check if text is not whitespace would be better
            cond = add_widget.nameEdit.text() != ''
            add_widget.buttonBox.button(
                QtWidgets.QDialogButtonBox.Apply).setEnabled(cond)
            add_widget.buttonBox.button(
                QtWidgets.QDialogButtonBox.Ok).setEnabled(cond)

        # Execute once to disable OK and Apply
        entry_modification_cb()
        # Connect signal to check at each text modification
        add_widget.nameEdit.textChanged.connect(entry_modification_cb)

        def add_single_manual_apply_cb():
            """Save new added birthdate"""
            for bcknd in self.bday_list.read_write_backends:
                if bcknd.TITLE == add_widget.saveComboBox.currentText():
                    name = add_widget.nameEdit.text()
                    birthdate = add_widget.dateWidget.selectedDate().toPyDate()
                    try:
                        bcknd.add(name, birthdate)
                    except BackendWriteError as exc:
                        self.main_window.show_error_message(str(exc))
                    else:
                        self.bday_list.add(name, birthdate)
            add_widget.nameEdit.clear()
            self.main_window.reload()

        # TODO: If apply, add birthdate
        add_widget.buttonBox.button(
            QtWidgets.QDialogButtonBox.Apply).clicked.connect(
                add_single_manual_apply_cb)

        # If OK, add birthdate and close dialog
        # If Cancel, just close dialog
        if add_widget.exec_():
            add_single_manual_apply_cb()
