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
"""
This snipped installs the translated files into the proper places.
"""
import sys
import os

DESTDIR = sys.argv[1]+"/usr/share/locale/"

for f in os.listdir("."):
    if f.endswith(".po"):
        start = "".join(f.split(".")[:-1])
        cmd = "msgfmt "+f+" -o "+DESTDIR+start+"/LC_MESSAGES/gbirthday.mo"

        os.popen('mkdir -p "'+ DESTDIR+start+'/LC_MESSAGES/"')
        os.popen(cmd)
