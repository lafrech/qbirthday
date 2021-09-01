"""About dialog"""

from PyQt5 import QtGui, QtWidgets, uic

from qbirthday import __about__ as about
from .paths import PICS_PATHS, UI_FILES_DIR


class AboutDialog(QtWidgets.QDialog):
    """About Dialog"""

    def __init__(self, main_window):

        super().__init__(main_window)

        uic.loadUi(str(UI_FILES_DIR / "aboutdialog.ui"), self)

        # About
        self.imageLabel.setPixmap(QtGui.QPixmap(PICS_PATHS["qbirthday"]))
        self.nameLabel.setText(f"{about.__title__} {about.__version__}")
        self.descLabel.setText(self.tr(about.__summary__))
        self.copyrightLabel.setText(
            "Copyright ©\n{}".format("\n".join(about.__copyright__))
        )
        self.uriLabel.setText("<a href={uri}>{uri}</a>".format(uri=about.__uri__))

        # Authors
        self.authorsTextEdit.insertPlainText("\n".join(about.__authors__))

        # Translators
        translators = self.tr("translator-credit")
        if translators == "translator-credit":
            translators = self.tr(
                "There are no translations or the translator "
                "doesn't want to get credits for that."
            )
        self.translatorsTextEdit.insertPlainText(translators)

        # Artists
        self.artistsTextEdit.insertPlainText(about.__artists__)

        # License
        self.licenseTextEdit.insertPlainText(about.__license_long__)
        self.licenseTextEdit.moveCursor(QtGui.QTextCursor.Start)
