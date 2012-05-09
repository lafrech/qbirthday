# -*- coding: UTF-8 -*-
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
from .__init__ import DATABASES
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

    def reload_gbirthday(self, *args):
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
        new_menu = gtk.ImageMenuItem(gtk.STOCK_REFRESH)
        new_menu.show()
        new_menu.connect_object('activate', self.reload_gbirthday, None)
        menu.append(new_menu)

        new_menu = gtk.ImageMenuItem(gtk.STOCK_ADD)
        new_menu.show()
        new_menu.connect_object("activate", self.add, "add birthday")
        menu.append(new_menu)

        new_menu = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        new_menu.show()
        new_menu.connect_object("activate", self.preferences_window,
                                "about")
        menu.append(new_menu)

        new_menu = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
        new_menu.show()
        new_menu.connect_object("activate", self.create_dialog, None)
        menu.append(new_menu)

        new_menu = gtk.ImageMenuItem(gtk.STOCK_QUIT)
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
                'Robert Wildburger <r.wildburger@gmx.at>',
                'Jérôme Lafréchoux <jerome@jolimont.fr>'
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
        self.showbd = self.gtk_get_top_window('', False, False, True)

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

        table = gtk.Table(5, 2, False)
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

        label = gtk.Label(_('ICS Calendar export'))
        table.attach(label, 0, 1, 3, 4)
        label.show()

        label = gtk.Label(_('Database'))
        table.attach(label, 0, 1, 5, 6)
        label.show()

        adjustment = gtk.Adjustment(int(self.conf.firstday), lower=-30,
                    upper=0, step_incr=-1, page_incr=0, page_size=0)
        spin_firstday = gtk.SpinButton(adjustment, climb_rate=0.0, digits=0)
        table.attach(spin_firstday, 1, 2, 0, 1)
        spin_firstday.show()

        adjustment = gtk.Adjustment(int(self.conf.lastday), lower=0, upper=90,
                    step_incr=1, page_incr=0, page_size=0)
        spin_lastday = gtk.SpinButton(adjustment, climb_rate=0.0, digits=0)
        table.attach(spin_lastday, 1, 2, 1, 2)
        spin_lastday.show()

        adjustment = gtk.Adjustment(int(self.conf.notify_future_bdays),
                    lower=0, upper=int(self.conf.lastday),
                    step_incr=1, page_incr=0, page_size=0)
        spin_notify_future_bdays = gtk.SpinButton(adjustment, climb_rate=0.0, 
                                                  digits=0)
        table.attach(spin_notify_future_bdays, 1, 2, 2, 3)
        spin_notify_future_bdays.show()

        # ICS export checkbox
        def ics_export_chk_cb(chk, button):
            '''Enable / disable ICS export setting widgets'''
            button.set_sensitive(chk.get_active())
        chk_export = gtk.CheckButton()
        chk_export.set_active(self.conf.ics_export)
        button = gtk.Button(stock=gtk.STOCK_PREFERENCES)
        button.set_sensitive(self.conf.ics_export)
        chk_export.connect("clicked", ics_export_chk_cb, button)
        button.connect("clicked", self.ics_export_config)
        hbox = gtk.HBox(False, 2)
        hbox.pack_start(chk_export, False, False, 0)
        hbox.pack_start(button, False, False, 1)
        table.attach(hbox, 1, 2, 3, 4)
        button.show()
        chk_export.show()
        hbox.show()

        # Separator
        hsep = gtk.HSeparator()
        table.attach(hsep, 0, 2, 4, 5)
        hsep.show()

        # Databases
        def db_select(widget, db):
            '''Enable / disable DB setting widgets'''
            self.db_buttons[db].set_sensitive(widget.get_active())

        def preferences_db(widget, db):
            '''Create and display DB config window'''
            pref_db = self.gtk_get_top_window(db.__class__.__name__ + ' ' + \
                                              _('Database Configuration'))

            vbox = gtk.VBox(False, 5)
            
            db.create_config(vbox, self.conf)

            # Cancel / apply / ok
            def preferences_cancel_cb(*args):
                '''Destroy windows (discard modifications)'''
                pref_db.destroy()
            
            def preferences_apply_cb(*args):
                '''Save modifications'''
                db.save_config(self.conf)
                self.conf.save()
    
            def preferences_ok_cb(*args):
                '''Save modifications and destroy window'''
                preferences_apply_cb()
                pref_db.destroy()
    
            hbox = gtk.HButtonBox()
            hbox.set_spacing(5)
            hbox.set_layout(gtk.BUTTONBOX_END)
            button = gtk.Button(stock=gtk.STOCK_APPLY)
            hbox.add(button)
            button.connect("clicked", preferences_apply_cb)
            button.show()
            button = gtk.Button(stock=gtk.STOCK_CANCEL)
            hbox.add(button)
            button.connect("clicked", preferences_cancel_cb)
            button.show()
            button = gtk.Button(stock=gtk.STOCK_OK)
            hbox.add(button)
            button.connect("clicked", preferences_ok_cb)
            button.show()
            vbox.pack_start(hbox, False, False, 0)
            hbox.show()

            vbox.show()
            pref_db.add(vbox)

            pref_db.set_modal(True)
            pref_db.show()

        vbox = gtk.VBox(False, 10)

        self.db_chk = {}
        self.db_buttons = {}
        for db in DATABASES:
            hbox = gtk.HBox(False, 2)
            vbox.pack_start(hbox, False, False, 0)

            self.db_chk[db] = gtk.CheckButton(db.TITLE)
            hbox.pack_start(self.db_chk[db], False, False, 0)
            if db.HAS_CONFIG:
                self.db_buttons[db] = gtk.Button(stock=gtk.STOCK_PREFERENCES)
                self.db_buttons[db].connect("clicked", preferences_db, db)
                self.db_buttons[db].show()
                hbox.pack_start(self.db_buttons[db], False, False, 1)
                self.db_buttons[db].set_sensitive(self.db_chk[db].get_active())
                self.db_chk[db].connect("toggled", db_select, db)
            if db.__class__.__name__ in self.conf.used_databases:
                self.db_chk[db].set_active(True)
            hbox.show()
            self.db_chk[db].show()
        table.attach(vbox, 1, 2, 5, 6)
        vbox.show()

        box.pack_start(table, True, True, 8)
        table.show()

        # Cancel / apply / ok
        def preferences_cancel_cb(*args):
            '''Destroy windows (discard modifications)'''
            preferences.destroy()
        
        def preferences_apply_cb(*args):
            '''Save modifications'''
            self.conf.firstday = spin_firstday.get_value_as_int()
            self.conf.lastday = spin_lastday.get_value_as_int()
            self.conf.notify_future_bdays = \
                spin_notify_future_bdays.get_value_as_int()
            self.conf.ics_export = chk_export.get_active()
            for db in DATABASES:
                if self.db_chk[db].get_active():
                    if not db.__class__.__name__ in self.conf.used_databases:
                        self.conf.used_databases.append(db.__class__.__name__)
                else:
                    if db.__class__.__name__ in self.conf.used_databases:
                        self.conf.used_databases.remove(db.__class__.__name__)
            self.conf.save()

        def preferences_ok_cb(*args):
            '''Save modifications and destroy window'''
            preferences_apply_cb()
            preferences.destroy()

        hbox = gtk.HButtonBox()
        hbox.set_spacing(5)
        hbox.set_layout(gtk.BUTTONBOX_END)
        button = gtk.Button(stock=gtk.STOCK_APPLY)
        hbox.add(button)
        button.connect("clicked", preferences_apply_cb)
        button.show()
        button = gtk.Button(stock=gtk.STOCK_CANCEL)
        hbox.add(button)
        button.connect("clicked", preferences_cancel_cb)
        button.show()
        button = gtk.Button(stock=gtk.STOCK_OK)
        hbox.add(button)
        button.connect("clicked", preferences_ok_cb)
        button.show()
        vbox.pack_start(hbox, False, False, 0)
        hbox.show()

        box.show()
        preferences.set_border_width(5)
        preferences.show()

    def ics_export_config(self, widget):
        '''Display ICS export settings window'''
        window = self.gtk_get_top_window(_('ICS Export configuration'))
        window.set_border_width(10)

        vbox = gtk.VBox(False, 10)

        # File path
        def set_filepath(widget, entry):
            '''File selection dialog'''
            chooser = gtk.FileChooserDialog(title='ICS Export file',
                                            action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                            buttons=(gtk.STOCK_CANCEL,
                                                     gtk.RESPONSE_CANCEL,
                                                     gtk.STOCK_OPEN,
                                                     gtk.RESPONSE_OK))
            
            # Default to current file
            (folder, file_name) = os.path.split(self.conf.ics_filepath)
            chooser.set_current_folder(folder)
            chooser.set_current_name(file_name)

            response = chooser.run()
            if response == gtk.RESPONSE_OK:
                entry.set_text(chooser.get_filename())
            chooser.destroy()

        hbox = gtk.HBox()

        label = gtk.Label(_("Export birthday list in iCalendar file:"))
        label.show()
        label.set_alignment(0, 0.5)
        vbox.pack_start(label, False, False, 0)


        filename = gtk.Entry()
        filename.set_text(self.conf.ics_filepath)
        filename.show()
        hbox.pack_start(filename, True, True, 0)
        button = gtk.Button(_("Browse"))
        new_img = gtk.Image()
        new_img.set_from_stock(gtk.STOCK_DIRECTORY, gtk.ICON_SIZE_BUTTON,)
        button.set_image(new_img)
        button.show()
        hbox.pack_start(button, False, False, 5)
        button.connect("clicked", set_filepath, filename)

        hbox.show()

        vbox.pack_start(hbox, False, False, 0)

        # ICS alarm
        def ics_alarm_chk_cb(chk):
            '''Enable / disable ICS alarm setting widgets'''
            self.ics_alarm_days_spin.set_sensitive(chk.get_active())
            self.ics_alarm_days_label.set_sensitive(chk.get_active())
            self.ics_alarm_custom_properties_label.set_sensitive( \
                chk.get_active())
            self.ics_alarm_custom_properties_scroll.set_sensitive( \
                chk.get_active())

        chk = gtk.CheckButton(_('Set alarms'))
        chk.set_active(self.conf.ics_alarm)
        chk.connect("clicked", ics_alarm_chk_cb)
        chk.show()
        vbox.pack_start(chk, False, False, 0)
        
        # ICS nb of days between alarm and birthday
        hbox = gtk.HBox()
        adjustment = gtk.Adjustment(int(self.conf.ics_alarm_days), lower=0,
                    upper=60, step_incr=1, page_incr=0, page_size=0)
        self.ics_alarm_days_spin = gtk.SpinButton(adjustment, climb_rate=0.0,
                                                  digits=0)
        self.ics_alarm_days_label = gtk.Label(_('days before each birthday'))
        self.ics_alarm_days_spin.set_sensitive(self.conf.ics_alarm)
        self.ics_alarm_days_label.set_sensitive(self.conf.ics_alarm)
        hbox.pack_start(self.ics_alarm_days_spin, False, False, 0)
        hbox.pack_start(self.ics_alarm_days_label, False, False, 0)
        self.ics_alarm_days_spin.show()
        self.ics_alarm_days_label.show()
        hbox.show()
        vbox.pack_start(hbox, False, False, 0)
        
        # Separator
        hsep = gtk.HSeparator()
        vbox.pack_start(hsep, False, False, 0)
        hsep.show()
        
        # Custom properties
        custom_properties_tooltip_str = ( \
            _("Use this if you know what you're doing. See RFC 2445."))

        # ICS VEVENT custom properties
        self.ics_custom_properties_label = \
            gtk.Label(_('Custom ICS properties for VEVENT'))
        self.ics_custom_properties_label.set_tooltip_text( \
            custom_properties_tooltip_str)
        self.ics_custom_properties_label.set_alignment(0, 0)
        vbox.pack_start(self.ics_custom_properties_label, False, False, 0)
        self.ics_custom_properties_label.show()
        textbuffer_event = gtk.TextBuffer()
        textbuffer_event.set_text(self.conf.ics_custom_properties)
        textview = gtk.TextView(buffer=textbuffer_event)
        textview.set_editable(True)
        textview.set_tooltip_text( \
            custom_properties_tooltip_str)
        self.ics_custom_properties_scroll = gtk.ScrolledWindow()
        self.ics_custom_properties_scroll.add_with_viewport(textview)
        self.ics_custom_properties_scroll.set_policy(gtk.POLICY_AUTOMATIC,
                                                     gtk.POLICY_AUTOMATIC)
        vbox.pack_start(self.ics_custom_properties_scroll, False, False, 0)
        self.ics_custom_properties_scroll.show()
        textview.show()

        # ICS VALARM custom properties
        self.ics_alarm_custom_properties_label = \
            gtk.Label(_('Custom ICS properties for VALARM'))
        self.ics_alarm_custom_properties_label.set_tooltip_text( \
            custom_properties_tooltip_str)
        self.ics_alarm_custom_properties_label.set_alignment(0, 0)
        self.ics_alarm_custom_properties_label.set_sensitive( \
            self.conf.ics_alarm)
        vbox.pack_start(self.ics_alarm_custom_properties_label,
                        False, False, 0)
        self.ics_alarm_custom_properties_label.show()
        textbuffer_alarm = gtk.TextBuffer()
        textbuffer_alarm.set_text(self.conf.ics_alarm_custom_properties)
        textview = gtk.TextView(buffer=textbuffer_alarm)
        textview.set_editable(True)
        textview.set_tooltip_text( \
            custom_properties_tooltip_str)
        self.ics_alarm_custom_properties_scroll = gtk.ScrolledWindow()
        self.ics_alarm_custom_properties_scroll.add_with_viewport(textview)
        self.ics_alarm_custom_properties_scroll.set_policy(gtk.POLICY_AUTOMATIC,
                                                           gtk.POLICY_AUTOMATIC)
        self.ics_alarm_custom_properties_scroll.set_sensitive( \
            self.conf.ics_alarm)
        vbox.pack_start(self.ics_alarm_custom_properties_scroll,
                        False, False, 0)
        self.ics_alarm_custom_properties_scroll.show()
        textview.show()

        # Cancel / apply / ok
        def ics_export_config_cancel_cb(*args):
            '''Destroy windows (discard modifications)'''
            window.destroy()
        
        def ics_export_config_apply_cb(*args):
            '''Save modifications'''
            self.conf.ics_filepath = filename.get_text()
            self.conf.ics_alarm = chk.get_active()
            self.conf.ics_alarm_days = \
                str(self.ics_alarm_days_spin.get_value_as_int())
            self.conf.ics_custom_properties = textbuffer_event.get_text( \
                textbuffer_event.get_start_iter(),
                textbuffer_event.get_end_iter())
            self.conf.ics_alarm_custom_properties = textbuffer_alarm.get_text( \
                textbuffer_alarm.get_start_iter(),
                textbuffer_alarm.get_end_iter())
            
            self.addressbook.export()

        def ics_export_config_ok_cb(*args):
            '''Save modifications and destroy window'''
            ics_export_config_apply_cb()
            window.destroy()

        hbox = gtk.HButtonBox()
        hbox.set_spacing(5)
        hbox.set_layout(gtk.BUTTONBOX_END)
        button = gtk.Button(stock=gtk.STOCK_APPLY)
        hbox.add(button)
        button.connect("clicked", ics_export_config_apply_cb)
        button.show()
        button = gtk.Button(stock=gtk.STOCK_CANCEL)
        hbox.add(button)
        button.connect("clicked", ics_export_config_cancel_cb)
        button.show()
        button = gtk.Button(stock=gtk.STOCK_OK)
        hbox.add(button)
        button.connect("clicked", ics_export_config_ok_cb)
        button.show()
        vbox.pack_start(hbox, False, False, 0)
        hbox.show()

        window.add(vbox)
        vbox.show()
        
        window.set_modal(True)
        window.show()

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

        vbox = gtk.VBox(False, 0)
        add_window.add(vbox)

        table = gtk.Table(3, 2, False)
        table.set_col_spacings(10)
        table.set_row_spacings(10)

        label = gtk.Label(_('Name'))
        label.set_alignment(1, 0.5)
        table.attach(label, 0, 1, 0, 1)
        label.show()

        label = gtk.Label(_('Birthday'))
        label.set_alignment(1, 0.5)
        table.attach(label, 0, 1, 1, 2)
        label.show()

        label = gtk.Label(_('Save to file/database'))
        label.set_alignment(1, 0.5)
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
        for db in DATABASES:
            if db.CAN_SAVE and \
               db.__class__.__name__ in self.addressbook.conf.used_databases:
                combobox.append_text(db.TITLE)
        combobox.set_active(0)
        combobox.show()
        table.attach(combobox, 1, 2, 2, 3)

        vbox.pack_start(table, True, True, 8)
        table.show()

        # Cancel / apply / ok
        def add_single_manual_cancel_cb(*args):
            '''Destroy windows (discard modifications)'''
            add_window.destroy()
        
        def add_single_manual_apply_cb(*args):
            '''Save new added person'''
            for db in DATABASES:
                if db.TITLE == combobox.get_active_text():
                    calend = list(calendar.get_date())
                    calend[1] += 1
                    # FIXME: ugly fix for #563405 adding to Lightning
                    if db.TITLE == 'Thunderbird/Icedove Lightning':
                        db.ab = self.addressbook
                    db.add(name.get_text(), datetime.date(*calend))
            name.set_text("")
            self.reload_gbirthday()

        def add_single_manual_ok_cb(*args):
            '''Save modifications and destroy window'''
            add_single_manual_apply_cb()
            add_window.destroy()

        hbox = gtk.HButtonBox()
        hbox.set_spacing(5)
        hbox.set_layout(gtk.BUTTONBOX_END)
        apply_button = gtk.Button(stock=gtk.STOCK_APPLY)
        apply_button.set_sensitive(False)
        hbox.add(apply_button)
        apply_button.connect("clicked", add_single_manual_apply_cb)
        apply_button.show()
        button = gtk.Button(stock=gtk.STOCK_CANCEL)
        hbox.add(button)
        button.connect("clicked", add_single_manual_cancel_cb)
        button.show()
        ok_button = gtk.Button(stock=gtk.STOCK_OK)
        ok_button.set_sensitive(False)
        hbox.add(ok_button)
        ok_button.connect("clicked", add_single_manual_ok_cb)
        ok_button.show()
        vbox.pack_start(hbox, False, False, 0)
        hbox.show()

        vbox.show()

        # Apply and OK only allowed in name not empty 
        def entry_modification_cb(*args):
            if name.get_text() != '':
                apply_button.set_sensitive(True)
                ok_button.set_sensitive(True)
            else:
                apply_button.set_sensitive(False)
                ok_button.set_sensitive(False)
        
        name.connect("changed", entry_modification_cb)

        add_window.set_border_width(5)
        add_window.show()

