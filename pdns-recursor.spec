Summary:	Modern, advanced and high performance recursing/non authoritative nameserver
Summary(pl.UTF-8):	Nowoczesny i zaawansowany buforujący serwer DNS o wysokiej wudajności
Name:		pdns-recursor
Version:	3.3
Release:	1
License:	GPL
Group:		Networking/Daemons
Source0:	http://downloads.powerdns.com/releases/%{name}-%{version}.tar.bz2
# Source0-md5:	87daeeebb6f7af9e07814ff6c43300dd
Source1:	%{name}.init
Source2:	%{name}.conf
URL:		http://www.powerdns.com/
BuildRequires:	boost-devel
Requires(post):	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	rc-scripts
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
	CONFIGDIR="%{_sysconfdir}/%{name}" \
	CC="%{__cc}" \
	CXX="%{__cxx}" \
	OPTFLAGS="%{rpmcxxflags}" \
	LDFLAGS="%{rpmldflags} -pthread"

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	BINDIR="%{_bindir}" \
	SBINDIR="%{_sbindir}" \
	CONFIGDIR="%{_sysconfdir}/%{name}" \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/init.d

rm -f $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/recursor.conf-dist
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/recursor.conf

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 32 djbdns
%useradd -u 68 -d /usr/share/empty -s /bin/false -c "PowerDNS Resolver User" -g djbdns pdns-recursor

%post
/sbin/chkconfig --add pdns-recursor
%service pdns-recursor restart

%preun
if [ "$1" = "0" ]; then
	%service pdns-recursor stop
	/sbin/chkconfig --del pdns-recursor
fi

%postun
if [ "$1" = "0" ]; then
	%userremove pdns-recursor
	%groupremove djbdns
fi

%files
%defattr(644,root,root,755)
%doc README
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%dir %{_sysconfdir}/%{name}
%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/recursor.conf
%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_bindir}/*
%{_mandir}/man1/*
