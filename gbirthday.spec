%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           gbirthday
Version:        0.5.3
Release:        1%{?dist}
Summary:        Birthday reminder for Evolution and some others
Group:          User Interface/Desktops
License:        GPLv2+
URL:            http://gbirthday.sourceforge.net
Source:         http://downloads.sourceforge.net/gbirthday/gbirthday-%{version}.tar.xz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

BuildRequires:  desktop-file-utils
BuildRequires:  gettext
BuildRequires:  intltool
Requires:       evolution
Requires:       python
Requires:       MySQL-python
Requires:       pygtk2

%description
GBirthday is a birthday reminder application that helps you to remember 
your Evolution, Thunderbird, Sunbird contacts' birthdays or from a MySQL
Server or a CSV File.
It puts an icon on notification area which will blink when there is any 
of your contacts' birthday today. You can also check if there is any of 
your contacs' birthday on next days.

%prep
%setup -q -c %{name}-%{version}

%build

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} sitelib=%{python_sitelib}
desktop-file-validate %{buildroot}/%{_datadir}/applications/%{name}.desktop
mkdir -p %{buildroot}%{_sysconfdir}/xdg/autostart/
desktop-file-install \
        --add-category="TrayIcon" \
        --add-only-show-in="GNOME;KDE;XFCE;" \
        --dir=%{buildroot}%{_sysconfdir}/xdg/autostart/ \
        %{buildroot}/%{_datadir}/applications/%{name}.desktop

%find_lang %{name}

%clean
rm -rf %{buildroot}

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc Changelog COPYING README
%{_bindir}/gbirthday
%{_datadir}/applications/%{name}.desktop
%{python_sitelib}/gbirthday/
%{_datadir}/pixmaps/gbirthday.png
%config(noreplace) %{_sysconfdir}/xdg/autostart/%{name}.desktop

%changelog
* Sat Nov 21 2009 Thomas Spura <tomspur@fedoraproject.org> 0.5.3-1
- new version

* Fri Oct 30 2009 Thomas Spura <tomspur@fedoraproject.org> 0.5.2-3
- BR: intltool

* Fri Oct 30 2009 Thomas Spura <tomspur@fedoraproject.org> 0.5.2-2
- little problem with 'make tag'

* Fri Oct 30 2009 Thomas Spura <tomspur@fedoraproject.org> 0.5.2-1
- New Release

* Wed Sep 23 2009 Thomas Spura <tomspur@fedoraproject.org> 0.5.1-1
- New Release
- Changing description (now also supports Thunderbird, Sunbird...

* Tue Aug 11 2009 Thomas Spura <tomspur@fedoraproject.org> 0.4.2-1
- new release

* Sat Aug 8 2009 Thomas Spura <tomspur@fedoraproject.org> 0.4.1-5
- desktop file is now config
- only start if a system tray is present

* Fri Jul 31 2009 Thomas Spura <tomspur@fedoraproject.org> 0.4.1-4
- License is GPLv2+
- deleting patches now applied upstream

* Wed Jul 22 2009 Thomas Spura <tomspur@fedoraproject.org> 0.4.1-3
- use only buildroot

* Wed Jul 22 2009 Thomas Spura <tomspur@fedoraproject.org> 0.4.1-2
- changing name of *.patch
- properly install .desktop-file in /etc/xdg/autostart/ too
- new Group: "User Interface/Desktops"

* Thu Jul 21 2009 Thomas Spura <tomspur@fedoraproject.org> 0.4.1-1
- Inital version of this spec file
