#!/usr/bin/env python
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
'''GBirthday

A KBirthday clone for Gnome environment, working with different 
data servers:
 - CSV-file (comma-seperated value)
 - MySQL
 - Evolution
 - Thunderbird/Icedove Lightning
 - Sunbrid / IceOwl

and relatively easy to extend for other data servers.
'''
### Original source from:
## pygtk-demo Status Icon: Nikos Kouremenos
## EvoBdayReminder.py: Axel Heim. http://www.axelheim.de/

import pygtk
pygtk.require('2.0')
import gtk

import os, re
import datetime
from datetime import date
import time
import subprocess
import gobject
import locale
import uuid

""" parse locales from python module
Do you say "1. January" or "January 1."?
"""
import locale
locale.setlocale(locale.LC_ALL, '')
day_at_place, month_at_place = 1, 2
if time.strftime('%x', (2000, 3, 1, 1, 0, 0, 0, 1, 0)).startswith("03"):
    day_at_place, month_at_place = 2, 1

import gettext
gettext.bindtextdomain("gbirthday")
_ = gettext.gettext

import ConfigParser

imageslocation = "/usr/share/pixmaps/gbirthday/"
languageslocation ="/usr/share/gbirthday/languages/"

birthday_today = False # someone has birthday today?!

'''database classes'''

class DataBase:
    '''
     inheritance class for all databases
     you can use this format to add new databases
     your DataBase implementation has to parse the data from your data source,
     and add it into the AddressBook (ab.add())
     you have to add your Database to the databases-list
    '''
    TITLE = 'Unknown'  # Title that will be displayed to the user
    TYPE = 'none'      # type that is used as identifier (e.g. for config file)
    CAN_SAVE = True    # new entries can be saved
    HAS_CONFIG = True  # additional config options for database connection or
                       # filename(s)
    widget = None      # the widget for additional config

    def parse(self):
        '''load file / open database connection'''
        pass

    def add(self, name, birthday):
        '''save new birthday to file/database (only if CAN_SAVE == true)'''
        pass

    def create_config(self, table):
        '''create additional pygtk config in config menu'''
        pass

    def update(self, f):
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

class Lightning(DataBase):
    '''Thunderbird/Lightning implementation'''
    TITLE = 'Thunderbird/Icedove Lightning'  # Title that will be displayed to the user
    TYPE = 'lightning'      # type that is used as identifier (e.g. for config file)
    CAN_SAVE = True    # new entries can be saved
    HAS_CONFIG = False # additional config options for database connection or
                       # filename(s)
    widget = None      # the widget for additional config
    THUNDERBIRD_LOCATION = os.path.join(os.environ['HOME'], 
        '.mozilla-thunderbird')

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
            showErrorMsg('error reading profile file %s' % configfile)

    def parse(self):
        '''open thunderbird sqlite-database'''
        if (os.path.exists(self.THUNDERBIRD_LOCATION)):
            self.get_config_file(self.THUNDERBIRD_LOCATION)

    def connect(self, filename):
        '''"connect" to sqlite3-database'''
        try:
            import sqlite3
        except:
            showErrorMsg('SQLite3 for python not installed')
        try:
            self.conn = sqlite3.connect (filename)
            self.cursor = self.conn.cursor()
        except Exception, msg:
            showErrorMsg('sqlite3 could not connect' + str(msg))


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
            ab.add(row[0], str(bday).split(' ')[0])
            

    def add(self, name, birthday):
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

class Sunbird(Lightning):
    '''Sunbird/Iceowl implementation (based on lightning)'''
    TITLE = 'Sunbird/Iceowl'
    TYPE = 'sunbird'
    CAN_SAVE = True   # new entries can be saved
    HAS_CONFIG = False # additional config options for database connection or
                       # filename(s)
    widget = None      # the widget for additional config
    MOZILLA_LOCATION = os.path.join(os.environ['HOME'], 
        '.mozilla')

    # load file / open database connection
    def parse(self):
        sunbird = os.path.join(self.MOZILLA_LOCATION, 'sunbird')
        iceowl = os.path.join(self.MOZILLA_LOCATION, 'iceowl')

        if (os.path.exists(sunbird)):
            # extract path from profiles.ini
            self.get_config_file(sunbird)
        elif (os.path.exists(iceowl)):
            self.get_config_file(iceowl)
        else:
            showErrorMsg(_('Neither iceowl nor sunbird is installed'))

