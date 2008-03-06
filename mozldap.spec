%define	nspr_version	4.6
%define	nspr_evr	1:%{nspr_version}
%define	nss_version	3.11
%define	nss_evr		1:%{nss_version}
%define	svrcore_version	4.0.3
Summary:	Mozilla LDAP C SDK
Summary(pl.UTF-8):	Biblioteki Mozilla LDAP C SDK
Name:		mozldap
Version:	6.0.5
Release:	1
License:	MPL v1.1 or GPL v2+ or LGPL v2.1+
Group:		Libraries
Source0:	ftp://ftp.mozilla.org/pub/mozilla.org/directory/c-sdk/releases/v%{version}/src/mozldap-%{version}.tar.gz
# Source0-md5:	9719bd5b9efc13f810c85a47fb8c6412
Patch0:		%{name}-link.patch
URL:		http://wiki.mozilla.org/LDAP_C_SDK
BuildRequires:	autoconf >= 2.13
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

%define		_noautoreqdep	libldap60.so libprldap60.so libssldap60.so

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
%patch0 -p1

%build
cd mozilla/directory/c-sdk
%{__autoconf}
%configure \
%ifarch %{x8664} ia64 ppc64 s390x
	--enable-64bit \
%endif
	--disable-debug \
	--enable-clu \
	--enable-optimize \
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
install -d $RPM_BUILD_ROOT{%{_includedir},%{_libdir}}/mozldap

cd mozilla
install dist/lib/lib*ldap*.so $RPM_BUILD_ROOT%{_libdir}
install dist/bin/ldap* $RPM_BUILD_ROOT%{_libdir}/mozldap
install dist/public/ldap/*.h $RPM_BUILD_ROOT%{_includedir}/mozldap
install directory/c-sdk/ldap/libraries/lib*/lib*60.a $RPM_BUILD_ROOT%{_libdir}

install -d $RPM_BUILD_ROOT%{_datadir}/mozldap%{_sysconfdir}
cd directory/c-sdk/ldap
cp -r examples $RPM_BUILD_ROOT%{_datadir}/mozldap
install examples/xmplflt.conf $RPM_BUILD_ROOT%{_datadir}/mozldap%{_sysconfdir}
install libraries/libldap/*.conf $RPM_BUILD_ROOT%{_datadir}/mozldap%{_sysconfdir}
cd -

install -d $RPM_BUILD_ROOT%{_pkgconfigdir}
sed directory/c-sdk/mozldap.pc.in -e "
	s,%%libdir%%,%{_libdir},g
	s,%%prefix%%,%{_prefix},g
	s,%%exec_prefix%%,%{_prefix},g
	s,%%includedir%%,%{_includedir}/mozldap,g
	s,%%NSPR_VERSION%%,%{nspr_version},g
	s,%%NSS_VERSION%%,%{nss_version},g
	s,%%MOZLDAP_VERSION%%,%{version},g
" > $RPM_BUILD_ROOT%{_pkgconfigdir}/mozldap.pc

cd $RPM_BUILD_ROOT%{_libdir}
for file in libssldap60.so libprldap60.so libldap60.so; do
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

%files devel
%defattr(644,root,root,755)
%{_includedir}/mozldap
%{_pkgconfigdir}/mozldap.pc
%{_datadir}/mozldap

%files static
%defattr(644,root,root,755)
%{_libdir}/libiutil60.a
%{_libdir}/liblber60.a
%{_libdir}/libldap60.a
%{_libdir}/libldif60.a

%files tools
%defattr(644,root,root,755)
%dir %{_libdir}/mozldap
%attr(755,root,root) %{_libdir}/mozldap/ldap*
