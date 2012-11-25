bindir = /usr/bin
datadir = /usr/share
sitelib = /usr/lib/python2.6/site-packages
pixmaps = $(datadir)/pixmaps
version = 0.6.7
DIST_DIR = dist

install = install -p
mkdir = mkdir -p
cp = cp -a
rm = rm -f
tar = tar --exclude=.git --exclude=*.pyc

python = /usr/bin/python

default:
	echo Nothing to do.

clean:
	$(rm) po/untitled.pot
	$(rm) *.tar.*
	$(rm) gbirthday.desktop
	$(rm) -r gbirthday-$(version) BUILDROOT noarch
	$(rm) gbirthday*.src.rpm
	find . -name \*.pyc -delete

install:
	intltool-merge -d ./po ./gbirthday.desktop.in ./gbirthday.desktop
	sed -i "s|@VER@|$(version)|g" src/gbirthday/__init__.py
	sed -i "s|/usr/bin/python|$(python)|g" src/gb
	$(mkdir) $(DESTDIR)$(pixmaps)
	$(install) -m 644 pics/gbirthday.png $(DESTDIR)$(pixmaps)
	$(mkdir) $(DESTDIR)$(sitelib)
	$(cp) src/gbirthday/ $(DESTDIR)$(sitelib)
	$(rm) $(DESTDIR)$(sitelib)/gbirthday/test*.py
	$(mkdir) $(DESTDIR)$(datadir)/applications/
	$(install) -m 644 gbirthday.desktop \
		$(DESTDIR)$(datadir)/applications/
	$(mkdir) $(DESTDIR)$(bindir)
	$(install) -m 755 src/gb $(DESTDIR)$(bindir)/gbirthday
	cd po && $(python) install_po.py $(DESTDIR)

uninstall:
	$(rm) $(DESTDIR)$(bindir)/gbirthday
	$(rm) $(DESTDIR)$(datadir)/applications/gbirthday.desktop
	$(rm) $(DESTDIR)$(datadir)/locale/*/LC_MESSAGES/gbirthday.mo
	$(rm) $(DESTDIR)$(pixmaps)/gbirthday.png
	$(rm) -r $(DESTDIR)$(sitelib)/gbirthday

snapshot: clean
	mkdir -p $(DIST_DIR)/gbirthday-$(version)
	rsync -avz --exclude=.git --exclude=$(DIST_DIR) ./ $(DIST_DIR)/gbirthday-$(version)

tar.gz:	snapshot
	cd $(DIST_DIR) && $(tar) -zcf gbirthday-$(version).tar.gz gbirthday-$(version)

tar.xz: snapshot
	cd $(DIST_DIR) && $(tar) -Jcf gbirthday-$(version).tar.xz gbirthday-$(version)

test:
	nosetests -v --with-coverage --cover-package=gbirthday

pot:
	cd po && intltool-update --pot -g gbirthday

rpm:	tar.xz
	cp gbirthday-*.tar.xz ~/rpmbuild/SOURCES
	rpmbuild -ba gbirthday.spec
