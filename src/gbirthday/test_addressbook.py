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
from .addressbook import AddressBook

AB = None

def setup():
    '''Setup addressbook.'''
    global AB
    AB = AddressBook()

def teardown():
    '''Clean addressbook.'''
    global AB
    AB = None

@with_setup(setup, teardown)
def test_init_no_bday():
    '''init_no_bday'''
    assert not AB.check_day(0)

@with_setup(setup, teardown)
def test_add_yyyymmdd_bday():
    '''add_YYYYMMDD_bday'''
    import time
    today = time.strftime("%Y%m%d", time.localtime(time.time()))
    AB.add('dummy', today)
    assert AB.check_day(0) == ['dummy']
    # today birthday -> needs to be in specific period
    assert AB.bdays_in_period()

@with_setup(setup, teardown)
def test_add_yyyymmdd_bday2():
    '''add_YYYY-MM-DD_bday'''
    import time
    today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    AB.add('dummy', today)
    assert AB.check_day(0) == ['dummy']
    # today birthday -> needs to be in specific period
    assert AB.bdays_in_period()

@with_setup(setup, teardown)
def test_add_bday_yesterday():
    '''add_YYYYMMDD_bday_yesterday'''
    import datetime
    now = datetime.date.today() + datetime.timedelta(-1)
    today = str(now)
    AB.add('dummy', today)
    assert AB.check_day(-1) == ['dummy']
    assert not AB.check_day(0)
    assert not AB.check_day(1)

@with_setup(setup, teardown)
def test_add_bday_tomorrow():
    '''add_YYYY-MM-DD_bday_tomorrow'''
    import datetime
    now = datetime.date.today() + datetime.timedelta(1)
    today = str(now)
    AB.add('dummy', today)
    assert not AB.check_day(-1)
    assert not AB.check_day(0)
    assert AB.check_day(1) == ['dummy']

@with_setup(setup, teardown)
def test_add_bday_twice():
    '''add_YYYY-MM-DD_bday_twice'''
    import time
    today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    AB.add('dummy', today)
    AB.add('dummy2', today)
    assert AB.check_day(0) == ['dummy', 'dummy2']
    # today birthday -> needs to be in specific period
    assert AB.bdays_in_period()

@with_setup(setup, teardown)
def test_add_bday_yesterday_twice():
    '''add_YYYYMMDD_bday_yesterday_twice'''
    import datetime
    now = datetime.date.today() + datetime.timedelta(-1)
    today = str(now)
    AB.add('dummy', today)
    AB.add('dummy2', today)
    assert AB.check_day(-1) == ['dummy', 'dummy2']
    assert not AB.check_day(0)
    assert not AB.check_day(1)

@with_setup(setup, teardown)
def test_add_bday_tomorrow_twice():
    '''add_YYYY-MM-DD_bday_tomorrow_twice'''
    import datetime
    now = datetime.date.today() + datetime.timedelta(1)
    today = str(now)
    AB.add('dummy', today)
    AB.add('dummy2', today)
    assert not AB.check_day(-1)
    assert not AB.check_day(0)
    assert AB.check_day(1) == ['dummy', 'dummy2']

@with_setup(setup, teardown)
def test_add_nobday():
    '''add_YYYYMMDD_nobday'''
    today = '20001010'
    AB.add('dummy', today)
    assert not AB.check_day(0)
    # birthday far away -> nothing in specific period
    assert not AB.bdays_in_period()

@with_setup(setup, teardown)
def test_add_nobday2():
    '''add_YYYY-MM-DD_nobday'''
    today = '2000-10-10'
    AB.add('dummy', today)
    assert not AB.check_day(0)
    # birthday far away -> nothing in specific period
    assert not AB.bdays_in_period()

@with_setup(setup, teardown)
def test_update():
    '''test, if update works with adding correctly'''
    import datetime
    now = datetime.date.today()
    now = str(now)
    assert not AB.check_day(0)
    AB.add('dummy', now)
    # add does not fill bdays_dict
    assert not AB.bdays_dict
    # but check does
    assert AB.check_day(0)
    assert AB.bdays_dict

@with_setup(setup, teardown)
def test_run_reload():
    '''simply run reload() once'''
    assert not AB.check_day(0)
    AB.reload()
    assert not AB.check_day(0)
