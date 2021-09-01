"""iCalendar export"""

import datetime as dt

from PyQt5 import QtCore

from .exceptions import ICSExportError


class ICSExport(QtCore.QObject):
    """iCalendar export"""

    def __init__(self, settings):
        super().__init__()
        self.settings = settings

    def write(self, birthdates):
        """Write iCalendar file"""

        self.settings.beginGroup("ics_export")
        conf_filepath = self.settings.value("filepath", type=str)
        conf_alarm = self.settings.value("alarm", type=bool)
        conf_alarm_days = self.settings.value("alarm_days", type=int)
        conf_custom_properties = self.settings.value("custom_properties", type=str)
        conf_alarm_custom_properties = self.settings.value(
            "alarm_custom_properties", type=str
        )
        self.settings.endGroup()

        try:
            with open(conf_filepath, "w") as ics_file:
                now = dt.datetime.now().strftime("%Y%m%dT%H%M%SZ")
                ics_file.write("BEGIN:VCALENDAR\n")
                ics_file.write("VERSION:2.0\n")
                ics_file.write("PRODID:-//qbirthday//EN\n")
                for index, bday in enumerate(birthdates):
                    ics_file.write("BEGIN:VEVENT\n")
                    ics_file.write(f"UID:{now}-{index}@qbirthday\n")
                    ics_file.write(f"CREATED:{now}\n")
                    ics_file.write(f"LAST-MODIFIED:{now}\n")
                    ics_file.write(f"DTSTAMP:{now}\n")
                    ics_file.write("DTSTART:{}\n".format(bday.strftime("%Y%m%d")))
                    ics_file.write("DURATION:PT0S\n")
                    ics_file.write("CATEGORIES:{}\n".format(self.tr("Birthday")))
                    ics_file.write(
                        "SUMMARY:{}{}\n".format(
                            self.tr("Birthday: "), birthdates[bday][0]
                        )
                    )
                    ics_file.write("CLASS:PRIVATE\n")
                    ics_file.write("TRANSP:TRANSPARENT\n")
                    ics_file.write("RRULE:FREQ=YEARLY\n")
                    if conf_alarm:
                        ics_file.write("BEGIN:VALARM\n")
                        ics_file.write("ACTION:DISPLAY\n")
                        ics_file.write(f"TRIGGER;VALUE=DURATION:-P{conf_alarm_days}D\n")
                        ics_file.write(
                            "DESCRIPTION:{}{}\n".format(
                                self.tr("Birthday: "), birthdates[bday][0]
                            )
                        )
                        if conf_alarm_custom_properties != "":
                            ics_file.write(conf_alarm_custom_properties)
                            ics_file.write("\n")
                        ics_file.write("END:VALARM\n")
                    if conf_custom_properties != "":
                        ics_file.write(conf_custom_properties)
                        ics_file.write("\n")
                    ics_file.write("END:VEVENT\n")
                ics_file.write("END:VCALENDAR")
        except OSError:
            raise ICSExportError(
                self.tr(f"Can't write iCalendar file: {conf_filepath}")
            )
