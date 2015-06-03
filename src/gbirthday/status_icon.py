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
from PyQt4 import QtCore, QtGui, uic
import time
import os

# own imports
from .__init__ import VERSION
from .__init__ import DATABASES
from .__init__ import MONTH_AT_PLACE, DAY_AT_PLACE
from .__init__ import CURRENT_DAY

from .preferences_dialog import PreferencesDialog

IMAGESLOCATION = os.sep.join(__file__.split(os.sep)[:-1]) + "/pics/"

class StatusIcon(QtGui.QSystemTrayIcon):
    '''Class to show status icon'''

    def __init__(self, main_window, addressbook, conf):
        '''create status icon'''
        
        # TODO: enlarge icon to best fit
        super().__init__(QtGui.QIcon(IMAGESLOCATION + 'birthday.png'), 
                         main_window)

        self.main_window = main_window
        self.addressbook = addressbook
        self.conf = conf
        
        # TODO: add nice icons        
        menu = QtGui.QMenu()
        menu.addAction("Refresh", self.reload_gbirthday)
        menu.addAction("Add", self.add_single_manual)
        menu.addAction("Preferences", 
            lambda: PreferencesDialog(self.conf, self.main_window).exec_())
        #menu.addAction("About", self.create_dialog)
        menu.addAction("Quit", QtCore.QCoreApplication.instance().quit)

        # Set context menu to open on right click
        self.setContextMenu(menu)

        # Display birthdays on left click
        def tray_icon_activated_cb(reason):
            if reason == QtGui.QSystemTrayIcon.Trigger:
                # Toggle birthday window visibility
                self.main_window.setVisible(not self.main_window.isVisible())
        self.activated.connect(tray_icon_activated_cb)

        self._reload_set_icon()
        
        def on_url(dialog, link):
            '''start default browser with gbirthday-website on click'''
            import webbrowser
            webbrowser.open(link)

    def reload_gbirthday(self, *args):
        '''reload gbirthday, reload data from databases'''
        self.addressbook.reload()
        self._reload_set_icon()
        self.main_window.refresh()

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
            # check if birthday today
            if self.addressbook.check_day(0):
                self.setIcon(QtGui.QIcon(
                    IMAGESLOCATION + 'birthdayred.png'))
            else:
                self.setIcon(QtGui.QIcon(
                    IMAGESLOCATION + 'birthday.png'))
        else:
            self.setIcon(QtGui.QIcon(
                IMAGESLOCATION + 'nobirthday.png'))

        # show notification of birthdays in the future
        try:
            # TODO: import this on top of script?
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

    # TODO: about dialog
#     def create_dialog(self):
#         '''create about dialog'''
#         QtGui.QMessageBox.about(self.app, 
#                                 "About GBirthday",
#                                 "GBirthday %s".format(VERSION))

#         dlg = self.dlg
#         dlg = gtk.AboutDialog()
#         dlg.set_version(VERSION)
#         dlg.set_comments(_('Birthday reminder'))
#         dlg.set_name("GBirthday")
#         image = gtk.gdk.pixbuf_new_from_file(IMAGESLOCATION + 'gbirthday.png')
#         dlg.set_logo(image)
#         dlg.set_icon_from_file(IMAGESLOCATION + 'birthday.png')
#         dlg.set_copyright('Copyright \u00A9 2007 Alex Mallo, 2009 Andreas Bresser, 2009 Thomas Spura')
#         dlg.set_license(
# '''Licensed under the GNU General Public License Version 2
# 
# GBirthday is free software; you can redistribute it and\/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# GBirthday is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.''')
#         dlg.set_authors([
#                 'Andreas Bresser <andreasbresser@gmail.com>',
#                 'Stefan Jurco <stefan.jurco@gmail.com>',
#                 'Alex Mallo <dernalis@gmail.com>',
#                 'Thomas Spura <tomspur@fedoraproject.org>',
#                 'Robert Wildburger <r.wildburger@gmx.at>',
#                 'Jérôme Lafréchoux <jerome@jolimont.fr>'
#                         ])
#         dlg.set_artists(['Alex Mallo <dernalis@gmail.com>'])
#         cred = _('translator-credit')
#         if cred != 'translator-credit':
#             dlg.set_translator_credits(cred)
#         else:
#             dlg.set_translator_credits(
#                 _("There are no translations or the translator doesn't want to get credits for that."))
#         dlg.set_website('http://gbirthday.sourceforge.net/')
# 
#         def close(w, res):
#             if res == gtk.RESPONSE_CANCEL:
#                 w.hide()
#         dlg.connect('response', close)
#         dlg.run()
    
    # TODO: Make dedicated class for add birthdate widget
    def add_single_manual(self):
        '''Add birthday dialog'''

        add_widget = uic.loadUi('ui/add.ui')

        # Fill database combobox
        # TODO: use index to allow DB name translation
        for db in DATABASES:
            if db.CAN_SAVE and \
               db.__class__.__name__ in self.addressbook.conf.used_databases:
                add_widget.saveComboBox.addItem(db.TITLE)
        
        # Apply and OK enabled only if name not empty 
        def entry_modification_cb():
            # TODO: check if text is not whitespace would be better
            cond = add_widget.nameEdit.text() != ''
            add_widget.buttonBox.button(
                QtGui.QDialogButtonBox.Apply).setEnabled(cond)
            add_widget.buttonBox.button(
                QtGui.QDialogButtonBox.Ok).setEnabled(cond)
        
        # Execute once to disable OK and Apply
        entry_modification_cb()
        # Connect signal to check at each text modification
        add_widget.nameEdit.textChanged.connect(entry_modification_cb)

        def add_single_manual_apply_cb():
            '''Save new added person'''
            for db in DATABASES:
                if db.TITLE == add_widget.saveComboBox.currentText():
                    birthdate = add_widget.dateWidget.selectedDate().toPyDate()
                    # FIXME: ugly fix for #563405 adding to Lightning
                    if db.TITLE == 'Thunderbird/Icedove Lightning':
                        db.ab = self.addressbook
                    db.add(add_widget.nameEdit.text(), birthdate)
            add_widget.nameEdit.clear()
            self.reload_gbirthday()

        # TODO: If apply, add birthdate
        add_widget.buttonBox.button(
            QtGui.QDialogButtonBox.Apply).clicked.connect(
                add_single_manual_apply_cb)
        
        # If OK, add birthdate and close dialog
        # If Cancel, just close dialog
        if add_widget.exec_():
            add_single_manual_apply_cb()

# if __name__ == "__main__":
#     _ = lambda x: x
