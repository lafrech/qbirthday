bindir = /usr/bin
datadir = /usr/share
pixmaps = $(datadir)/pixmaps
version = master

default:
	echo Nothing to do.

clean:
	rm -f po/untitled.pot
	rm -f *.tar.*
	rm -f gbirthday.desktop

install:
	intltool-merge -d ./po ./gbirthday.desktop.in ./gbirthday.desktop
	install -p -m 755 -d $(DESTDIR)$(datadir)/gbirthday
	install -p -m 755 -d $(DESTDIR)$(pixmaps)/gbirthday
	install -p -m 644 pics/*.png $(DESTDIR)$(pixmaps)/gbirthday/
	install -p -m 755  gbirthday.py $(DESTDIR)$(datadir)/gbirthday/
	install -p -m 755 -d $(DESTDIR)$(datadir)/gbirthday/languages/
	install -p -m 644 languages/*.lang \
		$(DESTDIR)$(datadir)/gbirthday/languages/
	mkdir -p $(DESTDIR)$(datadir)/applications/
	install -p -m 644 gbirthday.desktop $(DESTDIR)$(datadir)/applications/
	mkdir -p $(DESTDIR)$(bindir)
	install -p -m 755 $(DESTDIR)$(datadir)/gbirthday/gbirthday.py \
		$(DESTDIR)$(bindir)/gbirthday
	cd po && python install_po.py $(DESTDIR)

uninstall:
	rm -rvf $(DESTDIR)$(datadir)/gbirthday
	rm -rvf $(DESTDIR)$(pixmaps)/gbirthday
	rm -rvf $(DESTDIR)$(datadir)/applications/gbirthday.desktop
	rm -rvf $(DESTDIR)$(bindir)/gbirthday
	rm -rvf $(DESTDIR)$(datadir)/locale/*/LC_MESSAGES/gbirthday.mo

tar.gz:	clean
	tar --exclude=.git \
		-zcvf gbirthday-$(version).tar.gz *

tar.lzma: clean
	tar --use-compress-program=lzma --exclude=.git \
		-cvf gbirthday-$(version).tar.lzma *

pot:
	cd po && intltool-update --pot

rpm:	tar.lzma
	cp gbirthday-*.tar.lzma ~/rpmbuild/SOURCES
	rpmbuild -ba gbirthday.spec
