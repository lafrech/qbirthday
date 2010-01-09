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
Testing the addressbook module
'''
from nose import with_setup
import gbirthday

AB = None

def setup():
    '''Setup addressbook.'''
    global AB
    AB = gbirthday.AddressBook()

def teardown():
    '''Clean addressbook.'''
    global AB
    AB = None

@with_setup(setup, teardown)
def test_init_no_bday():
    '''init_no_bday'''
    assert not AB.check_day(0)

@with_setup(setup, teardown)
def test_add_YYYYMMDD_bday():
    '''add_YYYYMMDD_bday'''
    import time
    today = time.strftime("%Y%m%d", time.localtime(time.time()))
    AB.add('dummy', today)
    assert AB.check_day(0)

@with_setup(setup, teardown)
def test_add_YYYYMMDD_bday2():
    '''add_YYYY-MM-DD_bday'''
    import time
    today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    AB.add('dummy', today)
    assert AB.check_day(0)

@with_setup(setup, teardown)
def test_add_YYYYMMDD_bday_yesterday():
    '''add_YYYYMMDD_bday_yesterday'''
    import datetime
    now = datetime.date.today() + datetime.timedelta(-1)
    today = str(now)
    AB.add('dummy', today)
    assert AB.check_day(-1)
    assert not AB.check_day(0)
    assert not AB.check_day(1)

@with_setup(setup, teardown)
def test_add_YYYYMMDD_bday_tomorrow():
    '''add_YYYY-MM-DD_bday_tomorrow'''
    import datetime
    now = datetime.date.today() + datetime.timedelta(1)
    today = str(now)
    AB.add('dummy', today)
    assert not AB.check_day(-1)
    assert not AB.check_day(0)
    assert AB.check_day(1)

@with_setup(setup, teardown)
def test_add_YYYYMMDD_nobday():
    '''add_YYYYMMDD_nobday'''
    import time
    today = '20001010'
    AB.add('dummy', today)
    assert not AB.check_day(0)

@with_setup(setup, teardown)
def test_add_YYYYMMDD_nobday2():
    '''add_YYYY-MM-DD_nobday'''
    import time
    today = '2000-10-10'
    AB.add('dummy', today)
    assert not AB.check_day(0)

#TODO manage_bdays(self, conf) not yet tested
