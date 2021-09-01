"""Base class for all backends"""

import abc
import importlib

from PyQt5 import QtCore

from .exceptions import BackendMissingLibraryError


MISSING_LIB_ERR_STR = QtCore.QT_TRANSLATE_NOOP("Backends", "Missing {} library.")


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


def try_import(module_name, lib_name=None):
    """Import module

    In case of ImportError, raise BackendMissingLibraryError
    module_name: name of the module to import
    lib_name: name of the python lib containing the module
        (default to module_name)
    """
    lib_name = lib_name or module_name
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        import_err = QtCore.QCoreApplication.translate(
            "Backends", MISSING_LIB_ERR_STR
        ).format(lib_name)
        raise BackendMissingLibraryError(import_err)
    return module
