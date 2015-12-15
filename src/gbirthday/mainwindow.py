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

from PyQt4 import QtCore, QtGui

import datetime

from gbirthday import PICS_PATHS, load_ui
from .databases import DATABASES
from .settings import Settings
from .addressbook import AddressBook
from .statusicon import StatusIcon

class Birthday(QtCore.QObject):

    def __init__(self, delta_day, name, birthdate):

        super().__init__()

        self.label_image = QtGui.QLabel()
        self.label_day = QtGui.QLabel(str(birthdate.day))
        self.label_month = QtGui.QLabel(_(birthdate.strftime('%B')))
        self.label_name = QtGui.QLabel(name)
        self.label_age = QtGui.QLabel(_('{} Years').format(
            datetime.date.today().year - birthdate.year))

        self.label_day.setAlignment(QtCore.Qt.AlignRight |
                                    QtCore.Qt.AlignVCenter)

        # Birthday today
        if delta_day == 0:
            
            self.label_image.setPixmap(
                QtGui.QPixmap(PICS_PATHS['birthdaytoday']))
            
            self.label_when = QtGui.QLabel(_('Today'))
        
        # Birthday in the past
        elif delta_day < 0:
            
            self.label_image.setPixmap(
                QtGui.QPixmap(PICS_PATHS['birthdaylost']))
            
            if delta_day == -1:
                self.label_when = QtGui.QLabel(_('Yesterday'))
            else:
                ago = (_('%s Days ago') % str(delta_day * -1))
                self.label_when = QtGui.QLabel(ago)

            for label in [self.label_day, self.label_month, self.label_name, 
                          self.label_age, self.label_when]:
                label.setStyleSheet("QLabel { color : grey; }")
        
        # Birthday in the future
        else:

            self.label_image.setPixmap(
                QtGui.QPixmap(PICS_PATHS['birthdaynext']))

            if delta_day == 1:
                self.label_when = QtGui.QLabel(_('Tomorrow'))
            else:
                self.label_when = QtGui.QLabel(_('%s Days') % delta_day)

class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        
        super().__init__()
        
        self.setWindowFlags(QtCore.Qt.Tool |
                            QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.WindowStaysOnTopHint)  # ??
        
        load_ui('mainwindow.ui', self)

        self.databases = {}
        
        # Load settings
        self.settings = Settings()
        self.settings.load_defaults()

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

    def showEvent(self, event):
        
        super().showEvent(event)
        
        # Window shall appear under mouse cursor
        self.move(QtGui.QCursor.pos() - QtCore.QPoint(self.width() / 2, 0))

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
                self.birthdaysLayout.addWidget(birthday.label_image, row, 0)
                self.birthdaysLayout.addWidget(birthday.label_day, row, 1)
                self.birthdaysLayout.addWidget(birthday.label_month, row, 2)
                self.birthdaysLayout.addWidget(birthday.label_name, row, 3)
                self.birthdaysLayout.addWidget(birthday.label_when, row, 4)
                self.birthdaysLayout.addWidget(birthday.label_age, row, 5)

    def check_new_day(self):
        '''Check for new day
        
           Should be called e.g. every 60 seconds to check if day has changed.
        '''
        
        new_day = datetime.datetime.now().strftime("%d")
        
        if self.current_day != new_day:
            self.current_day = new_day
            self.reload()
