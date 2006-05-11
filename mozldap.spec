%define	nspr_version	4.6
%define	nspr_evr 1:%{nspr_version}
%define	nss_version	3.11
%define	nss_evr 1:%{nss_version}
%define	svrcore_version	4.0.1
%define	major		5
%define	minor		17
Summary:	Mozilla LDAP C SDK
Summary(pl):	Biblioteki Mozilla LDAP C SDK
Name:		mozldap
Version:	%{major}.%{minor}
Release:	0.2
License:	MPL/GPL/LGPL
Group:		Libraries
Source0:	ftp://ftp.mozilla.org/pub/mozilla.org/directory/c-sdk/releases/v%{major}.17/src/ldapcsdk-5.1.7.tar.gz
# Source0-md5:	66ddb43e984c0df67e21afb4dc6977b1
URL:		http://www.mozilla.org/directory/csdk.html
BuildRequires:	gawk
BuildRequires:	libstdc++-devel
BuildRequires:	nspr-devel >= %{nspr_evr}
BuildRequires:	nss-devel >= %{nss_evr}
BuildRequires:	perl-base
BuildRequires:	pkgconfig
#BuildRequires:	svrcore-devel >= %{svrcore_version}
Requires:	nspr >= %{nspr_evr}
Requires:	nss >= %{nss_evr}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The Mozilla LDAP C SDK is a set of libraries that allow applications
to communicate with LDAP directory servers. These libraries are
derived from the University of Michigan and Netscape LDAP libraries.
They use Mozilla NSPR and NSS for crypto.

%description -l pl
Mozilla LDAP C SDK to zestaw bibliotek pozwalaj±cych aplikacjom
komunikowaæ siê z serwerami us³ug katalogowych LDAP. Biblioteki te
wywodz± siê z bibliotek LDAP University of Michigan i Netscape.
Wykorzystuj± biblioteki Mozilla NSPR i NSS do kryptografii.

%package tools
Summary:	Tools for the Mozilla LDAP C SDK
Summary(pl):	Narzêdzia dla bibliotek Mozilla LDAP C SDK
Group:		Applications/System
Requires:	mozldap = %{version}-%{release}

%description tools
The mozldap-tools package provides the ldapsearch, ldapmodify, and
ldapdelete tools that use the Mozilla LDAP C SDK libraries.

%description tools -l pl
Ten pakiet dostarcza narzêdzia ldapsearch, ldapmodify i ldapdelete
wykorzystuj±ce biblioteki Mozilla LDAP C SDK.

%package devel
Summary:	Development files and examples for Mozilla LDAP C SDK
Summary(pl):	Pliki programistyczne i przyk³ady dla bibliotek Mozilla LDAP C SDK
Group:		Development/Libraries
Requires:	mozldap = %{version}-%{release}

%description devel
Header and other files for doing development with the Mozilla LDAP C
SDK.

%description devel -l pl
Pliki nag³ówkowe i inne do tworzenia oprogramowania z u¿yciem
bibliotek Mozilla LDAP C SDK

%package static
Summary:	Static Mozilla LDAP C SDK libraries
Summary(pl):	Statyczne biblioteki Mozilla LDAP C SDK
Group:		Development/Libraries
Requires:	mozldap-devel = %{version}-%{release}

%description static
Static Mozilla LDAP C SDK libraries.

%description static -l pl
Statyczne biblioteki Mozilla LDAP C SDK.

%prep
%setup -q -n mozilla

%build
# build local svrcore
%{__make} -C security/coreconf
%{__make} -C security/svrcore \
	CFLAGS="%{rpmcflags} -I. -I/usr/include/nspr -I/usr/include/nss"
# end svrcore

cd directory/c-sdk
%configure \
%ifarch %{x8664} ia64 ppc64 s390x
	--enable-64bit \
%endif
	--disable-debug \
	--enable-optimize \
	--with-nspr \
	--with-nspr-inc=%{_includedir}/nspr \
	--with-nspr-lib=%{_libdir} \
	--with-nss \
	--with-nss-inc=%{_includedir}/nss \
	--with-nss-lib=%{_libdir} \
	--with-svrcore \
	--with-svrcore-inc=$PWD/../../security/svrcore

%ifarch %{x8664} ppc64 ia64 s390x
USE_64=1
export USE_64
%endif

%{__make} \
	BUILDCLU=1 \
	HAVE_SVRCORE=1 \
	BUILD_OPT=1 \
	XCFLAGS="%{rpmcflags}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_includedir},%{_libdir}}/mozldap

install dist/lib/lib*ldap*.so $RPM_BUILD_ROOT%{_libdir}
install dist/bin/ldap* $RPM_BUILD_ROOT%{_libdir}/mozldap
install dist/public/ldap/*.h $RPM_BUILD_ROOT%{_includedir}/mozldap
install directory/c-sdk/ldap/libraries/lib*/lib*50.a $RPM_BUILD_ROOT%{_libdir}

install -d $RPM_BUILD_ROOT%{_datadir}/mozldap%{_sysconfdir}
cd directory/c-sdk/ldap
cp -r examples $RPM_BUILD_ROOT%{_datadir}/mozldap
install examples/xmplflt.conf $RPM_BUILD_ROOT%{_datadir}/mozldap%{_sysconfdir}
install libraries/libldap/*.conf $RPM_BUILD_ROOT%{_datadir}/mozldap%{_sysconfdir}
cd ..

install -d $RPM_BUILD_ROOT%{_pkgconfigdir}
sed mozldap.pc.in -e "
	s,%%libdir%%,%{_libdir},g
	s,%%prefix%%,%{_prefix},g
	s,%%exec_prefix%%,%{_prefix},g
	s,%%includedir%%,%{_includedir}/mozldap,g
	s,%%NSPR_VERSION%%,%{nspr_version},g
	s,%%NSS_VERSION%%,%{nss_version},g
	s,%%SVRCORE_VERSION%%,%{svrcore_version},g
	s,%%MOZLDAP_VERSION%%,%{version},g
" > $RPM_BUILD_ROOT%{_pkgconfigdir}/mozldap.pc

cd $RPM_BUILD_ROOT%{_libdir}
for file in libssldap50.so libprldap50.so libldap50.so; do
	mv $file $file.%{major}.%{minor}
	ln -s $file.%{major}.%{minor} $file.%{major}
	ln -s $file.%{major} $file
done

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so.%{major}.%{minor}
%attr(755,root,root) %{_libdir}/lib*.so.%{major}

%files tools
%defattr(644,root,root,755)
%dir %{_libdir}/mozldap
%attr(755,root,root) %{_libdir}/mozldap/ldap*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so
%{_includedir}/mozldap
%{_pkgconfigdir}/mozldap.pc
%{_datadir}/mozldap

%files static
%defattr(644,root,root,755)
%{_libdir}/lib*.a
