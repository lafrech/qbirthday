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
import time
import os

# own imports
from addressbook import *
from __init__ import databases, VERSION
from __init__ import MONTH_AT_PLACE, DAY_AT_PLACE

imageslocation = os.sep.join(__file__.split(os.sep)[:-1]) + "/pics/"


class StatusIcon():

    def __init__(self, ab, conf):
        '''create status icon'''
        self.icon = gtk.status_icon_new_from_file(imageslocation +
                            'birthday.png')
        self.ab = ab
        self.conf = conf
        self.showbd = None
        self.dlg = None
        list = ab.manage_bdays(conf)
        if len(list) > 0:
            self.icon.set_from_file(imageslocation + 'birthday.png')
        else:
            self.icon.set_from_file(imageslocation + 'nobirthday.png')
        self.icon.set_blinking(AddressBook.checktoday(ab))
        self.icon.connect('popup-menu', self.on_right_click)
        self.icon.connect('button_press_event', self.on_left_click, 20)

        def on_url(d, link, data):
            '''start default browser with gbirthday-website on click'''
            import subprocess
            subprocess.Popen(['sensible-browser',
                        'http://gbirthday.sourceforge.net/'])

        gtk.about_dialog_set_url_hook(on_url, None)

    def reload_gbirthday(self, text):
        '''reload gbirthday, reload data from databases'''
        self.ab.bdays = {}
        for db in databases:
            if (db.TYPE in self.conf.used_databases):
                db.parse(ab=self.ab, conf=self.conf)

        self.icon.set_blinking(AddressBook.checktoday(self.ab))
        list = self.ab.manage_bdays(self.conf)
        if len(list) > 0:
            self.icon.set_from_file(imageslocation + 'birthday.png')
        else:
            self.icon.set_from_file(imageslocation + 'nobirthday.png')

    def check_new_day(self):
        '''check for new birthday (check every 60 seconds)'''
        from __init__ import current_day

        new_day = time.strftime("%d", time.localtime(time.time()))
        if current_day != new_day:
            list = AddressBook.manage_bdays(self.ab, self.conf)
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

        if self.icon.get_blinking():
            blink_menu = gtk.ImageMenuItem(_('Stop blinking'))
            blink_img = gtk.Image()
            blink_img.set_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_MENU,)
            blink_menu.set_image(blink_img)
            blink_menu.show()
            blink_menu.connect_object('activate', self.stop_blinking,
                            'stop blinking')
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
        preferences_img.set_from_stock(gtk.STOCK_PREFERENCES,
                                gtk.ICON_SIZE_MENU,)
        preferences_menu.set_image(preferences_img)
        preferences_menu.show()
        preferences_menu.connect_object("activate", self.preferences_window,
                                "about")
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
        dlg = self.dlg
        dlg = gtk.AboutDialog()
        dlg.set_version(VERSION)
        dlg.set_comments(_('Birthday reminder'))
        dlg.set_name("GBirthday")
        image = gtk.gdk.pixbuf_new_from_file(imageslocation + 'gbirthday.png')
        dlg.set_logo(image)
        dlg.set_icon_from_file(imageslocation + 'birthday.png')
        dlg.set_copyright(u'Copyright \u00A9 2007 Alex Mallo, 2009 Andreas Bresser, 2009 Thomas Spura')
        dlg.set_license(
'''Licensed under the GNU General Public License Version 2

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
                _("There are no translations or the translator doesn't want to get credits for that."))
        dlg.set_website('http://gbirthday.sf.net/')

        def close(w, res):
            if res == gtk.RESPONSE_CANCEL:
                w.hide()
        dlg.connect('response', close)
        dlg.run()

    def finish_gbirthday(self, text):
        '''exit program'''
        if self.dlg is not None:
            self.dlg.destroy()
        gtk.main_quit()

    def on_right_click(self, icon, event_button, event_time):
        '''open menu window on right click'''
        self.make_menu(event_button, event_time, icon)

    def on_left_click(self, icon, event_button, event_time):
        '''close/open window with list of birthdays'''
        if event_button.button == 1: # left-click
            if event_button.type is not gtk.gdk._2BUTTON_PRESS:
                if not self.showbd:
                    self.openwindow()
                else:
                    self.closebdwindow('focus_out_event', self.closebdwindow, "")
            else:
                self.icon.set_blinking(False)
        else: # right-click
            # this is currently handled in on_right_click on its own
            pass


    def openwindow(self):
        '''open window that includes all birthdays'''
        self.showbd = self.gtk_get_top_window('', False, False)

        list = self.ab.manage_bdays(self.conf)

        box = gtk.HBox()
        box.set_border_width(5)
        box.show()
        frame = gtk.Frame(None)
        self.showbd.add(frame)
        table = gtk.Table(7, 6, False)
        box.pack_start(table, False, False, 0)
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
            label.set_markup('<b>\n    %s    \n</b>'
                        % _('No birthdays in specified period'))
        label.set_justify(gtk.JUSTIFY_RIGHT)
        event_box.add(label)
        label.show()
        style = label.get_style()
        event_box.modify_bg(gtk.STATE_NORMAL,
                    event_box.rc_get_style().bg[gtk.STATE_SELECTED])
        fila = fila + 1
        for cumple in list:
            image = gtk.Image()
            image.set_from_file(imageslocation + cumple[0])
            table.attach(image, 0, 1, fila, fila + 1)
            image.show()

            try:
                lang_month = unicode(time.strftime('%B',
                        (2000, int(cumple[5]), 1, 1, 0, 0, 0, 1, 0)))
            except:
                lang_month = str(cumple[5])
            if cumple[4] == 0:
                label = gtk.Label('<b>%s</b>' % lang_month)
                label.set_markup('<b>%s</b>' % lang_month)
            elif cumple[4] < 0:
                label = gtk.Label(lang_month)
                label.set_markup('<span foreground="grey">%s</span>'
                                    % lang_month)
            else:
                label = gtk.Label(lang_month)
            align = gtk.Alignment(0.0, 0.5, 0, 0)
            align.add(label)
            align.show()
            table.attach(align, MONTH_AT_PLACE,
                            MONTH_AT_PLACE + 1, fila, fila + 1)
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
            table.attach(align, DAY_AT_PLACE,
                            DAY_AT_PLACE + 1, fila, fila + 1)
            label.show()

            if cumple[4] == 0:
                label = gtk.Label("<b>" + cumple[2] + "</b>")
                label.set_markup("<b>" + cumple[2] + "</b>")
            elif cumple[4] < 0:
                label = gtk.Label(cumple[2])
                label.set_markup("<span foreground='grey'>" + cumple[2]
                                    + "</span>")
            else:
                label = gtk.Label(cumple[2])
            align = gtk.Alignment(0.0, 0.5, 0, 0)
            align.add(label)
            table.attach(align, 3, 4, fila, fila + 1)
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
            table.attach(align, 4, 5, fila, fila + 1)
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
            table.attach(align, 5, 6, fila, fila + 1)
            label.show()
            fila = fila + 1

        table.show()
        frame.show()
        self.showbd.show()
        self.showbd.connect('focus_out_event', self.closebdwindow, "text")

    def stop_blinking(self, text):
        '''stop blinking (only if icon blinks)'''
        self.icon.set_blinking(False)

    def preferences_window(self, textcw=None):
        '''show settings window'''
        global preferences
        preferences = self.gtk_get_top_window(_('Preferences'))

        box = gtk.VBox(False, 0)
        preferences.add(box)

        table = gtk.Table(3, 2, False)
        table.set_col_spacings(10)
        table.set_row_spacings(10)

        label = gtk.Label(_('Past birthdays'))
        table.attach(label, 0, 1, 0, 1)
        label.show()

        label = gtk.Label(_('Next birthdays'))
        table.attach(label, 0, 1, 1, 2)
        label.show()

        label = gtk.Label(_('Database'))
        table.attach(label, 0, 1, 2, 3)
        label.show()

        def get_new_preferences(uno, option, spin):
            '''set value for settings by spinner'''
            spin.update()
            if option == "firstday":
                self.conf.firstday = spin.get_value_as_int()
            elif option == "lastday":
                self.conf.lastday = spin.get_value_as_int()
            else:
                show_error_msg(_('Internal Error: Option %s not valid.')
                                % option)

        past = gtk.Adjustment(int(self.conf.firstday), lower=-30,
                    upper=0, step_incr=-1, page_incr=0, page_size=0)
        spin = gtk.SpinButton(past, climb_rate=0.0, digits=0)
        spin.connect("value-changed", get_new_preferences, "firstday", spin)
        table.attach(spin, 1, 2, 0, 1)
        spin.show()

        next = gtk.Adjustment(int(self.conf.lastday), lower=0, upper=90,
                    step_incr=1, page_incr=0, page_size=0)
        spin = gtk.SpinButton(next, climb_rate=0.0, digits=0)
        spin.connect("value-changed", get_new_preferences, "lastday", spin)
        table.attach(spin, 1, 2, 1, 2)
        spin.show()

        def db_select(widget, db):
            '''callback for checkboxes and update used_databases'''
            if (widget.get_active()):
                if not db.TYPE in self.conf.used_databases:
                    self.conf.used_databases.append(db.TYPE)
                    db.activate()
            else:
                if db.TYPE in self.conf.used_databases:
                    self.conf.used_databases.remove(db.TYPE)
                    db.deactivate()

        def preferences_db(widget, db):
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
            if db.TYPE in self.conf.used_databases:
                chkDB.set_active(True)
            chkDB.connect("toggled", db_select, db)
            hbox.pack_start(chkDB, False, False, 0)
            if db.HAS_CONFIG:
                button = gtk.Button(_('Configure'))
                button.connect("clicked", preferences_db, db)
                button.show()
                hbox.pack_start(button, False, False, 1)
            hbox.show()
            chkDB.show()
        table.attach(vbox, 1, 2, 2, 3)
        vbox.show()

        box.pack_start(table, True, True, 8)
        table.show()

        def finish_preferences(uno, texto):
            '''save settings after user clicked save and exit'''
            self.save_config()
            preferences.destroy()
        button = gtk.Button(_('Save & Close'))
        box.pack_start(button, False, False, 2)
        button.connect("clicked", finish_preferences, None)
        button.show()
        box.show()
        preferences.set_border_width(5)
        preferences.show()

    def save_config(self):
        '''save config in file'''
        for db in databases:
            db.update(self.conf)
        self.conf.save()

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

        fileButton = gtk.Button(
            _('Add multiple birthdays from file or database'))
        fileButton.connect("clicked", self.add_from_file, add_window)
        box.pack_start(fileButton)
        fileButton.show()

        box.show()
        add_window.set_border_width(5)
        add_window.show()
        '''

    def add_single_manual(self, widget, window):
        if window is not None:
            window.destroy()
        add_window = self.gtk_get_top_window(_('Add'))

        box = gtk.VBox(False, 0)
        add_window.add(box)

        table = gtk.Table(3, 2, False)
        table.set_col_spacings(10)
        table.set_row_spacings(10)

        label = gtk.Label(_('Name'))
        table.attach(label, 0, 1, 0, 1)
        label.show()

        label = gtk.Label(_('Birthday'))
        table.attach(label, 0, 1, 1, 2)
        label.show()

        label = gtk.Label(_('Save to file/database'))
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
        table.attach(combobox, 1, 2, 2, 3)

        box.pack_start(table, True, True, 8)
        table.show()

        button = gtk.Button(_('Save & Close'))
        box.pack_start(button, False, False, 2)
        button.connect("clicked", self.finish_add, combobox, name, date,
                        add_window)
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


        label = gtk.Label('select file/database')
        table.attach(label, 0, 1, 0, 1)
        label.show()

        liststore = gtk.ListStore(str)
        db_combo = gtk.combo_box_new_text()
        for db in databases:
            db_combo.append_text(db.TITLE)
        db_combo.set_active(0)
        db_combo.show()
        table.attach(db_combo, 1, 2, 0, 1)

        label = gtk.Label(_('Import Settings'))
        table.attach(label, 0, 1, 1, 2)
        label.show()

        label = gtk.Label('not needed')
        table.attach(label, 1, 2, 1, 2)
        label.show()

        label = gtk.Label(_('Database'))
        table.attach(label, 0, 1, 2, 3)
        label.show()

        liststore = gtk.ListStore(str)
        combobox = gtk.combo_box_new_text()
        for db in databases:
            if db.CAN_SAVE:
                combobox.append_text(db.TITLE)
        combobox.set_active(0)
        combobox.show()
        table.attach(combobox, 1, 2, 2, 3)

        box.pack_start(table, True, True, 8)
        table.show()

        label = gtk.Label(_('Export Settings'))
        table.attach(label, 0, 1, 3, 4)
        label.show()

        label = gtk.Label('not needed')
        table.attach(label, 1, 2, 3, 4)
        label.show()

        button = gtk.Button(_('Save & Close'))
        box.pack_start(button, False, False, 2)
        button.connect("clicked", self.finish_add, combobox, db_combo, '',
                        add_window)
        button.show()

        box.show()

        box.show()
        add_window.set_border_width(5)
        add_window.show()

    def closebdwindow(self, uno, dos, textcw):
        '''close about window'''
        if self.showbd:
            self.showbd.destroy()
            self.showbd = None

    ### gtk helper functions ###
    @staticmethod
    def gtk_get_top_window(title, decorated=True, center=True):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_decorated(decorated)
        if center:
            window.set_position(gtk.WIN_POS_CENTER)
        else:
            window.set_position(gtk.WIN_POS_MOUSE)
        window.set_title(title)
        window.set_icon_from_file(imageslocation + 'birthday.png')
        return window
