"""Status icon"""

from PyQt5 import QtCore, QtGui, QtWidgets

from .preferencesdialog import PreferencesDialog
from .aboutdialog import AboutDialog
from .paths import PICS_PATHS


class StatusIcon(QtWidgets.QSystemTrayIcon):
    """Status icon"""

    def __init__(self, main_window, settings):

        # TODO: enlarge icon to best fit
        super().__init__(QtGui.QIcon(PICS_PATHS["birthday"]), main_window)

        self.main_window = main_window
        self.bday_list = main_window.bday_list
        self.settings = settings

        # TODO: Is there a standard translation in Qt for those menu actions?
        menu = QtWidgets.QMenu()
        menu.addAction(
            QtGui.QIcon.fromTheme("view-refresh"),
            self.tr("Refresh"),
            self.main_window.reload,
        )
        menu.addAction(
            QtGui.QIcon.fromTheme("preferences-other"),
            self.tr("Preferences"),
            lambda: PreferencesDialog(self.settings, self.main_window).exec_(),
        )
        menu.addAction(
            QtGui.QIcon.fromTheme("help-about"),
            self.tr("About"),
            lambda: AboutDialog(self.main_window).exec_(),
        )
        menu.addAction(
            QtGui.QIcon.fromTheme("application-exit"),
            self.tr("Quit"),
            QtCore.QCoreApplication.instance().quit,
        )

        # Set context menu to open on right click
        self.setContextMenu(menu)

        # Display birthdays on left click
        def tray_icon_activated_cb(reason):
            if (
                reason == QtWidgets.QSystemTrayIcon.Trigger
                or reason == QtWidgets.QSystemTrayIcon.DoubleClick
            ):
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
                self.setIcon(QtGui.QIcon(PICS_PATHS["birthdayred"]))
            else:
                self.setIcon(QtGui.QIcon(PICS_PATHS["birthday"]))
        else:
            self.setIcon(QtGui.QIcon(PICS_PATHS["nobirthday"]))
