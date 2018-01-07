"""QBirthday exceptions"""


class QBirthdayError(Exception):
    """Generic QBirthday error"""


class ICSExportError(QBirthdayError):
    """ICS file export error"""
