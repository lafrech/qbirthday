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
        
        # General settings
        self.setValue('firstday', self.value('firstday', -2))
        self.setValue('lastday', self.value('lastday', 30))
        self.setValue('notify_future_birthdays', 
            self.value('notify_future_birthdays', 0))
        
        # Database settings
        for db in DATABASES:
            
            # Disable all DB by default
            self.setValue('{}/enabled'.format(db.__name__), 
                self.value('{}/enabled'.format(db.__name__), False))
            
            # Load DB specific default values
            for key, value in db.DEFAULTS.items():
                self.setValue('{}/{}'.format(db.__name__, key),
                    self.value('{}/{}'.format(db.__name__, key), value))

        # ICS export
        self.setValue('ics_export/enabled', 
            self.value('ics_export/enabled', False))
