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
import os

from gbirthday.databases import Lightning

class Sunbird(Lightning):
    '''Sunbird/Iceowl implementation (based on lightning)'''

    TITLE = 'Sunbird/Iceowl'
    CAN_SAVE = True

    def __init__(self, mainwindow):

        super().__init__(mainwindow)

        self.mozilla_location = os.path.join(os.environ['HOME'],
                '.mozilla')

    def parse(self):
        '''load file / open database connection'''
        sunbird = os.path.join(self.mozilla_location, 'sunbird')
        iceowl = os.path.join(self.mozilla_location, 'iceowl')

        if (os.path.exists(sunbird)):
            # extract path from profiles.ini
            self.get_config_file(sunbird)
        elif (os.path.exists(iceowl)):
            self.get_config_file(iceowl)
        else:
            # Missing package
            QtGui.QMessageBox.warning(self.mainwindow, 
                QtCore.QCoreApplication.applicationName(),
                _("Neither iceowl nor sunbird is installed"),
                QtGui.QMessageBox.Discard)
