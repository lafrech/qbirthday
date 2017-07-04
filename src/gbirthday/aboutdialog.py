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
from PyQt5 import QtGui, QtWidgets

from gbirthday import PICS_PATHS, load_ui
from gbirthday import __about__ as about


class AboutDialog(QtWidgets.QDialog):

    def __init__(self, main_window):

        super().__init__(main_window)

        load_ui('aboutdialog.ui', self)

        # About
        self.imageLabel.setPixmap(QtGui.QPixmap(
            PICS_PATHS['gbirthday']))
        self.nameLabel.setText(
            "{} {}".format(about.__title__, about.__version__))
        self.descLabel.setText(_(about.__summary__))
        self.copyrightLabel.setText(
            "Copyright © {}".format(about.__copyright__))
        self.uriLabel.setText(
            "<a href={uri}>{uri}</a>".format(uri=about.__uri__))

        # Authors
        self.authorsTextEdit.insertPlainText(about.__authors__)

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
