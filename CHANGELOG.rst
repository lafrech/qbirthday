Changelog
---------

0.7.0 (2024-11-27)
++++++++++++++++++

- Support Python 3.11, 3.12 and 3.13
- Drop Python 3.8
- Use pyproject.toml
- Drop qb script : users should install and use qbirthday command

0.7.0b5 (2023-07-04)
++++++++++++++++++++

- Fix passing coords as float to window move method
- Drop Python 3.7

0.7.0b4 (2022-02-16)
++++++++++++++++++++

- Support Python 3.10
- Require PyQt5>=5.15 and remove workaround for bug in PyQt5 < 5.12.4

0.7.0b3 (2021-09-01)
++++++++++++++++++++

- Support Python 3.8 and 3.9
- Drop Python 3.5 and 3.6

0.7.0b2 (2018-01-11)
++++++++++++++++++++

- Add license to wheel file
- Fix Lightning backend (thunderbird profile directory location)

0.7.0b1 (2018-01-09)
++++++++++++++++++++

- Rename as QBirthday
- Use Python3
- Use PyQt
- Remove pynotify notifications
- Remove "add" feature
- Remove Sundbird/Iceowl backend
- Replace Makefile with Setuptools setup.py
- CSV file delimiter configurable and must be consistent in the whole file
- Drop all translation files since translation is now based on Qt.
  It should be possible to migrate old translation files but most strings were
  changed in the code anyway.
- Add French translation.

0.6.10
++++++

- Fix to minor fix in last release...

0.6.9
+++++

- Minor fixes related to installation

0.6.8
+++++

- Remove Evolution as supported DB

0.6.7
+++++

- Fix bug if two birthdates same D-M different Y
- Fix bug in .ics export (UID must be unique)
- Translation updates: Cesky, Italian, French
- Tarball generation improvement in Makefile

0.6.6
+++++

- GUI revamp
- Hide from taskbar
- Store config in XDG_CONFIG_HOME or ~/.config
- Export gbirthday list as iCalendar file
- Use datetime instead of strings
- Translation updates: Italian, Finnish


0.6.5
+++++

- Reload addressbook, when clickint on 'Save & Close'
- Properly close about-dialog on 'X'
- Internal code clean up
- Translation update: Czech, Danish, Hebrew
- Fedora bugs:
  #598240 Fix crash, when adding person to cvs file

0.6.4
+++++

Bugfixing:
- Fedora bugs:
  #563405 Fix lightning crash
  #568190 Make csv_files variable optional in config
  #570196 When there is no evolution addressbook, silently abort parsing.
  #579097 sunbird 1.0 moved the database

0.6.3
+++++

Internal code clean up
Apply most suggestions from 2to3 script
    (all python2.6 can understand)

0.6.2
+++++

Fix annoying translation bug
(worth an own new version)

0.6.1
+++++

MySQL was wrong initialized (fedora #556210)
Fixed fedora bugs: #554780

0.6
+++

Partly implement some new languages
Bugfixing
Don't blink anymore, instead show red icon
Show notification of todays' birthdays
Show notification of next birthdays (configurable)
Fixed fedora bugs: #551795, #552642, #552946, #553571

0.5.6
+++++

Without evolution addressbook, don't crash (fedora bug #548007)

0.5.5
+++++

On double click, don't blink anymore.
Don't show 'don't blink', when not blinking atm
Bugfixing (fedora bug #546539)
Bugfixing (fedora bug #546869): wrong format of date from evolution
Use gnome-python2-evolution for getting vcards

0.5.4
+++++

Fix 00:00 bug
Don't show 'do not blink', when nobody has birthday today
    Should be done better, but the best for now.
    If made dynamically gtk mixes things around...

0.5.3
+++++

Install into python_sitelib
Follow indention as described in PEP8
Bugfixing (fedora bug #539774)

0.5.2
+++++

Added gettext support for easier translation
Translation system added at:
    http://www.transifex.net/projects/p/gbirthday/
Use python class ConfigParser for handling the config file
    !!! now in a different format !!!

0.5.1
+++++

Fixed bug with Categories in Lightning-SQLite-Database

0.5.0
+++++

Created 'Database'-Structure
Sdded support for CSV-files (comma-seperated value)
Added support for MySQL
Added support for Thunderbird/Icedove Lightning
Added support for Sunbrid / IceOwl
Fixed minor bugs

0.4.2
+++++

Added Makefile for (un)install instead bash script
Added License file with GPLv2+
Pics are now installed into /usr/share/pixmaps
Swiched to .tar.lzma

0.4.1
+++++

Fixed bug with month text and python 2.4.
Fixed bug with birthdays in same day and year.
Forced pygtk version to 2. It needs 2.10 to work.
Added support for multiple evolution addressbooks, by Stefan Jurco.
Inproved title box background color, now gets value from gtk theme.
Set greyscale when no birthdays in selected period.
Added Slovak translation, by Stefan Jurco.
Added Italian translation, by Alex Mallo.

0.4.0
+++++

Added internationalization, by Robert Wildburger.
Added languages: German, Spanish, French, Portuguese and Galician.
Fixed stop blinking bug which made it start to blink again each minute.

0.3.4
+++++

Fixed bug with data format that mades gbirthday to crash.

0.3.3
+++++

Rewrote about window with gtk.AboutDialog.
Added function to check and blink if there are birthdays today at midnight.
Improved preference spinners signals.
Set Past birthdays spinner as a reverse spinner.

0.3.2
+++++

Added preferences window to set past and next birthdays range.
Improved birthday data window when no birthday with message.
0.3.1
+++++

Fixed file as "lastname, firstname" backslash character issue.
Added configuration File: ~/.gbirthday.conf.

0.3.0
+++++

Set birthday data fake title background to label bg color.
Added birthday window fake frame.
Some about window lesser look improvements.
New icon set trying to follow tango guidelines
Changed stop blinking icon.

0.2.4
+++++

Erased negative sign in lost birthdays.
Fixed double click bug that aviod birthday data window close.
Set birthday data window icon.
Deleted lots of obsolete debugging lines.
Added About window.

0.2.3
+++++

Changed name shown from "Full Name" to "File as".
Best Alignement on birthday bindow.
Bold text on today birthdays.
Grey text on lost birthdays.

0.2.2
+++++

Added path to resources folder on image loading.
Added ugly install script.

0.2.1
+++++

Added years to birthdays window.
Best title look.

0.2.0
+++++

Moved birthday data to frameless left click (fake menu) window.
Splited data into a table.

0.1.2
+++++

Added "Reload" option.
Added "Stop blinking" option.

0.1.1
+++++

Fixed issue with 2 character months.

0.1.0
+++++

First version, Just a popup menu with birthday data and quit.
