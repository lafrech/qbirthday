"""Sunbird/Iceowl backend (based on Lightning)"""

import os

from .lightning import LightningBackend
from .exceptions import BackendMissingLibraryError


class SunbirdBackend(LightningBackend):
    """Sunbird/Iceowl backend (based on Lightning)"""

    NAME = 'Sunbird'
    TITLE = 'Sunbird/Iceowl'

    def __init__(self, settings):

        super().__init__(settings)

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
            raise BackendMissingLibraryError(
                _("Neither iceowl nor sunbird is installed"))
