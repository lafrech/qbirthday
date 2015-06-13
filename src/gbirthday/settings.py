# vim: foldmethod=marker
#{{{ License header: GPLv2+
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#}}}
from PyQt4 import QtCore

from .databases import DATABASES

class Settings(QtCore.QSettings):
    '''Handle configuration'''

    def load_defaults(self):
        
        # TODO
        # If no config exists (first launch ?),
        # check if values can be found in old config files
        #if not self.contains('firstday'):
        #    self.check_old_conf()

        # General settings
        self.setValue('firstday', self.value('firstday', -2))
        self.setValue('lastday', self.value('lastday', 30))
        self.setValue('notify_future_birthdays', 
            self.value('notify_future_birthdays', 0))
        
        # Database settings
        for db in DATABASES:
            self.setValue(db.__name__ + '/enabled', 
                self.value(db.__name__ + '/enabled', False))

        # ICS export
        self.setValue('ics_export/enabled', 
            self.value('ics_export/enabled', False))

        # Split DB with ' '
        #self.setValue('databases', self.value('databases'))

        # http://www.riverbankcomputing.com/pipermail/pyqt/2011-September/030480.html

#         used_db = get_setting_value("main", "databases", "")
#         if used_db != "":
#             self.used_databases = used_db.split("|")
#         else:
#             self.used_databases = []
#         #self.notify_future_bdays = int(get_setting_value("main",
#                                        "notify_future_bdays", 0))
#         
#         self.csv_files = eval(get_setting_value("main", "csv_files", 'None'))
#         
#         self.ics_export = bool(get_setting_value("ics_export", "export",
#                                                  'False'))
#         self.ics_filepath = get_setting_value("ics_export", "filepath",
#                                         self.base_data_path + '/gbirthday.ics')
#         self.ics_custom_properties = get_setting_value("ics_export",
#                                                 "custom_properties", '')
#         self.ics_alarm = bool(get_setting_value("ics_export", "alarm", 'False'))
#         self.ics_alarm_days = get_setting_value("ics_export", "alarm_days", '5')
#         self.ics_alarm_custom_properties = get_setting_value("ics_export",
#                                                 "alarm_custom_properties", '')
# 
#         try:
#             self.mysql.host = self.settings.get("mysql", "host")
#             self.mysql.port = self.settings.get("mysql", "port")
#             self.mysql.username = self.settings.get("mysql", "username")
#             self.mysql.password = self.settings.get("mysql", "password")
#             self.mysql.database = self.settings.get("mysql", "database")
#             self.mysql.table = self.settings.get("mysql", "table")
#             self.mysql.name_row = self.settings.get("mysql", "name_row")
#             self.mysql.date_row = self.settings.get("mysql", "date_row")

#     def check_old_conf(self):
#         # TODO
#         # TODO: if csv_files -> csv_file
#         
#         import os
#         import configparser
# 
#         settings = configparser.ConfigParser()
# 
#         # If XDG_CONFIG_HOME is defined, check there first
#         if ('XDG_CONFIG_HOME' in os.environ and 
#             os.path.isfile(os.path.join(os.environ['XDG_CONFIG_HOME'], 
#                                         'gbirthday/gbirthdayrc'))):
#             config_file_path = os.path.join(os.environ['XDG_CONFIG_HOME'],
#                                             'gbirthday/gbirthdayrc')
#         elif os.path.isfile(os.path.join(os.environ['HOME'], 
#                                          '.config/gbirthday/gbirthdayrc')):
#             config_file_path = os.path.join(os.environ['HOME'],
#                                             '.config/gbirthday/gbirthdayrc')
#         elif os.path.isfile(os.path.join(os.environ['HOME'], '.gbirthdayrc')):
#             config_file_path = os.path.join(os.environ['HOME'], '.gbirthdayrc')
# 
#        try:
#             with open(self.base_config_path + '/gbirthdayrc') as f:
#                 self.settings.read_file(f)
#         except IOError:
#             pass
#         
#         self.correct_settings()
#         
#     def correct_settings(self):
#         '''Update settings from older versions'''
#         
#         # Correct new settings, e.g. Evolution and not evolution anymore'''
#         def replace(old, new, changed):
#             '''replace old with new'''
#             for num, item in enumerate(self.used_databases):
#                 if self.used_databases[num] == old:
#                     changed = True
#                     self.used_databases[num] = new
#             return changed
# 
#         changed = False
#         changed = replace('evolution', 'Evolution', changed)
#         changed = replace('mysql', 'MySQL', changed)
#         changed = replace('csv', 'CSV', changed)
#         changed = replace('lightning', 'Lightning', changed)
#         changed = replace('sunbird', 'Sunbird', changed)
#         
#         if changed:
#             self.save()
# 
