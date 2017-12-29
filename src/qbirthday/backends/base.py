"""Base class for all backends"""

import abc


class BaseBackend(abc.ABC):
    """Abstract class for all backends

    To create a child class
    - create parse and add methods
    - override class attributes if needed
    """

    # Backend name
    NAME = ''
    # Backend name displayed to user
    TITLE = ''
    # Whether backend can save new birthdays
    CAN_SAVE = False
    # Configuration dialog
    CONFIG_DLG = None
    # Default configuration values
    DEFAULTS = {}

    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.bday_list = mainwindow.bday_list
        self.settings = mainwindow.settings

    @abc.abstractmethod
    def parse(self):
        """Load birthdays from file/database to birthday list"""

    @abc.abstractmethod
    def add(self, name, birthday):
        """Save birthday to file/database

        If CAN_SAVE is False, this method should raise NotImplementedError
        """
