bindir = /usr/bin
datadir = /usr/share
pixmaps = $(datadir)/pixmaps
version = 0.5.1

install = install -p
mkdir = mkdir -p

default:
	echo Nothing to do.

clean:
	rm -f po/untitled.pot
	rm -f *.tar.*
	rm -f gbirthday.desktop

install:
	intltool-merge -d ./po ./gbirthday.desktop.in ./gbirthday.desktop
	$(install) -m 755 -d $(DESTDIR)$(datadir)/gbirthday
	$(install) -m 755 -d $(DESTDIR)$(pixmaps)/gbirthday
	$(install) -m 644 pics/*.png $(DESTDIR)$(pixmaps)/gbirthday/
	$(install) -m 755  src/* $(DESTDIR)$(datadir)/gbirthday/
	$(mkdir) $(DESTDIR)$(datadir)/applications/
	$(install) -m 644 gbirthday.desktop \
		$(DESTDIR)$(datadir)/applications/
	$(mkdir) $(DESTDIR)$(bindir)
	ln -s $(datadir)/gbirthday/gbirthday.py \
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
		-zcf gbirthday-$(version).tar.gz *

tar.lzma: clean
	tar --use-compress-program=lzma --exclude=.git \
		-cf gbirthday-$(version).tar.lzma *

pot:
	cd po && intltool-update --pot

rpm:	tar.lzma
	cp gbirthday-*.tar.lzma ~/rpmbuild/SOURCES
	rpmbuild -ba gbirthday.spec
