Name:			gbirthday
Version:		0.4.1
Release:		5%{?dist}
Summary:		Birthday reminder for evolution
Group:			User Interface/Desktops
License:		GPLv2+
URL:			http://gbirthday.sourceforge.net
Source:			http://downloads.sourceforge.net/gbirthday/gbirthday-%{version}.tar.gz
BuildRoot:		%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:		noarch

BuildRequires:	desktop-file-utils
Requires:		evolution
Requires:		python
Requires:		pygtk2

%description
GBirthday is a birthday reminder application that helps you to remember 
your evolution contacts' birthdays.
It puts an icon on notification area which will blink when there is any 
of your contacts' birthday today. You can also check if there is any of 
your contacs' birthday on next days.

%prep
%setup -q -c %{name}-%{version}

%build

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
desktop-file-validate %{buildroot}/%{_datadir}/applications/%{name}.desktop
mkdir -p %{buildroot}%{_sysconfdir}/xdg/autostart/
desktop-file-install \
	--add-category="TrayIcon" \
	--add-only-show-in="GNOME;KDE;XFCE;" \
	--dir=%{buildroot}%{_sysconfdir}/xdg/autostart/ \
	%{buildroot}/%{_datadir}/applications/%{name}.desktop

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc Changelog COPYING
%{_bindir}/gbirthday
%{_datadir}/applications/%{name}.desktop
%{_datadir}/gbirthday/
%{_datadir}/pixmaps/gbirthday
%config(noreplace) %{_sysconfdir}/xdg/autostart/%{name}.desktop

%changelog
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
