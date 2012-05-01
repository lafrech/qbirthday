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
                show_error_msg(_('Could not load CSV-file:')
                                + filename)

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

    def remove_file(self, widget, tree, store, files):
        select = tree.get_selection()
        model, treeiter = select.get_selected()
        if treeiter is not None:
            files.remove(model.get_value(treeiter, 0))
            store.remove(treeiter)
        return

    def save_config(self, conf):
        conf.csv_files = self.tmp_csv_files
        
    def create_config(self, vbox, conf):
        '''create aditional options menu'''
        
        self.tmp_csv_files = conf.csv_files

        hbox = gtk.HBox(False, 5)

        # File list
        store = (gtk.ListStore(str))
        if self.tmp_csv_files:
            for csv_file in self.tmp_csv_files:
                store.append([str(csv_file)])
        tree = gtk.TreeView(store)
        tree.set_headers_visible(False)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("File"), renderer, text=0)
        tree.append_column(column)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(tree)
        scroll.set_size_request(400, -1)
        tree.show()
        scroll.show()
        hbox.pack_start(scroll, True, True, 0)

        # Add / remove buttons
        vbox_buttons = gtk.VBox(False, 5)

        def choose_file(widget):

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
                store.append([filename])
                if self.tmp_csv_files:
                    self.tmp_csv_files.append(filename)
                else:
                    self.tmp_csv_files = [filename]

            chooser.destroy()

        add_button = gtk.Button(stock=gtk.STOCK_ADD)
        add_button.connect("clicked", choose_file)
        add_button.show()
        vbox_buttons.pack_start(add_button, False, False, 0)

        remove_button = gtk.Button(stock=gtk.STOCK_REMOVE)
        remove_button.connect("clicked", self.remove_file, tree, store, 
                              self.tmp_csv_files)
        remove_button.show()
        vbox_buttons.pack_start(remove_button, False, False, 0)
        
        vbox_buttons.show()
        hbox.pack_start(vbox_buttons, False, False, 0)
        hbox.show()
        vbox.pack_start(hbox, False, False, 0)

