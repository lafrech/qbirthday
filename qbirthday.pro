SRCDIR = src/qbirthday
UIDIR = src/qbirthday/ui
I18NDIR = src/qbirthday/i18n

SOURCES = \
    $$SRCDIR/__init__.py \
    $$SRCDIR/__about__.py \
    $$SRCDIR/aboutdialog.py \
    $$SRCDIR/birthday_list.py \
    $$SRCDIR/ics_export.py \
    $$SRCDIR/mainwindow.py \
    $$SRCDIR/paths.py \
    $$SRCDIR/preferencesdialog.py \
    $$SRCDIR/settings.py \
    $$SRCDIR/statusicon.py \
    $$SRCDIR/backends/__init__.py \
    $$SRCDIR/backends/base.py \
    $$SRCDIR/backends/csv.py \
    $$SRCDIR/backends/exceptions.py \
    $$SRCDIR/backends/lightning.py \
    $$SRCDIR/backends/mysql.py \

FORMS = \
    $$UIDIR/aboutdialog.ui \
    $$UIDIR/csvpreferencesdialog.ui \
    $$UIDIR/icsexportpreferencesdialog.ui \
    $$UIDIR/mainwindow.ui \
    $$UIDIR/mysqlpreferencesdialog.ui \
    $$UIDIR/preferencesdialog.ui \

TRANSLATIONS = \
    $$I18NDIR/qbirthday_fr.ts \
