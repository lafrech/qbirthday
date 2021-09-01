"""QBirthday

A KBirthday clone working with different backends
and relatively easy to extend to use other backends.

Original source from:
- pygtk-demo Status Icon: Nikos Kouremenos
- EvoBdayReminder.py: Axel Heim. http://www.axelheim.de/
"""

import sys

from PyQt5 import QtCore, QtGui, QtWidgets

from .mainwindow import MainWindow
from .paths import PICS_PATHS, QM_FILES_DIR


def main():
    """Load settings, start status icon and get to work."""

    # TODO: Think twice about naming before releasing
    QtCore.QCoreApplication.setOrganizationName("QBirthday")
    QtCore.QCoreApplication.setApplicationName("qbirthday")

    app = QtWidgets.QApplication([])
    app.setWindowIcon(QtGui.QIcon(PICS_PATHS["qbirthday"]))

    # Internationalization
    # Use system locale
    locale = QtCore.QLocale.system().name()
    # Load default translator for Qt strings
    translator_qt = QtCore.QTranslator()
    translator_qt.load(
        f"qt_{locale}",
        QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath),
    )
    app.installTranslator(translator_qt)
    # Load translator for own strings
    translator = QtCore.QTranslator()
    translator.load(str(QM_FILES_DIR / f"qbirthday_{locale}"))
    app.installTranslator(translator)

    # TODO: is this the right way?
    app.setQuitOnLastWindowClosed(False)

    # Main window
    MainWindow()

    sys.exit(app.exec_())
