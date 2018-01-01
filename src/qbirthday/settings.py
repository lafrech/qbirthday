"""Settings module

Override QSettings to add default values
"""

from pathlib import Path

from PyQt5 import QtCore

from .backends import BACKENDS


DEFAULT_DATA_FILE_DIR = Path(
    QtCore.QStandardPaths.writableLocation(
        QtCore.QStandardPaths.GenericDataLocation)) / 'qbirthday'
DEFAULT_DATA_FILE_DIR.mkdir(exist_ok=True)

CONFIG_DEFAULTS = {
    'firstday': -2,
    'lastday': 30,
    'notify_future_birthdays': 0,
}

ICS_EXPORT_CONFIG_DEFAULTS = {
    'enabled': False,
    'filepath': str(DEFAULT_DATA_FILE_DIR / 'qbirthday.ics'),
    'alarm': False,
    'alarm_custom_properties': '',
    'alarm_days': 1,
    'custom_properties': '',
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
        self.beginGroup('ics_export')
        for key, val in ICS_EXPORT_CONFIG_DEFAULTS.items():
            self.setDefaultValue(key, val)
        self.endGroup()
        # Backend settings
        for bcknd in BACKENDS:
            self.beginGroup(bcknd.NAME)
            # Disable all backends by default
            self.setDefaultValue('enabled', False)
            # Load backend specific default values
            for key, val in bcknd.DEFAULTS.items():
                self.setDefaultValue(key, val)
            self.endGroup()
