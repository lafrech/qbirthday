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
from PyQt4 import QtCore, QtGui, uic

from .__init__ import DATABASES

class IcsExportPreferencesDialog(QtGui.QDialog):
    pass

class PreferencesDialog(QtGui.QDialog):

    def __init__(self, conf, parent=None):

        super().__init__(parent)
        
        uic.loadUi('ui/preferences_dialog.ui', self)

        self.conf = conf

        self.pastSpinBox.setValue(int(self.conf.firstday))
        self.nextSpinBox.setValue(int(self.conf.lastday))
        self.notifyNextSpinBox.setValue(int(self.conf.notify_future_bdays))
        self.icsExportCheckBox.setChecked(bool(self.conf.ics_export))
        self.icsExportButton.setEnabled(bool(self.conf.ics_export))

        self.icsExportCheckBox.stateChanged.connect(
            self.icsExportButton.setEnabled)
        self.icsExportButton.clicked.connect(
            lambda: IcsExportPreferencesDialog(self.conf, self).exec_())

        self.db_chkbx = {}
        
        for db in DATABASES:

            hbox = QtGui.QHBoxLayout()
            self.databasesLayout.addLayout(hbox)

            self.db_chkbx[db] = QtGui.QCheckBox(db.TITLE)
            db_used = bool(db.__class__.__name__ in self.conf.used_databases)
            self.db_chkbx[db].setChecked(db_used)
            hbox.addWidget(self.db_chkbx[db])
            if db.HAS_CONFIG:
                button = QtGui.QPushButton(_('Preferences'))
                button.setEnabled(db_used)
                self.db_chkbx[db].stateChanged.connect(button.setEnabled)
                # TODO: write conf class
                #button.clicked.connect(
                #    lambda: db.preferences_dialog(self.conf, self).exec_())
                hbox.addWidget(button)

        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.save)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.save)

    def save(self):

        print("save")

        self.conf.firstday = str(self.pastSpinBox.value())
        self.conf.lastday = str(self.nextSpinBox.value())
        self.conf.notify_future_bdays = str(self.notifyNextSpinBox.value())
        self.conf.ics_export = str(self.icsExportCheckBox.isChecked())
        [db.__class__.__name__ for db in DATABASES 
            if self.db_chkbx[db].isChecked()]
        self.conf.used_databases = [db.__class__.__name__ for db in DATABASES 
                                    if self.db_chkbx[db].isChecked()]
        print(self.conf.csv_files)
        self.conf.save()


