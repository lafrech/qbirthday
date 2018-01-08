Contributing Guidelines
=======================

Questions, Feature Requests, Bug Reports, and Feedback
------------------------------------------------------

Those should all be reported on the `Github Issue Tracker`_ .

.. _`Github Issue Tracker`: https://github.com/lafrech/qbirthday/issues


Code
----

- Report / fix issues.

- Add backends.


Translation
-----------

We're using Qt for the translations. It provides the nice Linguist GUI.

1. Update translation source files (.ts) with new strings when the code is modified
::

    $ pylupdate5 -noobsolete qbirthday.pro

2. Update translations (.ts) files using Qt Linguist GUI for each language

3. Create/update compiled translation files (.qm) for all languages
::

    $ lrelease -qt=5 qbirthday.pro


If you want to help translating but don't feel comfortable with this process, you may open an issue to request a new language and let the maintainer manage the .ts and .qm file creation.
