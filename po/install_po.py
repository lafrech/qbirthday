"""Install translated files into the proper places"""

import sys
import os

DESTDIR = sys.argv[1]+"/usr/share/locale/"

for f in os.listdir("."):
    if f.endswith(".po"):
        start = "".join(f.split(".")[:-1])
        cmd = "msgfmt "+f+" -o "+DESTDIR+start+"/LC_MESSAGES/qbirthday.mo"

        os.popen('mkdir -p "'+ DESTDIR+start+'/LC_MESSAGES/"')
        os.popen(cmd)
