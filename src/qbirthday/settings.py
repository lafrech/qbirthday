"""Settings module

Override QSettings to add default values
"""

from PyQt5 import QtCore

from .paths import GENERIC_DATA_LOCATION
from .backends import BACKENDS


CONFIG_DEFAULTS = {
    "firstday": -2,
    "lastday": 30,
}

ICS_EXPORT_CONFIG_DEFAULTS = {
    "enabled": False,
    "filepath": str(GENERIC_DATA_LOCATION / "qbirthday.ics"),
    "alarm": False,
    "alarm_custom_properties": "",
    "alarm_days": 1,
    "custom_properties": "",
}


class MissingDefaultError(Exception):
    """Missing parameter default value"""


class Settings(QtCore.QSettings):
    """QSettings child class with default values"""

    def setDefaultValue(self, key, value):  # pylint: disable=invalid-name
        """Set value unless it already exists"""
        self.setValue(key, self.value(key, value))

    def __init__(self):
        super().__init__()
        # General settings
        for key, val in CONFIG_DEFAULTS.items():
            self.setDefaultValue(key, val)
        # ICS export
        self.beginGroup("ics_export")
        for key, val in ICS_EXPORT_CONFIG_DEFAULTS.items():
            self.setDefaultValue(key, val)
        self.endGroup()
        # Backend settings
        for bcknd in BACKENDS:
            self.beginGroup(bcknd.id)
            # Disable all backends by default
            self.setDefaultValue("enabled", False)
            if bcknd.cls is not None:
                # If backend available, Load backend specific default values
                for key, val in bcknd.cls.DEFAULTS.items():
                    self.setDefaultValue(key, val)
            else:
                # If backend unavailable and enabled in config, warn user
                if self.value("enabled") is True:
                    # TODO: display warning
                    pass
            self.endGroup()
