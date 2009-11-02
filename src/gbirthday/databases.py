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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
'''Database classes:

'DataBase' from which everything inherits:
- CVS
- Evolution
- Lightning
- MySQL
- Sunbird

'''
import os
import re
import gtk

class DataBase:
    '''
     inheritance class for all databases
     you can use this format to add new databases
     your DataBase implementation has to parse the data from your data source,
     and add it into the AddressBook (ab.add())
     you have to add your Database to the databases-list
    '''
    def __init__(self, title='Unknown', type='none', can_save=True,
            has_config=True, widget=None):
        # Title that will be displayed to the user
        self.TITLE = title
        # type that is used as identifier (e.g. for config file)
        self.TYPE = type
        # new entries can be saved
        self.CAN_SAVE = can_save
        # additional config options for database connection or fukebane(s)
        self.HAS_CONFIG = can_save
        # the widget for additional config
        self.widget = widget

    def parse(self, ab, conf):
        '''load file / open database connection'''
        pass

    def add(self, name, birthday):
        '''save new birthday to file/database (only if CAN_SAVE == true)'''
        pass

    def create_config(self, table, conf):
        '''create additional pygtk config in config menu'''
        pass

    def update(self, conf):
        '''update and save values in file'''
        pass

    def activate(self):
        '''
        someone clicked on the checkbox for this DataBase, so show optional 
        settings
        (just set the created pygtk elements to visible)
        '''
        if (self.widget):
            self.widget.set_sensitive(True)
            self.text.set_sensitive(True)
            #self.widget.show()
            #self.text.show()

    def deactivate(self):
        '''
        someone clicked on the checkbox for this DataBase, so hide optional 
        settings
        (just hide the visible elements)
        ''' 
        if (self.widget):
            self.widget.set_sensitive(False)
            self.text.set_sensitive(False)
            #self.widget.hide()
            #self.text.hide()

class CSV(DataBase):
    '''import from CSV-file'''
    def __init__(self):
        DataBase.__init__(self, title='CSV-file (comma seperated value)', type='csv')
        self._seperators=['; ', ', ', ': ']   # possible seperators
        self.ab = None

    def parse(self, ab, conf):
        '''open and parse file'''
        self.ab = ab
        self.conf = conf
        for filename in conf.csv_files:
            if (os.path.exists(filename)):
                for line in file(filename):
                    # check, if any of the seperators are in the text
                    for sep in self._seperators:
                        if len(line.split(sep)) > 1:
                            date = line.split(sep, 1)[0]
                            name = line.split(sep, 1)[1][:-1]
                            ab.add(name, date)
                            break
            else:
                showErrorMsg(_('Could not save, CVS-file not set.')
                                + ':' + filename)

    def add(self, name, birthday):
        '''add new person with birthday to end of csv-file'''
        birthday = str(birthday)
        # TODO: show menu to select file?
        if len(conf.csv_files) == 0:
            showErrorMsg(_('CSV-file does not exist'))
            return
        filename = conf.csv_files[0]
        if (os.path.exists(filename)):
            f = file(conf.csv_files[0], 'a')
        else:
            f = file(conf.csv_files[0], 'w')
        f.write(birthday + ', ' + name + '\n')
        f.close()
        self.ab.add(name, birthday)
    
    def remove_file(self, widget, combobox, conf):
        index = combobox.get_active()
        if index >= 0:
            combobox.remove_text(index)
            conf.csv_files.remove(conf.csv_files[index])
        return

    def add_file(self, widget, combobox, entry, conf):
        filename = entry.get_text()
        combobox.append_text(filename)
        if conf.csv_files:
            conf.csv_files.append(filename)
        else:
            conf.csv_files = [filename]

    def create_config(self, pref, conf):
        '''create aditional options menu'''
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        hbox2 = gtk.HBox()
        vbox.pack_start(hbox)
        combobox = gtk.combo_box_new_text()
        if conf.csv_files:
            for csv_file in conf.csv_files:
                combobox.append_text(csv_file)
        combobox.set_active(0)
        combobox.show()
        hbox.pack_start(combobox)
        remove_button = gtk.Button('remove')
        remove_button.connect("clicked", self.remove_file, combobox, conf)
        remove_button.show()
        hbox.pack_start(remove_button, 0)
        hbox.show()
        
        entry = gtk.Entry()
        if conf.csv_files and len(conf.csv_files) > 0:
            entry.set_text(conf.csv_files[0])
        hbox2.pack_start(entry)
        entry.show()
        
        def choose_file(widget, entry):
            chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                          buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            filter = gtk.FileFilter()
            filter.set_name("All files")
            filter.add_pattern("*")
            chooser.add_filter(filter)

            filter = gtk.FileFilter()
            filter.set_name("CSV-Files")
            filter.add_mime_type("text/csv")
            filter.add_pattern("*.csv")
            chooser.add_filter(filter)

            response = chooser.run()
            if response == gtk.RESPONSE_OK:
                filename = chooser.get_filename()
                entry.set_text(filename)

            chooser.destroy()

        search_button = gtk.Button('select')
        search_button.connect("clicked", choose_file, entry)
        search_button.show()
        hbox2.pack_start(search_button)
        
        add_button = gtk.Button('add')
        add_button.connect("clicked", self.add_file, combobox, entry, conf)
        add_button.show()
        hbox2.pack_start(add_button)
        
        vbox.pack_start(hbox2)
        hbox2.show()
        pref.add(vbox)
        vbox.show()