class Evolution(DataBase):
    '''data import from the Evolution address book'''
    TITLE = 'Evolution'
    TYPE = 'evolution'
    CAN_SAVE = False
    HAS_CONFIG = False
    ADDRESS_BOOK_LOCATION = os.path.join(os.environ['HOME'], 
        '.evolution/addressbook/local/')
    _splitRE = re.compile(r'\r?\n')

    def parse(self, book=None):
        
        '''load and parse parse Evolution data files'''
        # get list of address books and extract their persons
        if (os.path.exists(self.ADDRESS_BOOK_LOCATION)):
            for addresser in os.listdir(self.ADDRESS_BOOK_LOCATION):
                location = os.path.join(self.ADDRESS_BOOK_LOCATION, addresser)
                for name in book or []:
                    location = os.path.join(location, 'subfolders', name)
                location = os.path.join(location, 'addressbook.db')
                addressbook = location
                try:
                    import bsddb
                except:
                    showErrorMsg('package bsddb not installed')
                try:
                    bsfile = bsddb.hashopen(addressbook)
                    for key in bsfile.keys():
                        data = bsfile[key]
                        if not data.startswith('BEGIN:VCARD'):
                            continue
                        self.parse_birthday(data)
                except bsddb.db.DBInvalidArgError, msg:
                    showErrorMsg('Error reading Evolution addressbook: %s' % msg[1])

    def parse_birthday(self, data):
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
            if (mostRecentName != '') and (mostRecentDate != ''):
                # if there already is a birthday add it to the list
                ab.add(mostRecentName, mostRecentDate)
                mostRecentName = ''
                mostRecentDate = ''

class CSV(DataBase):
    '''import from CSV-file'''
    TITLE = 'CSV-file (comma seperated value)'
    TYPE = 'csv'
    _seperators=['; ', ', ', ': ']   # possible seperators

    def parse(self):
        '''open and parse file'''
        for filename in csv_files:
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
        if len(csv_files) == 0:
            showErrorMsg(_('CSV-file does not exist'))
            return
        filename = csv_files[0]
        if (os.path.exists(filename)):
            f = file(csv_files[0], 'a')
        else:
            f = file(csv_files[0], 'w')
        f.write(birthday + ', ' + name + '\n')
        f.close()
        ab.add(name, birthday)
    
    def remove_file(self, widget, combobox):
        index = combobox.get_active()
        print index
        if index >= 0:
            combobox.remove_text(index)
            csv_files.remove(csv_files[index])
        return

    def add_file(self, widget, combobox, entry):
        filename = entry.get_text()
        combobox.append_text(filename)
        csv_files.append(filename)

    def create_config(self, pref):
        '''create aditional options menu'''
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        hbox2 = gtk.HBox()
        vbox.pack_start(hbox)
        combobox = gtk.combo_box_new_text()
        for csv_file in csv_files:
            combobox.append_text(csv_file)
        combobox.set_active(0)
        combobox.show()
        hbox.pack_start(combobox)
        remove_button = gtk.Button('remove')
        remove_button.connect("clicked", self.remove_file, combobox)
        remove_button.show()
        hbox.pack_start(remove_button, 0)
        hbox.show()
        
        entry = gtk.Entry()
        if len(csv_files) > 0:
            entry.set_text(csv_files[0])
        hbox2.pack_start(entry)
        entry.show()
        
        search_button = gtk.Button('select')
        search_button.connect("clicked", choose_file, entry)
        search_button.show()
        hbox2.pack_start(search_button)
        
        add_button = gtk.Button('add')
        add_button.connect("clicked", self.add_file, combobox, entry)
        add_button.show()
        hbox2.pack_start(add_button)
        
        vbox.pack_start(hbox2)
        hbox2.show()
        pref.add(vbox)
        vbox.show()

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

class MySQL(DataBase):
    '''MySQL database import'''
    TITLE = 'MySQL'
    TYPE = 'mysql'

    host = 'localhost'
    port = '3306'
    username = ''
    password = ''
    database = ''
    table = 'person'
    name_row = 'name'
    date_row = 'date'

    entries = []
    
    def connect(self):
        '''establish connection'''
        try:
            import MySQLdb
        except:
            showErrorMsg(_('MySQLdb is not installed. Please install MySQL for Python'))
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

    def parse(self):
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
        ab.add(name, birthday)

    def update(self, f):
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
            f.write("mysql_host=%s\n" % self.host)
            f.write("mysql_port=%s\n" % self.port)
            f.write("mysql_username=%s\n" % self.username)
            f.write("mysql_password=%s\n" % self.password)
            f.write("mysql_database=%s\n" % self.database)
            f.write("mysql_table=%s\n" % self.table)
            f.write("mysql_name_row=%s\n" % self.name_row)
            f.write("mysql_date_row=%s\n" % self.date_row)

    def create_config(self, pref):
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
    
