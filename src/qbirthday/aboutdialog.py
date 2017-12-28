"""About dialog"""

from PyQt5 import QtGui, QtWidgets

from qbirthday import PICS_PATHS, load_ui
from qbirthday import __about__ as about


class AboutDialog(QtWidgets.QDialog):

    def __init__(self, main_window):

        super().__init__(main_window)

        load_ui('aboutdialog.ui', self)

        # About
        self.imageLabel.setPixmap(QtGui.QPixmap(
            PICS_PATHS['qbirthday']))
        self.nameLabel.setText(
            "{} {}".format(about.__title__, about.__version__))
        self.descLabel.setText(_(about.__summary__))
        self.copyrightLabel.setText(
            "Copyright ©\n{}".format('\n'.join(about.__copyright__)))
        self.uriLabel.setText(
            "<a href={uri}>{uri}</a>".format(uri=about.__uri__))

        # Authors
        self.authorsTextEdit.insertPlainText('\n'.join(about.__authors__))

        # Translators
        translators = _('translator-credit')
        if translators == 'translator-credit':
            translators = _("There are no translations or the translator "
                     "doesn't want to get credits for that.")
        self.translatorsTextEdit.insertPlainText(translators)

        # Artists
        self.artistsTextEdit.insertPlainText(about.__artists__)

        # License
        self.licenseTextEdit.insertPlainText(about.__license_long__)
        self.licenseTextEdit.moveCursor(QtGui.QTextCursor.Start)