class Evolution(DataBase):
    '''data import from the Evolution address book'''
    def __init__(self):
        DataBase.__init__(self, title='Evolution', type='evolution',
                        can_save=False, has_config=False)
        self.ADDRESS_BOOK_LOCATION = os.path.join(os.environ['HOME'],
                        '.evolution/addressbook/local/')
        self._splitRE = re.compile(r'\r?\n')

    def parse(self, book=None, ab=None, conf=None):
        
        '''load and parse parse Evolution data files'''
        # get list of address books and extract their persons
        if (os.path.exists(self.ADDRESS_BOOK_LOCATION)):
            for addresser in os.listdir(self.ADDRESS_BOOK_LOCATION):
                location = os.path.join(self.ADDRESS_BOOK_LOCATION, addresser)
                for name in book or []:
                    location = os.path.join(location, 'subfolders', name)
                addressbook = os.path.join(location, 'addressbook.db')
                try:
                    import bsddb
                except:
                    showErrorMsg(_("Package %s is not installed." % "bsddb") )
                try:
                    bsfile = bsddb.hashopen(addressbook)
                    for key in bsfile.keys():
                        data = bsfile[key]
                        if not data.startswith('BEGIN:VCARD'):
                            continue
                        self.parse_birthday(data, ab)
                except bsddb.db.DBInvalidArgError, msg:
                    showErrorMsg(_('Error reading Evolution addressbook: %s' %
                                    msg[1]))

    def parse_birthday(self, data, ab):
        '''parse evolution addressbook. the file is in VCard format.'''
        lines = self._splitRE.split(data)
        mostRecentName = ''
        mostRecentDate = ''
        for line in lines:
            # ignore blank lines, lines without colon and 
            # lines that are just \x00
            if not line.strip() or line == '\x00' or \
               line.find(':') == -1:
                continue
            label, value = line.split(':', 1)
            # parse file, if the name is set in 'X-EVOLUTION-FILE-AS'
            # use it as display name
            if label == 'X-EVOLUTION-FILE-AS': 
                mostRecentName = value.replace("\,",",")
            # if 'BDAY' is set use BDAY als birthday
            if label == 'BDAY':
                mostRecentDate = value
            # if BDAY and  set create Person-data
            if mostRecentName and mostRecentDate:
                # if there already is a birthday add it to the list
                ab.add(mostRecentName, mostRecentDate)
                mostRecentName = ''
                mostRecentDate = ''

