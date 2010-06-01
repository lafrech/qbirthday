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
'''StatusIcon module'''
import gtk
import time
import os

# own imports
from .__init__ import VERSION
from .__init__ import MONTH_AT_PLACE, DAY_AT_PLACE
from .__init__ import CURRENT_DAY

IMAGESLOCATION = os.sep.join(__file__.split(os.sep)[:-1]) + "/pics/"


class StatusIcon():
    '''Class to show status icon'''

    def __init__(self, addressbook, conf):
        '''create status icon'''
        self.icon = gtk.status_icon_new_from_file(IMAGESLOCATION +
                            'birthday.png')
        self.addressbook = addressbook
        self.conf = conf
        self.showbd = None
        self.dlg = None
        self._reload_set_icon()
        self.icon.connect('popup-menu', self.on_right_click)
        self.icon.connect('button_press_event', self.on_left_click)

        def on_url(dialog, link):
            '''start default browser with gbirthday-website on click'''
            import webbrowser
            webbrowser.open(link)

        gtk.about_dialog_set_url_hook(on_url)

    def reload_gbirthday(self, dummy):
        '''reload gbirthday, reload data from databases'''
        self.addressbook.reload()
        self._reload_set_icon()

    def check_new_day(self):
        '''check for new birthday (check every 60 seconds)'''
        global CURRENT_DAY # TODO: import from __init__ here, fails whyever
        new_day = time.strftime("%d", time.localtime(time.time()))
        if CURRENT_DAY != new_day:
            CURRENT_DAY = new_day
            self._reload_set_icon()
        return True

    def _reload_set_icon(self):
        '''Check, if there is a birthday and set icon and notify accordingly.'''
        # reload addressbook
        self.addressbook.reload()
        # check if a birthday is in specified period
        if self.addressbook.bdays_in_period():
            self.icon.set_from_file(IMAGESLOCATION + 'birthday.png')
        else:
            self.icon.set_from_file(IMAGESLOCATION + 'nobirthday.png')

        # check if birthday today
        if self.addressbook.check_day(0):
            self.icon.set_from_file(IMAGESLOCATION + 'birthdayred.png')

        # show notification of birthdays in the future
        try:
            import pynotify
            if pynotify.init("gbirthday"):
                for day in range(self.conf.lastday+1):
                    noty_string = None
                    if day == 0:
                        noty_string = _("Birthday today:")
                    elif day <= self.conf.notify_future_bdays:
                        if day == 1:
                            noty_string = _("Birthday tomorrow:")
                        else:
                            noty_string = _("Birthday in %s Days:") % day
                    else:
                        continue
                    for name in self.addressbook.check_day(day):
                        notify = pynotify.Notification(
                                        noty_string, name)
                        notify.show()
        except ImportError:
            pass

    def make_menu(self, event_button, event_time, icon):
        '''create menu window'''
        menu = gtk.Menu()
        new_menu = gtk.ImageMenuItem(_('Reload'))
        new_img = gtk.Image()
        new_img.set_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_MENU,)
        new_menu.set_image(new_img)
        new_menu.show()
        new_menu.connect_object('activate', self.reload_gbirthday, None)
        menu.append(new_menu)

        new_menu = gtk.ImageMenuItem(_('Add'))
        new_img = gtk.Image()
        new_img.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_MENU,)
        new_menu.set_image(new_img)
        new_menu.show()
        new_menu.connect_object("activate", self.add, "add birthday")
        menu.append(new_menu)

        new_menu = gtk.ImageMenuItem(_('Preferences'))
        new_img = gtk.Image()
        new_img.set_from_stock(gtk.STOCK_PREFERENCES,
                                gtk.ICON_SIZE_MENU,)
        new_menu.set_image(new_img)
        new_menu.show()
        new_menu.connect_object("activate", self.preferences_window,
                                "about")
        menu.append(new_menu)

        new_menu = gtk.ImageMenuItem(_('About'))
        new_img = gtk.Image()
        new_img.set_from_stock(gtk.STOCK_ABOUT, gtk.ICON_SIZE_MENU,)
        new_menu.set_image(new_img)
        new_menu.show()
        new_menu.connect_object("activate", self.create_dialog, None)
        menu.append(new_menu)

        new_menu = gtk.ImageMenuItem(_('Quit'))
        new_img = gtk.Image()
        new_img.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU,)
        new_menu.set_image(new_img)
        new_menu.show()
        new_menu.connect_object("activate", self.finish_gbirthday, "file.quit")
        menu.append(new_menu)
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
        image = gtk.gdk.pixbuf_new_from_file(IMAGESLOCATION + 'gbirthday.png')
        dlg.set_logo(image)
        dlg.set_icon_from_file(IMAGESLOCATION + 'birthday.png')
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
        dlg.set_website('http://gbirthday.sourceforge.net/')

        def close(w, res):
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

    def on_left_click(self, icon, event_button):
        '''close/open window with list of birthdays'''
        # button == 1 -> left click
        if event_button.button == 1:
            if not self.showbd:
                self.openwindow()
            else:
                self.showbd.destroy()
                self.showbd = None

    def openwindow(self):
        '''open window that includes all birthdays'''
        import datetime
        self.showbd = self.gtk_get_top_window('', False, False)

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
        if self.addressbook.bdays_in_period():
            label.set_markup('<b>%s</b>' % _('Birthdays'))
        else:
            label.set_markup('<b>\n    %s    \n</b>'
                        % _('No birthdays in specified period'))
        label.set_justify(gtk.JUSTIFY_RIGHT)
        event_box.add(label)
        label.show()
        event_box.modify_bg(gtk.STATE_NORMAL,
                    event_box.rc_get_style().bg[gtk.STATE_SELECTED])
        fila = fila + 1

        def add_to_list(delta_day, name, fila):
            # search for birthdate
            for date, names in self.addressbook.bdays.items():
                if name in names:
                    birthdate = date
            birthdate = datetime.date(int(birthdate[:4]),
                                        int(birthdate[5:7]),
                                        int(birthdate[8:10]))

            try:
                lang_month = str(time.strftime('%B',
                        (2000, birthdate.month, 1, 1, 0, 0, 0, 1, 0)))
            except:
                lang_month = birthdate.month
            image = gtk.Image()
            day = birthdate.day
            years = _('%s Years') % (datetime.date.today().year -
                                        birthdate.year)
            # birthday today
            if delta_day == 0:
                image.set_from_file(IMAGESLOCATION + 'birthdaytoday.png')
                label_month = gtk.Label('<b>%s</b>' % lang_month)
                label_month.set_markup('<b>%s</b>' % lang_month)
                label_day = gtk.Label("<b>%s</b>" % day)
                label_day.set_markup("<b>%s</b>" % day)
                label_name = gtk.Label("<b>%s</b>" % name)
                label_name.set_markup("<b>%s</b>" % name)
                label_when = gtk.Label(_('Today'))
                label_when.set_markup('<b>%s</b>' % _('Today'))
                label_years = gtk.Label('<b>%s</b>' % years)
                label_years.set_markup('<b>%s</b>' % years)
            elif delta_day < 0:
                image.set_from_file(IMAGESLOCATION + 'birthdaylost.png')
                label_month = gtk.Label(lang_month)
                label_month.set_markup('<span foreground="grey">%s</span>'
                                    % lang_month)
                label_day = gtk.Label(day)
                label_day.set_markup('<span foreground="grey">%s</span>'
                                    % day)
                label_name = gtk.Label(name)
                label_name.set_markup("<span foreground='grey'>%s</span>"
                                    % name)
                label_years = gtk.Label(years)
                label_years.set_markup('<span foreground="grey">%s</span>' % years)
                if delta_day == -1:
                    label_when = gtk.Label(_('Yesterday'))
                    label_when.set_markup(
                        '<span foreground="grey">%s</span>' %
                                _('Yesterday'))
                else:
                    ago = (_('%s Days ago') % str(delta_day * -1))
                    label_when = gtk.Label(ago)
                    label_when.set_markup(
                            '<span foreground="grey">%s</span>' % ago)
            else:
                image.set_from_file(IMAGESLOCATION + 'birthdaynext.png')
                label_month = gtk.Label(lang_month)
                label_day = gtk.Label(day)
                label_name = gtk.Label(name)
                label_years = gtk.Label(years)
                if delta_day == 1:
                    label_when = gtk.Label(_('Tomorrow'))
                else:
                    label_when = gtk.Label(_('%s Days') % delta_day)

            table.attach(image, 0, 1, fila, fila + 1)
            image.show()

            label_month.show()
            label_day.show()
            label_name.show()
            label_when.show()
            label_years.show()

            align_month = gtk.Alignment(0.0, 0.5, 0, 0)
            align_month.add(label_month)
            align_month.show()
            align_day = gtk.Alignment(1.0, 0.5, 0, 0)
            align_day.add(label_day)
            align_day.show()
            align_name = gtk.Alignment(0.0, 0.5, 0, 0)
            align_name.add(label_name)
            align_name.show()
            align_when = gtk.Alignment(0.0, 0.5, 0, 0)
            align_when.add(label_when)
            align_when.show()
            align_years = gtk.Alignment(1.0, 0.5, 0, 0)
            align_years.add(label_years)
            align_years.show()

            table.attach(align_day, DAY_AT_PLACE,
                            DAY_AT_PLACE + 1, fila, fila + 1)
            table.attach(align_month, MONTH_AT_PLACE,
                            MONTH_AT_PLACE + 1, fila, fila + 1)
            table.attach(align_name, 3, 4, fila, fila + 1)
            table.attach(align_when, 4, 5, fila, fila + 1)
            table.attach(align_years, 5, 6, fila, fila + 1)

        for delta_day in range(self.conf.firstday, self.conf.lastday + 1):
            for name in self.addressbook.check_day(delta_day):
                add_to_list(delta_day, name, fila)
                fila = fila + 1

        table.show()
        frame.show()
        self.showbd.show()
        self.showbd.connect('focus_out_event', self.closebdwindow)

    def preferences_window(self, textcw=None):
        '''show settings window'''
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

        label = gtk.Label(_('Notification: Future birthdays'))
        table.attach(label, 0, 1, 2, 3)
        label.show()

        label = gtk.Label(_('Database'))
        table.attach(label, 0, 1, 3, 4)
        label.show()

        def get_new_preferences(uno, option, spin):
            '''set value for settings by spinner'''
            spin.update()
            if option == "firstday":
                self.conf.firstday = spin.get_value_as_int()
            elif option == "lastday":
                self.conf.lastday = spin.get_value_as_int()
            elif option == "notify_future":
                self.conf.notify_future_bdays = spin.get_value_as_int()
            else:
                pass

        adjustment = gtk.Adjustment(int(self.conf.firstday), lower=-30,
                    upper=0, step_incr=-1, page_incr=0, page_size=0)
        spin = gtk.SpinButton(adjustment, climb_rate=0.0, digits=0)
        spin.connect("value-changed", get_new_preferences, "firstday", spin)
        table.attach(spin, 1, 2, 0, 1)
        spin.show()

        adjustment = gtk.Adjustment(int(self.conf.lastday), lower=0, upper=90,
                    step_incr=1, page_incr=0, page_size=0)
        spin = gtk.SpinButton(adjustment, climb_rate=0.0, digits=0)
        spin.connect("value-changed", get_new_preferences, "lastday", spin)
        table.attach(spin, 1, 2, 1, 2)
        spin.show()

        adjustment = gtk.Adjustment(int(self.conf.notify_future_bdays),
                    lower=0, upper=int(self.conf.lastday),
                    step_incr=1, page_incr=0, page_size=0)
        spin = gtk.SpinButton(adjustment, climb_rate=0.0, digits=0)
        spin.connect("value-changed", get_new_preferences, "notify_future",
                    spin)
        table.attach(spin, 1, 2, 2, 3)
        spin.show()

        def db_select(widget, db):
            '''callback for checkboxes and update used_databases'''
            if (widget.get_active()):
                if not db.__class__.__name__ in self.conf.used_databases:
                    self.conf.used_databases.append(db.__class__.__name__)
                    db.activate()
            else:
                if db.__class__.__name__ in self.conf.used_databases:
                    self.conf.used_databases.remove(db.__class__.__name__)
                    db.deactivate()

        def preferences_db(widget, db):
            pref_db = self.gtk_get_top_window(_('Database Configuration'))

            db.create_config(pref_db)
            pref_db.set_modal(True)
            pref_db.show()

        vbox = gtk.VBox(False, 10)
        for db in self.addressbook.supported_databases:
            hbox = gtk.HBox(False, 2)
            vbox.pack_start(hbox, False, False, 3)

            chkDB = gtk.CheckButton(db.TITLE)
            if db.__class__.__name__ in self.conf.used_databases:
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
        table.attach(vbox, 1, 2, 3, 4)
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
        for database in self.addressbook.supported_databases:
            database.update()
        self.conf.save()
        self.addressbook.reload()
        self._reload_set_icon()

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
        '''Add birthday dialog.'''
        import datetime
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

        calendar = gtk.Calendar()
        table.attach(calendar, 1, 2, 1, 2)
        calendar.show()

        combobox = gtk.combo_box_new_text()
        for db in self.addressbook.supported_databases:
            if db.CAN_SAVE:
                combobox.append_text(db.TITLE)
        combobox.set_active(0)
        combobox.show()
        table.attach(combobox, 1, 2, 2, 3)

        box.pack_start(table, True, True, 8)
        table.show()

        def finish_add(uno, combo, name, calendar, window):
            '''save new added person'''
            for db in self.addressbook.supported_databases:
                if db.TITLE == combo.get_active_text():
                    calend = list(calendar.get_date())
                    calend[1] += 1
                    db.add(name.get_text(), datetime.date(*calend))
            window.destroy()

        button = gtk.Button(_('Save & Close'))
        box.pack_start(button, False, False, 2)
        button.connect("clicked", finish_add, combobox, name, calendar,
                        add_window)
        button.show()

        box.show()
        add_window.set_border_width(5)
        add_window.show()

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

        db_combo = gtk.combo_box_new_text()
        for db in self.addressbook.supported_databases:
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

        combobox = gtk.combo_box_new_text()
        for db in self.addressbook.supported_databases:
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

        def finish_add(uno, combo, name, calend, window):
            '''save new added person'''
            import datetime
            for db in self.addressbook.supported_databases:
                if db.TITLE == combo.get_active_text():
                    calend = list(calend.get_date())
                    calend[1] += 1
                    db.add(name.get_text(), datetime.date(*calend))
            window.destroy()
        button = gtk.Button(_('Save & Close'))
        box.pack_start(button, False, False, 2)
        button.connect("clicked", finish_add, combobox, db_combo, '',
                        add_window)
        button.show()

        box.show()

        box.show()
        add_window.set_border_width(5)
        add_window.show()

    def closebdwindow(self, uno, dos):
        '''close about window'''
        if self.showbd:
            self.showbd.destroy()
            self.showbd = None

    ### gtk helper functions ###
    @staticmethod
    def gtk_get_top_window(title, decorated=True, center=True):
        '''Get gtk top window.'''
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_decorated(decorated)
        if center:
            window.set_position(gtk.WIN_POS_CENTER)
        else:
            window.set_position(gtk.WIN_POS_MOUSE)
        window.set_title(title)
        window.set_icon_from_file(IMAGESLOCATION + 'birthday.png')
        return window

if __name__ == "__main__":
    _ = lambda x: x
