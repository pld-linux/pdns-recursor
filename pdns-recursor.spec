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
Version:	5.4.9
Release:	1
License:	GPL v2
Group:		Networking/Daemons
Source0:	https://downloads.powerdns.com/releases/%{name}-%{version}.tar.xz
# Source0-md5:	c5e797f095459cb90d37c12a8acd3dc6
Source1:	%{name}.init
# cd rec-rust-lib/rust
# cargo vendor-filterer --platform='*-unknown-linux-*' --tier=2
# cd ../..
# tar cJf %%{name}-crates-%%{version}.tar.xz rec-rust-lib/rust/vendor
Source2:	%{name}-crates-%{version}.tar.xz
# Source2-md5:	975757920a5dc3124e352260898ba67b
Patch0:		%{name}-nodcachedir.patch
Patch1:		%{name}-CVE-2026-52684.patch
URL:		http://www.powerdns.com/
BuildRequires:	boost-devel >= 1.54.0
BuildRequires:	cargo >= 1.64
BuildRequires:	curl-devel >= 7.21.3
BuildRequires:	fstrm-devel
BuildRequires:	libcap-devel
BuildRequires:	libsodium-devel
%ifarch x32
BuildRequires:	lua54-devel
%else
BuildRequires:	luajit-devel >= 2.0.2
%endif
BuildRequires:	openssl-devel
BuildRequires:	python3 >= 3.6
BuildRequires:	rpmbuild(macros) >= 2.050
BuildRequires:	rust
BuildRequires:	systemd-devel
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
%{?rust_req}
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
ExclusiveArch:	%{rust_arches}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
PowerDNS Recursor is a high performance non authoritative/recursing
DNS server.

%description -l pl.UTF-8
PowerDNS Recursor jest wysokowydajnym buforującym serwerem DNS.

%prep
%setup -q -a2
%patch -P0 -p1
%patch -P1 -p3

# use our offline registry
export CARGO_HOME="$(pwd)/.cargo"

mkdir -p "$CARGO_HOME"
cat >.cargo/config.toml <<EOF
[net]
offline = true

[source.crates-io]
replace-with = 'vendored-sources'

[source.vendored-sources]
directory = '$PWD/rec-rust-lib/rust/vendor'
EOF

%build
export CARGO_HOME="$(pwd)/.cargo"
export RUSTFLAGS="%{rpmrustflags}"
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
%ifarch %{ix86} x32
	--enable-experimental-64bit-time_t-support-on-glibc \
%endif
	--sysconfdir=%{_sysconfdir}/%{name} \
	--enable-dnstap \
	--enable-nod \
	--enable-systemd \
	--with-libcap \
	--with-libsodium \
	--with-service-group=djbdns

%{__make} V=1

%install
rm -rf $RPM_BUILD_ROOT
export CARGO_HOME="$(pwd)/.cargo"
export RUSTFLAGS="%{rpmrustflags}"

%{__make} install \
	SYSTEMD_DIR=%{systemdunitdir} \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
mv $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/recursor.yml{-dist,}
%{__sed} -i -e "s/^#   setgid: ''$/   setgid: 'djbdns'/g"		$RPM_BUILD_ROOT%{_sysconfdir}/%{name}/recursor.yml
%{__sed} -i -e "s/^#   setuid: ''$/   setuid: 'pdns-recursor'/g"	$RPM_BUILD_ROOT%{_sysconfdir}/%{name}/recursor.yml
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
