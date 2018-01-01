"""Sunbird/Iceowl backend (based on Lightning)"""

from pathlib import Path

from .lightning import LightningBackend
from .exceptions import BackendMissingLibraryError


class SunbirdBackend(LightningBackend):
    """Sunbird/Iceowl backend (based on Lightning)"""

    NAME = 'Sunbird'
    TITLE = 'Sunbird/Iceowl'

    def __init__(self, settings):

        super().__init__(settings)

        self.mozilla_location = Path.home() / '.mozilla'

    def parse(self):
        """load file / open database connection"""
        sunbird_filepath = self.mozilla_location / 'sunbird'
        iceowl_filepath = self.mozilla_location / 'iceowl'

        if sunbird_filepath.exists():
            # extract path from profiles.ini
            self.get_config_file(sunbird_filepath)
        elif iceowl_filepath.exists():
            self.get_config_file(iceowl_filepath)
        else:
            raise BackendMissingLibraryError(
                _("No iceowl / sunbird profile found"))
