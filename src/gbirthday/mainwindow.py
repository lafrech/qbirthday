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

import datetime

from PyQt5 import QtCore, QtGui, QtWidgets

from gbirthday import PICS_PATHS, load_ui
from .databases import DATABASES
from .addressbook import AddressBook
from .statusicon import StatusIcon


class Birthday(QtCore.QObject):

    def __init__(self, delta_day, name, birthdate):

        super().__init__()

        label_image = QtWidgets.QLabel()
        label_day = QtWidgets.QLabel(str(birthdate.day))
        label_month = QtWidgets.QLabel(_(birthdate.strftime('%B')))
        label_name = QtWidgets.QLabel(name)
        label_when = QtWidgets.QLabel()
        label_age = QtWidgets.QLabel(_('{} Years').format(
            datetime.date.today().year - birthdate.year))

        self.labels = [
            label_image,
            label_day,
            label_month,
            label_name,
            label_when,
            label_age
        ]

        label_day.setAlignment(QtCore.Qt.AlignRight |
                               QtCore.Qt.AlignVCenter)

        # Birthday today
        if delta_day == 0:
            label_image.setPixmap(QtGui.QPixmap(PICS_PATHS['birthdaytoday']))
            label_when.setText(_('Today'))
            for label in self.labels:
                label.setStyleSheet("QLabel { font: bold; }")

        # Birthday in the past
        elif delta_day < 0:
            label_image.setPixmap(QtGui.QPixmap(PICS_PATHS['birthdaylost']))
            if delta_day == -1:
                label_when.setText(_('Yesterday'))
            else:
                label_when.setText(_('%s Days ago') % str(delta_day * -1))

            for label in self.labels:
                label.setStyleSheet("QLabel { color : grey; }")

        # Birthday in the future
        else:
            label_image.setPixmap(QtGui.QPixmap(PICS_PATHS['birthdaynext']))
            if delta_day == 1:
                label_when.setText(_('Tomorrow'))
            else:
                label_when.setText(_('%s Days') % delta_day)

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowFlags(QtCore.Qt.Tool |
                            QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.WindowStaysOnTopHint)  # ??

        load_ui('mainwindow.ui', self)
        self.databases = {}

        # Load settings
        self.settings = QtCore.QSettings()
        self.load_default_settings()

        # Address book
        self.addressbook = AddressBook(self, self.settings)

        # Status icon
        self.status_icon = StatusIcon(self, self.settings)

        # Initialise current day
        self.current_day = datetime.datetime.now().strftime("%d")

        # Check every 60 seconds for new day
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.check_new_day)
        self.timer.start(60 * 1000)

        self.reload()

        # TODO: Catch mouse focus out and close window

    def load_default_settings(self):

        # General settings
        self.settings.setValue('firstday', self.settings.value('firstday', -2))
        self.settings.setValue('lastday', self.settings.value('lastday', 30))
        self.settings.setValue(
            'notify_future_birthdays',
            self.settings.value('notify_future_birthdays', 0)
        )

        # Database settings
        for db in DATABASES:

            # Disable all DB by default
            self.settings.setValue(
                '{}/enabled'.format(db.__name__),
                self.settings.value('{}/enabled'.format(db.__name__), False)
            )

            # Load DB specific default values
            for key, val in db.DEFAULTS.items():
                self.settings.setValue(
                    '{}/{}'.format(db.__name__, key),
                    self.settings.value('{}/{}'.format(db.__name__, key), val)
                )

        # ICS export
        self.settings.setValue(
            'ics_export/enabled',
            self.settings.value('ics_export/enabled', False)
        )

    def showEvent(self, event):

        super().showEvent(event)

        # Window shall appear under mouse cursor
        self.move(QtGui.QCursor.pos() - QtCore.QPoint(self.width() / 2, 0))

        # Ensure the window is not minimized on virtual desktop change
        self.showNormal()

    def reload(self):
        '''Reload data from databases'''

        # Instantiate database backends
        self.databases = {}
        for db in DATABASES:
            if self.settings.value(db.__name__ + '/enabled', type=bool):
                self.databases[db.__name__] = db(self)

        # Reload address book
        self.addressbook.reload()

        # Reload status icon
        self.status_icon.reload_set_icon()

        # Set title
        if self.addressbook.bdays_in_period():
            self.titleLabel.setText(_('Birthdays'))
        else:
            self.titleLabel.setText(_('No birthdays in specified period'))

        # Empty birthday list
        # http://stackoverflow.com/questions/4528347/
        for i in reversed(range(self.birthdaysLayout.count())):
            widget = self.birthdaysLayout.itemAt(i).widget()
            self.birthdaysLayout.removeWidget(widget)
            widget.setParent(None)

        # Add birthdays
        firstday = self.settings.value('firstday', type=int)
        lastday = self.settings.value('lastday', type=int)
        for delta_day in range(firstday, lastday + 1):
            for name in self.addressbook.check_day(delta_day):
                for date, names in self.addressbook.bdays.items():
                    if name in names:
                        birthdate = date

                birthday = Birthday(delta_day, name, birthdate)
                row = self.birthdaysLayout.rowCount()
                for col, label in enumerate(birthday.labels):
                    self.birthdaysLayout.addWidget(label, row, col)

    def check_new_day(self):
        '''Check for new day

           Should be called e.g. every 60 seconds to check if day has changed.
        '''
        new_day = datetime.datetime.now().strftime("%d")
        if self.current_day != new_day:
            self.current_day = new_day
            self.reload()