# list of all availabe databases
databases = [Evolution(), Lightning(), Sunbird(), CSV(), MySQL()]
# list of databases the user wants
used_databases = ['evolution']
# list of csv-files we want to read
csv_files = []

#other data classes and core program logic

class AddressBook:
    '''AdressBook that saves birthday and names'''
    bdays = {} # list of all birthdays. Format:
               # {birthday: [Name1, Name2]}
               # for example
               # {'1970-01-01': ['Bar, Foo', 'Time'], 
               #  '1967-12-12': ['Power, Max']}

    def add(self, name, birthday):
        '''add a new person'''
        birthday = str(birthday)
        if birthday in self.bdays:
            # check for double entry - we assume that people with the same name
            # and the same birthday exists only once in our universe
            if not (name in self.bdays[birthday]):
                self.bdays[birthday].append(name)
        else:
            self.bdays[birthday] = [name]

    def manageBdays(self):
        now = date.today()
        bdayKeys = self.bdays.keys()
        birthday_list = []
        temporal = []

        global firstday
        global lastday
        
        for d in range(firstday,lastday+1):
            sDate = now + datetime.timedelta(d)

            for k in range(len(self.bdays)):
                sDateDay = str(sDate.day)
                
                for name in self.bdays[bdayKeys[k]]:
                    if len(sDateDay) != 2: 
                        sDateDay = '0' + sDateDay
                    sDateMonth = str(sDate.month)
                    if len(sDateMonth) != 2: 
                        sDateMonth = '0' + sDateMonth

                    if bdayKeys[k].find('-'+sDateMonth+'-'+sDateDay) != -1:
                        if d == 0:
                            birthday_today = True
                            icono = 'birthdaytoday.png'
                        elif d < 0:
                            icono = 'birthdaylost.png'
                        else:
                            icono = 'birthdaynext.png'

                        bday = bdayKeys[k]
                        
                        ano, mes, dia = bday.split('-', 2)
                        ano = sDate.year - int(ano)

                        temporal = [icono, bday, name, str(d), d, 
                            sDate.month, sDate.day, ano]
                        birthday_list.append(temporal)
        return birthday_list

    def checktoday(self):

        now = date.today()
        bdayKeys = self.bdays.keys()
        birthday_today = False

        global D
        global T
        
        for d in range(0,1):
            sDate = now + datetime.timedelta(d)

            for k in range(len(self.bdays)):
                sDateDay = str(sDate.day)
                if len(sDateDay) != 2: 
                    sDateDay = '0' + sDateDay
                sDateMonth = str(sDate.month)
                if len(sDateMonth) != 2: 
                    sDateMonth = '0' + sDateMonth

                if bdayKeys[k].find('-'+sDateMonth+'-'+sDateDay) != -1:
                    if d == 0:
                        birthday_today = True
        return birthday_today


'''pygtk-functions'''

def showErrorMsg(message, title=None, parent=None):
    '''show an error error message as MessageDialog'''
    if (not title):
        title = 'Error'
    errmsg = gtk.MessageDialog(parent, type=gtk.MESSAGE_ERROR, 
        buttons=gtk.BUTTONS_OK, flags=gtk.DIALOG_MODAL,
        message_format=message)
    errmsg.set_title(title)
    errmsg.run()
    errmsg.destroy()

def StatusIcon(parent=None):
    '''create status icon'''
    global icon
    icon = gtk.status_icon_new_from_file(imageslocation + 'birthday.png')
    lista=ab.manageBdays()
    if len(lista) > 0:
        icon.set_from_file(imageslocation + 'birthday.png')
    else:
        icon.set_from_file(imageslocation + 'nobirthday.png')
    icon.set_blinking(AddressBook.checktoday(ab))
    icon.connect('popup-menu', on_right_click)
    icon.connect('activate', on_left_click, 20, 20)

