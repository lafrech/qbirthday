"""Birthday backends"""

from .csv import CSVBackend
from .lightning import LightningBackend
from .mysql import MySQLBackend
from .sunbird import SunbirdBackend

BACKENDS = [
    CSVBackend,
    MySQLBackend,
    LightningBackend,
    SunbirdBackend
]
