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
import os
from gbirthday.databases import DataBase
from gbirthday.gtk_funcs import show_error_msg

class CSV(DataBase):
    '''import from CSV-file'''

    def __init__(self):
        super(CSV, self).__init__(title='CSV-file (comma seperated value)')
        self._seperators = ['; ', ', ', ': ']   # possible seperators
        self.addressbook = None
        self.conf = None

    def parse(self, addressbook, conf):
        '''open and parse file'''
        # XXX: set addressbook in __init__?
        self.ab = addressbook
        self.addressbook = addressbook
        self.conf = conf
        if not conf.csv_files:
            return
        for filename in conf.csv_files:
            if (os.path.exists(filename)):
                for line in file(filename):
                    # check, if any of the seperators are in the text
                    for sep in self._seperators:
                        if len(line.split(sep)) > 1:
                            date = line.split(sep, 1)[0]
                            name = line.split(sep, 1)[1][:-1]
                            addressbook.add(name, date)
                            break
            else:
                show_error_msg(_('Could not load, CVS-file not set.')
                                + ':' + filename)

    def add(self, name, birthday):
        '''add new person with birthday to end of csv-file'''
        birthday = str(birthday)
        # TODO: show menu to select file?
        if len(self.conf.csv_files) == 0:
            show_error_msg(_('CSV-file does not exist'))
            return
        filename = self.conf.csv_files[0]
        if (os.path.exists(filename)):
            output_file = file(self.conf.csv_files[0], 'a')
        else:
            output_file = file(self.conf.csv_files[0], 'w')
        output_file.write(birthday + ', ' + name + '\n')
        output_file.close()
        self.addressbook.add(name, birthday)

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
            chooser = gtk.FileChooserDialog(title=None,
                                action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                buttons=(gtk.STOCK_CANCEL,
                                        gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN,
                                        gtk.RESPONSE_OK))
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
