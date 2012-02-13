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
from __future__ import absolute_import
import gtk
import os
import re
from gbirthday.databases import DataBase
from gbirthday.gtk_funcs import show_error_msg

class Evolution(DataBase):
    '''data import from the Evolution address book'''
    def __init__(self):
        super(Evolution, self).__init__(title='Evolution', can_save=False, 
                                        has_config=False)
        self._split_re = re.compile(r'\r?\n')
        
    def parse(self, addressbook=None, conf=None):
        '''load and parse parse Evolution data files'''
        # XXX: set addressbook in __init__?
        self.ab = addressbook
        try:
            import evolution
            # When there is no evolution addressbook, silently abort
            # parsing.
            if not evolution.ebook:
                return
        except ImportError:
            show_error_msg(_("You need to install python-evolution to use the evolution module"))
            return

        for book in evolution.ebook.list_addressbooks():
            ebook = evolution.ebook.open_addressbook(book[1])
            if not ebook:
                continue
            for contact in ebook.get_all_contacts():
                # contact.props.birth_date{.year, .month, .day} non-existing
                # -> using vcard
                vcard = contact.get_vcard_string()
                self.parse_birthday((contact.props.full_name, vcard), addressbook)

    def parse_birthday(self, data, addressbook):
        '''parse evolution addressbook. the file is in VCard format.'''
        # TODO change to contact.props.birth_date, no vcard would be needed
        full_name, vcard = data
        lines = self._split_re.split(vcard)
        for line in lines:
            # if BDAY is in vcard, use this as birthday
            if line.startswith('BDAY'):
                addressbook.add(full_name, line.split(':', 1)[1])