def make_menu(event_button, event_time, icon):
    '''create menu window'''
    menu = gtk.Menu()
    cerrar = gtk.Image()
    cerrar.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU,)
    recargar = gtk.ImageMenuItem(_('Reload'))
    recarga_img = gtk.Image()
    recarga_img.set_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_MENU,)
    recargar.set_image(recarga_img)
    recargar.show()
    recargar.connect_object('activate', reload_gbirthday, 'reload')
    menu.append(recargar)
    blink_menu = gtk.ImageMenuItem(_('Stop blinking'))
    blink_img = gtk.Image()
    blink_img.set_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_MENU,)
    blink_menu.set_image(blink_img)
    blink_menu.show()
    blink_menu.connect_object('activate', stop_blinking, 'stop blinking')
    menu.append(blink_menu)

    add_menu = gtk.ImageMenuItem(_('Add'))
    add_img = gtk.Image()
    add_img.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_MENU,)
    add_menu.set_image(add_img)
    add_menu.show()
    add_menu.connect_object("activate", add, "add birthday")
    menu.append(add_menu)

    preferences_menu = gtk.ImageMenuItem(_('Preferences'))
    preferences_img = gtk.Image()
    preferences_img.set_from_stock(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_MENU,)
    preferences_menu.set_image(preferences_img)
    preferences_menu.show()
    preferences_menu.connect_object("activate", preferences_window, "about")
    menu.append(preferences_menu)

    about_menu = gtk.ImageMenuItem(_('About'))
    about_img = gtk.Image()
    about_img.set_from_stock(gtk.STOCK_ABOUT, gtk.ICON_SIZE_MENU,)
    about_menu.set_image(about_img)
    about_menu.show()
    about_menu.connect_object("activate", create_dialog, None)
    menu.append(about_menu)

    salir = gtk.ImageMenuItem(_('Quit'))
    salir.set_image(cerrar)
    salir.show()
    salir.connect_object("activate", finish_gbirthday, "file.quit")
    menu.append(salir)
    menu.popup(None, None,
        gtk.status_icon_position_menu, event_button,
        event_time, icon)

def on_right_click(icon, event_button, event_time):
    '''open menu window on right click'''
    make_menu(event_button, event_time, icon)
    
def on_left_click(icon, event_button, event_time):
    '''close/open window with list of birthdays'''
    global showbdcheck
    if showbdcheck == 0:
        showbdcheck = 1
        openwindow()
    else:
        closebdwindow('focus_out_event', closebdwindow, "")

