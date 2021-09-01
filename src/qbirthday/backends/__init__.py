"""Birthday backends"""

import importlib
from collections import namedtuple

from .exceptions import BackendMissingLibraryError


# TODO: translate display names

# Backend description tuple
# id: short name used in settings file
# name: translatable display name
# cls: backend class or None is ImportError
# exc_str: translatable import error message or None
BackendDescription = namedtuple("BackendDescription", ["id", "name", "cls", "exc_str"])

BACKENDS = []

for module_name in ("csv", "mysql", "lightning"):
    try:
        module = importlib.import_module(f"qbirthday.backends.{module_name}")
    except BackendMissingLibraryError as exc:
        BACKENDS.append(
            BackendDescription(exc.bcknd_id, exc.bcknd_name, None, str(exc))
        )
    else:
        bcknd_id = getattr(module, "BACKEND_ID")
        bcknd_name = getattr(module, "BACKEND_NAME")
        bcknd_cls = getattr(module, "BACKEND")
        BACKENDS.append(BackendDescription(bcknd_id, bcknd_name, bcknd_cls, None))
