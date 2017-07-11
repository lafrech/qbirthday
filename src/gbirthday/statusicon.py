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

from PyQt5 import QtCore, QtGui, QtWidgets

from gbirthday import PICS_PATHS, load_ui
from .preferencesdialog import PreferencesDialog
from .aboutdialog import AboutDialog


class StatusIcon(QtWidgets.QSystemTrayIcon):
    '''Class to show status icon'''

    def __init__(self, main_window, settings):
        '''create status icon'''

        # TODO: enlarge icon to best fit
        super().__init__(QtGui.QIcon(PICS_PATHS['birthday']),
                         main_window)

        self.main_window = main_window
        self.settings = settings

        # TODO: Add action enabled only if at least one DB selected
        menu = QtWidgets.QMenu()
        menu.addAction(
            QtGui.QIcon.fromTheme("view-refresh"),
            "Refresh",
            self.main_window.reload)
        menu.addAction(
            QtGui.QIcon.fromTheme("list-add"),
            "Add",
            self.add_single_manual)
        menu.addAction(
            QtGui.QIcon.fromTheme("preferences-other"),
            "Preferences",
            lambda: PreferencesDialog(self.settings, self.main_window).exec_())
        menu.addAction(
            QtGui.QIcon.fromTheme("help-about"),
            "About",
            lambda: AboutDialog(self.main_window).exec_())
        menu.addAction(
            QtGui.QIcon.fromTheme("application-exit"),
            "Quit",
            QtCore.QCoreApplication.instance().quit)

        # Set context menu to open on right click
        self.setContextMenu(menu)

        # Display birthdays on left click
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
        '''Check, if there is a birthday and set icon and notify accordingly.'''

        addressbook = self.main_window.addressbook

        # check if a birthday is in specified period
        if addressbook.bdays_in_period():
            # check if birthday today
            if addressbook.check_day(0):
                self.setIcon(QtGui.QIcon(PICS_PATHS['birthdayred']))
            else:
                self.setIcon(QtGui.QIcon(PICS_PATHS['birthday']))
        else:
            self.setIcon(QtGui.QIcon(PICS_PATHS['nobirthday']))

        # show notification of birthdays in the future
        try:
            # TODO: import this on top of script?
            import pynotify
            if pynotify.init("gbirthday"):
                lastday = self.settings.value('lastday', type=int)
                notify_future_bdays = self.settings.value(
                    'notify_future_bdays ', type=int)
                for day in range(lastday+1):
                    noty_string = None
                    if day == 0:
                        noty_string = _("Birthday today:")
                    elif day <= notify_future_bdays:
                        if day == 1:
                            noty_string = _("Birthday tomorrow:")
                        else:
                            noty_string = _("Birthday in %s Days:") % day
                    else:
                        continue
                    for name in addressbook.check_day(day):
                        notify = pynotify.Notification(
                                        noty_string, name)
                        notify.show()
        except ImportError:
            pass

    # TODO: Make dedicated class for add birthdate widget
    def add_single_manual(self):
        '''Add birthday dialog'''

        add_widget = load_ui('add.ui')

        # Fill database combobox
        # TODO: use index to allow DB name translation
        for db in self.main_window.databases.values():
            if db.CAN_SAVE:
                add_widget.saveComboBox.addItem(db.TITLE)

        # Apply and OK enabled only if name not empty 
        def entry_modification_cb():
            # TODO: check if text is not whitespace would be better
            cond = add_widget.nameEdit.text() != ''
            add_widget.buttonBox.button(
                QtWidgets.QDialogButtonBox.Apply).setEnabled(cond)
            add_widget.buttonBox.button(
                QtWidgets.QDialogButtonBox.Ok).setEnabled(cond)

        # Execute once to disable OK and Apply
        entry_modification_cb()
        # Connect signal to check at each text modification
        add_widget.nameEdit.textChanged.connect(entry_modification_cb)

        def add_single_manual_apply_cb():
            '''Save new added person'''
            for db in self.main_window.databases.values():
                if db.TITLE == add_widget.saveComboBox.currentText():
                    birthdate = add_widget.dateWidget.selectedDate().toPyDate()
                    # FIXME: ugly fix for #563405 adding to Lightning
                    if db.TITLE == 'Thunderbird/Icedove Lightning':
                        db.ab = self.main_window.addressbook
                    db.add(add_widget.nameEdit.text(), birthdate)
            add_widget.nameEdit.clear()
            self.main_window.reload()

        # TODO: If apply, add birthdate
        add_widget.buttonBox.button(
            QtWidgets.QDialogButtonBox.Apply).clicked.connect(
                add_single_manual_apply_cb)

        # If OK, add birthdate and close dialog
        # If Cancel, just close dialog
        if add_widget.exec_():
            add_single_manual_apply_cb()