def openwindow():
    '''open window that includes all birthdays'''
    global showbd 
    global showbdcheck
    showbd = gtk.Window(gtk.WINDOW_TOPLEVEL)
    showbd.set_decorated(False)
    showbd.set_position(gtk.WIN_POS_MOUSE)
    showbd.set_icon_from_file(imageslocation + 'birthday.png')
    showbd.set_border_width(0)

    lista=AddressBook.manageBdays(ab)
    listaiconos = []

    box = gtk.HBox()
    box.set_border_width(5)
    box.show()
    frame = gtk.Frame(None)
    showbd.add(frame)
    table = gtk.Table(7, 6, False)
    box.pack_start(table, False , False, 0)
    frame.add(box)
    table.set_col_spacings(10)
    fila = 0
    event_box = gtk.EventBox()
    table.attach(event_box, 0, 6, 0, 1)
    event_box.show()
    label = gtk.Label("GBirthday")
    if len(lista) > 0:
        label.set_markup('<b>%s</b>' % _('Birthdays'))
    else:
        label.set_markup('<b>\n    %s    \n</b>' % _('No birthdays in specified period'))
    label.set_justify(gtk.JUSTIFY_RIGHT)
    event_box.add(label)
    label.show()
    style = label.get_style()
    event_box.modify_bg(gtk.STATE_NORMAL, event_box.rc_get_style().bg[gtk.STATE_SELECTED])
    fila = fila +1
    for cumple in lista:
        image = gtk.Image()
        image.set_from_file(imageslocation + cumple[0])
        table.attach(image, 0, 1, fila, fila+1)
        image.show()

        lang_month = time.strftime('%B', (2000, int(cumple[5]), 1, 1, 0, 0, 0, 1, 0))
        if cumple[4] == 0:
            label = gtk.Label('<b>%s</b>' % lang_month)
            label.set_markup('<b>%s</b>' % lang_month)
        elif cumple[4] < 0:
            label = gtk.Label(lang_month)
            label.set_markup('<span foreground="grey">%s</span>' % lang_month)
        else:
            label = gtk.Label(lang_month)
        align = gtk.Alignment(0.0, 0.5, 0, 0)
        align.add(label)
        align.show()
        table.attach(align, month_at_place, 
                        month_at_place+1, fila, fila+1)
        label.show()

        c = str(cumple[6])
        if cumple[4] == 0:
            label = gtk.Label("<b>%s</b>" % c)
            label.set_markup("<b>%s</b>" % c)
        elif cumple[4] < 0:
            label = gtk.Label(str(cumple[6]))
            label.set_markup('<span foreground="grey">%s</span>' % c)
        else:
            label = gtk.Label(str(cumple[6]))
        align = gtk.Alignment(1.0, 0.5, 0, 0)
        align.add(label)
        align.show()
        table.attach(align, day_at_place, 
                        day_at_place+1, fila, fila+1)
        label.show()

        if cumple[4] == 0:
            label = gtk.Label("<b>" + cumple[2] + "</b>")
            label.set_markup("<b>" + cumple[2] + "</b>")
        elif cumple[4] < 0:
            label = gtk.Label(cumple[2])
            label.set_markup("<span foreground='grey'>" + cumple[2] + "</span>")
        else:
            label = gtk.Label(cumple[2])
        align = gtk.Alignment(0.0, 0.5, 0, 0)
        align.add(label)
        table.attach(align, 3, 4, fila, fila+1)
        align.show()
        label.show()

        if cumple[4] == 0:
            label = gtk.Label(_('Today'))
            label.set_markup('<b>%s</b>' % _('Today'))
        elif cumple[4] == -1:
            label = gtk.Label(_('Yesterday'))
            label.set_markup('<span foreground="grey">%s</span>' % 
                _('Yesterday'))
        elif cumple[4] < -1:
            ago = (_('%s Days ago') % str(cumple[4] * -1))
            label = gtk.Label(ago)
            label.set_markup('<span foreground="grey">%s</span>' % ago)
        elif cumple[4] == 1:
            label = gtk.Label(_('Tomorrow'))
        else:
            label = gtk.Label(cumple[3] + " " + _('Days'))
        align = gtk.Alignment(0.0, 0.5, 0, 0)
        align.add(label)
        align.show()
        table.attach(align, 4, 5, fila, fila+1)
        label.show()

        years = '%s %s' % (str(cumple[7]), _('Years'))
        if cumple[4] == 0:
            label = gtk.Label('<b>%s</b>' % years)
            label.set_markup('<b>%s</b>' % years)
        elif cumple[4] < 0:
            label = gtk.Label(years)
            label.set_markup('<span foreground="grey">%s</span>' % years)
        else:
            label = gtk.Label(years)
        align = gtk.Alignment(1.0, 0.5, 0, 0)
        align.add(label)
        align.show()
        table.attach(align, 5, 6, fila, fila+1)
        label.show()
        fila = fila +1

    table.show()
    frame.show()
    showbd.show()
    showbd.connect('focus_out_event', closebdwindow,"texto")

def closebdwindow(uno, dos, textocw):
    '''close about window'''
    global showbdcheck
    showbdcheck = 0
    showbd.destroy()

def on_url(d, link, data):
    '''start default browser with gbirthday-website on click'''
    subprocess.Popen(['sensible-browser', 'http://gbirthday.sourceforge.net/'])

gtk.about_dialog_set_url_hook(on_url, None)

def create_dialog(uno):
    '''create about dialog'''
    global dlg
    dlg = gtk.AboutDialog()
    dlg.set_version("0.5.2")
    dlg.set_comments(_('Birthday reminder'))
    dlg.set_name("GBirthday")
    image = gtk.gdk.pixbuf_new_from_file(imageslocation + 'gbirthday.png')
    dlg.set_logo(image)
    dlg.set_icon_from_file(imageslocation + 'birthday.png')
    dlg.set_copyright(u'Copyright \u00A9 2007 Alex Mallo, 2009 Andreas Bresser, 2009 Thomas Spura')
    dlg.set_license('''Licensed under the GNU General Public License Version 2

GBirthday is free software; you can redistribute it and\/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

GBirthday is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.''')
    dlg.set_authors(['Alex Mallo <dernalis@gmail.com>', 
                     'Robert Wildburger <r.wildburger@gmx.at>', 
                     'Stefan Jurco <stefan.jurco@gmail.com>', 
                     'Andreas Bresser <andreas@phidev.org>',
                     'Thomas Spura <tomspur@fedoraproject.org>'])
    dlg.set_artists(['Alex Mallo <dernalis@gmail.com>'])
    dlg.set_translator_credits(_('translator-credit'))
    dlg.set_website('http://gbirthday.sf.net/')
    def close(w, res):
        if res == gtk.RESPONSE_CANCEL:
            w.hide()
    dlg.connect('response', close)
    dlg.run()

