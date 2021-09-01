"""Module defining paths

PICS_DIR, UI_FILES_DIR and QM_FILES_DIR are Path instances
They must be cast as str when fed to Qt objects

PICS_PATHS is a dict of strings
"""

from pathlib import Path

from PyQt5 import QtCore


GENERIC_DATA_LOCATION = (
    Path(
        QtCore.QStandardPaths.writableLocation(
            QtCore.QStandardPaths.GenericDataLocation
        )
    )
    / "QBirthday"
)
APP_DATA_LOCATION = (
    Path(QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppDataLocation))
    / "QBirthday"
)

# Create default data storage directories
GENERIC_DATA_LOCATION.mkdir(exist_ok=True)
APP_DATA_LOCATION.mkdir(exist_ok=True)


PICS_DIR = Path(__file__).parent / "pics"

PICS_PATHS = {
    "birthdaylost": str(PICS_DIR / "birthdaylost.png"),
    "birthdaynext": str(PICS_DIR / "birthdaynext.png"),
    "birthday": str(PICS_DIR / "birthday.png"),
    "birthdayred": str(PICS_DIR / "birthdayred.png"),
    "birthdaytoday": str(PICS_DIR / "birthdaytoday.png"),
    "qbirthday": str(PICS_DIR / "qbirthday.png"),
    "nobirthday": str(PICS_DIR / "nobirthday.png"),
}

UI_FILES_DIR = Path(__file__).parent / "ui"

QM_FILES_DIR = Path(__file__).parent / "i18n"
