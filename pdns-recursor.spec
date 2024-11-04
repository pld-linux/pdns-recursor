# TODO:
# - consider
#	--enable-dns-over-tls
#	--with-libdecaf / libsodium
#	--with-net-snmp
# - SysV init script requires update.
# Some resources are generated using regal.
Summary:	Modern, advanced and high performance recursing/non authoritative nameserver
Summary(pl.UTF-8):	Nowoczesny i zaawansowany buforujący serwer DNS o wysokiej wydajności
Name:		pdns-recursor
Version:	5.1.2
Release:	1
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://downloads.powerdns.com/releases/%{name}-%{version}.tar.bz2
# Source0-md5:	26d26a034649a2ea04c67fcde8782598
Source1:	%{name}.init
URL:		http://www.powerdns.com/
BuildRequires:	boost-devel >= 1.54.0
BuildRequires:	cargo >= 1.64
BuildRequires:	curl-devel >= 7.21.3
BuildRequires:	fstrm-devel
BuildRequires:	libcap-devel
BuildRequires:	libsodium-devel
BuildRequires:	luajit-devel >= 2.0.2
BuildRequires:	openssl-devel
BuildRequires:	protobuf-devel
BuildRequires:	python3 >= 3.6
BuildRequires:	systemd-devel
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
%{__sed} -i -e 's/localstatedir/nodcachedir/g' settings/rust/Makefile.am

%build
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--sysconfdir=%{_sysconfdir}/%{name} \
	--with-service-group=djbdns

%{__make} V=1

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	SYSTEMD_DIR=%{systemdunitdir} \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
mv $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/recursor.yml-dist	$RPM_BUILD_ROOT%{_sysconfdir}/%{name}/recursor.yml
%{__sed} -i -e "s/^#   setgid: ''$/setgid: 'djbdns'/g"		$RPM_BUILD_ROOT%{_sysconfdir}/%{name}/recursor.yml
%{__sed} -i -e "s/^#   setuid: ''$/setuid: 'pdns-recursor'/g"	$RPM_BUILD_ROOT%{_sysconfdir}/%{name}/recursor.yml
%{__mkdir_p} $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/{nod,udr}

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
%attr(644,root,root) %{systemdunitdir}/%{name}*.service
%dir %{_sysconfdir}/%{name}
%attr(640,root,djbdns) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/recursor.yml
%attr(755,root,root) %{_bindir}/rec_control
%attr(755,root,root) %{_sbindir}/pdns_recursor
%{_mandir}/man1/*.1*
%attr(775,root,djbdns) %{_localstatedir}/lib/%{name}
