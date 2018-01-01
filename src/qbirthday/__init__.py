"""QBirthday

A KBirthday clone working with different backends
and relatively easy to extend to use other backends.

Original source from:
- pygtk-demo Status Icon: Nikos Kouremenos
- EvoBdayReminder.py: Axel Heim. http://www.axelheim.de/
"""

import os
import sys
import locale

from PyQt5 import QtCore, QtGui, QtWidgets, uic

# parse locales from python module
# Do you say "1. January" or "January 1."?
locale.setlocale(locale.LC_ALL, '')

# for FreeBSD users: if no i18n is whished, no gettext package will be
# available and standard messages are displayed insted a try to use
# translated strings
try:
    import gettext
    gettext.install("qbirthday")
except ImportError:
    _ = lambda x: x  # noqa

IMAGES_LOCATION = os.path.join(os.path.dirname(__file__), 'pics')

PICS_PATHS = {
    'birthdaylost': os.path.join(IMAGES_LOCATION, 'birthdaylost.png'),
    'birthdaynext': os.path.join(IMAGES_LOCATION, 'birthdaynext.png'),
    'birthday': os.path.join(IMAGES_LOCATION, 'birthday.png'),
    'birthdayred': os.path.join(IMAGES_LOCATION, 'birthdayred.png'),
    'birthdaytoday': os.path.join(IMAGES_LOCATION, 'birthdaytoday.png'),
    'qbirthday': os.path.join(IMAGES_LOCATION, 'qbirthday.png'),
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

    # TODO: Think twice about naming before releasing
    QtCore.QCoreApplication.setOrganizationName("QBirthday")
    QtCore.QCoreApplication.setApplicationName("qbirthday")

    app = QtWidgets.QApplication([])
    app.setWindowIcon(QtGui.QIcon(PICS_PATHS['qbirthday']))

    # TODO: is this the right way?
    app.setQuitOnLastWindowClosed(False)

    # Main window
    MainWindow()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
