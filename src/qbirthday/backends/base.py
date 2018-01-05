"""Base class for all backends"""

import abc

from PyQt5 import QtCore


class AbstractQObjectMetaclass(QtCore.pyqtWrapperType, abc.ABCMeta):
    """Metaclass for an abstract class inheriting QObject

    See https://stackoverflow.com/questions/46837947/
    """


class BaseROBackend(QtCore.QObject, metaclass=AbstractQObjectMetaclass):
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


class BaseRWBackend(BaseROBackend):
    """Abstract class for all backends

    To create a child class
    - create parse and add methods
    - override class attributes if needed
    """

    @abc.abstractmethod
    def add(self, name, birthday):
        """Save birthday to file/database"""
