Summary:	Modern, advanced and high performance recursing/non authoritative nameserver
Summary(pl.UTF-8):	Nowoczesny i zaawansowany buforujący serwer DNS o wysokiej wydajności
Name:		pdns-recursor
Version:	3.6.0
Release:	1
License:	GPL
Group:		Networking/Daemons
Source0:	http://downloads.powerdns.com/releases/%{name}-%{version}.tar.bz2
# Source0-md5:	95f21e6d64c1332aeca9fa3f786dd0a2
Source1:	%{name}.init
URL:		http://www.powerdns.com/
BuildRequires:	boost-devel
Requires(post):	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	rc-scripts
Requires:	systemd-units
Provides:	group(djbdns)
Provides:	nameserver
Provides:	user(pdns-recursor)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
PowerDNS Recursor is a high performance non authoritative/recursing
DNS server.

%description -l pl.UTF-8
PowerDNS Recursor jest wysokowydajnym buforującym serwerem DNS.

%prep
%setup -q

%build
%{__make} \
	BINDIR="%{_bindir}" \
	SBINDIR="%{_sbindir}" \
	SYSCONFDIR="%{_sysconfdir}/%{name}" \
	CC="%{__cc}" \
	CXX="%{__cxx}" \
	OPTFLAGS="%{rpmcxxflags}" \
	LDFLAGS="%{rpmldflags} -pthread"

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	BINDIR="%{_bindir}" \
	SBINDIR="%{_sbindir}" \
	SYSCONFDIR="%{_sysconfdir}/%{name}" \
	DESTDIR=$RPM_BUILD_ROOT

rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/init.d
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install -d $RPM_BUILD_ROOT%{systemdunitdir}
install contrib/systemd-pdns-recursor.service $RPM_BUILD_ROOT%{systemdunitdir}/%{name}.service
mv $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/recursor.conf-dist $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/recursor.conf
sed -i 's/^# setgid=$/setgid=djbdns/g' $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/recursor.conf
sed -i 's/^# setuid=$/setuid=pdns-recursor/g' $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/recursor.conf

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 32 djbdns
%useradd -u 68 -d /usr/share/empty -s /bin/false -c "PowerDNS Resolver User" -g djbdns pdns-recursor

%post
/sbin/chkconfig --add pdns-recursor
%service pdns-recursor restart
%systemd_post %{name}.service

%preun
if [ "$1" = "0" ]; then
	%service pdns-recursor stop
	/sbin/chkconfig --del pdns-recursor
fi
%systemd_preun %{name}.service

%postun
if [ "$1" = "0" ]; then
	%userremove pdns-recursor
	%groupremove djbdns
fi
%systemd_reload

%files
%defattr(644,root,root,755)
%doc README
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(644,root,root) %{systemdunitdir}/%{name}.service
%dir %{_sysconfdir}/%{name}
%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/recursor.conf
%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_bindir}/*
%{_mandir}/man1/*
