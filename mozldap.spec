%define	nspr_version	4.6
%define	nspr_evr 1:%{nspr_version}
%define	nss_version	3.11
%define	nss_evr 1:%{nss_version}
%define	svrcore_version	4.0.1
%define	major		5
%define	minor		17
Summary:	Mozilla LDAP C SDK
Summary(pl):	Mozilla LDAP C SDK
Name:		mozldap
Version:	%{major}.%{minor}
Release:	0.1
License:	MPL/GPL/LGPL
Group:		System
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

%package tools
Summary:	Tools for the Mozilla LDAP C SDK
Group:		System
Requires:	mozldap = %{version}-%{release}

%description tools
The mozldap-tools package provides the ldapsearch, ldapmodify, and
ldapdelete tools that use the Mozilla LDAP C SDK libraries.

%package devel
Summary:	Development libraries and examples for Mozilla LDAP C SDK
Group:		Development/Libraries
Requires:	mozldap = %{version}-%{release}

%description devel
Header and Library files for doing development with the Mozilla LDAP C
SDK

%prep
%setup -q -n mozilla

%build
%ifarch x86_64 ppc64 ia64 s390x
arg64="--enable-64bit"
%endif

# build local svrcore
cd security/coreconf
%{__make}
cd ../../security/svrcore
%{__make} \
	CFLAGS="%{rpmcflags} -I. -I/usr/include/nspr -I/usr/include/nss"
cd ../..
# end svrcore

cd directory/c-sdk
%configure $arg64 \
	--with-nspr \
	--with-nspr-inc=%{_includedir}/nspr \
	--with-nspr-lib=%{_libdir} \
	--with-nss \
	--with-nss-inc=%{_includedir}/nss \
	--with-nss-lib=%{_libdir} \
	--with-svrcore \
	--with-svrcore-inc=$PWD/../../security/svrcore \
	--enable-optimize \
	--disable-debug

%ifarch x86_64 ppc64 ia64 s390x
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

install dist/lib/lib*ldap*.so* $RPM_BUILD_ROOT%{_libdir}
install dist/bin/ldap* $RPM_BUILD_ROOT%{_libdir}/mozldap
install dist/public/ldap/*.h $RPM_BUILD_ROOT%{_includedir}/mozldap

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

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so.%{major}.%{minor}
%attr(755,root,root) %{_libdir}/lib*.so.%{major}

%files tools
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/mozldap/ldap*

%files devel
%defattr(644,root,root,755)
%{_pkgconfigdir}/mozldap.pc
%{_includedir}/mozldap
%{_datadir}/mozldap
%{_libdir}/lib*.so
