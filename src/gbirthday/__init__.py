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
'''GBirthday

A KBirthday clone working with different data servers:
 - CSV-file (comma-seperated value)
 - MySQL
 - Thunderbird/Icedove Lightning
 - Sunbrid / IceOwl

and relatively easy to extend for other data servers.
'''
### Original source from:
## pygtk-demo Status Icon: Nikos Kouremenos
## EvoBdayReminder.py: Axel Heim. http://www.axelheim.de/

VERSION = "@VER@"

from PyQt4 import QtCore, QtGui, uic

import os
import sys

# parse locales from python module
# Do you say "1. January" or "January 1."?
import locale
locale.setlocale(locale.LC_ALL, '')

# for FreeBSD users: if no i18n is whished, no gettext package will be
# available and standard messages are displayed insted a try to use
# translated strings
try:
    import gettext
    gettext.install("gbirthday")
except ImportError:
    _ = lambda x: x

IMAGES_LOCATION = os.path.join(os.path.dirname(__file__), 'pics')

PICS_PATHS = {
    'birthdaylost': os.path.join(IMAGES_LOCATION, 'birthdaylost.png'),
    'birthdaynext': os.path.join(IMAGES_LOCATION, 'birthdaynext.png'),
    'birthday': os.path.join(IMAGES_LOCATION, 'birthday.png'),
    'birthdayred': os.path.join(IMAGES_LOCATION, 'birthdayred.png'),
    'birthdaytoday': os.path.join(IMAGES_LOCATION, 'birthdaytoday.png'),
    'gbirthday': os.path.join(IMAGES_LOCATION, 'gbirthday.png'),
    'nobirthday': os.path.join(IMAGES_LOCATION, 'nobirthday.png'),
}

UI_FILES_LOCATION = os.path.join(os.path.dirname(__file__), 'ui')

def load_ui(ui_file, widget=None):
    '''Load UI file into widget and return widget
    
       inputs:
       - ui file path relative to ui files directory
       - (optionnal) widget : if None, a new widget is created
    '''
    return uic.loadUi(os.path.join(UI_FILES_LOCATION, ui_file), widget)

def main():
    '''Load settings, start status icon and get to work.'''
    from .mainwindow import MainWindow

    # TODO: Think twice about naming before releasing
    QtCore.QCoreApplication.setOrganizationName("GBirthday");
    QtCore.QCoreApplication.setApplicationName("gbirthday");

    app = QtGui.QApplication([])
    # TODO: is this the right way?
    app.setQuitOnLastWindowClosed(False)
    
    # Main window
    main_window = MainWindow()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
