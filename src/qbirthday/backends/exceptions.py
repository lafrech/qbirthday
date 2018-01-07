"""Backend exceptions"""

from qbirthday.exceptions import QBirthdayError


class BackendError(QBirthdayError):
    """Generic backend error"""


class BackendMissingLibraryError(BackendError):
    """Missing backend library"""


class BackendReadError(BackendError):
    """Error while reading from file/database"""


class BackendWriteError(BackendError):
    """Error while writing to file/database"""
