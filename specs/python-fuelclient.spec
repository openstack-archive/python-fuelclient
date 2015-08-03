%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%define name python-fuelclient
%{!?version: %define version 7.0.0}
%{!?release: %define release 1}

Summary:    Console utility for working with fuel rest api
Name:       %{name}
Version:    %{version}
Release:    %{release}
Source0:    %{name}-%{version}.tar.gz
License:    Apache
Group:      Development/Libraries
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix:     %{_prefix}

BuildArch:  noarch

BuildRequires: python-setuptools
BuildRequires: python-pbr > 0.7
BuildRequires: python-pbr < 1.0

Requires: python >= 2.6
Requires: python <= 2.7

Requires: python-argparse == 1.2.1

Requires: PyYAML >= 3.1.0
Requires: PyYAML <= 3.10

Requires: python-requests >= 2.1.0
Requires: python-requests <= 2.2.1

Requires: python-keystoneclient >= 1:0.10.0
Requires: python-keystoneclient <= 1:1.1.0

Requires: python-cliff >= 1.7.0
Requires: python-cliff <= 1.9.0

Requires: python-six >= 1.7.0
Requires: python-six <= 1.9.0

Requires: python-oslo-serialization >= 1.0.0
Requires: python-oslo-serialization <= 1.2.0

Requires: python-oslo-i18n >= 1.3.0
Requires: python-oslo-i18n <= 1.7.0

Requires: python-oslo-utils < 1:2.0.0

Requires: python-oslo-config < 1:2.0.0

%description
Summary: Console utility for working with fuel rest api

%prep
%setup -cq -n %{name}-%{version}

%build
cd %{_builddir}/%{name}-%{version} && python setup.py build

%install
rm -rf $RPM_BUILD_ROOT
cd %{_builddir}/%{name}-%{version} && python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{python2_sitelib}/*
%{_bindir}/*