def db_select(widget, db):
    '''callback for checkboxes and update used_databases'''
    if (widget.get_active()):
        if not db.TYPE in used_databases:
            used_databases.append(db.TYPE)
            db.activate()
    else:
        if db.TYPE in used_databases:
            used_databases.remove(db.TYPE)
            db.deactivate()

def preferences_db(widget, db):
    global imageslocation
    global preferences
    pref_db = gtk.Window(gtk.WINDOW_TOPLEVEL)
    pref_db.set_decorated(True)
    pref_db.set_position(gtk.WIN_POS_CENTER)
    pref_db.set_title(_('Database Configuration'))
    pref_db.set_icon_from_file(imageslocation + 'birthday.png')
    
    
    db.create_config(pref_db)
    pref_db.set_modal(True)
    pref_db.show()


def preferences_window(textocw=None):
    '''show settings window'''
    global imageslocation
    global preferences
    preferences = gtk.Window(gtk.WINDOW_TOPLEVEL)
    preferences.set_decorated(True)
    preferences.set_position(gtk.WIN_POS_CENTER)
    preferences.set_title(_('Preferences'))
    preferences.set_icon_from_file(imageslocation + 'birthday.png')

    box = gtk.VBox(False, 0)
    preferences.add(box)

    table = gtk.Table(3, 2, False)
    table.set_col_spacings(10)
    table.set_row_spacings(10)

    label= gtk.Label(_('Past birthdays'))
    table.attach(label, 0, 1, 0, 1)
    label.show()

    label= gtk.Label(_('Next birthdays'))
    table.attach(label, 0, 1, 1, 2)
    label.show()

    label= gtk.Label(_('Database'))
    table.attach(label, 0, 1, 2, 3)
    label.show()

    past = gtk.Adjustment(firstday, lower=-30, upper=0, step_incr=-1, 
        page_incr=0, page_size=0)
    spin = gtk.SpinButton(past, climb_rate=0.0, digits=0)
    spin.connect("value-changed", cambiar_preferencias,"firstday", spin)
    table.attach(spin,1, 2, 0, 1)
    spin.show()

    next = gtk.Adjustment(lastday, lower=0, upper=90, step_incr=1, 
        page_incr=0, page_size=0)
    spin = gtk.SpinButton(next, climb_rate=0.0, digits=0)
    spin.connect("value-changed", cambiar_preferencias,"lastday", spin)
    table.attach(spin,1, 2, 1, 2)
    spin.show()

    vbox = gtk.VBox(False, 10)
    for db in databases:
        hbox = gtk.HBox(False, 2)
        vbox.pack_start(hbox, False, False, 3)
        
        chkDB = gtk.CheckButton(db.TITLE)
        if db.TYPE in used_databases:
            chkDB.set_active(True)
        chkDB.connect("toggled", db_select, db)
        hbox.pack_start(chkDB, False , False, 0)
        if db.HAS_CONFIG:
            button = gtk.Button(_('Configure'))
            button.connect("clicked", preferences_db, db)
            button.show()
            hbox.pack_start(button, False, False, 1)
        hbox.show()
        chkDB.show()
    table.attach(vbox,1, 2, 2, 3)
    vbox.show()

    box.pack_start(table, True , True, 8)
    table.show()

    button = gtk.Button(_('Save & Close'))
    box.pack_start(button, False , False, 2)
    button.connect("clicked", finish_preferences, None)
    button.show()
    box.show()
    preferences.set_border_width(5)
    preferences.show()

def cambiar_preferencias(uno, opcion, spin):
    '''set value for settings by spinner'''
    global firstday
    global lastday
    spin.update()
    if opcion == "firstday": firstday = spin.get_value_as_int()
    elif opcion == "lastday": lastday = spin.get_value_as_int()
    else: showErrorMsg(_('Internal Error: Option %s not valid.') % opcion)

