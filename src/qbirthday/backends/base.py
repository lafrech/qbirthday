"""Base class for all backends"""

import abc

from PyQt5 import QtCore


class AbstractQObjectMetaclass(type(QtCore.QObject), abc.ABCMeta):
    """Metaclass for an abstract class inheriting QObject

    See https://stackoverflow.com/questions/46837947/
    """


class BaseBackend(QtCore.QObject, metaclass=AbstractQObjectMetaclass):
    """Abstract class for read-only backends

    To create a child class
    - create parse method
    - override class attributes if needed
    """

    # Backend name
    NAME = ''
    # Backend name displayed to user
    TITLE = ''
    # Configuration dialog
    CONFIG_DLG = None
    # Default configuration values
    DEFAULTS = {}

    def __init__(self, settings):
        super().__init__()
        self.settings = settings

    @abc.abstractmethod
    def parse(self):
        """Return birthdates as list of (name, date) tuples"""
