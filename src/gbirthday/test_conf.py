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
Testing the conf class
'''
from nose import with_setup
from .__init__ import Conf

conf = None

# TODO: move ~/.gbirthdayrc arround for empty testing
def setup():
    '''Setup database.'''
    global conf
    conf = Conf()

# TODO: move ~/.gbirthdayrc back again
def teardown():
    '''Clean database.'''
    global conf
    conf = None

def test_init():
    '''initialize conf'''
    assert conf.settings
    assert conf.mysql
