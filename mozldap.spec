%define	nspr_version	4.6
%define	nspr_evr	1:%{nspr_version}
%define	nss_version	3.11
%define	nss_evr		1:%{nss_version}
%define	svrcore_version	4.0.3
Summary:	Mozilla LDAP C SDK
Summary(pl.UTF-8):	Biblioteki Mozilla LDAP C SDK
Name:		mozldap
Version:	6.0.7
Release:	3
License:	MPL v1.1 or GPL v2+ or LGPL v2.1+
Group:		Libraries
Source0:	http://ftp.mozilla.org/pub/mozilla.org/directory/c-sdk/releases/v%{version}/src/%{name}-%{version}.tar.gz
# Source0-md5:	6e1b8ace4931a6839fe4cb027d23b5ac
Patch0:		%{name}-link.patch
Patch1:		%{name}-ac.patch
URL:		http://wiki.mozilla.org/LDAP_C_SDK
BuildRequires:	autoconf >= 2.13
BuildRequires:	automake
BuildRequires:	cyrus-sasl-devel >= 2.0
BuildRequires:	gawk
BuildRequires:	libstdc++-devel
BuildRequires:	nspr-devel >= %{nspr_evr}
BuildRequires:	nss-devel >= %{nss_evr}
BuildRequires:	perl-base
BuildRequires:	pkgconfig
BuildRequires:	svrcore-devel >= %{svrcore_version}
Requires:	nspr >= %{nspr_evr}
Requires:	nss >= %{nss_evr}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_noautoreqdep	libldap60.so libprldap60.so libssldap60.so libldif60.so

%description
The Mozilla LDAP C SDK is a set of libraries that allow applications
to communicate with LDAP directory servers. These libraries are
derived from the University of Michigan and Netscape LDAP libraries.
They use Mozilla NSPR and NSS for crypto.

%description -l pl.UTF-8
Mozilla LDAP C SDK to zestaw bibliotek pozwalających aplikacjom
komunikować się z serwerami usług katalogowych LDAP. Biblioteki te
wywodzą się z bibliotek LDAP University of Michigan i Netscape.
Wykorzystują biblioteki Mozilla NSPR i NSS do kryptografii.

%package devel
Summary:	Development files and examples for Mozilla LDAP C SDK
Summary(pl.UTF-8):	Pliki programistyczne i przykłady dla bibliotek Mozilla LDAP C SDK
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	nspr-devel >= %{nspr_evr}
Requires:	nss-devel >= %{nss_evr}

%description devel
Header and other files for doing development with the Mozilla LDAP C
SDK.

%description devel -l pl.UTF-8
Pliki nagłówkowe i inne do tworzenia oprogramowania z użyciem
bibliotek Mozilla LDAP C SDK

%package static
Summary:	Static Mozilla LDAP C SDK libraries
Summary(pl.UTF-8):	Statyczne biblioteki Mozilla LDAP C SDK
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static Mozilla LDAP C SDK libraries.

%description static -l pl.UTF-8
Statyczne biblioteki Mozilla LDAP C SDK.

%package tools
Summary:	Tools for the Mozilla LDAP C SDK
Summary(pl.UTF-8):	Narzędzia dla bibliotek Mozilla LDAP C SDK
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}
Requires:	svrcore >= %{svrcore_version}

%description tools
The mozldap-tools package provides the ldapsearch, ldapmodify, and
ldapdelete tools that use the Mozilla LDAP C SDK libraries.

%description tools -l pl.UTF-8
Ten pakiet dostarcza narzędzia ldapsearch, ldapmodify i ldapdelete
wykorzystujące biblioteki Mozilla LDAP C SDK.

%prep
%setup -q
%patch0 -p3
%patch1 -p3

%build
cp -f /usr/share/automake/config.sub c-sdk/config/autoconf
DISTDIR=$(pwd)/dist
cd c-sdk
%{__autoconf}
%configure \
%ifarch %{x8664} ia64 ppc64 s390x
	--enable-64bit \
%endif
	--disable-debug \
	--enable-clu \
	--enable-optimize \
	--with-dist-prefix=$DISTDIR \
	--with-sasl \
	--with-system-nspr \
	--with-system-nss \
	--with-system-svrcore

%ifarch %{x8664} ppc64 ia64 s390x
USE_64=1
export USE_64
%endif

%{__make} \
	XCFLAGS="%{rpmcflags}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{{%{_includedir},%{_libdir}}/mozldap,%{_bindir},%{_sysconfdir}/%{name}}

install dist/lib/lib*.so $RPM_BUILD_ROOT%{_libdir}
install dist/lib/lib*.a $RPM_BUILD_ROOT%{_libdir}
install dist/public/ldap/*.h $RPM_BUILD_ROOT%{_includedir}/mozldap
install dist/bin/ldap* $RPM_BUILD_ROOT%{_bindir}
# what really uses these and proper install dir?
install dist/etc/* $RPM_BUILD_ROOT%{_sysconfdir}/%{name}

install -d $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
cp -a c-sdk/ldap/examples/* $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

install -d $RPM_BUILD_ROOT%{_pkgconfigdir}
sed c-sdk/mozldap.pc.in -e "
	s,%%prefix%%,%{_prefix},g
	s,%%exec_prefix%%,%{_prefix},g
	s,%%libdir%%,%{_libdir},g
	s,%%includedir%%,%{_includedir}/mozldap,g
	s,%%bindir%%,%{_bindir},g
	s,%%major%%,6,g
	s,%%minor%%,0,g
	s,%%submin%%,7,g
	s,%%libsuffix%%,60,g
	s,%%NSPR_VERSION%%,%{nspr_version},g
	s,%%NSS_VERSION%%,%{nss_version},g
	s,%%MOZLDAP_VERSION%%,%{version},g
" > $RPM_BUILD_ROOT%{_pkgconfigdir}/mozldap.pc

cd $RPM_BUILD_ROOT%{_libdir}
for file in lib*.so; do
	mv $file $file.%{version}
	ln -s $file.%{version} $file
done

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libldap60.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libldap60.so
%attr(755,root,root) %{_libdir}/libprldap60.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libprldap60.so
%attr(755,root,root) %{_libdir}/libssldap60.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libssldap60.so
%attr(755,root,root) %{_libdir}/libldif60.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libldif60.so

%files devel
%defattr(644,root,root,755)
%{_includedir}/mozldap
%{_pkgconfigdir}/mozldap.pc
%{_examplesdir}/%{name}-%{version}

%files static
%defattr(644,root,root,755)
%{_libdir}/libiutil60.a
%{_libdir}/liblber60.a
%{_libdir}/libldap60.a
%{_libdir}/libldif60.a

%files tools
%defattr(644,root,root,755)
%dir %{_sysconfdir}/%{name}
%{_sysconfdir}/%{name}/ldapfilter.conf
%{_sysconfdir}/%{name}/ldapfriendly
%{_sysconfdir}/%{name}/ldapsearchprefs.conf
%{_sysconfdir}/%{name}/ldaptemplates.conf
# NOTE: these probably collide with openldap
%attr(755,root,root) %{_bindir}/ldapcmp
%attr(755,root,root) %{_bindir}/ldapcompare
%attr(755,root,root) %{_bindir}/ldapdelete
%attr(755,root,root) %{_bindir}/ldapmodify
%attr(755,root,root) %{_bindir}/ldappasswd
%attr(755,root,root) %{_bindir}/ldapsearch