def finish_gbirthday(texto):
    '''exit program'''
    if dlg != None:
        dlg.destroy()
    gtk.main_quit()

def finish_preferences(uno,texto):
    '''save settings after user clicked save and exit'''
    save_config()
    preferences.destroy()

def finish_add(uno, combo, name, calend, window):
    '''save new added person'''
    for db in databases:
        if db.TITLE == combo.get_active_text():
            calend = list(calend.get_date())
            calend[1] += 1
            db.add(name.get_text(), datetime.date(*calend))
    window.destroy()

def save_list(l):
    '''create a string that can be saved in a file'''
    return str(l)[2:-2].replace("', '", ',')

def save_config():
    '''save config in file'''
    global firstday
    global lastday
    f = open(os.environ['HOME']+'/.gbirthday.conf','w')
    f.write('firstday=%i\n' % firstday)
    f.write('lastday=%i\n' % lastday)
    f.write('databases=%s\n' % save_list(used_databases))
    f.write('csvfiles=%s\n' % save_list(csv_files))
    for db in databases:
        db.update(f)
    f.close()

def reload_gbirthday(texto):
    '''reload gbirthday, reload data from databases'''
    global ab
    global icon
    start()
    icon.set_blinking(AddressBook.checktoday(ab))
    lista=AddressBook.manageBdays(ab)
    if len(lista) > 0:
        icon.set_from_file(imageslocation + 'birthday.png')
    else:
        icon.set_from_file(imageslocation + 'nobirthday.png')

def stop_blinking(texto):
    '''stop blinking (only if icon blinks)'''
    global icon
    icon.set_blinking(False)

def add_single_manual(widget, window):
    if window != None: window.destroy()
    add_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    add_window.set_decorated(True)
    add_window.set_position(gtk.WIN_POS_CENTER)
    add_window.set_title(_('Add'))
    add_window.set_icon_from_file(imageslocation + 'birthday.png')

    box = gtk.VBox(False, 0)
    add_window.add(box)

    table = gtk.Table(3, 2, False)
    table.set_col_spacings(10)
    table.set_row_spacings(10)

    label= gtk.Label(_('Name'))
    table.attach(label, 0, 1, 0, 1)
    label.show()

    label= gtk.Label(_('Birthday'))
    table.attach(label, 0, 1, 1, 2)
    label.show()

    label= gtk.Label(_('Save to file/database'))
    table.attach(label, 0, 1, 2, 3)
    label.show()

    name = gtk.Entry()
    name.set_text("")
    table.attach(name, 1, 2, 0, 1)
    name.show()

    date = gtk.Calendar()
    table.attach(date, 1, 2, 1, 2)
    date.show()

    liststore = gtk.ListStore(str)
    combobox = gtk.combo_box_new_text()
    for db in databases:
        if db.CAN_SAVE:
            combobox.append_text(db.TITLE)
    combobox.set_active(0)
    combobox.show()
    table.attach(combobox,1, 2, 2, 3)

    box.pack_start(table, True , True, 8)
    table.show()

    button = gtk.Button(_('Save & Close'))
    box.pack_start(button, False , False, 2)
    button.connect("clicked", finish_add, combobox, name, date, add_window)
    button.show()
    
    box.show()
    add_window.set_border_width(5)
    add_window.show()

def add_from_file(widget, window):
    window.destroy()
    add_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    add_window.set_decorated(True)
    add_window.set_position(gtk.WIN_POS_CENTER)
    add_window.set_title(_('Add'))
    add_window.set_icon_from_file(imageslocation + 'birthday.png')
    
    box = gtk.VBox(False, 0)
    add_window.add(box)

    table = gtk.Table(3, 2, False)
    table.set_col_spacings(10)
    table.set_row_spacings(10)
    
    
    label= gtk.Label('select file/database')
    table.attach(label, 0, 1, 0, 1)
    label.show()
    
    liststore = gtk.ListStore(str)
    db_combo = gtk.combo_box_new_text()
    for db in databases:
        db_combo.append_text(db.TITLE)
    db_combo.set_active(0)
    db_combo.show()
    table.attach(db_combo,1, 2, 0, 1)
    
    label= gtk.Label(_('Import Settings'))
    table.attach(label, 0, 1, 1, 2)
    label.show()
    
    label= gtk.Label('not needed')
    table.attach(label, 1, 2, 1, 2)
    label.show()
    
    label= gtk.Label(_('Database'))
    table.attach(label, 0, 1, 2, 3)
    label.show()
    
    liststore = gtk.ListStore(str)
    combobox = gtk.combo_box_new_text()
    for db in databases:
        if db.CAN_SAVE:
            combobox.append_text(db.TITLE)
    combobox.set_active(0)
    combobox.show()
    table.attach(combobox,1, 2, 2, 3)

    box.pack_start(table, True , True, 8)
    table.show()

    label= gtk.Label(_('Export Settings'))
    table.attach(label, 0, 1, 3, 4)
    label.show()
    
    label= gtk.Label('not needed')
    table.attach(label, 1, 2, 3, 4)
    label.show()

    button = gtk.Button(_('Save & Close'))
    box.pack_start(button, False , False, 2)
    button.connect("clicked", finish_add, combobox, db_combo, '', add_window)
    button.show()
    
    box.show()
    
    box.show()
    add_window.set_border_width(5)
    add_window.show()