#     def add_from_file(self, widget, window):
#         window.destroy()
#         add_window = self.gtk_get_top_window(_('Add'))
#
#         box = gtk.VBox(False, 0)
#         add_window.add(box)
#
#         table = gtk.Table(3, 2, False)
#         table.set_col_spacings(10)
#         table.set_row_spacings(10)
#
#
#         label = gtk.Label('select file/database')
#         table.attach(label, 0, 1, 0, 1)
#         label.show()
#
#         db_combo = gtk.combo_box_new_text()
#         for db in DATABASES:
#             db_combo.append_text(db.TITLE)
#         db_combo.set_active(0)
#         db_combo.show()
#         table.attach(db_combo, 1, 2, 0, 1)
#
#         label = gtk.Label(_('Import Settings'))
#         table.attach(label, 0, 1, 1, 2)
#         label.show()
#
#         label = gtk.Label('not needed')
#         table.attach(label, 1, 2, 1, 2)
#         label.show()
#
#         label = gtk.Label(_('Database'))
#         table.attach(label, 0, 1, 2, 3)
#         label.show()
# 
#         combobox = gtk.combo_box_new_text()
#         for db in DATABASES:
#             if db.CAN_SAVE:
#                 combobox.append_text(db.TITLE)
#         combobox.set_active(0)
#         combobox.show()
#         table.attach(combobox, 1, 2, 2, 3)
#
#         box.pack_start(table, True, True, 8)
#         table.show()
#
#         label = gtk.Label(_('Export Settings'))
#         table.attach(label, 0, 1, 3, 4)
#         label.show()
#
#         label = gtk.Label('not needed')
#         table.attach(label, 1, 2, 3, 4)
#         label.show()
#
#         def finish_add(uno, combo, name, calend, window):
#             '''save new added person'''
#             import datetime
#             for db in DATABASES:
#                 if db.TITLE == combo.get_active_text():
#                     calend = list(calend.get_date())
#                     calend[1] += 1
#                     db.add(name.get_text(), datetime.date(*calend))
#             window.destroy()
#         button = gtk.Button(_('Save & Close'))
#         box.pack_start(button, False, False, 2)
#         button.connect("clicked", finish_add, combobox, db_combo, '',
#                         add_window)
#         button.show()
#
#         box.show()
#
#         box.show()
#         add_window.set_border_width(5)
#         add_window.show()

    def closebdwindow(self, uno, dos):
        '''close about window'''
        if self.showbd:
            self.showbd.destroy()
            self.showbd = None

    ### gtk helper functions ###
    @staticmethod
    def gtk_get_top_window(title, decorated=True, center=True, 
                           hide_in_taskbar=False):
        '''Get gtk top window.'''
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_decorated(decorated)
        if center:
            window.set_position(gtk.WIN_POS_CENTER)
        else:
            window.set_position(gtk.WIN_POS_MOUSE)
        window.set_title(title)
        window.set_icon_from_file(IMAGESLOCATION + 'birthday.png')
        window.set_skip_taskbar_hint(hide_in_taskbar)
        window.set_border_width(10)
        
        # Close window if Escape key is pressed
        def keypress(widget, event) :
	    if event.keyval == gtk.keysyms.Escape :
		window.destroy()
        window.connect("key-press-event", keypress)

        return window

if __name__ == "__main__":
    _ = lambda x: x
