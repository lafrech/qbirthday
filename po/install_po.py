import sys
import os

destdir = sys.argv[1]+"/usr/share/locale"

for f in os.listdir("."):
    if f.endswith(".po"):
        start = "".join(f.split(".")[:-1])
        cmd = "msgfmt "+f+" -o "+destdir+"/"+start+"/LC_MESSAGES/gbirthday.mo"
        #print "calling:", cmd
        os.popen('mkdir -p "'+ destdir+'/'+start+'/LC_MESSAGES/"')
        os.popen(cmd)
