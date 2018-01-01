"""QBirthday

A KBirthday clone working with different backends
and relatively easy to extend to use other backends.

Original source from:
- pygtk-demo Status Icon: Nikos Kouremenos
- EvoBdayReminder.py: Axel Heim. http://www.axelheim.de/
"""

import sys
import locale

from PyQt5 import QtCore, QtGui, QtWidgets, uic

from .paths import PICS_PATHS, UI_FILES_DIR

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


def load_ui(ui_file, widget=None):
    '''Load UI file into widget and return widget

       inputs:
       - ui file path relative to ui files directory
       - (optionnal) widget : if None, a new widget is created
    '''
    return uic.loadUi(str(UI_FILES_DIR / ui_file), widget)


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
