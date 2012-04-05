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
import gtk
from gbirthday.databases import DataBase
from gbirthday.gtk_funcs import show_error_msg

class MySQL(DataBase):
    '''MySQL database import'''

    def __init__(self):
        super(MySQL, self).__init__(title='MySQL')
        self.host = 'localhost'
        self.port = '3306'
        self.username = ''
        self.password = ''
        self.database = ''
        self.table = 'person'
        self.name_row = 'name'
        self.date_row = 'date'
        self.ab = None
        self.cursor = None
        self.conn = None

    def connect(self):
        '''establish connection'''
        try:
            import MySQLdb
        except:
            show_error_msg(_("Package %s is not installed." % "MySQLdb"))
        try:
            self.conn = MySQLdb.connect(host=self.host,
                                    port=int(self.port),
                                    user=self.username,
                                    passwd=self.password,
                                    db=self.database)
            self.cursor = self.conn.cursor()
        except Exception as msg:
            show_error_msg(_('Could not connect to MySQL-Server')
                            + str(msg))
            return False
        return True

    def parse(self, addressbook, conf):
        '''connect to mysql-database and get data'''
        # XXX: set addressbook in __init__?
        self.ab = addressbook
        if not self.connect():
            return
        try:
            qry = ("SELECT %s, %s FROM %s"
                        % (self.name_row, self.date_row, self.table))
            self.cursor.execute(qry)
            rows = self.cursor.fetchall()
            for row in rows:
                addressbook.add(row[0], str(row[1]))
        except Exception as msg:
            show_error_msg(_('Could not execute MySQL-query')
                            + ': %s\n %s' % (qry, str(msg)))
        self.conn.close()

    def add(self, name, birthday):
        '''insert new Birthday to database'''
        birthday = str(birthday)
        self.connect()
        try:
            qry = ("INSERT INTO %s (%s, %s) VALUES ('%s', '%s')" %
                (self.table, self.name_row, self.date_row, name, birthday))
            self.cursor.execute(qry)
        except Exception as msg:
            show_error_msg(_('Could not execute MySQL-query')
                            + ': %s\n %s' % (qry, str(msg)))
        self.conn.close()
        self.ab.add(name, birthday)

    def save_config(self, conf):
        '''Save modifications'''
        self.host = self.entries[0].get_text()
        self.port = self.entries[1].get_text()
        self.username = self.entries[2].get_text()
        self.password = self.entries[3].get_text()
        self.database = self.entries[4].get_text()
        self.table = self.entries[5].get_text()
        self.name_row = self.entries[6].get_text()
        self.date_row = self.entries[7].get_text()
        conf.MySQL = self


    def create_config(self, vbox, conf):
        '''create additional mysql config in config menu'''
        
        values = [
                  ['Host', self.host],
                  ['Port', self.port],
                  ['Username', self.username],
                  ['Password', self.password],
                  ['Database', self.database],
                  ['Table', self.table],
                  ['Name row', self.name_row],
                  ['Date row', self.date_row]
                 ]
        self.entries = []

        sqltable = gtk.Table(len(values), 2, False)
        sqltable.set_col_spacings(5)
        for i, value in enumerate(values):
            label = gtk.Label(value[0])
            label.set_alignment(1, 0.5)
            label.show()
            sqltable.attach(label, 0, 1, i, i + 1)

            entry = gtk.Entry()
            entry.set_text(value[1])
            entry.show()
            self.entries.append(entry)
            sqltable.attach(entry, 1, 2, i, i + 1)
        
        sqltable.show()
        vbox.pack_start(sqltable, False, False, 0)

