bindir = /usr/bin
datadir = /usr/share
default:
	echo Nothing to do.

install:
	echo Creating gbirthday folder
	mkdir -p $(DESTDIR)$(datadir)/gbirthday
	echo $(DESTDIR)
	echo asdf
	chmod 775 $(DESTDIR)$(datadir)/gbirthday
	echo Creating pics folder
	mkdir $(DESTDIR)$(datadir)/gbirthday/pics
	chmod 775 $(DESTDIR)$(datadir)/gbirthday/pics
	echo Moving pics to pics folder
	cp -v pics/*.png $(DESTDIR)$(datadir)/gbirthday/pics
	chmod 664 $(DESTDIR)$(datadir)/gbirthday/pics/*.png
	echo moving python file to gbirthday folder
	cp -v gbirthday.py $(DESTDIR)$(datadir)/gbirthday/
	chmod 775 $(DESTDIR)$(datadir)/gbirthday/gbirthday.py
	echo Creating languages folder
	mkdir $(DESTDIR)$(datadir)/gbirthday/languages
	chmod 775 $(DESTDIR)$(datadir)/gbirthday/languages/
	echo Moving languages to languages floder
	cp -v languages/*.lang $(DESTDIR)$(datadir)/gbirthday/languages/
	echo Creating menu item
	mkdir -p $(DESTDIR)$(datadir)/applications/
	cp -v gbirthday.desktop $(DESTDIR)$(datadir)/applications/
	echo Linking python file in bin folder
	mkdir -p $(DESTDIR)$(bindir)
	mv $(DESTDIR)$(datadir)/gbirthday/gbirthday.py $(DESTDIR)$(bindir)/gbirthday
	chmod 775 $(DESTDIR)$(bindir)/gbirthday

uninstall:
	rm -rvf $(DESTDIR)$(datadir)/gbirthday
	rm -rvf $(DESTDIR)$(datadir)/applications/gbirthday.desktop
	rm -rvf $(DESTDIR)$(bindir)/gbirthday
