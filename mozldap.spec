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
Source0:	ftp://ftp.mozilla.org/pub/mozilla.org/directory/c-sdk/releases/v%{major}.17/src/ldapcsdk-%{version}.tar.gz
# Source0-md5	453341111111111
URL:		http://www.mozilla.org/directory/csdk.html
BuildRequires:	gawk
BuildRequires:	nspr-devel >= %{nspr_evr}
BuildRequires:	nss-devel >= %{nss_evr}
BuildRequires:	pkgconfig
BuildRequires:	svrcore-devel >= %{svrcore_version}
Requires:	nspr >= %{nspr_evr}
Requires:	nss >= %{nss_evr}
Provides:	mozldap
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The Mozilla LDAP C SDK is a set of libraries that allow applications
to communicate with LDAP directory servers. These libraries are
derived from the University of Michigan and Netscape LDAP libraries.
They use Mozilla NSPR and NSS for crypto.

%package tools
Summary:	Tools for the Mozilla LDAP C SDK
Group:		System
BuildRequires:	nspr-devel >= %{nspr_evr}
BuildRequires:	nss-devel >= %{nss_evr}
BuildRequires:	svrcore-devel >= %{svrcore_version}
Requires:	mozldap = %{version}-%{release}
Provides:	mozldap-tools

%description tools
The mozldap-tools package provides the ldapsearch, ldapmodify, and
ldapdelete tools that use the Mozilla LDAP C SDK libraries.

%package devel
Summary:	Development libraries and examples for Mozilla LDAP C SDK
Group:		Development/Libraries
BuildRequires:	nspr-devel >= %{nspr_evr}
BuildRequires:	nss-devel >= %{nss_evr}
Requires:	mozldap = %{version}-%{release}
Provides:	mozldap-devel

%description devel
Header and Library files for doing development with the Mozilla LDAP C
SDK

%prep
%setup -q

%build
%ifarch x86_64 ppc64 ia64 s390x
arg64="--enable-64bit"
%endif

%configure $arg64 \
		--with-nss		\
		--with-system-svrcore	\
		--enable-optimize	\
		--disable-debug

# Enable compiler optimizations and disable debugging code
BUILD_OPT=1
export BUILD_OPT

# Generate symbolic info for debuggers
XCFLAGS=%{rpmcflags}
export XCFLAGS

PKG_CONFIG_ALLOW_SYSTEM_LIBS=1
PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=1

export PKG_CONFIG_ALLOW_SYSTEM_LIBS
export PKG_CONFIG_ALLOW_SYSTEM_CFLAGS

%ifarch x86_64 ppc64 ia64 s390x
USE_64=1
export USE_64
%endif

cd mozilla/directory/c-sdk
%{__make} BUILDCLU=1 HAVE_SVRCORE=1 BUILD_OPT=1
%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_includedir}/mozldap
install -d $RPM_BUILD_ROOT%{_libdir}
install -d $RPM_BUILD_ROOT%{_libdir}/mozldap

# Copy the binary libraries we want
for file in libssldap50.so libprldap50.so libldap50.so; do
	install mozilla/dist/lib/$file $RPM_BUILD_ROOT%{_libdir}
done

# Copy the binaries we want
for file in ldapsearch ldapmodify ldapdelete ldapcmp ldapcompare; do
	install mozilla/dist/bin/$file $RPM_BUILD_ROOT%{_libdir}/mozldap
done

# Copy the include files
for file in mozilla/dist/public/ldap/*.h; do
	install -m 644 $file $RPM_BUILD_ROOT%{_includedir}/mozldap
done

# Copy the developer files
install -d $RPM_BUILD_ROOT%{_datadir}/mozldap
cp -r mozilla/directory/c-sdk/ldap/examples $RPM_BUILD_ROOT%{_datadir}/mozldap
install -d $RPM_BUILD_ROOT%{_datadir}/mozldap%{_sysconfdir}
install mozilla/directory/c-sdk/ldap/examples/xmplflt.conf $RPM_BUILD_ROOT%{_datadir}/mozldap%{_sysconfdir}
install mozilla/directory/c-sdk/ldap/libraries/libldap/ldaptemplates.conf $RPM_BUILD_ROOT%{_datadir}/mozldap%{_sysconfdir}
install mozilla/directory/c-sdk/ldap/libraries/libldap/ldapfilter.conf $RPM_BUILD_ROOT%{_datadir}/mozldap%{_sysconfdir}
install mozilla/directory/c-sdk/ldap/libraries/libldap/ldapsearchprefs.conf $RPM_BUILD_ROOT%{_datadir}/mozldap%{_sysconfdir}

# Rename the libraries and create the symlinks
cd $RPM_BUILD_ROOT%{_libdir}
for file in libssldap50.so libprldap50.so libldap50.so; do
	mv $file $file.%{major}.${minor}
	ln -s $file.%{major}.%{minor} $file.%{major}
	ln -s $file.%{major} $file
done

# Set up our package file
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


%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%{_libdir}/libssldap50.so
%{_libdir}/libprldap50.so
%{_libdir}/libldap50.so
%attr(755,root,root) %{_libdir}/libssldap50.so.%{major}
%attr(755,root,root) %{_libdir}/libprldap50.so.%{major}
%attr(755,root,root) %{_libdir}/libldap50.so.%{major}
%attr(755,root,root) %{_libdir}/libssldap50.so.%{major}.%{minor}
%attr(755,root,root) %{_libdir}/libprldap50.so.%{major}.%{minor}
%attr(755,root,root) %{_libdir}/libldap50.so.%{major}.%{minor}

%files tools
%defattr(644,root,root,755)
%{_libdir}/mozldap/ldapsearch
%{_libdir}/mozldap/ldapmodify
%{_libdir}/mozldap/ldapdelete
%{_libdir}/mozldap/ldapcmp
%{_libdir}/mozldap/ldapcompare

%files devel
%defattr(644,root,root,755)
%{_pkgconfigdir}/mozldap.pc
%{_includedir}/mozldap
%{_datadir}/mozldap
