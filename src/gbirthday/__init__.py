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

VERSION = "0.5.2"

import gtk

import os
import datetime
from datetime import date
import time

""" parse locales from python module
Do you say "1. January" or "January 1."?
"""
import locale
locale.setlocale(locale.LC_ALL, '')
day_at_place, month_at_place = 1, 2
if time.strftime('%x', (2000, 3, 1, 1, 0, 0, 0, 1, 0)).startswith("03"):
    day_at_place, month_at_place = 2, 1

# for FreeBSD users: if no i18n is whished, no gettext package won't be
# available and standard messages are displayed insted a try to use
# translated strings
try:
    import gettext
    gettext.install("gbirthday")
except ImportError:
    _ = lambda x: x

import ConfigParser

imageslocation = os.sep.join(__file__.split(os.sep)[:-1])+"/pics/"

birthday_today = False # someone has birthday today?!

'''database classes'''

from databases import *
    
# list of all availabe databases
databases = [Evolution(), Lightning(), Sunbird(), CSV(), MySQL()]

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

        global conf
        
        for d in range(int (conf.firstday), int (conf.lastday)+1):
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
                            pic = 'birthdaytoday.png'
                        elif d < 0:
                            pic = 'birthdaylost.png'
                        else:
                            pic = 'birthdaynext.png'

                        bday = bdayKeys[k]
                        
                        ano, mes, dia = bday.split('-', 2)
                        ano = sDate.year - int(ano)

                        temporal = [pic, bday, name, str(d), d,
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

class StatusIcon():
    def __init__(self, ab, conf):
        '''create status icon'''
        self.icon = gtk.status_icon_new_from_file(imageslocation + 'birthday.png')
        self.ab = ab
        self.conf = conf
        list=ab.manageBdays()
        if len(list) > 0:
            self.icon.set_from_file(imageslocation + 'birthday.png')
        else:
            self.icon.set_from_file(imageslocation + 'nobirthday.png')
        self.icon.set_blinking(AddressBook.checktoday(ab))
        self.icon.connect('popup-menu', self.on_right_click)
        self.icon.connect('activate', self.on_left_click, 20, 20)

        def on_url(d, link, data):
            '''start default browser with gbirthday-website on click'''
            import subprocess
            subprocess.Popen(['sensible-browser', 'http://gbirthday.sourceforge.net/'])

        gtk.about_dialog_set_url_hook(on_url, None)

    def reload_gbirthday(self, text):
        '''reload gbirthday, reload data from databases'''
        start(self.ab, self.conf)
        self.icon.set_blinking(AddressBook.checktoday(self.ab))
        list=AddressBook.manageBdays(self.ab)
        if len(list) > 0:
            self.icon.set_from_file(imageslocation + 'birthday.png')
        else:
            self.icon.set_from_file(imageslocation + 'nobirthday.png')

    def check_new_day(self):
        '''check for new birthday (check every 60 seconds)'''
        global current_day
        new_day = time.strftime("%d", time.localtime(time.time()))
        if current_day != new_day:
            list=AddressBook.manageBdays(self.ab)
            if len(list) > 0:
                self.icon.set_from_file(imageslocation + 'birthday.png')
            else:
                self.icon.set_from_file(imageslocation + 'nobirthday.png')
            self.icon.set_blinking(AddressBook.checktoday(self.ab))
            current_day = new_day
        return True

    def make_menu(self, event_button, event_time, icon):
        '''create menu window'''
        menu = gtk.Menu()
        cerrar = gtk.Image()
        cerrar.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU,)
        recargar = gtk.ImageMenuItem(_('Reload'))
        recarga_img = gtk.Image()
        recarga_img.set_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_MENU,)
        recargar.set_image(recarga_img)
        recargar.show()
        recargar.connect_object('activate', self.reload_gbirthday, 'reload')
        menu.append(recargar)
        blink_menu = gtk.ImageMenuItem(_('Stop blinking'))
        blink_img = gtk.Image()
        blink_img.set_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_MENU,)
        blink_menu.set_image(blink_img)
        blink_menu.show()
        blink_menu.connect_object('activate', self.stop_blinking, 'stop blinking')
        menu.append(blink_menu)

        add_menu = gtk.ImageMenuItem(_('Add'))
        add_img = gtk.Image()
        add_img.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_MENU,)
        add_menu.set_image(add_img)
        add_menu.show()
        add_menu.connect_object("activate", self.add, "add birthday")
        menu.append(add_menu)

        preferences_menu = gtk.ImageMenuItem(_('Preferences'))
        preferences_img = gtk.Image()
        preferences_img.set_from_stock(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_MENU,)
        preferences_menu.set_image(preferences_img)
        preferences_menu.show()
        preferences_menu.connect_object("activate", self.preferences_window, "about")
        menu.append(preferences_menu)

        about_menu = gtk.ImageMenuItem(_('About'))
        about_img = gtk.Image()
        about_img.set_from_stock(gtk.STOCK_ABOUT, gtk.ICON_SIZE_MENU,)
        about_menu.set_image(about_img)
        about_menu.show()
        about_menu.connect_object("activate", self.create_dialog, None)
        menu.append(about_menu)

        salir = gtk.ImageMenuItem(_('Quit'))
        salir.set_image(cerrar)
        salir.show()
        salir.connect_object("activate", self.finish_gbirthday, "file.quit")
        menu.append(salir)
        menu.popup(None, None,
            gtk.status_icon_position_menu, event_button,
            event_time, icon)

    def create_dialog(self, uno):
        '''create about dialog'''
        global dlg
        dlg = gtk.AboutDialog()
        dlg.set_version(VERSION)
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
        dlg.set_authors([
                'Andreas Bresser <andreas@phidev.org>',
                'Stefan Jurco <stefan.jurco@gmail.com>',
                'Alex Mallo <dernalis@gmail.com>',
                'Thomas Spura <tomspur@fedoraproject.org>',
                'Robert Wildburger <r.wildburger@gmx.at>'
                        ])
        dlg.set_artists(['Alex Mallo <dernalis@gmail.com>'])
        cred = _('translator-credit')
        if cred != 'translator-credit':
            dlg.set_translator_credits(cred)
        else:
            dlg.set_translator_credits(
                _("There are no translations or the translator doesn't want to get credits for that.") )
        dlg.set_website('http://gbirthday.sf.net/')
        def close(w, res):
            if res == gtk.RESPONSE_CANCEL:
                w.hide()
        dlg.connect('response', close)
        dlg.run()

    def finish_gbirthday(self, text):
        '''exit program'''
        if dlg is not None:
            dlg.destroy()
        gtk.main_quit()

    def on_right_click(self, icon, event_button, event_time):
        '''open menu window on right click'''
        self.make_menu(event_button, event_time, icon)

    def on_left_click(self, icon, event_button, event_time):
        '''close/open window with list of birthdays'''
        global showbdcheck
        if showbdcheck == 0:
            showbdcheck = 1
            self.openwindow()
        else:
            self.closebdwindow('focus_out_event', self.closebdwindow, "")

    def openwindow(self):
        '''open window that includes all birthdays'''
        global showbd
        global showbdcheck
        showbd = self.gtk_get_top_window('', False, False)

        list=AddressBook.manageBdays(self.ab)

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
        if len(list) > 0:
            label.set_markup('<b>%s</b>' % _('Birthdays'))
        else:
            label.set_markup('<b>\n    %s    \n</b>' % _('No birthdays in specified period'))
        label.set_justify(gtk.JUSTIFY_RIGHT)
        event_box.add(label)
        label.show()
        style = label.get_style()
        event_box.modify_bg(gtk.STATE_NORMAL, event_box.rc_get_style().bg[gtk.STATE_SELECTED])
        fila = fila +1
        for cumple in list:
            image = gtk.Image()
            image.set_from_file(imageslocation + cumple[0])
            table.attach(image, 0, 1, fila, fila+1)
            image.show()

            try:
                lang_month = unicode (time.strftime('%B', (2000, int(cumple[5]), 1, 1, 0, 0, 0, 1, 0)) )
            except:
                lang_month = str(cumple[5])
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
        showbd.connect('focus_out_event', self.closebdwindow, "text")

    def stop_blinking(self, text):
        '''stop blinking (only if icon blinks)'''
        self.icon.set_blinking(False)

    def preferences_window(self, textcw=None):
        '''show settings window'''
        global imageslocation
        global preferences
        global conf
        preferences = self.gtk_get_top_window(_('Preferences'))

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

        def get_new_preferences(uno, option, spin):
            '''set value for settings by spinner'''
            global conf
            spin.update()
            if option == "firstday": conf.firstday = spin.get_value_as_int()
            elif option == "lastday": conf.lastday = spin.get_value_as_int()
            else:
                showErrorMsg(_('Internal Error: Option %s not valid.') % option)

        past = gtk.Adjustment(int (conf.firstday), lower=-30, upper=0, step_incr=-1,
                            page_incr=0, page_size=0)
        spin = gtk.SpinButton(past, climb_rate=0.0, digits=0)
        spin.connect("value-changed", get_new_preferences, "firstday", spin)
        table.attach(spin,1, 2, 0, 1)
        spin.show()

        next = gtk.Adjustment(int (conf.lastday), lower=0, upper=90, step_incr=1,
                            page_incr=0, page_size=0)
        spin = gtk.SpinButton(next, climb_rate=0.0, digits=0)
        spin.connect("value-changed", get_new_preferences, "lastday", spin)
        table.attach(spin,1, 2, 1, 2)
        spin.show()

        def db_select(widget, db):
            '''callback for checkboxes and update used_databases'''
            global conf
            if (widget.get_active()):
                if not db.TYPE in conf.used_databases:
                    conf.used_databases.append(db.TYPE)
                    db.activate()
            else:
                if db.TYPE in conf.used_databases:
                    conf.used_databases.remove(db.TYPE)
                    db.deactivate()

        def preferences_db(widget, db):
          #  global imageslocation
            global preferences
            pref_db = self.gtk_get_top_window(_('Database Configuration'))

            db.create_config(pref_db, self.conf)
            pref_db.set_modal(True)
            pref_db.show()

        vbox = gtk.VBox(False, 10)
        for db in databases:
            hbox = gtk.HBox(False, 2)
            vbox.pack_start(hbox, False, False, 3)

            chkDB = gtk.CheckButton(db.TITLE)
            if db.TYPE in conf.used_databases:
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

        def finish_preferences(uno, texto):
            '''save settings after user clicked save and exit'''
            self.save_config()
            preferences.destroy()
        button = gtk.Button(_('Save & Close'))
        box.pack_start(button, False , False, 2)
        button.connect("clicked", finish_preferences, None)
        button.show()
        box.show()
        preferences.set_border_width(5)
        preferences.show()

    def save_config(self):
        '''save config in file'''
        global conf
        for db in databases:
            db.update(conf)
        conf.save()

    def add(self, text):
        '''Show Dialog to add new Person - not yet implemented!'''
        self.add_single_manual(None, None)
        '''
        add_window = self.gtk_get_top_window(_('Add'))

        box = gtk.VBox(False, 0)
        add_window.add(box)

        manualButton = gtk.Button(_('Add single birthday manually'))
        manualButton.connect("clicked", self.add_single_manual, add_window)
        box.pack_start(manualButton)
        manualButton.show()

        fileButton = gtk.Button(_('Add multiple birthdays from file or database'))
        fileButton.connect("clicked", self.add_from_file, add_window)
        box.pack_start(fileButton)
        fileButton.show()

        box.show()
        add_window.set_border_width(5)
        add_window.show()
        '''

    def add_single_manual(self, widget, window):
        if window is not None: window.destroy()
        add_window = self.gtk_get_top_window(_('Add'))

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
        button.connect("clicked", self.finish_add, combobox, name, date, add_window)
        button.show()

        box.show()
        add_window.set_border_width(5)
        add_window.show()

    def finish_add(self, uno, combo, name, calend, window):
        '''save new added person'''
        for db in databases:
            if db.TITLE == combo.get_active_text():
                calend = list(calend.get_date())
                calend[1] += 1
                db.add(name.get_text(), datetime.date(*calend))
        window.destroy()

    def add_from_file(self, widget, window):
        window.destroy()
        add_window = self.gtk_get_top_window(_('Add'))

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
        button.connect("clicked", self.finish_add, combobox, db_combo, '', add_window)
        button.show()

        box.show()

        box.show()
        add_window.set_border_width(5)
        add_window.show()

    @staticmethod
    def closebdwindow(uno, dos, textcw):
        '''close about window'''
        global showbdcheck
        showbdcheck = 0
        showbd.destroy()

    ### gtk helper functions ###
    @staticmethod
    def gtk_get_top_window(title, decorated=True, center=True):
        global imageslocation
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_decorated(decorated)
        if center:
            window.set_position(gtk.WIN_POS_CENTER)
        else:
            window.set_position(gtk.WIN_POS_MOUSE)
        window.set_title(title)
        window.set_icon_from_file(imageslocation + 'birthday.png')
        return window

