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
'''
Testing the databases module
'''
from nose import with_setup
from .databases import DataBase

database = None

def setup():
    '''Setup database.'''
    global database
    database = DataBase()

def teardown():
    '''Clean database.'''
    global database
    database = None

@with_setup(setup, teardown)
def test_init_no_bday():
    '''init_database'''
    assert database
    database.parse()
    assert database
    database.add('name', 'birthday')
    assert database
    database.update()
    assert database
    database.create_config('table')
    assert database
    database.update()
    assert database

@with_setup(setup, teardown)
def test_activate():
    '''test (de)activate'''
    class wid():
        def __init__(self):
            self.sensitive = False

        def set_sensitive(self, set_to):
            self.sensitive = set_to

    database.widget = wid()

    database.activate()
    assert database.widget.sensitive
    database.deactivate()
    assert not database.widget.sensitive
    database.deactivate()
    assert not database.widget.sensitive
    database.activate()
    assert database.widget.sensitive

def test_evolution():
    '''evolution is working with local evolution setup?'''
    from .databases import Evolution
    e = Evolution()
    e.parse()
    assert (e.TITLE == 'Evolution')
    assert (not e.addressbook)