class Lightning(DataBase):
    '''Thunderbird/Lightning implementation'''
    def __init__(self, title='Thunderbird/Icedove Lightning', type='lightning',
                has_config=False):
        DataBase.__init__(self, title=title, type=type, has_config=has_config)
        self.THUNDERBIRD_LOCATION = os.path.join(os.environ['HOME'],
            '.mozilla.thunderbird')
        self.ab = None

    def get_config_file(self, configfile):
        profilefile = os.path.join(configfile, 'profiles.ini')
        if os.path.isfile(profilefile):
            cp = ConfigParser.ConfigParser()
            cp.read(profilefile)
            profiles = {} # dict of founded profiles
            for sec in cp.sections():
                if sec.lower().startswith("profile"):
                    profiles[sec] = {}
                    for opt in cp.options(sec):
                        profiles[sec][opt.lower()] = cp.get(sec, opt)
            # get all data from profiles
            for profile in profiles:
                if profiles[profile]['isrelative']:
                    location = os.path.join(configfile, profiles[profile]['path'])
                else:
                    location = profiles[profile]['path']
                location = os.path.join(location, 'storage.sdb')
                if os.path.isfile(location):
                    self.parse_birthday(location)
        else:
            showErrorMsg(_('Error reading profile file: %s' % configfile))

    def parse(self, ab, conf):
        '''open thunderbird sqlite-database'''
        if (os.path.exists(self.THUNDERBIRD_LOCATION)):
            self.get_config_file(self.THUNDERBIRD_LOCATION)
        self.ab = ab

    def connect(self, filename):
        '''"connect" to sqlite3-database'''
        try:
            import sqlite3
        except:
            showErrorMsg(_("Package %s is not installed." % "SQLite3"))
        try:
            self.conn = sqlite3.connect (filename)
            self.cursor = self.conn.cursor()
        except Exception, msg:
            showErrorMsg(_('sqlite3 could not connect: %s' % str(msg)) )


    def parse_birthday(self, filename):
        self.connect(filename)
        qry = '''SELECT title, event_start FROM cal_events ce
              INNER JOIN cal_properties cp
              ON ce.id = cp.item_id
              WHERE cp.key == 'CATEGORIES' AND
              cp.value == 'Birthday' AND
              ce.title != '';'''
        self.cursor.execute(qry)
        for row in self.cursor:
            bday = datetime.datetime.utcfromtimestamp(int(row[1]) / 1000000)
            self.ab.add(row[0], str(bday).split(' ')[0])
            

    def add(self, name, birthday):
        import uuid
        # create new uuid
        event_date = int(birthday.strftime("%s"))
        event_start = (event_date + 86400) * 1000000
        event_end = (event_date + 172800) * 1000000
        uid = str(uuid.uuid4())
        create_time = str(int(time.time())*1000000)
        try:
            qry = '''SELECT id from cal_calendars LIMIT 1;'''
            self.cursor.execute (qry)
            rows = self.cursor.fetchall()
            calender_id = rows[0][0]
            # lets assume there is at least one calendar
            # TODO: implement code to insert new calendar if it none exists!
            
            qry = '''INSERT INTO "cal_events"
                (cal_id, id, time_created, last_modified, title, flags, 
                event_start, event_start_tz, event_end, event_end_tz)
                VALUES
                ('%s', '%s', '%s', '%s', '%s', 28, '%s', 'floating', '%s', 
                 'floating'); ''' % (calender_id, uid, create_time, 
                              create_time, name, event_start, event_end)
            self.cursor.execute(qry)
            
            qry = '''INSERT INTO cal_properties
                     (item_id, key, value)
                     VALUES
                     ('%s', 'CATEGORIES', 'Birthday');''' % uid
            self.cursor.execute (qry)
            qry = '''INSERT INTO cal_properties
                     (item_id, key, value)
                     VALUES
                     ('%s', 'TRANSP', 'TRANSPARENT');''' % uid
            self.cursor.execute (qry)
            qry = '''INSERT INTO cal_properties
                     (item_id, key, value)
                     VALUES
                     ('%s', 'X-MOZ-GENERATION', '1');''' % uid
            self.cursor.execute (qry)
            # birthday repeats yearly
            qry = '''INSERT INTO "cal_recurrence" 
                     (item_id, recur_index, recur_type, is_negative, count, 
                     interval)
                     VALUES
                     ('%s', 1, 'YEARLY', 0, -1, 1);''' %uid
            self.cursor.execute (qry)
            self.conn.commit()
        except Exception, msg:
            showErrorMsg(_('Could not execute SQLite-query')
                            + ': %s\n %s' % (qry, str(msg)))
        ab.add(name, str(birthday))

