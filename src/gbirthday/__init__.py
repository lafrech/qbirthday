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

from PyQt4 import QtCore, QtGui

import sys
import time
from textwrap import dedent

# parse locales from python module
# Do you say "1. January" or "January 1."?
import locale
locale.setlocale(locale.LC_ALL, '')
DAY_AT_PLACE, MONTH_AT_PLACE = 1, 2
if time.strftime('%x', (2000, 3, 1, 1, 0, 0, 0, 1, 0)).startswith("03"):
    DAY_AT_PLACE, MONTH_AT_PLACE = 2, 1

# for FreeBSD users: if no i18n is whished, no gettext package will be
# available and standard messages are displayed insted a try to use
# translated strings
try:
    import gettext
    gettext.install("gbirthday")
except ImportError:
    _ = lambda x: x

CURRENT_DAY = time.strftime("%d", time.localtime(time.time()))

def main():
    '''Load settings, start status icon and get to work.'''
    from .main_window import MainWindow

    # TODO: Think twice about naming before releasing
    QtCore.QCoreApplication.setOrganizationName("GBirthday");
    QtCore.QCoreApplication.setApplicationName("gbirthday");

    # check every 60 seconds for new day
    # TODO: update until end of day according to current clock settings?
    #       (might not the best idea if user changes current time)
    # TODO: Use Qt something for this
    #import gobject
    #gobject.timeout_add(60000, main_window.check_new_day)
    
    app = QtGui.QApplication([])
    # TODO: is this the right way?
    app.setQuitOnLastWindowClosed(False)
    
    # Main window
    main_window = MainWindow()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
