bindir = /usr/bin
datadir = /usr/share
sitelib = $(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib(True)")
pixmaps = $(datadir)/pixmaps
version = 0.6.10
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
	$(rm) qbirthday.desktop
	$(rm) -r qbirthday-$(version) BUILDROOT noarch
	$(rm) qbirthday*.src.rpm
	find . -name \*.pyc -delete

install:
	intltool-merge -d ./po ./qbirthday.desktop.in ./qbirthday.desktop
	sed -i "s|@VER@|$(version)|g" src/qbirthday/__init__.py
	sed -i "s|/usr/bin/python|$(python)|g" src/qb
	$(mkdir) $(DESTDIR)$(pixmaps)
	$(install) -m 644 pics/qbirthday.png $(DESTDIR)$(pixmaps)
	$(mkdir) $(DESTDIR)$(sitelib)
	$(cp) src/qbirthday/ $(DESTDIR)$(sitelib)
	$(rm) $(DESTDIR)$(sitelib)/qbirthday/test*.py
	$(mkdir) $(DESTDIR)$(datadir)/applications/
	$(install) -m 644 qbirthday.desktop \
		$(DESTDIR)$(datadir)/applications/
	$(mkdir) $(DESTDIR)$(bindir)
	$(install) -m 755 src/qb $(DESTDIR)$(bindir)/qbirthday
	cd po && $(python) install_po.py $(DESTDIR)

uninstall:
	$(rm) $(DESTDIR)$(bindir)/qbirthday
	$(rm) $(DESTDIR)$(datadir)/applications/qbirthday.desktop
	$(rm) $(DESTDIR)$(datadir)/locale/*/LC_MESSAGES/qbirthday.mo
	$(rm) $(DESTDIR)$(pixmaps)/qbirthday.png
	$(rm) -r $(DESTDIR)$(sitelib)/qbirthday

snapshot: clean
	mkdir -p $(DIST_DIR)/qbirthday-$(version)
	rsync -avz --exclude=.* --exclude=$(DIST_DIR) ./ $(DIST_DIR)/qbirthday-$(version)

tar.gz:	snapshot
	cd $(DIST_DIR) && $(tar) -zcf qbirthday-$(version).tar.gz qbirthday-$(version)

tar.xz: snapshot
	cd $(DIST_DIR) && $(tar) -Jcf qbirthday-$(version).tar.xz qbirthday-$(version)

test:
	nosetests -v --with-coverage --cover-package=qbirthday

pot:
	cd po && intltool-update --pot -g qbirthday

rpm:	tar.xz
	cp qbirthday-*.tar.xz ~/rpmbuild/SOURCES
	rpmbuild -ba qbirthday.spec