class MySQL(DataBase):
    '''MySQL database import'''
    def __init__(self):
        DataBase.__init__(self, title='MySQL', type='mysql')
        self.host = 'localhost'
        self.port = '3306'
        self.username = ''
        self.password = ''
        self.database = ''
        self.table = 'person'
        self.name_row = 'name'
        self.date_row = 'date'
        self.ab = None

        self.entries = []
    
    def connect(self):
        '''establish connection'''
        try:
            import MySQLdb
        except:
            showErrorMsg(_("Package %s is not installed." % "MySQLdb" ))
        try:
            self.conn = MySQLdb.connect (host = self.host, 
                                    port=int(self.port), 
                                    user = self.username, 
                                    passwd = self.password, 
                                    db = self.database)
            self.cursor = self.conn.cursor()
        except Exception, msg:
            showErrorMsg(_('Could not connect to MySQL-Server')
                            + str(msg))

    def parse(self, ab, conf):
        '''connect to mysql-database and get data'''
        self.connect()
        try:
            qry = "SELECT %s, %s FROM %s" % (self.name_row, self.date_row, self.table)
            self.cursor.execute (qry)
            rows = self.cursor.fetchall ()
            for row in rows:
                ab.add(row[0], str(row[1]))
        except Exception, msg:
            showErrorMsg(_('Could not execute MySQL-query')
                            + ': %s\n %s' % (qry, str(msg)))
        self.conn.close()

    def add(self, name, birthday):
        '''insert new Birthday to database'''
        birthday = str(birthday)
        self.connect()
        try:
            qry = ("INSERT INTO %s (%s, %s) VALUES ('%s', '%s')" % 
                (self.table, self.name_row, self.date_row, name, birthday))
            self.cursor.execute (qry)
        except Exception, msg:
            showErrorMsg(_('Could not execute MySQL-query')
                            + ': %s\n %s' % (qry, str(msg)))
        self.conn.close()
        self.ab.add(name, birthday)

    def update(self, conf):
        '''update and save values'''
        if self.entries and self.entries != []:
            self.host = self.entries[0].get_text()
            self.port = self.entries[1].get_text()
            self.username = self.entries[2].get_text()
            self.password = self.entries[3].get_text()
            self.database = self.entries[4].get_text()
            self.table = self.entries[5].get_text()
            self.name_row = self.entries[6].get_text()
            self.date_row = self.entries[7].get_text()

            conf.MySQL = self

    def create_config(self, pref, conf):
        '''create additional mysql config in config menu'''
        table = gtk.Table(1, 2)

        label= gtk.Label(_('MySQL-Database')) # Label for MySQL, just translate 'Database'
        self.text = label
        table.attach(label, 0, 1, 0, 1)
        label.show()

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
        i = 0
        for value in values:
            label = gtk.Label(value[0])
            label.show()
            sqltable.attach(label, 0, 1, i, i+1)

            entry = gtk.Entry()
            entry.set_text(value[1])
            entry.show()
            self.entries.append(entry)
            sqltable.attach(entry, 1, 2, i, i+1)
            i+=1
        sqltable.show()
        table.attach(sqltable,1, 2, 0, 1)
        self.widget = sqltable
        table.show()
        pref.add(table)

class Sunbird(Lightning):
    '''Sunbird/Iceowl implementation (based on lightning)'''
    def __init__(self):
        Lightning.__init__(self, title='Sunbird/Iceowl', type='sunbird',
                            has_config=False)
        self.MOZILLA_LOCATION = os.path.join(os.environ['HOME'],
                '.mozilla')

    # load file / open database connection
    def parse(self, ab, conf):
        sunbird = os.path.join(self.MOZILLA_LOCATION, 'sunbird')
        iceowl = os.path.join(self.MOZILLA_LOCATION, 'iceowl')

        if (os.path.exists(sunbird)):
            # extract path from profiles.ini
            self.get_config_file(sunbird)
        elif (os.path.exists(iceowl)):
            self.get_config_file(iceowl)
        else:
            showErrorMsg(_('Neither iceowl nor sunbird is installed'))
