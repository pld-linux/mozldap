#
# TODO:
# Conditional build:
%define	nspr_version	4.6
%define	nss_version	3.11
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
######		Unknown group!
Source0:	ftp://ftp.mozilla.org/pub/mozilla.org/directory/c-sdk/releases/v%{version}/src/ldapcsdk-%{version}.tar.gz
# Source0-md5	453341111111111
URL:		http://www.mozilla.org/directory/csdk.html
Requires:	nspr >= %{nspr_version}
Requires:	nss >= %{nss_version}
BuildRequires:	nspr-devel >= %{nspr_version}
BuildRequires:	nss-devel >= %{nss_version}
BuildRequires:	svrcore-devel >= %{svrcore_version}
BuildRequires:	pkgconfig
BuildRequires:	gawk
Provides:	mozldap
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The Mozilla LDAP C SDK is a set of libraries that allow applications
to communicate with LDAP directory servers. These libraries are
derived from the University of Michigan and Netscape LDAP libraries.
They use Mozilla NSPR and NSS for crypto.

%description -l pl
x

%package tools
Summary:	Tools for the Mozilla LDAP C SDK
Group:		System
######		Unknown group!
Requires:	mozldap = %{version}-%{release}
BuildRequires:	nspr-devel >= %{nspr_version}
BuildRequires:	nss-devel >= %{nss_version}
BuildRequires:	svrcore-devel >= %{svrcore_version}
Provides:	mozldap-tools

%description tools
The mozldap-tools package provides the ldapsearch, ldapmodify, and
ldapdelete tools that use the Mozilla LDAP C SDK libraries.

%description tools -l pl
x

%package devel
Summary:	Development libraries and examples for Mozilla LDAP C SDK
Group:		Development/Libraries
Requires:	mozldap = %{version}-%{release}
BuildRequires:	nspr-devel >= %{nspr_version}
BuildRequires:	nss-devel >= %{nss_version}
Provides:	mozldap-devel

%description devel
Header and Library files for doing development with the Mozilla LDAP C
SDK

%description devel -l pl
x

%prep

%setup -q
#-n
#cd mozilla/directory/c-sdk

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

# Set up our package file
%{__mkdir_p} $RPM_BUILD_ROOT/%{_libdir}/pkgconfig
%{__cat} mozldap.pc.in | sed -e "s,%%libdir%%,%{_libdir},g" \
                          -e "s,%%prefix%%,%{_prefix},g" \
                          -e "s,%%exec_prefix%%,%{_prefix},g" \
                          -e "s,%%includedir%%,%{_includedir}/mozldap,g" \
                          -e "s,%%NSPR_VERSION%%,%{nspr_version},g" \
                          -e "s,%%NSS_VERSION%%,%{nss_version},g" \
                          -e "s,%%SVRCORE_VERSION%%,%{svrcore_version},g" \
                          -e "s,%%MOZLDAP_VERSION%%,%{version},g" > \
                          $RPM_BUILD_ROOT/%{_libdir}/pkgconfig/mozldap.pc

%install
# There is no make install target so we'll do it ourselves.

rm -rf $RPM_BUILD_ROOT
%{__mkdir_p} $RPM_BUILD_ROOT/%{_includedir}/mozldap
%{__mkdir_p} $RPM_BUILD_ROOT/%{_libdir}
%{__mkdir_p} $RPM_BUILD_ROOT/%{_libdir}/mozldap

# Copy the binary libraries we want
for file in libssldap50.so libprldap50.so libldap50.so
do
  %{__install} -m 755 mozilla/dist/lib/$file $RPM_BUILD_ROOT/%{_libdir}
done

# Copy the binaries we want
for file in ldapsearch ldapmodify ldapdelete ldapcmp ldapcompare
do
  %{__install} -m 755 mozilla/dist/bin/$file $RPM_BUILD_ROOT/%{_libdir}/mozldap
done

# Copy the include files
for file in mozilla/dist/public/ldap/*.h
do
  %{__install} -m 644 $file $RPM_BUILD_ROOT/%{_includedir}/mozldap
done

# Copy the developer files
%{__mkdir_p} $RPM_BUILD_ROOT%{_datadir}/mozldap
cp -r mozilla/directory/c-sdk/ldap/examples $RPM_BUILD_ROOT%{_datadir}/mozldap
%{__mkdir_p} $RPM_BUILD_ROOT%{_datadir}/mozldap%{_sysconfdir}
%{__install} -m 644 mozilla/directory/c-sdk/ldap/examples/xmplflt.conf $RPM_BUILD_ROOT%{_datadir}/mozldap%{_sysconfdir}
%{__install} -m 644 mozilla/directory/c-sdk/ldap/libraries/libldap/ldaptemplates.conf $RPM_BUILD_ROOT%{_datadir}/mozldap%{_sysconfdir}
%{__install} -m 644 mozilla/directory/c-sdk/ldap/libraries/libldap/ldapfilter.conf $RPM_BUILD_ROOT%{_datadir}/mozldap%{_sysconfdir}
%{__install} -m 644 mozilla/directory/c-sdk/ldap/libraries/libldap/ldapsearchprefs.conf $RPM_BUILD_ROOT%{_datadir}/mozldap%{_sysconfdir}

# Rename the libraries and create the symlinks
cd $RPM_BUILD_ROOT/%{_libdir}
for file in libssldap50.so libprldap50.so libldap50.so
do
  mv $file $file.${major}.${minor}
  ln -s $file.${major}.%{minor} $file.${major}
  ln -s $file.${major} $file
done

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig >/dev/null 2>/dev/null

%postun
/sbin/ldconfig >/dev/null 2>/dev/null

%files
%defattr(644,root,root,755)
%{_libdir}/libssldap50.so
%{_libdir}/libprldap50.so
%{_libdir}/libldap50.so
%{_libdir}/libssldap50.so.%{major}
%{_libdir}/libprldap50.so.%{major}
%{_libdir}/libldap50.so.%{major}
%{_libdir}/libssldap50.so.%{major}.%{minor}
%{_libdir}/libprldap50.so.%{major}.%{minor}
%{_libdir}/libldap50.so.%{major}.%{minor}

%files tools
%defattr(644,root,root,755)
%{_libdir}/mozldap/ldapsearch
%{_libdir}/mozldap/ldapmodify
%{_libdir}/mozldap/ldapdelete
%{_libdir}/mozldap/ldapcmp
%{_libdir}/mozldap/ldapcompare

%files devel
%defattr(644,root,root,755)
%{_libdir}/pkgconfig/mozldap.pc
%{_includedir}/mozldap
%{_datadir}/mozldap
