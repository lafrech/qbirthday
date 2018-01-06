"""Birthday backends"""

from .csv import CSVBackend
from .lightning import LightningBackend
from .mysql import MySQLBackend

BACKENDS = [
    CSVBackend,
    MySQLBackend,
    LightningBackend,
]