# not needed atm, will be possibly deleted
def save_list(l):
    '''create a string that can be saved in a file'''
    return str(l)[2:-2].replace("', '", ',')

def start(ab, conf):
    '''(re)create AdressBook and parse data'''
    ab.bdays = {}
    for db in databases:
        if (db.TYPE in conf.used_databases):
            db.parse(ab=ab, conf=conf)

class Conf:
    def __init__(self):
        import ConfigParser
        self.firstday = self.lastday = None
        self.ab = None
        self.csv_files = None
        self.MySQL = None
        self.settings = ConfigParser.ConfigParser()
        try:
            self.settings.readfp( file(os.environ['HOME']+"/.gbirthdayrc") )
        except IOError:
            self.settings.add_section("main")
            self.default_values()
        else:
            if self.settings.has_section("main"):
                self.sync_to_mem()
            else:
                settings.add_section("main")
                self.default_values()

    def default_values(self):
        self.firstday = -2
        self.lastday = 30
        self.used_databases = ['evolution']
        self.csv_files = None

    def sync_to_mem(self):
        self.firstday = self.settings.get("main", "firstday")
        self.lastday = self.settings.get("main", "lastday")
        self.csv_files = self.settings.get("main", "csv_files")
        self.used_databases = self.settings.get("main", "databases")
        try:
            MySQL.host = self.settings.get("mysql", "host")
            MySQL.port = self.settings.get("mysql", "port")
            MySQL.username = self.settings.get("mysql", "username")
            MySQL.passwort = self.settings.get("mysql", "password")
            MySQL.database = self.settings.get("mysql", "database")
            MySQL.table = self.settings.get("mysql", "table")
            MySQL.name_row = self.settings.get("mysql", "name_row")
            MySQL.date_row = self.settings.get("mysql", "date_row")
        except ConfigParser.NoSectionError:
            pass

    def sync_to_settings(self):
        self.settings.set("main", "firstday", self.firstday)
        self.settings.set("main", "lastday", self.lastday)
        self.settings.set("main", "databases", self.used_databases)
        self.settings.set("main", "csv_files", self.csv_files)
        if self.MySQL:
            if not self.settings.has_section("mysql"):
                self.settings.add_section("mysql")
            self.settings.set("mysql", "host", self.MySQL.host)
            self.settings.set("mysql", "port", self.MySQL.port)
            self.settings.set("mysql", "username", self.MySQL.username)
            self.settings.set("mysql", "password", self.MySQL.password)
            self.settings.set("mysql", "database", self.MySQL.database)
            self.settings.set("mysql", "table", self.MySQL.table)
            self.settings.set("mysql", "name_raw", self.MySQL.name_row)
            self.settings.set("mysql", "date_raw", self.MySQL.date_raw)

    def save(self):
        self.sync_to_settings()
        self.settings.write( file(os.environ['HOME']+"/.gbirthdayrc", "w") )

def main():
    global status_icon
    global showbdcheck
    global dlg
    global current_day
    dlg= None
    showbdcheck = 0

    # try to load settings
    global conf
    conf = Conf()

    # load data and fill AddressBook
    ab = AddressBook()
    start(ab, conf)

    # show status icon
    status_icon = StatusIcon(ab, conf)
    current_day = time.strftime("%d", time.localtime(time.time()))

    # check every 60 seconds for new day
    # TODO: update until end of day according to current clock settings?
    #       (might not the best idea if user changes current time)
    import gobject
    gobject.timeout_add(60000, status_icon.check_new_day)
    gtk.main()

if __name__ == '__main__':
    main()