#     def preferences_window(self, textcw=None):
#         '''show settings window'''
#         preferences = self.gtk_get_top_window(_('Preferences'))
# 
#         box = gtk.VBox(False, 0)
#         preferences.add(box)
# 
#         table = gtk.Table(5, 2, False)
#         table.set_col_spacings(10)
#         table.set_row_spacings(10)
# 
#         label = gtk.Label(_('Past birthdays'))
#         table.attach(label, 0, 1, 0, 1)
#         label.show()
# 
#         label = gtk.Label(_('Next birthdays'))
#         table.attach(label, 0, 1, 1, 2)
#         label.show()
# 
#         label = gtk.Label(_('Notification: Future birthdays'))
#         table.attach(label, 0, 1, 2, 3)
#         label.show()
# 
#         label = gtk.Label(_('ICS Calendar export'))
#         table.attach(label, 0, 1, 3, 4)
#         label.show()
# 
#         label = gtk.Label(_('Database'))
#         table.attach(label, 0, 1, 5, 6)
#         label.show()
# 
#         adjustment = gtk.Adjustment(int(self.conf.firstday), lower=-30,
#                     upper=0, step_incr=-1, page_incr=0, page_size=0)
#         spin_firstday = gtk.SpinButton(adjustment, climb_rate=0.0, digits=0)
#         table.attach(spin_firstday, 1, 2, 0, 1)
#         spin_firstday.show()
# 
#         adjustment = gtk.Adjustment(int(self.conf.lastday), lower=0, upper=90,
#                     step_incr=1, page_incr=0, page_size=0)
#         spin_lastday = gtk.SpinButton(adjustment, climb_rate=0.0, digits=0)
#         table.attach(spin_lastday, 1, 2, 1, 2)
#         spin_lastday.show()
# 
#         adjustment = gtk.Adjustment(int(self.conf.notify_future_bdays),
#                     lower=0, upper=int(self.conf.lastday),
#                     step_incr=1, page_incr=0, page_size=0)
#         spin_notify_future_bdays = gtk.SpinButton(adjustment, climb_rate=0.0, 
#                                                   digits=0)
#         table.attach(spin_notify_future_bdays, 1, 2, 2, 3)
#         spin_notify_future_bdays.show()
# 
#         # ICS export checkbox
#         def ics_export_chk_cb(chk, button):
#             '''Enable / disable ICS export setting widgets'''
#             button.set_sensitive(chk.get_active())
#         chk_export = gtk.CheckButton()
#         chk_export.set_active(self.conf.ics_export)
#         button = gtk.Button(stock=gtk.STOCK_PREFERENCES)
#         button.set_sensitive(self.conf.ics_export)
#         chk_export.connect("clicked", ics_export_chk_cb, button)
#         button.connect("clicked", self.ics_export_config)
#         hbox = gtk.HBox(False, 2)
#         hbox.pack_start(chk_export, False, False, 0)
#         hbox.pack_start(button, False, False, 1)
#         table.attach(hbox, 1, 2, 3, 4)
#         button.show()
#         chk_export.show()
#         hbox.show()
# 
#         # Separator
#         hsep = gtk.HSeparator()
#         table.attach(hsep, 0, 2, 4, 5)
#         hsep.show()
# 
#         # Databases
#         def db_select(widget, db):
#             '''Enable / disable DB setting widgets'''
#             self.db_buttons[db].set_sensitive(widget.get_active())
# 
#         def preferences_db(widget, db):
#             '''Create and display DB config window'''
#             pref_db = self.gtk_get_top_window(db.__class__.__name__ + ' ' + \
#                                               _('Database Configuration'))
# 
#             vbox = gtk.VBox(False, 5)
#             
#             db.create_config(vbox, self.conf)
# 
#             # Cancel / apply / ok
#             def preferences_cancel_cb(*args):
#                 '''Destroy windows (discard modifications)'''
#                 pref_db.destroy()
#             
#             def preferences_apply_cb(*args):
#                 '''Save modifications'''
#                 db.save_config(self.conf)
#                 self.conf.save()
#     
#             def preferences_ok_cb(*args):
#                 '''Save modifications and destroy window'''
#                 preferences_apply_cb()
#                 pref_db.destroy()
#     
#             hbox = gtk.HButtonBox()
#             hbox.set_spacing(5)
#             hbox.set_layout(gtk.BUTTONBOX_END)
#             button = gtk.Button(stock=gtk.STOCK_APPLY)
#             hbox.add(button)
#             button.connect("clicked", preferences_apply_cb)
#             button.show()
#             button = gtk.Button(stock=gtk.STOCK_CANCEL)
#             hbox.add(button)
#             button.connect("clicked", preferences_cancel_cb)
#             button.show()
#             button = gtk.Button(stock=gtk.STOCK_OK)
#             hbox.add(button)
#             button.connect("clicked", preferences_ok_cb)
#             button.show()
#             vbox.pack_start(hbox, False, False, 0)
#             hbox.show()
# 
#             vbox.show()
#             pref_db.add(vbox)
# 
#             pref_db.set_modal(True)
#             pref_db.show()
# 
#         vbox = gtk.VBox(False, 10)
# 
#         self.db_chk = {}
#         self.db_buttons = {}
#         for db in DATABASES:
#             hbox = gtk.HBox(False, 2)
#             vbox.pack_start(hbox, False, False, 0)
# 
#             self.db_chk[db] = gtk.CheckButton(db.TITLE)
#             hbox.pack_start(self.db_chk[db], False, False, 0)
#             if db.HAS_CONFIG:
#                 self.db_buttons[db] = gtk.Button(stock=gtk.STOCK_PREFERENCES)
#                 self.db_buttons[db].connect("clicked", preferences_db, db)
#                 self.db_buttons[db].show()
#                 hbox.pack_start(self.db_buttons[db], False, False, 1)
#                 self.db_buttons[db].set_sensitive(self.db_chk[db].get_active())
#                 self.db_chk[db].connect("toggled", db_select, db)
#             if db.__class__.__name__ in self.conf.used_databases:
#                 self.db_chk[db].set_active(True)
#             hbox.show()
#             self.db_chk[db].show()
#         table.attach(vbox, 1, 2, 5, 6)
#         vbox.show()
# 
#         box.pack_start(table, True, True, 8)
#         table.show()
# 
#         # Cancel / apply / ok
#         def preferences_cancel_cb(*args):
#             '''Destroy windows (discard modifications)'''
#             preferences.destroy()
#         
#         def preferences_apply_cb(*args):
#             '''Save modifications'''
#             self.conf.firstday = spin_firstday.get_value_as_int()
#             self.conf.lastday = spin_lastday.get_value_as_int()
#             self.conf.notify_future_bdays = \
#                 spin_notify_future_bdays.get_value_as_int()
#             self.conf.ics_export = chk_export.get_active()
#             for db in DATABASES:
#                 if self.db_chk[db].get_active():
#                     if not db.__class__.__name__ in self.conf.used_databases:
#                         self.conf.used_databases.append(db.__class__.__name__)
#                 else:
#                     if db.__class__.__name__ in self.conf.used_databases:
#                         self.conf.used_databases.remove(db.__class__.__name__)
#             self.conf.save()
# 
#         def preferences_ok_cb(*args):
#             '''Save modifications and destroy window'''
#             preferences_apply_cb()
#             preferences.destroy()
# 
#         hbox = gtk.HButtonBox()
#         hbox.set_spacing(5)
#         hbox.set_layout(gtk.BUTTONBOX_END)
#         button = gtk.Button(stock=gtk.STOCK_APPLY)
#         hbox.add(button)
#         button.connect("clicked", preferences_apply_cb)
#         button.show()
#         button = gtk.Button(stock=gtk.STOCK_CANCEL)
#         hbox.add(button)
#         button.connect("clicked", preferences_cancel_cb)
#         button.show()
#         button = gtk.Button(stock=gtk.STOCK_OK)
#         hbox.add(button)
#         button.connect("clicked", preferences_ok_cb)
#         button.show()
#         vbox.pack_start(hbox, False, False, 0)
#         hbox.show()
# 
#         box.show()
#         preferences.set_border_width(5)
#         preferences.show()
# 
#     def ics_export_config(self, widget):
#         '''Display ICS export settings window'''
#         window = self.gtk_get_top_window(_('ICS Export configuration'))
#         window.set_border_width(10)
# 
#         vbox = gtk.VBox(False, 10)
# 
#         # File path
#         def set_filepath(widget, entry):
#             '''File selection dialog'''
#             chooser = gtk.FileChooserDialog(title='ICS Export file',
#                                             action=gtk.FILE_CHOOSER_ACTION_SAVE,
#                                             buttons=(gtk.STOCK_CANCEL,
#                                                      gtk.RESPONSE_CANCEL,
#                                                      gtk.STOCK_OPEN,
#                                                      gtk.RESPONSE_OK))
#             
#             # Default to current file
#             (folder, file_name) = os.path.split(self.conf.ics_filepath)
#             chooser.set_current_folder(folder)
#             chooser.set_current_name(file_name)
# 
#             response = chooser.run()
#             if response == gtk.RESPONSE_OK:
#                 entry.set_text(chooser.get_filename())
#             chooser.destroy()
# 
#         hbox = gtk.HBox()
# 
#         label = gtk.Label(_("Export birthday list in iCalendar file:"))
#         label.show()
#         label.set_alignment(0, 0.5)
#         vbox.pack_start(label, False, False, 0)
# 
# 
#         filename = gtk.Entry()
#         filename.set_text(self.conf.ics_filepath)
#         filename.show()
#         hbox.pack_start(filename, True, True, 0)
#         button = gtk.Button(_("Browse"))
#         new_img = gtk.Image()
#         new_img.set_from_stock(gtk.STOCK_DIRECTORY, gtk.ICON_SIZE_BUTTON,)
#         button.set_image(new_img)
#         button.show()
#         hbox.pack_start(button, False, False, 5)
#         button.connect("clicked", set_filepath, filename)
# 
#         hbox.show()
# 
#         vbox.pack_start(hbox, False, False, 0)
# 
#         # ICS alarm
#         def ics_alarm_chk_cb(chk):
#             '''Enable / disable ICS alarm setting widgets'''
#             self.ics_alarm_days_spin.set_sensitive(chk.get_active())
#             self.ics_alarm_days_label.set_sensitive(chk.get_active())
#             self.ics_alarm_custom_properties_label.set_sensitive( \
#                 chk.get_active())
#             self.ics_alarm_custom_properties_scroll.set_sensitive( \
#                 chk.get_active())
# 
#         chk = gtk.CheckButton(_('Set alarms'))
#         chk.set_active(self.conf.ics_alarm)
#         chk.connect("clicked", ics_alarm_chk_cb)
#         chk.show()
#         vbox.pack_start(chk, False, False, 0)
#         
#         # ICS nb of days between alarm and birthday
#         hbox = gtk.HBox()
#         adjustment = gtk.Adjustment(int(self.conf.ics_alarm_days), lower=0,
#                     upper=60, step_incr=1, page_incr=0, page_size=0)
#         self.ics_alarm_days_spin = gtk.SpinButton(adjustment, climb_rate=0.0,
#                                                   digits=0)
#         self.ics_alarm_days_label = gtk.Label(_('days before each birthday'))
#         self.ics_alarm_days_spin.set_sensitive(self.conf.ics_alarm)
#         self.ics_alarm_days_label.set_sensitive(self.conf.ics_alarm)
#         hbox.pack_start(self.ics_alarm_days_spin, False, False, 0)
#         hbox.pack_start(self.ics_alarm_days_label, False, False, 0)
#         self.ics_alarm_days_spin.show()
#         self.ics_alarm_days_label.show()
#         hbox.show()
#         vbox.pack_start(hbox, False, False, 0)
#         
#         # Separator
#         hsep = gtk.HSeparator()
#         vbox.pack_start(hsep, False, False, 0)
#         hsep.show()
#         
#         # Custom properties
#         custom_properties_tooltip_str = ( \
#             _("Use this if you know what you're doing. See RFC 2445."))
# 
#         # ICS VEVENT custom properties
#         self.ics_custom_properties_label = \
#             gtk.Label(_('Custom ICS properties for VEVENT'))
#         self.ics_custom_properties_label.set_tooltip_text( \
#             custom_properties_tooltip_str)
#         self.ics_custom_properties_label.set_alignment(0, 0)
#         vbox.pack_start(self.ics_custom_properties_label, False, False, 0)
#         self.ics_custom_properties_label.show()
#         textbuffer_event = gtk.TextBuffer()
#         textbuffer_event.set_text(self.conf.ics_custom_properties)
#         textview = gtk.TextView(buffer=textbuffer_event)
#         textview.set_editable(True)
#         textview.set_tooltip_text( \
#             custom_properties_tooltip_str)
#         self.ics_custom_properties_scroll = gtk.ScrolledWindow()
#         self.ics_custom_properties_scroll.add_with_viewport(textview)
#         self.ics_custom_properties_scroll.set_policy(gtk.POLICY_AUTOMATIC,
#                                                      gtk.POLICY_AUTOMATIC)
#         vbox.pack_start(self.ics_custom_properties_scroll, False, False, 0)
#         self.ics_custom_properties_scroll.show()
#         textview.show()
# 
#         # ICS VALARM custom properties
#         self.ics_alarm_custom_properties_label = \
#             gtk.Label(_('Custom ICS properties for VALARM'))
#         self.ics_alarm_custom_properties_label.set_tooltip_text( \
#             custom_properties_tooltip_str)
#         self.ics_alarm_custom_properties_label.set_alignment(0, 0)
#         self.ics_alarm_custom_properties_label.set_sensitive( \
#             self.conf.ics_alarm)
#         vbox.pack_start(self.ics_alarm_custom_properties_label,
#                         False, False, 0)
#         self.ics_alarm_custom_properties_label.show()
#         textbuffer_alarm = gtk.TextBuffer()
#         textbuffer_alarm.set_text(self.conf.ics_alarm_custom_properties)
#         textview = gtk.TextView(buffer=textbuffer_alarm)
#         textview.set_editable(True)
#         textview.set_tooltip_text( \
#             custom_properties_tooltip_str)
#         self.ics_alarm_custom_properties_scroll = gtk.ScrolledWindow()
#         self.ics_alarm_custom_properties_scroll.add_with_viewport(textview)
#         self.ics_alarm_custom_properties_scroll.set_policy(gtk.POLICY_AUTOMATIC,
#                                                            gtk.POLICY_AUTOMATIC)
#         self.ics_alarm_custom_properties_scroll.set_sensitive( \
#             self.conf.ics_alarm)
#         vbox.pack_start(self.ics_alarm_custom_properties_scroll,
#                         False, False, 0)
#         self.ics_alarm_custom_properties_scroll.show()
#         textview.show()
# 
#         # Cancel / apply / ok
#         def ics_export_config_cancel_cb(*args):
#             '''Destroy windows (discard modifications)'''
#             window.destroy()
#         
#         def ics_export_config_apply_cb(*args):
#             '''Save modifications'''
#             self.conf.ics_filepath = filename.get_text()
#             self.conf.ics_alarm = chk.get_active()
#             self.conf.ics_alarm_days = \
#                 str(self.ics_alarm_days_spin.get_value_as_int())
#             self.conf.ics_custom_properties = textbuffer_event.get_text( \
#                 textbuffer_event.get_start_iter(),
#                 textbuffer_event.get_end_iter())
#             self.conf.ics_alarm_custom_properties = textbuffer_alarm.get_text( \
#                 textbuffer_alarm.get_start_iter(),
#                 textbuffer_alarm.get_end_iter())
#             
#             self.addressbook.export()
# 
#         def ics_export_config_ok_cb(*args):
#             '''Save modifications and destroy window'''
#             ics_export_config_apply_cb()
#             window.destroy()
# 
#         hbox = gtk.HButtonBox()
#         hbox.set_spacing(5)
#         hbox.set_layout(gtk.BUTTONBOX_END)
#         button = gtk.Button(stock=gtk.STOCK_APPLY)
#         hbox.add(button)
#         button.connect("clicked", ics_export_config_apply_cb)
#         button.show()
#         button = gtk.Button(stock=gtk.STOCK_CANCEL)
#         hbox.add(button)
#         button.connect("clicked", ics_export_config_cancel_cb)
#         button.show()
#         button = gtk.Button(stock=gtk.STOCK_OK)
#         hbox.add(button)
#         button.connect("clicked", ics_export_config_ok_cb)
#         button.show()
#         vbox.pack_start(hbox, False, False, 0)
#         hbox.show()
# 
#         window.add(vbox)
#         vbox.show()
#         
#         window.set_modal(True)
#         window.show()
# 
#    def add(self, text):
#        '''Show Dialog to add new Person - not yet implemented!'''
#        self.add_single_manual(None, None)