def add(texto):
    '''Show Dialog to add new Person - not yet implemented!'''
    add_single_manual(None, None)
'''
    add_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    add_window.set_decorated(True)
    add_window.set_position(gtk.WIN_POS_CENTER)
    add_window.set_title(_('Add'))
    add_window.set_icon_from_file(imageslocation + 'birthday.png')

    box = gtk.VBox(False, 0)
    add_window.add(box)
    
    manualButton = gtk.Button(_('Add single birthday manually'))
    manualButton.connect("clicked", add_single_manual, add_window)
    box.pack_start(manualButton)
    manualButton.show()
    
    fileButton = gtk.Button(_('Add multiple birthdays from file or database'))
    fileButton.connect("clicked", add_from_file, add_window)
    box.pack_start(fileButton)
    fileButton.show()
    
    box.show()
    add_window.set_border_width(5)
    add_window.show()
'''

def check_new_day():
    '''check for new birthday (check every 60 seconds)'''
    global dia
    diahoy = time.strftime("%d", time.localtime(time.time()))
    if dia != diahoy:
        lista=AddressBook.manageBdays(ab)
        if len(lista) > 0:
            icon.set_from_file(imageslocation + 'birthday.png')
        else:
            icon.set_from_file(imageslocation + 'nobirthday.png')
        icon.set_blinking(AddressBook.checktoday(ab))
        dia = diahoy
    return True

def start():
    '''(re)create AdressBook and parse data'''
    global ab
    ab.bdays = {}
    for db in databases:
        if (db.TYPE in used_databases):
            db.parse()

if __name__ == '__main__':
    global firstday
    global lastday
    global ab
    global icon
    global icono
    global showbdcheck
    global dlg
    global dia
    dlg= None
    showbdcheck = 0

    # try to load settings
    try:
        f = open(os.environ['HOME']+"/.gbirthday.conf",'r')
    except IOError:
        firstday = -2
        lastday = 30
        used_databases = ['evolution']
        save_config()
        print "Created configuration file."
        # show settings dialog
        preferences_window()
        # TODO: stop program until user settings are set?
    else:
        # parse config file
        for line in f:
            line = line.replace("\n","")
            label, value = line.split('=', 1)
            if label == "firstday": firstday = int(value)
            elif label == "lastday": lastday = int(value)
            elif label == "csvfiles":
                if len(value) > 2: 
                    csv_files = value.split(',')
            elif label == "mysql_host": MySQL.host = value
            elif label == "mysql_port": MySQL.port = value
            elif label == "mysql_username": MySQL.username = value
            elif label == "mysql_password": MySQL.password = value
            elif label == "mysql_database": MySQL.database = value
            elif label == "mysql_table": MySQL.table = value
            elif label == "mysql_name_row": MySQL.name_row = value
            elif label == "mysql_date_row": MySQL.date_row = value
            elif label == "databases" and len(value) > 2: 
                used_databases = value.split(',')
            else: showErrorMsg(_("Unhandled value in gbirthday.conf: %s") % str(line))
        f.close()

    # load data and fill AddressBook
    ab = AddressBook()
    start()

    # show status icon
    icono = StatusIcon()
    dia = time.strftime("%d", time.localtime(time.time()))

    # check every 60 seconds for new day
    # TODO: update until end of day according to current clock settings?
    #       (might not the best idea if user changes current time)
    gobject.timeout_add(60000, check_new_day)
    gtk.main()
