"""Sunbird/Iceowl backend (based on lightning)"""

import os

from PyQt5 import QtCore, QtWidgets

from qbirthday.databases import Lightning


class Sunbird(Lightning):
    '''Sunbird/Iceowl implementation (based on lightning)'''

    TITLE = 'Sunbird/Iceowl'
    CAN_SAVE = True

    def __init__(self, mainwindow):

        super().__init__(mainwindow)

        self.mozilla_location = os.path.join(os.environ['HOME'], '.mozilla')

    def parse(self):
        '''load file / open database connection'''
        sunbird = os.path.join(self.mozilla_location, 'sunbird')
        iceowl = os.path.join(self.mozilla_location, 'iceowl')

        if os.path.exists(sunbird):
            # extract path from profiles.ini
            self.get_config_file(sunbird)
        elif os.path.exists(iceowl):
            self.get_config_file(iceowl)
        else:
            # Missing package
            QtWidgets.QMessageBox.warning(
                self.mainwindow,
                QtCore.QCoreApplication.applicationName(),
                _("Neither iceowl nor sunbird is installed"),
                QtWidgets.QMessageBox.Discard
            )
