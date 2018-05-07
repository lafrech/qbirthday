*********
QBirthday
*********

QBirthday is a birthday reminder status icon.


Features
========

- Several backends available (CSV file, Lightning, MySQL databse).
- Extendable to other backends.
- iCalendar export.


Requirements
============

QBirthday runs on Python >= 3.5.

It requires PyQt5 and optionally depends on mysqlclient if a MySQL database is used as backend.


Installation
============

Either as root or in a Python3 virtual environment:
::

    $ pip install qbirthday

To use MySQL backend, install mysqlclient:
::

    $ pip install mysqlclient

Note: If running with the global Python interpreter (i.e. not in a virtualenv), the default Python interpreter is probably Python2. In this case, you may have to install and use `pip3` rather than `pip`.


History
=======

QBirthday is a Qt port of GBirthday, a GTK application.


Project links
=============

- PyPI: https://pypi.python.org/pypi/marshmallow
- Changelog: https://github.com/lafrech/qbirthday/blob/master/CHANGELOG.rst
- Issues: https://github.com/lafrech/qbirthday/issues


License
=======

QBirthday is distributed under GPLv2 license (see LICENSE file).
